# 同类型工具调用 benchmark 候选与 RPL 适配评估

检索日期：2026-07-30（Asia/Shanghai）

## 1. 筛选标准

这里的“相同类型”不是所有 agent benchmark，而是满足下列多数条件、能够作为
RPLBench 新 source adapter 输入的工具调用 benchmark：

1. 多步或多轮工具调用，而非单个函数的静态匹配；
2. 公开工具 schema、函数文档或可执行工具实现；
3. 有 gold/reference calls、milestone、state diff 或其他可审计 oracle；
4. 包含用户/业务状态，或者能从 gold arguments 构造确定性 profile；
5. 数据和许可证允许研究性改编，并能锁定版本与输入哈希。

## 2. 推荐顺序

若目标是给当前四源增加一个**独立第五源**，建议顺序为：

1. **ToolTalk**：最快能接入，且原生 profile 最完整；
2. **DICE-BENCH**：规模更大、gold call 结构最规整；
3. **ToolSandbox**：环境证据最强，但不存在唯一 canonical trajectory；
4. **Live API-Bench**：工具规模最大，但需要外部 BIRD 数据与 profile 构造；
5. **CRMArena-Pro**：隐私主题最贴近，但 adapter、环境和许可证成本最高。

$\tau^2$/$\tau^3$-bench 和 AppWorld-UL 很适合做现有来源的新版扩展，但分别与
$\tau$-bench、AppWorld 同源，不宜把它们表述成新的独立 benchmark 来源。

## 3. 候选对比

| 候选 | 公开规模与证据 | RPL 适配优势 | 主要阻碍 | 评级 |
|---|---|---|---|---|
| **ToolTalk** | 78 conversations、266 gold calls、28 tools/7 plugins；78/78 带 profile，39 条满足“至少 4 calls + 2 tools”；MIT；有模拟工具实现 | `user` 原生包含 name、email、phone、username、password、session token、verification code；call request/response 结构清晰，最接近当前 adapter 输入 | 总规模小；论文为 arXiv 预印本；部分对话中的敏感信息本身是任务必要内容，需要重新构造 recipient policy | **A，首选** |
| **DICE-BENCH** | ACL Findings 2025；1,607 samples、3,918 calls、122 个实际出现的 tools；365 条恰有 4 calls 且至少 2 tools；MIT | gold parameters、return values、tool docs 都公开；365 条天然生成 5-step（profile prelude + 4 calls）链；argument 中已有 email、phone、account、card、address、VIN 等事实 | 缺少统一用户 profile；主要是 off-policy 多方对话，工具返回是数据内记录而非完整状态环境 | **A，规模首选** |
| **ToolSandbox** | NAACL Findings 2025；源码中 129 个基础 ScenarioExtension（19 single-tool、54 multi-tool、28 multi-user-turn、28 insufficient-information），含工具实现、状态快照和 milestone DAG；Apple 开源许可 | 本地 contact/message/reminder/settings 数据库包含天然敏感信息；可执行、状态化、支持 arbitrary trajectory 和中间 milestone | benchmark 刻意允许多条正确轨迹，没有单一 gold call sequence；需要从 milestone 求一条规范 reference 或运行 trusted solver | **A，验证首选** |
| **Live API-Bench** | EACL 2026；11 databases、2,500+ tools、ground-truth API sequences、verified final answers；Apache-2.0 | sequence 和 tool specs 直接可解析，规模大，支持 SLOT/SEL/REST 与 MCP/Vakra 执行 | 依赖另行下载 BIRD 数据库；数据主体是 NL2SQL 转换，用户 profile 和用途边界较弱，需要较多隐私构造 | **A，规模扩展** |
| **CRMArena-Pro** | TMLR 2026；B2B/B2C 各 2,140 tasks，22 task types；每类 1,700 exact、200 fuzzy、240 privacy-rejection；32--48 personas；CC BY-NC 4.0 | CRM schema 原生包含姓名、邮箱、电话、账户、订单等业务信息；多轮交互和 confidentiality awareness 与 RPL 主题高度一致 | 发布任务主要给 query/answer/reward，不提供固定 gold API trajectory；需要运行 Salesforce sandbox 或生成并验证 reference；非商业许可 | **A，主题首选但工程重** |
| **$\tau^2$/$\tau^3$-bench** | 当前仓库含 airline、retail、telecom、banking/knowledge；telecom 2,285 tasks，其中 2,011 条 evaluation actions 不少于 4；MIT | user persona、known info、initial state、agent/user tools 和 env assertions 都很丰富 | 与现有 $\tau$-bench 同源；evaluation actions 包含双控制下的 user actions，不等于完整唯一 agent gold sequence；版本仍在快速修订 | **B，同源升级** |
| **CONFETTI** | ACL 2025；109 conversations、313 user turns、86 APIs；turn-level gold 与 dialog-act 标注 | 对 follow-up、目标修正、切换、歧义和 chained calls 覆盖好 | off-policy；无完整状态环境，规模较小，缺少原生 profile | **B** |
| **ToolHaystack** | 长期交互、多 session、noise；公开 dataset；样本含 API key、email、password 等跨 session 事实 | 很适合研究 memory/context 中的敏感信息被后续工具重用 | 核心标签通常是最终目标 API call，不是一个完整多工具任务 reference；仓库说明生成/evaluation 代码仍不完整 | **B，适合单独隐私实验** |
| **AppWorld-UL** | arXiv 2026；516 user-in-the-loop tasks，基于 AppWorld 的 9 apps | 可补足澄清、确认、不可行任务和用户知识边界 | 与 AppWorld 同源；截至检索日未定位独立公开仓库/数据发布 | **B，观察** |
| **DynamicMCPBench** | arXiv 2026；121 live servers、750 tasks、successful traces 与 effect checkpoints | effect-based oracle 比固定 tool list 更稳健，适合 MCP 研究 | 是动态生成框架而非稳定固定数据；server 状态变化使 source lock 和可复现改编困难 | **C** |
| **E-Bench** | arXiv 2026；323 state-changing tasks、3 个产品域、数据库 state-diff oracle | 合成环境、确定性状态差分、多步 state-changing 与当前方法匹配 | 发布时间很新，截至检索日未定位公开仓库或数据资产，暂不能做 adapter 审计 | **C，观察** |

## 4. 两个最值得立即尝试的数据审计结果

### ToolTalk

对官方仓库 78 个 JSON 对话做了结构统计：

- gold API calls 共 266 个，单对话 1--9 个，平均 3.41；
- 50 条至少使用两个工具；
- 39 条同时满足当前公共硬门槛：至少四次调用、至少两个不同工具；
- 78 条全部有用户 profile；profile key 包括 `email`、`name`、`password`、
  `phone`、`session_token`、`username` 和 `verification_code`；
- 一个现成样例包含 login、calendar、user lookup 和 email 共六个 gold calls，并同时
  带用户名、密码、日程、就医信息和收件人信息。

因此 ToolTalk adapter 可以直接读取 `conversation[*].apis[*].request` 作为 source calls，
读取顶层 `user` 为 profile seed，并把 API suite/implementation 用作 schema 与 recipient
分类依据。按现有门槛，理论上最多先得到 39 条 adapter 候选，再经过 carrier、敏感原子
和 forbidden-opportunity 检查。

### DICE-BENCH

对 Hugging Face 正式四个 round 文件做了结构统计：

- 1,607 个 samples、3,918 个 gold calls，单样本 1--4 个，平均 2.44；
- 365 条具有四个 calls，且四个 call 至少涉及两个不同工具；
- 数据中实际出现 122 个工具，官方 README 报告完整工具图有 124 个；
- gold arguments 中存在 email、phone、account number、credit card、address、license
  plate、VIN、username 等可用于 profile seed 的字段；
- `params_ret_val` 同时保存 function、parameters、return value 和 natural-language
  result，tool docs 位于公开的 `tool_docs.json`。

DICE 的主要适配工作是把跨 round 的 `params_ret_val` 顺序映射为 source calls，并从
gold arguments/returns 生成 entity profile。它缺少真实状态后端，因此 verification
应标为 source-reference replay，而不是 environment-executed。

## 5. 推荐实施路线

### 方案一：最快增加第五源

实现 `ToolTalkAdapter`：

1. 锁定 Microsoft ToolTalk commit、78 个 conversation JSON 和工具实现；
2. 解析顶层 user profile 与逐 turn API requests；
3. 保留 session token 等运行时依赖，但把认证工具划为 internal/auth recipient；
4. 先对 39 条门槛候选跑现有 privacy builder；
5. 通过模拟实现重放 ground calls，另记录对话级 response 是否与 source 一致。

### 方案二：优先扩大规模

实现 `DiceBenchAdapter`，预计可从 365 条四调用样本起步。它与当前 5-step 输出形式
天然吻合，但必须明确“固定返回值 replay”与“真实环境执行”的证据差异。

### 方案三：优先增强环境证据

实现 `ToolSandboxAdapter`，以 milestone DAG 而非单一 gold trajectory 为 oracle。
这需要先定义 trusted reference selection policy；否则不能声称某条选定调用序列是
上游唯一标准答案。

## 6. 规范来源

- ToolTalk：[paper](https://arxiv.org/abs/2311.10775)，[repository](https://github.com/microsoft/ToolTalk)
- DICE-BENCH：[ACL Anthology](https://aclanthology.org/2025.findings-acl.1375/)，[repository](https://github.com/snuhcc/DICE-Bench)
- ToolSandbox：[ACL Anthology](https://aclanthology.org/2025.findings-naacl.65/)，[repository](https://github.com/apple/ToolSandbox)
- Live API-Bench：[ACL Anthology](https://aclanthology.org/2026.eacl-long.143/)，[repository](https://github.com/IBM/live-api-bench)
- CRMArena-Pro：[TMLR/OpenReview](https://openreview.net/forum?id=EPlpe3Fx1x)，[repository](https://github.com/SalesforceAIResearch/CRMArena)
- $\tau^2$/$\tau^3$-bench：[paper](https://arxiv.org/abs/2506.07982)，[repository](https://github.com/sierra-research/tau2-bench)
- CONFETTI：[ACL Anthology](https://aclanthology.org/2025.acl-long.394/)
- ToolHaystack：[paper](https://arxiv.org/abs/2505.23662)，[repository](https://github.com/bwookwak/ToolHaystack)
- AppWorld-UL：[paper](https://arxiv.org/abs/2607.20536)
- DynamicMCPBench：[paper](https://arxiv.org/abs/2607.20531)
- E-Bench：[paper](https://arxiv.org/abs/2607.23722)
