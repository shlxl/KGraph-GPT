# GraphRAG-Extract-Best-Example-CoralWind-zh

## 用途
用于 GraphRAG 的“抽取→建图→检索/推理→答案+证据”端到端测试。覆盖多跳、别名、时间限定、否定/谣言澄清、冲突与消歧、事件与数量聚合等关键场景。

## 目录结构
- /corpus/*.txt             —— 原始语料（带句子编号 S1...）
- /gold/graph.jsonl         —— 标准答案图谱（四/五元组+限定词+证据定位）
- /gold/mentions.jsonl      —— 实体规范化与别名表
- /eval/queries.jsonl       —— 测试问题与期望答案（图模式、约束、证据要求）
- /eval/scoring.json        —— 评分规则（图匹配、数值误差、证据命中）
- /README.md                —— 使用说明（含最小复现实验命令）

## 最小复现实验
1. 将 /corpus 建入你的文本索引（句子为最小证据单元）。
2. 抽取器输出（head, relation, tail, qualifiers, evidence[{doc,sents}...]），并对齐 /gold/mentions.jsonl。
3. 构建知识图（支持 alias_of、part_of、nearby、negated:* 等关系）。
4. 对 /eval/queries.jsonl 运行检索/推理，返回“答案 + 命中文档/句子”。
5. 用 /gold/graph.jsonl 与 /eval/scoring.json 计算指标，并生成逐题报告（推荐输出差异与证据比对）。

## 设计亮点
- 别名与等同（海曦一期≡海曦一号；CR-2026）。
- 地理层级链（保护区→海域→城市→省→国家）。
- 同名消歧（两个“周启明”）。
- 否定与谣言澄清（鲸搁浅被权威否认）。
- 事件与因果区分（溢油由疏浚承包商引起，非风电项目）。
- 数值与聚合（资金累加到4.0亿元，带来源拆分）。

