# 四个源 benchmark 原文与相似工作检索

检索日期：2026-07-30（Asia/Shanghai）

## 1. 结论

四个源 benchmark 都有可正式引用的原始论文，并已把官方 PDF 下载到 `papers/`。其中
$\tau$-bench、BFCL、API-Bank 和 AppWorld 分别对应 ICLR 2025、ICML 2025、EMNLP
2023 和 ACL 2024。不要用 Gorilla 论文替代 BFCL 论文，也不要用当前仓库中的
$\tau^2$/$\tau^3$-bench 说明替代本项目所锁定的原始 $\tau$-bench 论文。

相似工作中，和 RPLBench 最接近的是 ToolPrivacyBench、AgentSCOPE 与 Privacy in
Action。TOP-Bench、POLAR-Bench、PrivacyAlign、AgentCIBench 和 PiSAs 也高度相关，
但分别研究组合推断、主动探测、人工规范对齐、GUI 跨应用披露和多用户数据 spill，
不能直接当作“同一个问题”。除四个源 benchmark 的正式会议论文外，2025--2026
年新增工作目前主要是 arXiv 预印本，写作时应明确其发表状态。

## 2. 四个 benchmark 的原始论文

| Benchmark | 应引用的原文 | 正式出处 | 规范链接 | 本地 PDF | 核验要点 |
|---|---|---|---|---|---|
| $\tau$-bench | Shunyu Yao, Noah Shinn, Pedram Razavi, Karthik Narasimhan. “$\tau$-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains.” | ICLR 2025, pp. 9965--10017 | [ICLR proceedings](https://proceedings.iclr.cc/paper_files/paper/2025/hash/1b126cc38b8638e07bef37e7b2bb72bf-Abstract-Conference.html); [arXiv:2406.12045](https://arxiv.org/abs/2406.12045) | `papers/tau_bench_iclr2025.pdf`（53 页） | 本项目使用旧版 $\tau$-bench 锁定数据；仓库现在推荐 $\tau^3$-bench，但不应静默更换来源。 |
| BFCL | Shishir G. Patil et al. “The Berkeley Function Calling Leaderboard (BFCL): From Tool Use to Agentic Evaluation of Large Language Models.” | ICML 2025, PMLR 267:48371--48392 | [PMLR](https://proceedings.mlr.press/v267/patil25a.html) | `papers/bfcl_icml2025.pdf`（22 页） | Gorilla (2023) 介绍模型和 APIBench，不是 BFCL leaderboard 的原始论文；当前使用的 BFCL v4 数据仍应以 BFCL 论文为主引用，版本细节再引仓库/变更日志。 |
| API-Bank | Minghao Li et al. “API-Bank: A Comprehensive Benchmark for Tool-Augmented LLMs.” | EMNLP 2023, pp. 3102--3116 | [ACL Anthology](https://aclanthology.org/2023.emnlp-main.187/), DOI: 10.18653/v1/2023.emnlp-main.187 | `papers/api_bank_emnlp2023.pdf`（15 页） | 论文同时描述可运行的 73-API 评测系统、314 个 tool-use dialogues 和训练数据；本项目锁定仓库中 214 个 Level-1 given-description 和 50 个 Level-2 ToolSearcher 结构化对话。 |
| AppWorld | Harsh Trivedi et al. “AppWorld: A Controllable World of Apps and People for Benchmarking Interactive Coding Agents.” | ACL 2024 Long Papers, pp. 16022--16076 | [ACL Anthology](https://aclanthology.org/2024.acl-long.850/), DOI: 10.18653/v1/2024.acl-long.850 | `papers/appworld_acl2024.pdf`（55 页） | ACL 2024 Best Resource Paper；论文中的完整 benchmark 为 750 tasks，本项目的 147 条是带可用 execution logs 的锁定子集，二者规模不能混写。 |

## 3. 最相似的工作（按与 RPLBench 的接近程度排序）

### A. 直接相关，建议进入正文相关工作

1. **ToolPrivacyBench** — [arXiv:2606.28061](https://arxiv.org/abs/2606.28061)，
   `papers/toolprivacybench_arxiv2606.28061.pdf`。它直接定义 purpose-bound、
   need-to-know 的多工具轨迹隐私审计，并从包括本项目四个来源在内的 benchmark
   改编 1,000 条任务。与 RPLBench 的区别是：它主要比较 agent 的任务成功与实际
   过度披露；RPLBench 当前更强调四源适配、reference-preserving 构造、参数级配对
   call 和可复现证据边界。

2. **AgentSCOPE: Evaluating Contextual Privacy Across Agentic Workflows** —
   [arXiv:2603.04902](https://arxiv.org/abs/2603.04902)，
   `papers/agentscope_arxiv2603.04902.pdf`。它用 Privacy Flow Graph 对 agent pipeline
   的每个边界做 contextual-integrity 标注，覆盖 62 个多工具场景和 8 个监管领域。
   它与 RPLBench 都反对只看最终输出；区别是 AgentSCOPE 同时审计 agent query、
   tool response 等各类 flow，而 RPLBench 聚焦发送给工具的冗余敏感参数。

3. **Privacy in Action** — [arXiv:2509.17488](https://arxiv.org/abs/2509.17488)，
   `papers/privacy_in_action_arxiv2509.17488.pdf`。该工作把静态 PrivacyLens 改造成
   动态 MCP/A2A 环境（PrivacyLens-Live），并提出 PrivacyChecker mitigation。
   与 RPLBench 的交点是动态 agent 行为与中间协议消息；区别是它以 contextual
   integrity 和防护器为中心，而不是以源 benchmark 的 gold calls 与 optional
   parameter 差分为中心。

4. **Agent Tools Orchestration Leaks More / TOP-Bench** —
   [arXiv:2512.16310](https://arxiv.org/abs/2512.16310)，
   `papers/top_bench_arxiv2512.16310.pdf`。TOP-R 指多个单独不敏感的工具返回经组合
   推理后产生敏感结论。它评估的是 final-response semantic disclosure，泄露机制是
   compositional inference；RPL 是把已经存在的敏感原子直接多传给不需要它的工具。
   两者很适合在论文中并列，说明“直接过度披露”和“组合推断泄露”是不同问题。

5. **POLAR-Bench** — [arXiv:2605.19127](https://arxiv.org/abs/2605.19127)，
   `papers/polar_bench_arxiv2605.19127.pdf`。它让可信 agent 携带显式隐私政策，与主动
   探测隐私的第三方模型交互，评估 privacy--utility trade-off。其 adversarial probing
   威胁模型不同于 RPLBench 的正常任务、非对抗性冗余披露。

6. **PrivacyAlign** — [arXiv:2606.21710](https://arxiv.org/abs/2606.21710)，
   `papers/privacyalign_arxiv2606.21710.pdf`。它收集 599 名标注者对 1,350 个 agent
   隐私场景的 3,516 条详细标注，并用于 judge 与 reward alignment。它适合支持
   RPLBench 的人工授权复核设计，但 human norm judgment 不能替代确定性的 gold-atom
   与 recipient-policy 审计。

### B. 邻近工作，建议简短对照或放补充材料

- **AgentCIBench / Capable but Careless** — [arXiv:2606.23189](https://arxiv.org/abs/2606.23189)，
  `papers/agentcibench_arxiv2606.23189.pdf`。研究 computer-use agent 的 visual
  co-location、任务歧义过度披露和 recipient misalignment；观察点是 GUI/跨应用动作。
- **PiSAs** — [arXiv:2607.05318](https://arxiv.org/abs/2607.05318)，
  `papers/pisas_arxiv2607.05318.pdf`。研究共享多用户 agent 中经输出、agent 间通信和
  memory 发生的跨用户数据 spill。
- **AgentSecBench** — [arXiv:2605.26269](https://arxiv.org/abs/2605.26269)，
  `papers/agentsecbench_arxiv2605.26269.pdf`。以 noninterference、provenance projection
  和 channel closure 组织提示注入、检索保密与工具能力完整性，属于安全机制视角。
- **Minim** — [arXiv:2606.13949](https://arxiv.org/abs/2606.13949)，
  `papers/minim_arxiv2606.13949.pdf`。在 UI observation 离开设备前建立 task-conditioned
  minimal view，是“发送前数据最小化”的防护工作，而非 benchmark 构建工作。
- **PrivacyLens**（NeurIPS 2024）与 **CONFAIDE**（ICLR 2024）仍应保留：前者强调
  privacy judgment 与 action 的差距，后者把 contextual integrity 用于 LLM 信息分享
  判断。它们是理论和行为评测前史，但不审计完整多工具轨迹。
- **TRAP** — [arXiv:2606.18996](https://arxiv.org/abs/2606.18996)：任务必须使用隐私字段，
  同时抵抗自然语言主动抽取；重点是 task-completion 与 extraction resistance 的张力。
- **SlotGuard** — [arXiv:2607.17147](https://arxiv.org/abs/2607.17147)：保护发送到远程模型
  provider 的 agent transcript，处理路径、凭据和跨轮引用；接收方边界与工具 API 不同。

## 4. 建议写进论文的定位句

可在“背景与相关工作”中加入如下段落，再按最终篇幅压缩：

> 近期 agent 隐私评测开始从最终回复扩展到执行轨迹与系统边界。ToolPrivacyBench
> 以 purpose-bound policy 审计多工具调用及后端日志；AgentSCOPE 将 agent pipeline
> 分解为逐边界 Privacy Flow Graph；Privacy in Action 则在 MCP/A2A 动态环境中评估
> 隐私规范与 mitigation。与这些工作相比，本文不提出覆盖全部信息流的通用隐私
> benchmark，而聚焦可复现的数据构建问题：在保持四个上游 benchmark 的 reference
> calls 不变时，构造仅增加冗余敏感 optional 参数的配对调用，并公开 source replay、
> recipient policy 与验证证据。其他相邻基准分别研究跨工具组合推断（TOP-Bench）、
> 主动第三方探测（POLAR-Bench）、多用户数据 spill（PiSAs）和 GUI 跨应用披露
> （AgentCIBench），其泄露机制与本文的参数级非必要直接披露不同。

## 5. 检索与核验方法

- 原文：优先使用 ICLR Proceedings、PMLR 和 ACL Anthology 的正式 landing page、PDF
  和 BibTeX；arXiv 仅补充预印本编号。
- 相似工作：通过 arXiv API 组合检索 `LLM agents + privacy`、`tool use + privacy`、
  `contextual integrity + agent`、`privacy over-disclosure`、`data minimization` 等查询，
  再逐篇核对标题、作者、摘要、发布日期和 primary category。
- 纳入标准：必须明确涉及 agent 行动、工具/协议/GUI/多用户信息流或 purpose-bound
  privacy；仅讨论训练数据记忆、membership inference 或普通聊天隐私的工作未列入核心表。
- 发表状态：四个源 benchmark 为正式同行评审会议论文；上面新增的 2025--2026 工作
  截至检索日主要为 arXiv 预印本，引用时不要写成已被会议接收，除非后续另行核实。
