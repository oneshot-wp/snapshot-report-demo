# 内容数据周报：小范围付费试做

已有内容平台的授权导出，却每周都要重复合并、删重和算数？可以先从一份固定格式的周报开始。

**参考服务价：人民币599元。** 这是下述范围的售前价格说明；收到脱敏样本、确认适配性后另发正式报价及交付安排。没有自动下单或付款入口。代码样品可免费查看，服务费对应配置、核对与交付支持。

## 这个范围包含什么

- 一种已符合本仓库字段定义的JSON数组输入；原始CSV、Excel、字段转换另行评估。
- 约定一个发布周，按平台与内容ID保留最新累计快照，生成现有Markdown报告及可追溯JSON。
- 在双方确认的Python运行环境中交付源码、运行命令、字段说明，以及样本核对结果。
- 一轮对约定字段或报告文字的修正。新增数据源、统计指标和报表属于新范围，须先重新确认。

数据量、机器环境和交付日期在正式报价前确认，不承诺未测过的吞吐量。你可以选择仅看免费样品，或确认适合后再讨论服务。

## 先看实际输出

- [合成数据报告](example-report.md)
- [对应结构化输出](example-report.json)
- [运行与测试方法](README.md)

样品使用5行合成数据，有1条重复快照。报告指定发布周纳入3条内容。它不是客户案例，也没有证明任何客户收入或内容增长。

## 怎样验收

先用双方确认的脱敏样本，写清每个指标的预期值。验收时核对重复快照保留规则、日期边界、缺失指标、汇总结果及每条来源。若输入结构或统计口径不适用，先说明，不把当前样品当成已适配完成品。

当前不包括账号登录、平台抓取、API接入、Excel图表、图形后台、自动发布或定时运行。开发采用AI辅助方式，按输入、输出和可复现测试核对。

## 免费询问入口

可在本仓库 [Issues](https://github.com/oneshot-wp/snapshot-report-demo/issues) 提交标题为“周报需求询问”的问题，只写：

1. 数据来源类型、现有文件格式与大致行数；
2. 目前每周要手工做哪些操作；
3. 想得到的报告和希望交付的日期。

**Issues是公开页面。不要提交真实客户数据、账号、联系方式、密钥或未公开业务文件。** 首轮仅讨论需求；脱敏样本的传输方式和授权在后续单独确认。正式范围、验收与付款安排均须双方确认，询问本身不产生费用。

---

## English summary

A small, AI-assisted local reporting service for authorized content-data exports. Indicative service price: CNY599 for one agreed input schema and the existing report template, subject to a separate written scope and quote. The sample source is free to inspect; the service covers configuration, verification and handoff support.

This repository currently reads a standardized JSON array and produces Markdown plus traceable JSON. It does not connect to platforms, scrape accounts, process Excel natively or publish content. The examples are synthetic, with no client-results claims.

For a free scope enquiry, open an issue describing only file format, approximate size and desired report. Issues are public: do not post personal, customer, account or confidential data. No payment is accepted through this repository.
