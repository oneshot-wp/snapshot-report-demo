"""Local reporting prototype; input metrics are cumulative snapshots."""
import argparse
from datetime import date, datetime, timedelta, timezone
import json
from pathlib import Path

METRICS = ('views', 'likes', 'comments', 'shares')
SHANGHAI = timezone(timedelta(hours=8))


def timestamp(value):
    try:
        result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except (AttributeError, TypeError, ValueError) as exc:
        raise ValueError('Timestamp must be ISO 8601 with timezone') from exc
    if result.tzinfo is None:
        raise ValueError('Timestamp needs a timezone')
    return result


def build_report(rows, week):
    start = date.fromisoformat(week)
    end = start + timedelta(days=7)
    if not isinstance(rows, list):
        raise ValueError('Input must be a JSON array')
    latest = {}
    for source in rows:
        if not isinstance(source, dict):
            raise ValueError('Each record must be an object')
        for field in ('platform', 'post_id'):
            if not isinstance(source.get(field), str) or not source[field].strip():
                raise ValueError(f'{field} must be a nonempty string')
        published = timestamp(source.get('published_at'))
        observed = timestamp(source.get('observed_at'))
        if observed < published:
            raise ValueError('Observation precedes publication')
        row = {field: source[field] for field in ('platform', 'post_id')}
        row.update(published_at=published.isoformat(), observed_at=observed.isoformat())
        for metric in METRICS:
            value = source.get(metric)
            if value is not None and (type(value) is not int or value < 0):
                raise ValueError(f'{metric} must be a nonnegative integer or null')
            row[metric] = value
        key = (row['platform'], row['post_id'])
        if key in latest:
            old = latest[key]
            if timestamp(old['published_at']) != published:
                raise ValueError('Conflicting publication date for the same post')
            previous = timestamp(old['observed_at'])
            if observed == previous and any(old[m] != row[m] for m in METRICS):
                raise ValueError('Conflicting metrics for identical snapshot time')
            if observed <= previous:
                continue
        latest[key] = row
    records = [row for row in latest.values()
               if start <= timestamp(row['published_at']).astimezone(SHANGHAI).date() < end]
    records.sort(key=lambda r: (r['platform'], r['post_id']))
    platforms = []
    for name in sorted({row['platform'] for row in records}):
        group = [row for row in records if row['platform'] == name]
        result = {'platform': name, 'posts': len(group), 'metric_coverage': {}}
        for metric in METRICS:
            values = [row[metric] for row in group if row[metric] is not None]
            result['metric_coverage'][metric] = f'{len(values)}/{len(group)}'
            result[metric] = sum(values) if len(values) == len(group) else None
        complete = all(result[m] is not None for m in METRICS)
        result['interaction_rate'] = (
            sum(result[m] for m in METRICS[1:]) / result['views']
            if complete and result['views'] else None)
        platforms.append(result)
    return {'week_start': start.isoformat(), 'week_end_exclusive': end.isoformat(),
            'timezone': 'UTC+08:00', 'basis': 'publication cohort, latest cumulative snapshots',
            'input_rows': len(rows), 'duplicate_snapshots': len(rows) - len(latest),
            'included_posts': len(records), 'platforms': platforms, 'records': records}


def markdown(report):
    lines = ['# 内容表现周报｜本地演示', '',
             f"发布区间：{report['week_start']} 至 {report['week_end_exclusive']}（不含结束日，北京时间）。", '',
             '口径：本区间发布内容的最新累计快照，不是本周互动增量。不同发布时间的曝光时长不同，不能据此推断内容优劣。',
             '不同平台分开展示；缺失指标不填零。互动率＝（点赞＋评论＋分享）/浏览，任一指标缺失时不计算。', '',
             f"输入{report['input_rows']}行；重复快照{report['duplicate_snapshots']}行；纳入内容{report['included_posts']}条。", '',
             '| 平台 | 内容数 | 浏览 | 点赞 | 评论 | 分享 | 互动率 |',
             '|---|---:|---:|---:|---:|---:|---:|']
    def cell(value):
        return '缺失' if value is None else str(value)
    for group in report['platforms']:
        name = group['platform'].replace('|', '\\|').replace('\n', ' ').replace('\r', ' ')
        rate = group['interaction_rate']
        values = [name, str(group['posts'])] + [cell(group[m]) for m in METRICS]
        values.append('不可计算' if rate is None else f'{rate:.2%}')
        lines.append('| ' + ' | '.join(values) + ' |')
    lines += ['', '## 核查事项', '',
              '输出JSON保留每条内容ID、发布时间、观测时间和指标，可逐条复查。',
              '先补齐缺失数据，再比较同平台、相近曝光时长的内容；演示不自动生成未经证实的增长结论。']
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--week', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        rows = json.loads(args.input.read_text(encoding='utf-8-sig'))
        report = build_report(rows, args.week)
        text = markdown(report)
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(2, f'Invalid input: {exc}\n')
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (args.output / 'report.md').write_text(text, encoding='utf-8')
    print(f"Generated report: {report['included_posts']} posts, {len(report['platforms'])} platforms")


if __name__ == '__main__':
    main()
