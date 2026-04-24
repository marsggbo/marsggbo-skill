# hexin — answers

Total: 126


---

## 个性化llm的memory方向怎么样?

`link: https://www.zhihu.com/question/1957619016504967717/answer/2023430823353788148 · created: 1775203501`


你有没有想过，当你让 ChatGPT "记住你喜欢简洁的回答"，或者让代码助手"别忘了这个项目用的是 TypeScript"时，这些信息究竟去了哪里？

这个问题比表面看起来复杂得多。LLM 本身是"无状态"的——每次对话都是从零开始，模型并没有一个专门的"记忆区"来存放你的偏好。那些看似被"记住"的信息，可能被塞进了 prompt，可能缓存在某个向量数据库里，也可能通过微调烧进了模型参数。每种方式都有自己的代价和局限。

来自港科大、新加坡 A\*STAR 等机构的研究团队最近发表了一篇综述，试图回答一个更根本的问题：**这些看似迥异的"记忆"机制，背后有没有统一的设计逻辑？** 他们的答案是肯定的，并且提出了一个简洁的框架来理解整个领域。

**论文链接**：[LLM Agent Memory: A Survey from a Unified Representation–Management Perspective](https://link.zhihu.com/?target=https%3A//doi.org/10.20944/preprints202603.0359.v1)

---

## 1. 长上下文不等于好记忆

先澄清一个常见的误解。

GPT-4 Turbo 支持 128K token，Claude 3 号称能处理 200K，Gemini 1.5 Pro 更是喊出了百万 token 的口号。看起来记忆问题已经被"暴力解决"了——上下文窗口足够大，把所有历史对话都塞进去不就行了？

事情没那么简单。研究者们发现了一个有趣的现象叫"lost in the middle"：当你把关键信息埋在长文本的中间位置时，模型往往会"视而不见"。注意力机制理论上能看到所有 token，但实际上它对头尾更敏感，中间的信息容易被稀释。更实际的问题是成本——注意力计算的复杂度是 ![O(n^2)](https://www.zhihu.com/equation?tex=O%28n%5E2%29)，上下文翻倍意味着计算量翻四倍，这在生产环境中是不可接受的。

所以，**记忆的本质不是"看到更多"，而是"记住关键"** 。这篇综述的出发点正在于此：与其关注上下文能装多少 token，不如关注信息如何被选择性地保留、组织和检索。

---

## 2. 一个统一的视角

![](https://picx.zhimg.com/v2-a6140841cf4d4258cda569b61c8082eb_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='3790' height='2098'></svg>)

综述的核心贡献是提出了一个理解 LLM 记忆的统一框架。思路其实很直观：任何记忆系统都要回答两个问题——**信息存在哪里？如何操作它？**

第一个问题关于"表示"。LLM 的记忆可以存在三个地方：直接写在 prompt 里的自然语言、推理过程中缓存的中间向量（典型如 KV Cache）、以及烧录在模型权重里的参数化知识。三者的特性截然不同：

| 表示形式 | 存储位置 | 核心优势 | 主要局限 |
| --- | --- | --- | --- |
| 自然语言 Token | Prompt 上下文 | 显式、可编辑、无需训练 | 占用上下文窗口，查询效率受限 |
| 中间表示 (Latent) | KV Cache / 向量库 | 高效、运行时可修改 | 容量有限，仅会话内有效 |
| 模型参数 | 权重 | 持久化、无检索开销 | 修改困难，易遗忘旧知识 |

第二个问题关于"管理"。无论选择哪种表示，记忆系统都需要处理三个操作：构建（存什么、怎么组织）、更新（如何维护和淘汰）、查询（如何找到相关信息）。有意思的是，这三个操作在不同表示下的难点完全不同。

论文用一个决策矩阵揭示了这种差异：

| 记忆表示 | 适合的知识类型 | 核心瓶颈 | 设计重点 |
| --- | --- | --- | --- |
| Token | 短期情景 + 语义知识 | 查询 | 如何在有限上下文中选出高信号子集 |
| Latent | 短期情景记忆 | 更新 | 固定容量下的缓存调度与压缩 |
| Parameter | 长期程序 + 语义知识 | 写入 | 避免灾难性遗忘和知识冲突 |

这个框架的价值在于，它让我们能用同一套语言比较表面上毫不相关的技术——RAG 系统和 KV Cache 压缩算法，看起来是两个领域，但本质上都在解决"有限容量下的记忆管理"问题，只是一个管理文本片段，一个管理向量。

![](https://pic1.zhimg.com/v2-dc168812ce25455426e93b1c276c7b31_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2756' height='2018'></svg>)

---

### 3.1 Token 作为记忆：显式但脆弱

最直观的做法是把记忆直接写成自然语言，塞进 prompt。这就是 RAG（检索增强生成）的基本思路：维护一个外部知识库，需要时检索相关片段注入上下文。

RAG 的精妙之处在于它把"记忆"问题转化成了"检索"问题。检索是信息领域研究了几十年的老问题，有成熟的工具和方法论——向量数据库、倒排索引、BM25、语义嵌入——这些都可以直接拿来用。

![](https://picx.zhimg.com/v2-1d4b494c112d170923cef6e37cbdb431_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2718' height='1858'></svg>)

但 RAG 的挑战也很明显：**检索的是片段，而非完整的知识**。想象你在问一个跨越多个文档的复杂问题，答案需要综合三个段落的信息，而每个段落单独看都不像是"相关"的——这时候简单的相似度检索就会失效。

研究者们为此发展出各种技巧。HyDE（Hypothetical Document Embeddings）让模型先"假想"一个答案，再用这个假想答案去检索真实文档——有点像"先猜后验"。Step-Back Prompting 则是反过来，把具体问题抽象成更通用的形式，检索更宽泛的背景知识后再回答原问题。这些方法的共同点是：**不直接检索，而是先改造查询**。

另一条路是把记忆组织成更结构化的形式。HippoRAG 借鉴了人脑海马体的工作方式，用知识图谱连接记忆片段，支持沿着关系边进行多跳推理。GraphReader 则是让 Agent 在图结构上"游走"，边走边决定下一步往哪个方向探索。这类方法的代价是构建和维护结构的额外开销，但在需要复杂推理的场景下回报也很可观。

对于多轮对话的 Agent，记忆管理变得更复杂。不仅要存储信息，还要随着交互演化。A-MEM 模仿 Zettelkasten 笔记法，让记忆以互联的"笔记"形式增长，新记忆自动链接到相关的旧记忆。Reflexion 则走得更远：Agent 不仅记录发生了什么，还会反思"为什么失败"，把经验教训提炼成可复用的策略。这已经不是简单的存储，而是接近人类的"经验学习"了。

---

### 3.2 KV Cache：被低估的运行时记忆

如果你用过大模型推理框架，对 KV Cache 一定不陌生。它的原理很简单：Transformer 在自回归生成时，每个新 token 都需要和之前所有 token 做注意力计算。如果每次都从头算，复杂度是 ![O(n^2)](https://www.zhihu.com/equation?tex=O%28n%5E2%29)；但如果把之前 token 的 Key 和 Value 向量缓存起来，新 token 只需要算自己的部分，复杂度就降到了 ![O(n)](https://www.zhihu.com/equation?tex=O%28n%29)。

这本来是个纯粹的工程优化，但如果从记忆的角度看，KV Cache 其实是**模型对上下文的隐式编码**。它不是原始文本，而是文本经过注意力机制"消化"后的中间表示，某种程度上比原始 token 更"接近"模型的内部理解。

问题在于，KV Cache 的大小随序列长度线性增长，而 GPU 显存是有限的。当上下文达到几万 token，缓存就会成为瓶颈。于是就有了各种"压缩"策略。

![](https://picx.zhimg.com/v2-5c78987ab9d5c00fe2d0fcdb24fffcf9_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2696' height='2272'></svg>)

最直接的思路是**淘汰不重要的 token**。StreamingLLM 发现了一个有趣的现象：注意力分数往往集中在序列开头的几个 token 上（即使它们在语义上并不重要），这被称为"attention sink"。基于这个发现，它只保留开头几个 token 和最近的滑动窗口，其余全部丢弃，就能支持无限长的流式生成。H2O 则更精细，它追踪每个 token 的累积注意力分数，只保留"heavy hitter"——那些真正被频繁关注的 token。

另一条路是**压缩而非丢弃**。MiniCache 发现相邻层的 KV 向量高度相似，可以跨层共享；ChunkKV 则是把语义相近的 token 合并成一个"超级 token"，保留语义信息的同时减少条目数量。还有量化的路线：KIVI 用非对称 2-bit 量化，几乎不损失精度的情况下把缓存压缩到原来的八分之一。

这些方法和操作系统里的内存管理高度相似——淘汰策略像 LRU/LFU，压缩像内存去重，分层缓存像虚拟内存。这不是偶然，而是因为底层问题是同构的：**有限容量下的高效数据管理**。

---

### 3.3 参数作为记忆：持久但危险

最"持久"的记忆是直接写进模型权重。预训练过程本质上就是在做这件事：把海量文本中的知识压缩成几十亿个浮点数。

参数化记忆的好处是一劳永逸——不需要检索，不需要缓存，知识就在那里，推理时自动激活。研究表明，Transformer 的 FFN 层可以被理解为一个巨大的 key-value 存储，特定的神经元甚至对应特定的事实知识。

![](https://picx.zhimg.com/v2-5fc180f3071d1f8d472c7ab3b03dbe08_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2010' height='1850'></svg>)

但代价也很明显：**参数一旦写入，就很难修改**。这不仅是工程问题，更是科学问题。"灾难性遗忘"是持续学习领域的老大难：微调模型学习新知识时，旧知识会被覆盖。EWC 等方法通过正则化约束"重要参数"的变化来缓解这个问题，但远没有根本解决。

模型编辑（Model Editing）是另一种思路：不是全局微调，而是**精准修改特定事实**。想象你要把模型对"埃菲尔铁塔在哪个城市"的回答从巴黎改成伦敦（纯假设），模型编辑试图找到负责这个事实的神经元并定点修改。ROME、MEMIT 等方法在这条路上取得了进展，但问题是：事实在模型里并不是孤立存储的，修改一个事实可能连带影响相关知识的一致性。

WISE 提出了一个有趣的架构：维护两套记忆——稳定的"预训练知识"和可编辑的"后天知识"，查询时用路由机制决定访问哪一套。这有点像人脑的长期记忆和工作记忆的分离，但在工程上如何高效实现还是开放问题。

模型合并（Model Merging）则是从另一个角度利用参数记忆：把多个微调模型的权重"融合"成一个，期望继承各自的能力。最简单的做法是参数平均，但这往往导致性能下降——不同任务的知识可能编码在同一组参数上，直接平均会相互干扰。TIES、DARE 等方法通过稀疏化和冲突解决来缓解这个问题，但对任务兼容性仍然敏感。

---

## 4. 没有银弹，只有权衡

把三种记忆表示放在一起看，会发现一个有趣的规律：**选择不同的表示，本质上是在选择不同的瓶颈**。

![](https://picx.zhimg.com/v2-b60afea3b8b3c87e3c9ce074eed22f7c_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2724' height='782'></svg>)

Token 记忆的瓶颈在查询。上下文窗口就那么大，你不可能把所有历史都塞进去，必须选择"放什么"。这个选择做好了，模型能看到正确的信息；做不好，关键证据就被遗漏了。

KV Cache 的瓶颈在更新。显存就那么多，你必须决定"留什么、扔什么"。淘汰策略太激进会丢失重要上下文，太保守会撑爆缓存。

参数记忆的瓶颈在写入。权重就那么一份，你必须确保"新知识进去的同时旧知识不能出来"。做好了是增量学习，做不好就是灾难性遗忘。

这意味着，没有一种记忆表示能通吃所有场景。实用的系统需要**分层组合**：用参数存储长期稳定的知识和技能，用 KV Cache 维持会话内的连续性，用 Token 引入即时的外部证据。统一的管理接口（构建-更新-查询）则是粘合这些层次的"控制平面"。

---

## 5. 接下来会去哪里

综述最后讨论了几个开放方向，我觉得其中两个特别值得关注。

第一是**训练和推理的边界正在模糊**。传统上，训练是离线的、批量的；推理是在线的、即时的。但在长期运行的 Agent 场景下，这个区分不再清晰——Agent 需要在运行中学习新知识、适应新用户，同时不能遗忘已有能力。这要求一种新的系统架构，能在推理时高效地做轻量级参数更新，而这正是目前的框架（无论是 PyTorch 还是各种推理引擎）不擅长的。

第二是**跨领域的方法迁移**。操作系统研究内存管理几十年了，数据库研究查询优化也几十年了，里面有大量成熟的技术——分页、淘汰策略、索引结构、执行计划——可以借鉴到 LLM 记忆系统。事实上已经有人在做这件事：vLLM 的 PagedAttention 就是把操作系统的分页思想用到了 KV Cache 管理上。但这只是冰山一角，还有大量的经典方法等待被重新发现。

---

## 写在最后

这篇综述做的事情，不是简单地列举"有哪些方法"，而是试图回答"为什么会有这些方法、它们在解决什么共同的问题"。统一的"表示-管理"框架虽然简洁，但确实能把一堆看似不相关的工作串联起来，让人看到全局的图景。

如果你在做 LLM 应用，这个框架或许能帮你更清晰地思考记忆系统的设计选择：你的场景需要什么类型的记忆？瓶颈在哪个环节？有没有可以借鉴的现有方案？

如果你在做 LLM 系统研究，这篇综述的参考文献列表本身就很有价值——几乎涵盖了 2023-2025 年记忆相关工作的全貌。


---

## MoE研究方向?

`link: https://www.zhihu.com/question/1896217990099362659/answer/2010734591607071939 · created: 1772176484`


最近我们针对稀疏MoE大模型推理优化的工作 ExpertFlow 被顶会DAC 2026接收了，今天想和大家聊聊我们做这个工作的初衷、踩过的坑，以及它到底解决了MoE落地里的什么真问题。

先交代下背景：现在MoE模型火是真的火，Mixtral、DeepSeek-MoE、Qwen-MoE这些开源模型，用远低于稠密大模型的单token计算量，就能跑出差不多的效果，堪称大模型规模化的“性价比之王”。但我们自己跑模型的时候，却结结实实踩了个大坑：

就拿最经典的Mixtral-8×7B来说，全量加载模型权重就要96GB显存，单张A100 80G直接OOM。但离谱的是，这个模型46.7B参数里，有45.1B都是专家模块，单轮输入里，每个token只会激活其中2个专家——**90%以上的参数全程闲着，却把显存占得满满当当**。

这也是整个行业做MoE推理的核心矛盾：MoE的优势是“稀疏激活”，但落地时却被“全量加载”的内存瓶颈卡死了。

## 先说说现有方案解决不了的三个痛点

行业里其实早有思路：把不用的专家放到CPU内存里，只把当前要用的加载到GPU，也就是“专家卸载”。但我们把现有方案都跑了一遍，发现三个绕不开的硬伤，也是我们最终要解决的核心问题：

第一个是**预测像“开盲盒”**。要提前加载专家，就得先预测token会激活哪些专家。之前的方案要么是启发式的，靠统计规律瞎蒙，准度低到离谱；要么是逐层预测的，走一步看一步，上一层算完才知道下一层要找哪个专家，根本没法提前做全局调度，预取的优势完全发挥不出来。

第二个是**专家“空跑”太严重**。解码阶段最头疼的，就是token路由太碎了。经常出现一个批次里，每个token都要找不同的专家，最后一个批次激活了所有专家，但每个专家只处理1个token。GPU的专家算子，处理1个token和处理4个token的开销几乎没差，就像大货车每次只拉一个快递，油费都赚不回来，算力利用率低到离谱。

第三个是**缓存“该留的不留，该踢的不踢”**。主流的LRU缓存策略，只看专家最近用没用，完全不管MoE的路由规律。经常出现下一层马上就要用的专家被提前踢出去了，不用的专家反而占着显存，缓存命中率忽上忽下，CPU-GPU来回传数据，延迟直接拉满。

我们当时就想：能不能做一套统一的系统，把“预测-调度-缓存”这三件事打通，而不是各做各的？这就是ExpertFlow的由来。

## ExpertFlow的核心思路：用“全局预测”，把被动推理变成主动调度

ExpertFlow不是单点的优化，而是一套端到端的协同优化系统，核心就是用一个超轻量的路由预测器，提前拿到所有token、所有层的全局路由信息，然后用这个信息去指导token调度和专家缓存，从根上解决上面三个问题。

整个系统就三个核心模块，我们可以叫它“三板斧”，今天给大家掰开揉碎了讲：

![](https://pica.zhimg.com/v2-de9ef2cb6478aaebd5b25e1aea985c0a_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1288' height='1250'></svg>)

### 第一板斧：RPP路由路径预测器，一次性算完所有层的路由，告别“走一步看一步”

之前的预测方案，最大的问题就是串行依赖，必须逐层算。我们直接换了个思路：用一个T5风格的编解码架构，**单次前向传播，直接输出所有token、所有MoE层的专家激活概率**。

![](https://picx.zhimg.com/v2-b207b50ad875ec5117dcf25ea4369a5f_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='840' height='762'></svg>)

简单说，之前的方案是“爬楼梯，上一层才知道下一层往哪走”，我们的RPP是“直接坐电梯到顶楼，把整栋楼的路线全看清了”。这样一来，在第一个MoE层开始算之前，我们就拿到了完整的全局路由规划，提前预取、全局调度都有了基础。

最关键的是，我们把这个预测器做的极致轻量化：最终的模型大小只有**7.21MB**，带来的计算开销几乎可以忽略不计。准度还特别能打：域内场景预测准确率最高能到95%，就算跨任务跨数据集，也只掉5-10个百分点，远甩之前的启发式方案。

当时我们测跨域效果的时候还挺意外的：用对话数据集训的预测器，放到翻译、摘要任务里照样能用，说明它学到的不是数据集的表面规律，而是MoE模型本身的路由行为模式，这也是它能落地的核心前提。

### 第二板斧：TS Token调度器，给token“拼车”，让专家别再“空跑”

有了全局路由信息，我们就能解决专家利用率低的问题了。

之前的token批次是按输入顺序排的，就像乘客随机上出租车，每辆车都要跑不同的地方，最后所有路都要跑一遍，每辆车只拉一个人。我们的TS做的事，就是**把要去同一个“地方”（路由路径相似）的token，重新拼成一个新批次**。

![](https://pic1.zhimg.com/v2-9b025c5f27606c8c2ad537ff800f45d8_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='936' height='766'></svg>)

比如两个批次各4个token，原本每个批次都要激活4个专家，每个专家只处理1个token；重排之后，每个批次只需要激活2个专家，每个专家处理2个token。专家的调用次数直接砍半，单专家处理的token数翻倍，GPU算力利用率一下就上来了。

当然，工程上也踩了不少坑：token重排会打乱KV缓存的顺序，我们专门做了Merge和Reindex两个轻量操作，保证注意力计算的语义完全不变；还设计了双批次流水线，让当前批次的模型计算，和下一个批次的预测、调度并行跑，把额外开销完全隐藏掉，最终调度的CPU开销不到10ms。

![](https://pica.zhimg.com/v2-a520e7e84732728785042e09bc258a3d_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1118' height='380'></svg>)

从实测来看，专家数量越多，TS的收益越明显：Switch-128模型上，吞吐量直接提了17%，就算是专家数最少的Switch-32，也有3%的稳定提升。

### 第三板斧：ECE专家缓存引擎，提前给专家留好“车位”，缓存命中率直接拉满

有了预测的路由信息，缓存策略就不用再“事后补救”了，而是可以“提前规划”。

传统的LRU缓存，是给每层固定分几个缓存槽位，用完了再淘汰，完全不考虑接下来要用什么。我们的ECE不一样：**根据预测的路由信息，跨层自适应分配缓存槽位，提前预取接下来要用的专家**。

![](https://picx.zhimg.com/v2-f7ece73523a6bdc7e117e471dcb70100_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1844' height='1324'></svg>)

举个最简单的例子：GPU缓存只能放4个专家，预测到第一层要用3个，第二层要用2个。我们会先给第一层分3个槽位，第二层分1个，提前把最可能用到的4个专家加载进来；等第一层的专家算完释放了槽位，再立刻加载第二层剩下的专家，全程没有多余的加载和卸载。

当然，预测不可能100%准确，我们还做了实时纠错机制：算的过程中发现预测错了，就用高低优先级队列，在当前专家计算的同时，异步完成专家的换入换出，把I/O和计算完全重叠，就算有预测误差，也不会影响吞吐量。

最终的效果是：缓存命中率最高能到\*\*91.96%\*\*，比LRU策略最高提升了61.15%。尤其是大批次高吞吐的场景，LRU的命中率会暴跌，而我们的策略依然能保持稳定。

![](https://pic1.zhimg.com/v2-57a76a4ac2fe7fcb63ef71ceafea0eb6_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1170' height='694'></svg>)

## 实测效果：到底能带来多大的提升？

我们在单张NVIDIA A40 48G显卡上做了全量实验，覆盖了Switch Transformer、Mixtral-8×7B、Qwen1.5-MoE、Deepseek-MoE这6个主流MoE模型，还有对话、翻译、摘要、数学解题4类典型任务，对比了Cache-MoE、SE-MoE这些业界主流的基线方案。

这里挑几个最实在的结果和大家说：

![](https://pic1.zhimg.com/v2-8cc8b48463d9492854490d5d7235b3a0_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2900' height='624'></svg>)![](https://pic1.zhimg.com/v2-72caebebc1336cd25fc1ef0359e97b3f_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1510' height='788'></svg>)

1. **显存占用砍到极致**：相比全量加载到GPU，我们最高能降低\*\*93.72%\*\*的峰值显存。Switch-128模型从15.26GB降到了1.03GB；之前全量加载直接OOM的Mixtral-8×7B，我们用15.99GB显存就能流畅跑起来。
2. **吞吐量提升拉满**：在显存卡得最死的场景下，Switch-128模型的吞吐量是SE-MoE基线的**10倍**；在Mixtral、Qwen、Deepseek这些主流开源模型上，也能稳定做到比Cache-MoE基线高2倍左右的吞吐量。就算用跨域的预测器，这个收益也完全不掉。

当然，我们也得客观说：10倍的提升是极端受限场景下的结果，更能体现方案的上限；在常规的推理场景里，我们能稳定做到1.5-2倍的吞吐量提升，同时显存占用砍到原来的1/5-1/10，这个收益对于实际落地来说，已经非常实在了。

## 聊聊后续：这个工作到底能用来做什么？

很多朋友问我们，这个工作除了发论文，实际落地的价值在哪？这里也和大家说说我们的思考，也算是对未来工作的展望：

首先最直接的，**大幅降低MoE模型的部署门槛**。现在大家想跑个大一点的MoE模型，至少要高端显卡甚至多卡，而用我们的方案，消费级显卡也能跑起来Mixtral-8×7B级别的模型，中小团队、个人开发者不用再被硬件卡脖子，就能基于MoE模型做自己的应用。

其次，**给云端大模型推理服务降本**。现在大模型推理服务，显存成本是大头。用ExpertFlow，同等显存资源下能承载更高的并发，同时降低推理延迟，尤其是现在很多企业都在用MoE模型做私有化部署，这个方案能直接帮他们省下大量的硬件成本。

再往远了说，这个工作的核心——**精准的全局路由预测**，能做的事远不止单卡卸载。比如分布式MoE推理里，我们可以用路由信息指导专家的分布式放置，减少跨节点通信；还能结合路由规律做模型剪枝、量化、蒸馏，进一步压缩MoE模型；甚至端侧MoE的部署，也能靠这套思路做CPU-NPU的异构调度，让MoE模型真正跑到端侧设备上。

我们也在计划把这套系统开源，让更多开发者能用上，也欢迎业界的同行们一起交流优化。

## 最后说点心里话

其实做这个工作的过程中，我们也踩了无数的坑：一开始预测器做的又大又慢，token重排把KV缓存搞乱了，缓存预取和计算的重叠总是调不好……但好在最终我们拿出了一套能真正解决问题的方案，也得到了DAC审稿人的认可。

当然，这个工作也不是完美的：比如超长序列场景下的预测精度还有提升空间，和动态批处理、vLLM这些主流推理框架的适配也还有很多工作要做。MoE模型的系统优化，还有太多值得深挖的地方，我们也会在这个方向继续深耕下去。

如果大家对这个工作有什么疑问或者建议，欢迎在评论区交流，我们也会尽可能回复大家。


---

## 如何评价DeepSeek最新的「条件记忆」和字节Seed团队「Over-Encoding」之间的关联？

`link: https://www.zhihu.com/question/1995200812075480347/answer/1995935427778069329 · created: 1768648088`


2026 年初，DeepSeek 连续发布了两篇备受关注的论文。元旦发布的《mHC：Manifold‑Constrained Hyper‑Connections》从残差连接入手，提出带流形约束的超连接结构；1 月 13 日发布的《Conditional Memory via Scalable Lookup: A New Axis of Sparsity for Large Language Models》则引入条件记忆模块，让语言模型具备原生的知识查找能力。这两项工作并非凭空诞生，它们以字节 Seed 团队的研究为出发点，通过再设计和工程实践推进了大模型底层的技术演进。

## 从超连接到流形约束：HC 与 mHC 的演化

![](https://pica.zhimg.com/v2-34702bb0502ac5c3c94c9fe1a18e5e91_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1280' height='864'></svg>)

残差连接是现代 Transformer 和 ResNet 架构的核心。字节团队在 2024 年提出的 Hyper‑Connections (HC) 突破了传统残差（图 a）连接将输入直接相加的范式。HC （图 b）通过扩展残差流的宽度并增加连接的复杂度，引入了一种在层间混合信息的新方式，即“深度轴上的注意力”，在不增加单元计算量的前提下显著提高了网络的拓扑表达能力。然而，HC 的矩阵是完全自由的，这种设计牺牲了原本残差连接中的恒等映射特性。当网络跨多个层堆叠时，残差流的平均信号会失去保持，导致信号放大或衰减，训练不稳定，并且拓宽的流还带来额外的访存开销。

DeepSeek 的 mHC 是在此基础上的改进。论文发现，保持信号平均值是稳定深层训练的关键，因此通过将 HC 的残差映射投射到一种受约束的流形上恢复这一性质。具体来说，他们使用 Sinkhorn‑Knopp 算法将 HC 的可学习矩阵投射到 Birkhoff 多面体，即双随机矩阵集合中，使得行和列之和均为 1。这样的投影保证多层组合后仍保持恒等映射，信号不会爆炸或消失。同时，mHC 在系统层面进行了优化，通过核融合、混合精度内核以及 DualPipe 调度中的重计算和通信重叠，有效减小了访存成本，整体增加的训练时间约为 6.7％。mHC 保留了 HC 带来的表达能力，又克服了训练不稳定和硬件效率低的问题。

我们可以粗略地理解两者的贡献比例：HC 提出了“扩大残差流”和“学习连接强度”这一新的设计范式，占据主要的技术贡献；而 mHC 在此基础上引入流形约束和系统共设计，使得这种架构在大规模模型上可用，占据改进中的重要部分。这样的演化说明字节的基础研究为新工作奠定了重要基础，而 DeepSeek 则通过数学约束和工程设计让这条路线更实用。

## 从 LID 视角看流形的重要性

我自己的早期研究曾在神经网络结构搜索中使用过“流形”这一概念，并提出了《NAS-LID: Efficient Neural Architecture Search with Local Intrinsic Dimension》算法。我们在 NAS‑LID 中引入了局部本征维度 (Local Intrinsic Dimension，LID) 来衡量神经网络每一层激活在流形上的维度。实验发现，表现好的模型在训练过程中先将输入升维，然后再降维，其逐层 LID 值呈现“先增后降”的趋势，而表现差的模型无法完成先增过程。这一观察提示模型在学习阶段需要扩展特征空间以更好地分离类别，随后再进行压缩。基于这些规律，我们设计了基于 LID 的指标来预测模型性能并加速搜索。下图展示了我们在不同模型上的 LID 变化趋势：

![](https://picx.zhimg.com/v2-4bffc863675bcfbd5be4d2af1e76c3e5_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='605' height='485'></svg>)

这一图中，横轴为层数（做了归一化，0 表示输入成，1 表示输出层），纵轴为每层输出 activation 的 LID 数值，红色曲线对应性能较好的模型，蓝色曲线对应性能较差的模型。红色曲线在浅层快速升高，随后在高层逐步下降，说明模型在前半部分主动扩展特征维度，后半部分逐步提炼信息。而蓝色曲线则基本平滑，缺少升维阶段。mHC 利用流形约束保证残差流处在受限的几何空间，与 LID 揭示的升维—降维过程不谋而合：一个好的表示学习路径既要能够扩充表示，也要在后续收敛到稳定的低维结构。

## Engram 条件记忆：让模型学会快速查找

![](https://pic1.zhimg.com/v2-e4d1c9950e3b3a0737632f3e154e3752_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1280' height='738'></svg>)

Engram 是 deepseek另一篇论文《Conditional Memory via Scalable Lookup》 中提出的新的结构，它关注的是另一类稀疏性问题。直观上，Engram 想做的事很简单：当模型读到某个 token 时，不只依赖注意力和 FFN 去“算”知识，而是先问一句：这段上下文里有没有我见过的高频短语/实体模式？如果有，就像查字典一样把对应的向量“捞出来”再用。

你看上图左侧（整体结构），Engram 被放在 Transformer block 里，和 Attention、MoE 一样是一个可插拔模块；右侧放大图展示了它内部的“查找”过程。我们首先回顾一下 N-gram 算法原理：

Engram 采用一种现代化的 N‑gram 嵌入表来实现 O(1) 查表。那什么是 N-gram 呢？

> N-gram 本质上就是把一段文本（按字/词/token 切分后的序列）里所有连续的 n 个片段都枚举出来并统计其出现规律。比如把“我 / 爱 / 北京”按词切分，2-gram就是“连续两个词”的所有组合：先取前两个得到“我爱”，再往右挪一格取后两个得到“爱北京”；3-gram就是“连续三个词”的组合，因为整句刚好只有三个词，所以只有一个 3-gram：“我爱北京”。传统 n-gram 语言模型用“前面 n-1 个词”去预测“下一个词”，因此能很好捕捉固定搭配、常见短语、命名实体等局部规律。  
> n-gram 的难点在于：n 越大，可能的片段组合数增长很快，直接存完整的统计表会非常大、也很稀疏，所以工程上常用剪枝、哈希等方式控制规模。在大模型语境里，“n-gram 思想”经常以更简单的形式出现：把常见的 n-gram 当作一种可查表的“局部记忆/特征”，需要时直接查到对应的表示，用来补足模型对局部模式和静态知识的快速调用，而不是每次都靠多层计算去重建。

现在我们继续以上图中的句子 “Only Alexander the Great …” 为例，当处理到 token “Great” 时，Engram 会构造以当前 token 结尾的后缀 n-gram——比如 2-gram: “the Great”，3-gram: “Alexander the Great”（图里正是这两个例子），然后分别经过 Hash 映射到若干个嵌入表索引，取出对应的 2-Gram Embedding / 3-Gram Embedding。这些向量可以理解为“常见短语/命名实体”的静态记忆条目：模型不用每次都靠多层计算去重建“Alexander the Great 是一个整体实体”的知识，而是可以在常数时间里把这个表示直接取出来。

但查表得到的向量本身是“静态的”，不保证每次都该用。所以上图右侧还画了门控/匹配：来自上游层的 hidden state 会作为 query，与检索到的 n-gram 记忆做相似度匹配，得到一个标量门值（用不用、用多少）；再通过一个轻量的卷积/局部融合扩大感受野，把门控信号对齐到相邻 token；最后把“门控后的记忆”通过残差加回主干。一句话：Engram 不是把查表结果硬塞给模型，而是让模型根据当前上下文选择性地启用记忆，从而减少哈希冲突或噪声带来的干扰。

Engram 不仅在算法上引入了新的稀疏维度，在系统设计上也处处考虑了实际效率。由于查找索引是确定性的，训练阶段嵌入表可以按标准模型并行方式分片；推理阶段更可以利用预取重叠策略，在计算前层输出时从主机内存中预取所需嵌入，实现查表与计算并行。论文利用 Zipf 分布的特点，将频繁访问的嵌入放在 GPU 内存，低频部分存储在容量大的 NVMe 存储介质，从而在几乎不牺牲吞吐的前提下支持数百亿参数级别的记忆表。

除了模块设计，论文还提出了“稀疏参数分配”这一优化问题，即如何在固定的稀疏参数预算下在 MoE 专家和 Engram 嵌入之间分配参数。通过在两种计算规模下进行系统实验，他们发现验证损失随分配比例呈现典型的 U 形曲线，全部参数用于 MoE 时反而性能较差，而将 20–25 %的稀疏参数转移到记忆侧可以获得更好的效果。这说明条件计算和条件记忆是互补的维度，而非彼此竞争。

## Engram 与 Over‑Encoding 的区别

Engram 的核心并不是“再造一个更大的词表”，而是把 n-gram 这类短语信息做成模型内部可调用的记忆：遇到像 “Alexander the Great” 这种高频实体/短语时，模型可以通过哈希把对应的 2-gram、3-gram 映射到记忆表里，在常数时间取回向量表示；再用来自当前上下文的隐藏状态做门控，决定“要不要用、用多少”，最后残差融合回主干网络。直观理解就是：让模型在需要“回忆”时可以先查一下，而不是完全靠多层注意力去把静态知识重新算出来。

这听起来和字节 Seed 团队提出的 Over-Encoding（同样利用 n-gram / 短语表）很相似，那有什么不同呢？这里需要先理清关系：Over-Encoding 是 《Over-tokenized transformer: Vocabulary is generally worth scaling》 论文提出的“输入侧”做法——通过显著扩大输入词表，把大量 n-gram/短语作为更细粒度的 token 单元“前置”到 embedding 层，从而增强编码阶段的表达能力；而 Over-Tokenized Transformer 还进一步提出 Over-Decoding（输出侧扩展与训练目标设计），两者合起来构成一个“从输入到输出都在扩展 tokenization 维度”的完整框架。换句话说，Over-Encoding 更像是“把词表做大、把输入表征做强”，而 Engram 更像是“把查表能力做成块内记忆，让它在更深层参与推理与知识调用”。

![](https://pic1.zhimg.com/v2-8f8d5c778265a0661064f617fa5ea158_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1208' height='930'></svg>)

DeepSeek 的 Engram 论文在实验上也把这点讲得很清楚，你看这张图：横轴是 Embedding Slots 数量（可理解为记忆表/扩展词表的容量），纵轴是 Validation Loss（越低越好）。最上面那条几乎水平的 Pure MoE 线说明：如果把稀疏预算几乎都花在 MoE 专家上，只做“条件计算”，并不会随着 embedding 容量增加而带来类似的收益；而绿色的 Over-Encoding 曲线随 slots 增大明显下降，表示“把预算投到更大的 n-gram 输入词表”确实能带来收益（图中标注的 gain from overencoding）。关键在于紫色的 Engram：在相近的 slots 范围内，它整体更低，且随着容量扩展持续下降，说明 Engram 不只是重复 Over-Encoding 的输入侧扩词表，而是在其基础上额外挖出了收益（图中 additional gain on top of overencoding）。简单来说：扩大输入词表确实有效，但把查表做成“可控、可插拔的条件记忆模块”，还能让模型在更深层把这些“查到的知识”用起来，因此收益更进一步、更可扩展。

## 结语：基础研究的积累与技术演进

把 DeepSeek 这两篇论文放一起看，其实挺有意思：同一条技术路线并不是谁一锤子砸出来的，而是大家在公开论文、开源代码、可复现实验的基础上，一点点把想法打磨成“能用的东西”。字节 Seed 先把 HC、Over-Encoding 这些方向性的点子讲清楚、做出可验证的结果；DeepSeek 再往前推一步，把它们变得更稳、更省、更适配大规模模型，最后落到 mHC 和 Engram 这种“你真的可以拿去用”的模块上。讨论差异不是为了扯“谁抄谁”，而是能清楚看到开源与公开研究如何把单点创新变成集体进步；更让人欣慰的是，国内团队这几年在基础研究和开源上的产出越来越密集，也越来越有国际影响力——希望这不只让我们在全球 AI 圈更有底气，也能让产业更愿意投入、岗位更愿意开出来，让更多“牛马”少点无意义的加班和重复造轮子，多点能沉淀、能成长、能写进简历的真东西。期待未来有更多好工作、好项目、好生态，大家在一个更良性、更开放的环境里一起往前冲。


---

## 怎么通俗地解释svd奇异值分解以及作用？

`link: https://www.zhihu.com/question/330814299/answer/1967654003111364533 · created: 1761905271`


## SVD 是怎么被“想出来”的？——从一个朴素问题出发

你有没有见过这样的公式？

![M = U \Sigma V^T \\](https://www.zhihu.com/equation?tex=M+%3D+U+%5CSigma+V%5ET+%5C%5C)

看起来挺简洁，对吧？但当你翻开教材，发现这背后藏着一堆正交矩阵、奇异值、特征向量……瞬间头大。

我每次看到 SVD，都忍不住想：这玩意儿到底是怎么被“想出来”的？是某个数学家喝多了咖啡，突然梦见上帝说：“听着，所有矩阵都能拆成三步走……”

今天，我们不背公式，不套定理。我们要还原 SVD 的“发明”过程——从一个最朴素的问题出发：**一个矩阵，到底对向量做了什么？**

---

## 一、矩阵左乘 = 沿坐标轴的伸缩（从最简单例子开始）

我们从一个最简单的 ![2 \times 2](https://www.zhihu.com/equation?tex=2+%5Ctimes+2) 对角矩阵入手：

![D = \begin{bmatrix} 3 & 0 \\ 0 & 1 \end{bmatrix} \\](https://www.zhihu.com/equation?tex=D+%3D+%5Cbegin%7Bbmatrix%7D+3+%26+0+%5C%5C+0+%26+1+%5Cend%7Bbmatrix%7D+%5C%5C)

取任意向量 ![\mathbf{x} = \begin{bmatrix} x_1 \\ x_2 \end{bmatrix}](https://www.zhihu.com/equation?tex=%5Cmathbf%7Bx%7D+%3D+%5Cbegin%7Bbmatrix%7D+x_1+%5C%5C+x_2+%5Cend%7Bbmatrix%7D)，左乘后得到：

![D \mathbf{x} = \begin{bmatrix} 3x_1 \\ x_2 \end{bmatrix} \\](https://www.zhihu.com/equation?tex=D+%5Cmathbf%7Bx%7D+%3D+%5Cbegin%7Bbmatrix%7D+3x_1+%5C%5C+x_2+%5Cend%7Bbmatrix%7D+%5C%5C)

这意味着：**输入向量在标准基方向 ![\mathbf{e}_1 = (1,0)^T](https://www.zhihu.com/equation?tex=%5Cmathbf%7Be%7D_1+%3D+%281%2C0%29%5ET) 和 ![\mathbf{e}_2 = (0,1)^T](https://www.zhihu.com/equation?tex=%5Cmathbf%7Be%7D_2+%3D+%280%2C1%29%5ET) 上被独立拉伸**——![x](https://www.zhihu.com/equation?tex=x) 方向放大 3 倍，![y](https://www.zhihu.com/equation?tex=y) 方向不变。

这个例子揭示了矩阵左乘的本质：**线性变换 = 对输入空间的各个方向进行伸缩（可能还混合）**。  
而对角矩阵之所以“干净”，是因为它恰好以标准基为伸缩方向，没有混合。

但现实中的矩阵通常不是对角的。那么问题来了：**非对角矩阵是否也能找到自己的“伸缩方向”？**

---

## 二、EVD：方阵的“主伸缩方向”与秩的含义

考虑一个对称方阵：

![A = \begin{bmatrix} 2 & 1 \\ 1 & 2 \end{bmatrix} \\](https://www.zhihu.com/equation?tex=A+%3D+%5Cbegin%7Bbmatrix%7D+2+%26+1+%5C%5C+1+%26+2+%5Cend%7Bbmatrix%7D+%5C%5C)

我们寻找那些**被 ![A](https://www.zhihu.com/equation?tex=A) 作用后只伸缩、不转向**的向量 ![\mathbf{v}](https://www.zhihu.com/equation?tex=%5Cmathbf%7Bv%7D)，即满足：

![A \mathbf{v} = \lambda \mathbf{v} \\](https://www.zhihu.com/equation?tex=A+%5Cmathbf%7Bv%7D+%3D+%5Clambda+%5Cmathbf%7Bv%7D+%5C%5C)

这就是**特征方程**，其中 ![\lambda](https://www.zhihu.com/equation?tex=%5Clambda) 是特征值，![\mathbf{v}](https://www.zhihu.com/equation?tex=%5Cmathbf%7Bv%7D) 是对应的特征向量。

对上面的 ![A](https://www.zhihu.com/equation?tex=A)，解得两组解：

* ![\lambda_1 = 3](https://www.zhihu.com/equation?tex=%5Clambda_1+%3D+3)，对应 ![\mathbf{v}_1 = \begin{bmatrix} 1 \\ 1 \end{bmatrix}](https://www.zhihu.com/equation?tex=%5Cmathbf%7Bv%7D_1+%3D+%5Cbegin%7Bbmatrix%7D+1+%5C%5C+1+%5Cend%7Bbmatrix%7D)
* ![\lambda_2 = 1](https://www.zhihu.com/equation?tex=%5Clambda_2+%3D+1)，对应 ![\mathbf{v}_2 = \begin{bmatrix} 1 \\ -1 \end{bmatrix}](https://www.zhihu.com/equation?tex=%5Cmathbf%7Bv%7D_2+%3D+%5Cbegin%7Bbmatrix%7D+1+%5C%5C+-1+%5Cend%7Bbmatrix%7D)

将这两个向量单位化（归一化），得到标准正交基：

![\mathbf{q}_1 = \frac{1}{\sqrt{2}} \begin{bmatrix} 1 \\ 1 \end{bmatrix}, \quad \mathbf{q}_2 = \frac{1}{\sqrt{2}} \begin{bmatrix} 1 \\ -1 \end{bmatrix} \\](https://www.zhihu.com/equation?tex=%5Cmathbf%7Bq%7D_1+%3D+%5Cfrac%7B1%7D%7B%5Csqrt%7B2%7D%7D+%5Cbegin%7Bbmatrix%7D+1+%5C%5C+1+%5Cend%7Bbmatrix%7D%2C+%5Cquad+%5Cmathbf%7Bq%7D_2+%3D+%5Cfrac%7B1%7D%7B%5Csqrt%7B2%7D%7D+%5Cbegin%7Bbmatrix%7D+1+%5C%5C+-1+%5Cend%7Bbmatrix%7D+%5C%5C)

把它们拼成正交矩阵 ![Q = [\mathbf{q}_1, \mathbf{q}_2]](https://www.zhihu.com/equation?tex=Q+%3D+%5B%5Cmathbf%7Bq%7D_1%2C+%5Cmathbf%7Bq%7D_2%5D)，则 ![Q^T Q = I](https://www.zhihu.com/equation?tex=Q%5ET+Q+%3D+I)。  
由于 ![A \mathbf{q}_i = \lambda_i \mathbf{q}_i](https://www.zhihu.com/equation?tex=A+%5Cmathbf%7Bq%7D_i+%3D+%5Clambda_i+%5Cmathbf%7Bq%7D_i) 对每个列都成立，我们可以把所有等式合写为：

![A Q = Q \Lambda \quad \Rightarrow \quad A = Q \Lambda Q^T \\](https://www.zhihu.com/equation?tex=A+Q+%3D+Q+%5CLambda+%5Cquad+%5CRightarrow+%5Cquad+A+%3D+Q+%5CLambda+Q%5ET+%5C%5C)

其中

![\Lambda = \begin{bmatrix} 3 & 0 \\ 0 & 1 \end{bmatrix} \\](https://www.zhihu.com/equation?tex=%5CLambda+%3D+%5Cbegin%7Bbmatrix%7D+3+%26+0+%5C%5C+0+%26+1+%5Cend%7Bbmatrix%7D+%5C%5C)

这就是**特征值分解（EVD）**。它告诉我们：**任何可对角化的方阵，本质上只是在一组特定正交方向上做独立伸缩**。

---

### 满秩 vs 低秩：不只是数学，更是能力

一个 ![n \times n](https://www.zhihu.com/equation?tex=n+%5Ctimes+n) 矩阵的“能力”取决于它有多少个非零特征值。

* **满秩矩阵**：比如  
   ![A = \begin{bmatrix} 2 & 1 \\ 1 & 2 \end{bmatrix} \\](https://www.zhihu.com/equation?tex=A+%3D+%5Cbegin%7Bbmatrix%7D+2+%26+1+%5C%5C+1+%26+2+%5Cend%7Bbmatrix%7D+%5C%5C) 有两个非零特征值（3 和 1），秩为 2。它能对**任意方向**的输入产生非零输出——换句话说，它可以“操控”整个 2D 空间。
* **低秩矩阵**：比如  
   ![B = \begin{bmatrix} 1 & 1 \\ 1 & 1 \end{bmatrix} \\](https://www.zhihu.com/equation?tex=B+%3D+%5Cbegin%7Bbmatrix%7D+1+%26+1+%5C%5C+1+%26+1+%5Cend%7Bbmatrix%7D+%5C%5C) 特征值为 2 和 0，秩为 1。它只能在方向 ![\begin{bmatrix}1 \\ 1\end{bmatrix}](https://www.zhihu.com/equation?tex=%5Cbegin%7Bbmatrix%7D1+%5C%5C+1%5Cend%7Bbmatrix%7D) 上拉伸，而在垂直方向 ![\begin{bmatrix}1 \\ -1\end{bmatrix}](https://www.zhihu.com/equation?tex=%5Cbegin%7Bbmatrix%7D1+%5C%5C+-1%5Cend%7Bbmatrix%7D) 上输出恒为零。**无论你输入什么，结果永远落在一条直线上**。

在深度学习中，这种差异至关重要：

* **满秩变换**（如初始权重）具有最大表达能力，能响应任意输入变化；
* **低秩更新**（如微调时的 ![\Delta W](https://www.zhihu.com/equation?tex=%5CDelta+W)）则表明：模型真正需要调整的，往往只是少数几个“敏感方向”。

这正是 **LoRA**（Low-Rank Adaptation）有效的核心原因：我们不需要改动整个高维权重矩阵，只需在低维子空间中微调，就能高效适配新任务。

但 EVD 有一个致命限制：**它只适用于方阵**。一旦矩阵是“长方形”的，比如 ![M \in \mathbb{R}^{n \times m}](https://www.zhihu.com/equation?tex=M+%5Cin+%5Cmathbb%7BR%7D%5E%7Bn+%5Ctimes+m%7D) 且 ![n \ne m](https://www.zhihu.com/equation?tex=n+%5Cne+m)，特征方程 ![M \mathbf{v} = \lambda \mathbf{v}](https://www.zhihu.com/equation?tex=M+%5Cmathbf%7Bv%7D+%3D+%5Clambda+%5Cmathbf%7Bv%7D) 就因维度不匹配而失去意义。

于是，我们必须回答一个更一般的问题：**非方阵如何描述其“伸缩行为”？**

---

## 三、SVD：为非方阵找到“跨空间的主方向”

面对 ![M \in \mathbb{R}^{n \times m}](https://www.zhihu.com/equation?tex=M+%5Cin+%5Cmathbb%7BR%7D%5E%7Bn+%5Ctimes+m%7D)，我们放弃“输入输出方向相同”的执念，转而问：

> 是否存在输入空间的一组标准正交基 ![\{\mathbf{v}_1, \dots, \mathbf{v}_m\}](https://www.zhihu.com/equation?tex=%5C%7B%5Cmathbf%7Bv%7D_1%2C+%5Cdots%2C+%5Cmathbf%7Bv%7D_m%5C%7D) 和输出空间的一组标准正交基 ![\{\mathbf{u}_1, \dots, \mathbf{u}_n\}](https://www.zhihu.com/equation?tex=%5C%7B%5Cmathbf%7Bu%7D_1%2C+%5Cdots%2C+%5Cmathbf%7Bu%7D_n%5C%7D)，使得  
>  ![M \mathbf{v}_i = \sigma_i \mathbf{u}_i \quad (i = 1, \dots, r = \min(n,m)) \\](https://www.zhihu.com/equation?tex=M+%5Cmathbf%7Bv%7D_i+%3D+%5Csigma_i+%5Cmathbf%7Bu%7D_i+%5Cquad+%28i+%3D+1%2C+%5Cdots%2C+r+%3D+%5Cmin%28n%2Cm%29%29+%5C%5C)

这个等式是我们希望达成的目标：**第 ![i](https://www.zhihu.com/equation?tex=i) 个输入主方向 ![\mathbf{v}_i](https://www.zhihu.com/equation?tex=%5Cmathbf%7Bv%7D_i)，只激发第 ![i](https://www.zhihu.com/equation?tex=i) 个输出主方向 ![\mathbf{u}_i](https://www.zhihu.com/equation?tex=%5Cmathbf%7Bu%7D_i)，放大 ![\sigma_i](https://www.zhihu.com/equation?tex=%5Csigma_i) 倍**。

我们按拉伸强度从大到小排序：![\sigma_1 \geq \sigma_2 \geq \cdots \geq \sigma_r \geq 0](https://www.zhihu.com/equation?tex=%5Csigma_1+%5Cgeq+%5Csigma_2+%5Cgeq+%5Ccdots+%5Cgeq+%5Csigma_r+%5Cgeq+0)。

更一般的表示是

![MV=U\Sigma \\](https://www.zhihu.com/equation?tex=MV%3DU%5CSigma+%5C%5C)

后面我们可以知道![V](https://www.zhihu.com/equation?tex=V)是正交矩阵，所以上式两边都右乘![V^T](https://www.zhihu.com/equation?tex=V%5ET)，就可以得到常见的 SVD 的形式了

![MVV^T=MVV^{-1}=M=U\Sigma V^T \\](https://www.zhihu.com/equation?tex=MVV%5ET%3DMVV%5E%7B-1%7D%3DM%3DU%5CSigma+V%5ET+%5C%5C)

### 3.1 以最强方向 \sigma_1 为例

回归正题，我们该如何计算 ![\sigma_i](https://www.zhihu.com/equation?tex=%5Csigma_i)呢？我们以最强方向，即 ![\sigma_1](https://www.zhihu.com/equation?tex=%5Csigma_1)为最大值的情况为例。

假设存在单位向量 ![\mathbf{v}_1](https://www.zhihu.com/equation?tex=%5Cmathbf%7Bv%7D_1) 和 ![\mathbf{u}_1](https://www.zhihu.com/equation?tex=%5Cmathbf%7Bu%7D_1)，使得：

![M \mathbf{v}_1 = \sigma_1 \mathbf{u}_1, \quad \|\mathbf{v}_1\| = \|\mathbf{u}_1\| = 1. \\](https://www.zhihu.com/equation?tex=M+%5Cmathbf%7Bv%7D_1+%3D+%5Csigma_1+%5Cmathbf%7Bu%7D_1%2C+%5Cquad+%5C%7C%5Cmathbf%7Bv%7D_1%5C%7C+%3D+%5C%7C%5Cmathbf%7Bu%7D_1%5C%7C+%3D+1.+%5C%5C)

两边取范数，得：

![\|M \mathbf{v}_1\| = \|\sigma_1 \mathbf{u}_1\| = \sigma_1. \\](https://www.zhihu.com/equation?tex=%5C%7CM+%5Cmathbf%7Bv%7D_1%5C%7C+%3D+%5C%7C%5Csigma_1+%5Cmathbf%7Bu%7D_1%5C%7C+%3D+%5Csigma_1.+%5C%5C)

因此，![\sigma_1](https://www.zhihu.com/equation?tex=%5Csigma_1) 就是 ![M](https://www.zhihu.com/equation?tex=M) 在单位输入下能产生的最大输出长度。  
换句话说，![\sigma_1](https://www.zhihu.com/equation?tex=%5Csigma_1) 是如下优化问题的解：

![\sigma_1 = \max_{\|\mathbf{v}\| = 1} \|M \mathbf{v}\|. \\](https://www.zhihu.com/equation?tex=%5Csigma_1+%3D+%5Cmax_%7B%5C%7C%5Cmathbf%7Bv%7D%5C%7C+%3D+1%7D+%5C%7CM+%5Cmathbf%7Bv%7D%5C%7C.+%5C%5C)

由于范数非负，等价于最大化其平方：

![\sigma_1^2=  \max_{\|\mathbf{v}\| = 1} \|M \mathbf{v}\|^2 = \max_{\|\mathbf{v}\| = 1} \mathbf{v}^T (M^T M) \mathbf{v}. \\](https://www.zhihu.com/equation?tex=%5Csigma_1%5E2%3D++%5Cmax_%7B%5C%7C%5Cmathbf%7Bv%7D%5C%7C+%3D+1%7D+%5C%7CM+%5Cmathbf%7Bv%7D%5C%7C%5E2+%3D+%5Cmax_%7B%5C%7C%5Cmathbf%7Bv%7D%5C%7C+%3D+1%7D+%5Cmathbf%7Bv%7D%5ET+%28M%5ET+M%29+%5Cmathbf%7Bv%7D.+%5C%5C)

### 3.2 计算奇异值和右奇异矩阵 V

记 ![A = M^T M](https://www.zhihu.com/equation?tex=A+%3D+M%5ET+M)。矩阵 ![A](https://www.zhihu.com/equation?tex=A) 是 ![m \times m](https://www.zhihu.com/equation?tex=m+%5Ctimes+m) 实对称矩阵，且对任意 ![\mathbf{v}](https://www.zhihu.com/equation?tex=%5Cmathbf%7Bv%7D) 有 ![\mathbf{v}^T A \mathbf{v} \geq 0](https://www.zhihu.com/equation?tex=%5Cmathbf%7Bv%7D%5ET+A+%5Cmathbf%7Bv%7D+%5Cgeq+0)，故 ![A](https://www.zhihu.com/equation?tex=A) 半正定。记 ![A](https://www.zhihu.com/equation?tex=A) 的特征值按非增序排列为 ![\lambda_1 \geq \lambda_2 \geq \cdots \geq \lambda_m \geq 0](https://www.zhihu.com/equation?tex=%5Clambda_1+%5Cgeq+%5Clambda_2+%5Cgeq+%5Ccdots+%5Cgeq+%5Clambda_m+%5Cgeq+0)，对应的标准正交特征向量为 ![\mathbf{q}_1, \dots, \mathbf{q}_m](https://www.zhihu.com/equation?tex=%5Cmathbf%7Bq%7D_1%2C+%5Cdots%2C+%5Cmathbf%7Bq%7D_m)，即

![A \mathbf{q}_i = \lambda_i \mathbf{q}_i \\](https://www.zhihu.com/equation?tex=A+%5Cmathbf%7Bq%7D_i+%3D+%5Clambda_i+%5Cmathbf%7Bq%7D_i+%5C%5C)

瑞利商的极值性质表明(原理推导见本节末尾）：

![\max_{\|\mathbf{v}\| = 1} \mathbf{v}^T A \mathbf{v} = \lambda_1, \\](https://www.zhihu.com/equation?tex=%5Cmax_%7B%5C%7C%5Cmathbf%7Bv%7D%5C%7C+%3D+1%7D+%5Cmathbf%7Bv%7D%5ET+A+%5Cmathbf%7Bv%7D+%3D+%5Clambda_1%2C+%5C%5C)

且最大值在 ![\mathbf{v} = \mathbf{q}_1](https://www.zhihu.com/equation?tex=%5Cmathbf%7Bv%7D+%3D+%5Cmathbf%7Bq%7D_1) 处取得。更一般地，对 ![k = 1, \dots, m](https://www.zhihu.com/equation?tex=k+%3D+1%2C+%5Cdots%2C+m)，

![\max_{\substack{\|\mathbf{v}\| = 1 \\ \mathbf{v} \perp \mathbf{q}_1, \dots, \mathbf{q}_{k-1}}} \mathbf{v}^T A \mathbf{v} = \lambda_k, \\](https://www.zhihu.com/equation?tex=%5Cmax_%7B%5Csubstack%7B%5C%7C%5Cmathbf%7Bv%7D%5C%7C+%3D+1+%5C%5C+%5Cmathbf%7Bv%7D+%5Cperp+%5Cmathbf%7Bq%7D_1%2C+%5Cdots%2C+%5Cmathbf%7Bq%7D_%7Bk-1%7D%7D%7D+%5Cmathbf%7Bv%7D%5ET+A+%5Cmathbf%7Bv%7D+%3D+%5Clambda_k%2C+%5C%5C)

在 ![\mathbf{v} = \mathbf{q}_k](https://www.zhihu.com/equation?tex=%5Cmathbf%7Bv%7D+%3D+%5Cmathbf%7Bq%7D_k) 处取得。说人话就是，第k 大的值就是![\lambda_k](https://www.zhihu.com/equation?tex=%5Clambda_k)，而且是在![v=q_k](https://www.zhihu.com/equation?tex=v%3Dq_k)时可以得到。

所以

![\sigma_i^2 = \max_{\|\mathbf{v}\| = 1} \mathbf{v}^T (M^T M) \mathbf{v} = \lambda_i   \quad i = 1, \dots, m, \\](https://www.zhihu.com/equation?tex=%5Csigma_i%5E2+%3D+%5Cmax_%7B%5C%7C%5Cmathbf%7Bv%7D%5C%7C+%3D+1%7D+%5Cmathbf%7Bv%7D%5ET+%28M%5ET+M%29+%5Cmathbf%7Bv%7D+%3D+%5Clambda_i+++%5Cquad+i+%3D+1%2C+%5Cdots%2C+m%2C+%5C%5C)

则 ![\sigma_i=\sqrt{\lambda_i}, \sigma_1 \geq \sigma_2 \geq \cdots \geq \sigma_m \geq 0](https://www.zhihu.com/equation?tex=%5Csigma_i%3D%5Csqrt%7B%5Clambda_i%7D%2C+%5Csigma_1+%5Cgeq+%5Csigma_2+%5Cgeq+%5Ccdots+%5Cgeq+%5Csigma_m+%5Cgeq+0)，且

![v_i=q_i \\](https://www.zhihu.com/equation?tex=v_i%3Dq_i+%5C%5C)

至此，我们成功求解了矩阵 V和奇异值矩阵![\Sigma](https://www.zhihu.com/equation?tex=%5CSigma)

> **瑞利商性质**：对实对称矩阵 ![A](https://www.zhihu.com/equation?tex=A)，定义其**瑞利商**为  
>  ![R_A(\mathbf{c}) = \frac{\mathbf{c}^T A \mathbf{c}}{\mathbf{c}^T \mathbf{c}}, \quad \mathbf{c} \ne \mathbf{0}. \\](https://www.zhihu.com/equation?tex=R_A%28%5Cmathbf%7Bc%7D%29+%3D+%5Cfrac%7B%5Cmathbf%7Bc%7D%5ET+A+%5Cmathbf%7Bc%7D%7D%7B%5Cmathbf%7Bc%7D%5ET+%5Cmathbf%7Bc%7D%7D%2C+%5Cquad+%5Cmathbf%7Bc%7D+%5Cne+%5Cmathbf%7B0%7D.+%5C%5C) 当 ![\|\mathbf{c}\| = 1](https://www.zhihu.com/equation?tex=%5C%7C%5Cmathbf%7Bc%7D%5C%7C+%3D+1) 时，![R_A(\mathbf{c}) = \mathbf{c}^T A \mathbf{c}](https://www.zhihu.com/equation?tex=R_A%28%5Cmathbf%7Bc%7D%29+%3D+%5Cmathbf%7Bc%7D%5ET+A+%5Cmathbf%7Bc%7D)。  
> 设 ![A](https://www.zhihu.com/equation?tex=A) 的特征值按非增序排列为 ![\lambda_1 \geq \lambda_2 \geq \cdots \geq \lambda_m \geq 0](https://www.zhihu.com/equation?tex=%5Clambda_1+%5Cgeq+%5Clambda_2+%5Cgeq+%5Ccdots+%5Cgeq+%5Clambda_m+%5Cgeq+0)，对应的标准正交特征向量为 ![\mathbf{q}_1, \dots, \mathbf{q}_m](https://www.zhihu.com/equation?tex=%5Cmathbf%7Bq%7D_1%2C+%5Cdots%2C+%5Cmathbf%7Bq%7D_m)，即  
>  ![A \mathbf{q}_i = \lambda_i \mathbf{q}_i, \quad \mathbf{q}_i^T \mathbf{q}_j = \delta_{ij}. \\](https://www.zhihu.com/equation?tex=A+%5Cmathbf%7Bq%7D_i+%3D+%5Clambda_i+%5Cmathbf%7Bq%7D_i%2C+%5Cquad+%5Cmathbf%7Bq%7D_i%5ET+%5Cmathbf%7Bq%7D_j+%3D+%5Cdelta_%7Bij%7D.+%5C%5C) 瑞利商的极值性质表明：  
>  ![\max_{\|\mathbf{c}\| = 1} \mathbf{c}^T A \mathbf{c} = \lambda_1, \\](https://www.zhihu.com/equation?tex=%5Cmax_%7B%5C%7C%5Cmathbf%7Bc%7D%5C%7C+%3D+1%7D+%5Cmathbf%7Bc%7D%5ET+A+%5Cmathbf%7Bc%7D+%3D+%5Clambda_1%2C+%5C%5C) 且最大值在 ![\mathbf{c} = \mathbf{q}_1](https://www.zhihu.com/equation?tex=%5Cmathbf%7Bc%7D+%3D+%5Cmathbf%7Bq%7D_1) 处取得。更一般地，对 ![k = 1, \dots, m](https://www.zhihu.com/equation?tex=k+%3D+1%2C+%5Cdots%2C+m)，  
>  ![\max_{\substack{\|\mathbf{c}\| = 1 \\ \mathbf{c} \perp \mathbf{q}_1, \dots, \mathbf{q}_{k-1}}} \mathbf{c}^T A \mathbf{c} = \lambda_k, \\](https://www.zhihu.com/equation?tex=%5Cmax_%7B%5Csubstack%7B%5C%7C%5Cmathbf%7Bc%7D%5C%7C+%3D+1+%5C%5C+%5Cmathbf%7Bc%7D+%5Cperp+%5Cmathbf%7Bq%7D_1%2C+%5Cdots%2C+%5Cmathbf%7Bq%7D_%7Bk-1%7D%7D%7D+%5Cmathbf%7Bc%7D%5ET+A+%5Cmathbf%7Bc%7D+%3D+%5Clambda_k%2C+%5C%5C) 在 ![\mathbf{c} = \mathbf{q}_k](https://www.zhihu.com/equation?tex=%5Cmathbf%7Bc%7D+%3D+%5Cmathbf%7Bq%7D_k) 处取得。 因此，令  
>  ![\sigma_i = \sqrt{\lambda_i}, \quad \mathbf{c}_i = \mathbf{q}_i, \quad i = 1, \dots, m, \\](https://www.zhihu.com/equation?tex=%5Csigma_i+%3D+%5Csqrt%7B%5Clambda_i%7D%2C+%5Cquad+%5Cmathbf%7Bc%7D_i+%3D+%5Cmathbf%7Bq%7D_i%2C+%5Cquad+i+%3D+1%2C+%5Cdots%2C+m%2C+%5C%5C) 则 ![\sigma_1 \geq \sigma_2 \geq \cdots \geq \sigma_m \geq 0](https://www.zhihu.com/equation?tex=%5Csigma_1+%5Cgeq+%5Csigma_2+%5Cgeq+%5Ccdots+%5Cgeq+%5Csigma_m+%5Cgeq+0)，且  
>  ![\|M \mathbf{c}_i\|^2 = \mathbf{c}_i^T A \mathbf{c}_i = \lambda_i = \sigma_i^2. \\](https://www.zhihu.com/equation?tex=%5C%7CM+%5Cmathbf%7Bc%7D_i%5C%7C%5E2+%3D+%5Cmathbf%7Bc%7D_i%5ET+A+%5Cmathbf%7Bc%7D_i+%3D+%5Clambda_i+%3D+%5Csigma_i%5E2.+%5C%5C)

### 3.3 构造左奇异矩阵

令 ![r = \operatorname{rank}(M)](https://www.zhihu.com/equation?tex=r+%3D+%5Coperatorname%7Brank%7D%28M%29)。由于 ![\operatorname{rank}(M) = \operatorname{rank}(M^T M)](https://www.zhihu.com/equation?tex=%5Coperatorname%7Brank%7D%28M%29+%3D+%5Coperatorname%7Brank%7D%28M%5ET+M%29)，有 ![\sigma_i > 0](https://www.zhihu.com/equation?tex=%5Csigma_i+%3E+0) 当且仅当 ![i \leq r](https://www.zhihu.com/equation?tex=i+%5Cleq+r)。

对每个 ![i = 1, \dots, r](https://www.zhihu.com/equation?tex=i+%3D+1%2C+%5Cdots%2C+r)，根据最前面的定义![M \mathbf{v}_i = \sigma_i \mathbf{u}_i](https://www.zhihu.com/equation?tex=M+%5Cmathbf%7Bv%7D_i+%3D+%5Csigma_i+%5Cmathbf%7Bu%7D_i)，我们有

![\mathbf{u}_i = \frac{1}{\sigma_i} M \mathbf{v}_i. \\](https://www.zhihu.com/equation?tex=%5Cmathbf%7Bu%7D_i+%3D+%5Cfrac%7B1%7D%7B%5Csigma_i%7D+M+%5Cmathbf%7Bv%7D_i.+%5C%5C)

至此就可算出对应的![\sigma_i,v_i,u_i](https://www.zhihu.com/equation?tex=%5Csigma_i%2Cv_i%2Cu_i)。我们会发现求得的 ![u_i](https://www.zhihu.com/equation?tex=u_i)也是基坐标，彼此正交：

![\|\mathbf{u}_i\| = \frac{1}{\sigma_i} \|M \mathbf{v}_i\| = \frac{1}{\sigma_i} \cdot \sigma_i = 1, \\](https://www.zhihu.com/equation?tex=%5C%7C%5Cmathbf%7Bu%7D_i%5C%7C+%3D+%5Cfrac%7B1%7D%7B%5Csigma_i%7D+%5C%7CM+%5Cmathbf%7Bv%7D_i%5C%7C+%3D+%5Cfrac%7B1%7D%7B%5Csigma_i%7D+%5Ccdot+%5Csigma_i+%3D+1%2C+%5C%5C)

且

![M \mathbf{v}_i = \sigma_i \mathbf{u}_i. \\](https://www.zhihu.com/equation?tex=M+%5Cmathbf%7Bv%7D_i+%3D+%5Csigma_i+%5Cmathbf%7Bu%7D_i.+%5C%5C)

对 ![i \ne j \leq r](https://www.zhihu.com/equation?tex=i+%5Cne+j+%5Cleq+r)，有

![\mathbf{u}_i^T \mathbf{u}_j = \frac{1}{\sigma_i \sigma_j} \mathbf{v}_i^T M^T M \mathbf{v}_j = \frac{1}{\sigma_i \sigma_j} \mathbf{v}_i^T (\sigma_j^2 \mathbf{v}_j) = \sigma_j \cdot \mathbf{v}_i^T \mathbf{v}_j = 0, \\](https://www.zhihu.com/equation?tex=%5Cmathbf%7Bu%7D_i%5ET+%5Cmathbf%7Bu%7D_j+%3D+%5Cfrac%7B1%7D%7B%5Csigma_i+%5Csigma_j%7D+%5Cmathbf%7Bv%7D_i%5ET+M%5ET+M+%5Cmathbf%7Bv%7D_j+%3D+%5Cfrac%7B1%7D%7B%5Csigma_i+%5Csigma_j%7D+%5Cmathbf%7Bv%7D_i%5ET+%28%5Csigma_j%5E2+%5Cmathbf%7Bv%7D_j%29+%3D+%5Csigma_j+%5Ccdot+%5Cmathbf%7Bv%7D_i%5ET+%5Cmathbf%7Bv%7D_j+%3D+0%2C+%5C%5C)

故 ![\{\mathbf{u}_1, \dots, \mathbf{u}_r\}](https://www.zhihu.com/equation?tex=%5C%7B%5Cmathbf%7Bu%7D_1%2C+%5Cdots%2C+%5Cmathbf%7Bu%7D_r%5C%7D) 是 ![\mathbb{R}^n](https://www.zhihu.com/equation?tex=%5Cmathbb%7BR%7D%5En) 中的标准正交向量组。

前面计算的![u_i](https://www.zhihu.com/equation?tex=u_i)是与![v_i](https://www.zhihu.com/equation?tex=v_i)一一对应的，但是当 ![r < n](https://www.zhihu.com/equation?tex=r+%3C+n)时，剩下的![u_i](https://www.zhihu.com/equation?tex=u_i)该如何计算呢？我们会发现存在 ![n - r](https://www.zhihu.com/equation?tex=n+-+r) 维子空间

![\mathcal{U}_\perp = \left\{ \mathbf{x} \in \mathbb{R}^n \,\middle|\, \mathbf{u}_i^T \mathbf{x} = 0,\ \forall i = 1, \dots, r \right\}. \\](https://www.zhihu.com/equation?tex=%5Cmathcal%7BU%7D_%5Cperp+%3D+%5Cleft%5C%7B+%5Cmathbf%7Bx%7D+%5Cin+%5Cmathbb%7BR%7D%5En+%5C%2C%5Cmiddle%7C%5C%2C+%5Cmathbf%7Bu%7D_i%5ET+%5Cmathbf%7Bx%7D+%3D+0%2C%5C+%5Cforall+i+%3D+1%2C+%5Cdots%2C+r+%5Cright%5C%7D.+%5C%5C)

在 ![\mathcal{U}_\perp](https://www.zhihu.com/equation?tex=%5Cmathcal%7BU%7D_%5Cperp) 中任取一组标准正交基 ![\{\mathbf{u}_{r+1}, \dots, \mathbf{u}_n\}](https://www.zhihu.com/equation?tex=%5C%7B%5Cmathbf%7Bu%7D_%7Br%2B1%7D%2C+%5Cdots%2C+%5Cmathbf%7Bu%7D_n%5C%7D)，则最终的左奇异矩阵为

![U = [\mathbf{u}_1, \dots, \mathbf{u}_n] \in \mathbb{R}^{n \times n} \\](https://www.zhihu.com/equation?tex=U+%3D+%5B%5Cmathbf%7Bu%7D_1%2C+%5Cdots%2C+%5Cmathbf%7Bu%7D_n%5D+%5Cin+%5Cmathbb%7BR%7D%5E%7Bn+%5Ctimes+n%7D+%5C%5C)

为正交矩阵。

### 3.4 拼装 SVD

令

* ![V = [\mathbf{v}_1, \dots, \mathbf{v}_m] \in \mathbb{R}^{m \times m}](https://www.zhihu.com/equation?tex=V+%3D+%5B%5Cmathbf%7Bv%7D_1%2C+%5Cdots%2C+%5Cmathbf%7Bv%7D_m%5D+%5Cin+%5Cmathbb%7BR%7D%5E%7Bm+%5Ctimes+m%7D)，
* ![\Sigma \in \mathbb{R}^{n \times m}](https://www.zhihu.com/equation?tex=%5CSigma+%5Cin+%5Cmathbb%7BR%7D%5E%7Bn+%5Ctimes+m%7D) 为对角矩阵，其对角元为 ![\sigma_1, \dots, \sigma_r](https://www.zhihu.com/equation?tex=%5Csigma_1%2C+%5Cdots%2C+%5Csigma_r)，其余元素为 0。

由 ![M \mathbf{v}_i = \sigma_i \mathbf{u}_i](https://www.zhihu.com/equation?tex=M+%5Cmathbf%7Bv%7D_i+%3D+%5Csigma_i+%5Cmathbf%7Bu%7D_i) 对 ![i = 1, \dots, r](https://www.zhihu.com/equation?tex=i+%3D+1%2C+%5Cdots%2C+r) 成立，且对 ![i > r](https://www.zhihu.com/equation?tex=i+%3E+r) 有 ![\sigma_i = 0](https://www.zhihu.com/equation?tex=%5Csigma_i+%3D+0)，可得矩阵等式

![M V = U \Sigma. \\](https://www.zhihu.com/equation?tex=M+V+%3D+U+%5CSigma.+%5C%5C)

由于 ![V](https://www.zhihu.com/equation?tex=V) 正交（![V^T V = I_m](https://www.zhihu.com/equation?tex=V%5ET+V+%3D+I_m)），右乘 ![V^T](https://www.zhihu.com/equation?tex=V%5ET) 得

![M = U \Sigma V^T. \\](https://www.zhihu.com/equation?tex=M+%3D+U+%5CSigma+V%5ET.+%5C%5C)

---

## 结语

SVD 并非凭空定义的数学魔术，而是为了解决“**非方阵如何描述伸缩**”这一朴素问题，从对角矩阵 → EVD → 跨空间推广，一步步自然推导出的必然结果。

当你再看到 ![M = U \Sigma V^T](https://www.zhihu.com/equation?tex=M+%3D+U+%5CSigma+V%5ET)，请记住：  
**它只是在说——先转一下，再拉伸，再转一下。**  
而这，就是所有线性变换最干净的表达方式。


---

## 将来想在LLM（large language model）领域深耕，需要哪些基本的数学知识?

`link: https://www.zhihu.com/question/633347275/answer/1965425933080048711 · created: 1761374058`


LLM 技术更新换代非常快，这篇文章筛选记录写的非常好（我个人认为）的文章，浅显易懂，对于初学者或者进一步理解都很有帮助，当然不排除和穿插个人私货哈哈，也欢迎大家评论区投稿，大家一起选出写得好的文章。

未来会持续更新。。。

## 1. 数学基础

* 矩的概念

像 Adam 优化器中会有梯度的一阶和二阶矩，这篇文章很好的解释了什么叫一阶，二阶，什么叫做矩（moment）

[统计学中「矩」这个概念是怎么引入的？它为什么被称为矩？它与物理意义上的矩有什么相同与不同？](https://www.zhihu.com/question/19915565/answer/233262673)

* SVD 原理详解：

[尝试从源头来理解 SVD 原理和计算](https://zhuanlan.zhihu.com/p/1967653700144181450)

## 2. LLM 模型和优化

* FlashAttention 详解：

[FlashAttention 的速度优化原理是怎样的？](https://www.zhihu.com/question/611236756/answer/3132304304)

* Rope 详解：

[图解RoPE旋转位置编码及其特性](https://zhuanlan.zhihu.com/p/667864459)

* MLA 详解：

[deepseek技术解读(1)-彻底理解MLA（Multi-Head Latent Attention）](https://zhuanlan.zhihu.com/p/16730036197)

* diffusion 详解：

[OpenAI 的视频生成大模型Sora的核心技术详解（一）：Diffusion模型原理和代码详解](https://zhuanlan.zhihu.com/p/683418039)

## 3. 强化学习

* PPO 详解：

[拆解大语言模型RLHF中的PPO](https://zhuanlan.zhihu.com/p/645225982)

## 4. 系统优化（分布式训练和推理）

* 分布式并行训练策略简介：

[深度学习并行训练算法一锅炖: DDP, TP, PP, ZeRO](https://zhuanlan.zhihu.com/p/581677880)

* All-reduce 详解：

[手把手推导Ring All-reduce的数学性质](https://zhuanlan.zhihu.com/p/504957661)

* ZeRO 算法详解

[DeepSpeed之ZeRO系列：将显存优化进行到底](https://zhuanlan.zhihu.com/p/513571706)[图解大模型训练之：数据并行下篇( DeepSpeed ZeRO，零冗余优化)](https://zhuanlan.zhihu.com/p/618865052)


---

## 大模型的DPO、PPO都是什么？

`link: https://www.zhihu.com/question/658316700/answer/1964816970181501543 · created: 1761228870`


## 1. 强化学习基础：行业黑话

想象你正在和一个刚训练好的语言模型聊天。你问：“今天过得怎么样？”  
模型可能回：“还行。” 也可能回：“我是个 AI，没有感情。”  
人类觉得前者更自然、更友好——这就是**偏好反馈**。强化学习（RL）在 LLM 中的核心任务，就是让模型学会生成“人类更喜欢”的回复。

为了做到这一点，我们需要一套语言来描述这个过程。下面我们以 LLM 场景为基础介绍几个 RL 的“行业黑话”。

## 1.1 基本概念

1. **时刻** ![t](https://www.zhihu.com/equation?tex=t)：就是对话的第几步。比如：

* ![t=0](https://www.zhihu.com/equation?tex=t%3D0)：用户输入 “今天过得怎么样？” → 这是初始状态 ![s_0](https://www.zhihu.com/equation?tex=s_0)
* ![t=1](https://www.zhihu.com/equation?tex=t%3D1)：模型输出第一个词 “今” → 动作 ![a_0 = \text{“今”}](https://www.zhihu.com/equation?tex=a_0+%3D+%5Ctext%7B%E2%80%9C%E4%BB%8A%E2%80%9D%7D)
* ![t=2](https://www.zhihu.com/equation?tex=t%3D2)：模型输出第二个词 “天” → 动作 ![a_1 = \text{“天”}](https://www.zhihu.com/equation?tex=a_1+%3D+%5Ctext%7B%E2%80%9C%E5%A4%A9%E2%80%9D%7D)
* … 直到生成完整回复，比如 “今天过得不错！”

**2. 状态 ![s_t](https://www.zhihu.com/equation?tex=s_t) 通常就是到第 ![t](https://www.zhihu.com/equation?tex=t) 步为止已生成的 token 序列**（包括用户输入和模型已输出的部分）

**3. 动作 ![a_t](https://www.zhihu.com/equation?tex=a_t) 就是模型在第 ![t](https://www.zhihu.com/equation?tex=t) 步选择的下一个 token**。

4. **奖励 ![r_t](https://www.zhihu.com/equation?tex=r_t)：这是人类（或奖励模型）对模型行为的真实反馈信号**。比如：

+ 如果模型最终生成了“今天过得不错！”，人类觉得回答的不错，打 5 分 → 这个分数会折算成一个\*\*最终奖励 ![r_T](https://www.zhihu.com/equation?tex=r_T)\*\*（通常只在序列结束时给，即最后一个 token）
+ 中间步骤一般没有即时奖励（![r_t = 0](https://www.zhihu.com/equation?tex=r_t+%3D+0) for ![t < T](https://www.zhihu.com/equation?tex=t+%3C+T)）

**5. 价值** ![v](https://www.zhihu.com/equation?tex=v)：奖励 ![r](https://www.zhihu.com/equation?tex=r) 是**真实的、来自外部的信号**（比如人类打分），相对应的，**价值（value）是对未来奖励的估计**——因为模型不能预知未来，只能靠猜。

## 1.2. 价值（Value）：对未来奖励的“预判”

既然模型不能看到未来，它就需要一个“预判能力”：**我现在处在某个状态，未来大概能拿多少分？**

这就引出了两个核心函数：

### 1) 状态价值函数 V(s_t)

![V(s_t) = \sum_{a \in \mathcal{A}} \pi(a|s_t) \, Q(s_t, a) \\](https://www.zhihu.com/equation?tex=V%28s_t%29+%3D+%5Csum_%7Ba+%5Cin+%5Cmathcal%7BA%7D%7D+%5Cpi%28a%7Cs_t%29+%5C%2C+Q%28s_t%2C+a%29+%5C%5C)

它表达的是：**在当前已生成的对话上下文 ![s_t](https://www.zhihu.com/equation?tex=s_t)（比如用户刚问完 “今天过得怎么样？”，而模型还没开始回答，或已输出“今”），模型按照当前策略继续生成后续内容，平均能获得多少人类打分**。

* ![\pi(a|s_t)](https://www.zhihu.com/equation?tex=%5Cpi%28a%7Cs_t%29) 是模型在状态 ![s_t](https://www.zhihu.com/equation?tex=s_t) 下选择下一个词 ![a](https://www.zhihu.com/equation?tex=a) 的概率（例如在“今天过得怎么样？”之后，选“今”还是“还”）；
* ![Q(s_t, a)](https://www.zhihu.com/equation?tex=Q%28s_t%2C+a%29) 表示如果此刻选了某个具体词 ![a](https://www.zhihu.com/equation?tex=a)，最终能拿到的预期总分；
* 把所有可能的下一个词按模型当前的偏好加权平均，就得到了该状态的整体“预期得分”——也就是 ![V(s_t)](https://www.zhihu.com/equation?tex=V%28s_t%29)。

举个例子：当模型已经输出 “今天过得”，它会评估：“按我现在的风格继续回答，人类大概率会觉得自然，可能打 4 分”，于是 ![V(s_t) \approx 4](https://www.zhihu.com/equation?tex=V%28s_t%29+%5Capprox+4)。

### 2) 动作价值函数 Q(s_t, a)

![Q(s_t, a) = r_t + \gamma V(s_{t+1}) + \gamma^2 V(s_{t+2}) + \cdots \\](https://www.zhihu.com/equation?tex=Q%28s_t%2C+a%29+%3D+r_t+%2B+%5Cgamma+V%28s_%7Bt%2B1%7D%29+%2B+%5Cgamma%5E2+V%28s_%7Bt%2B2%7D%29+%2B+%5Ccdots+%5C%5C)

它表达的是：**如果我现在处于状态 ![s_t](https://www.zhihu.com/equation?tex=s_t)（比如上下文是“今天过得”），并选择动作 ![a](https://www.zhihu.com/equation?tex=a)（比如生成“不”），那么我能获得当前的真实奖励 ![r_t](https://www.zhihu.com/equation?tex=r_t)（通常是 0，因为回复还没结束），再加上未来所有状态价值的折扣和**。

对应到 LLM 应用场景就表示：

> “如果我现在在‘今天过得’后面接‘不’，形成‘今天过得不’，那接下来我大概率会说‘错！’，组成一句完整、积极的回复，最终人类可能会打 5 分。”

其中：

* ![r_t](https://www.zhihu.com/equation?tex=r_t) 是**真实发生的奖励**，但在 LLM 生成过程中，**只有完整回复结束后才有非零值**（例如人类打分 ![r_T = 5](https://www.zhihu.com/equation?tex=r_T+%3D+5)）；在中间步骤（如生成“今”“天”时），![r_t = 0](https://www.zhihu.com/equation?tex=r_t+%3D+0)；
* ![V(s_{t+1}), V(s_{t+2}), \dots](https://www.zhihu.com/equation?tex=V%28s_%7Bt%2B1%7D%29%2C+V%28s_%7Bt%2B2%7D%29%2C+%5Cdots) 是**模型自己估计的未来价值**（比如生成“不”之后，预估“今天过得不错！”能拿 4.9 分）；
* ![\gamma \in [0,1]](https://www.zhihu.com/equation?tex=%5Cgamma+%5Cin+%5B0%2C1%5D) 是折扣因子（如 0.95），表示“未来的分不如现在的分值钱”——越靠后的 token 对当前决策的影响越小。

虽然中间每一步的 ![r_t = 0](https://www.zhihu.com/equation?tex=r_t+%3D+0)，但 ![Q(s_t, a)](https://www.zhihu.com/equation?tex=Q%28s_t%2C+a%29) 依然非常关键：它通过 ![V(s_{t+1})](https://www.zhihu.com/equation?tex=V%28s_%7Bt%2B1%7D%29) 等未来价值，把**对最终人类反馈的预判**传递回当前决策。这正是 LLM 在生成每个词时具备“前瞻能力”的来源——它不是随机选词，而是基于“这样说人类会不会喜欢”的长期预期来做选择。

> **为什么估计的价值函数 Q 里包含真实的 ![r_t](https://www.zhihu.com/equation?tex=r_t)？**  
> 因为 RL 的目标是**用真实奖励来校准价值估计**。模型通过不断对比“预测的未来得分”和“实际拿到的奖励”，来修正自己的 ![V](https://www.zhihu.com/equation?tex=V) 和 ![Q](https://www.zhihu.com/equation?tex=Q) 函数。

## 2. PPO：RLHF 的“老大哥”

PPO（Proximal Policy Optimization）是传统 RLHF（基于人类反馈的强化学习）流程中的核心算法，是 openai 在 2016年左右提出来的。原来 closeAI 的成功在那个时候就开始蓄力了。PPO的目标很直接：**让语言模型生成更受人类欢迎的回复**。

## PPO 中的几个关键角色

![](https://pic1.zhimg.com/v2-d9bb68f1c8eb0ec0643180813082b461_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='869' height='333'></svg>)
> 注：![\oplus](https://www.zhihu.com/equation?tex=%5Coplus) 表示 token 拼接；![T](https://www.zhihu.com/equation?tex=T) 是生成回复的长度（可变，但训练时通常 padding 到固定长度）。

## PPO 的两阶段训练流程

PPO通过分阶段解耦“数据生成”和“策略学习”，在保证训练稳定性的同时，让模型逐步学会生成更符合人类偏好的回复。整个流程分为如下两个阶段：

### 阶段 1：采样与反馈（Sample + Label）

目标：用**当前策略模型**生成一批回复，并利用**冻结的奖励模型**打分，再结合**当前评论家模型**估计价值，最终为每个 token 动作计算出**优势（Advantage）** 和**回报（Return）**，作为后续训练的监督信号。

> **关键点**：此阶段**不更新任何模型参数**，只是“收集数据”。Policy 和 Critic 在采样时使用的是当前最新参数，但输出会被 detach（视为常数），作为“旧策略”和“旧评论家”的快照。

参与模型与接口

![](https://picx.zhimg.com/v2-b1d8734cdf174d3d43756db834bee2b9_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='840' height='225'></svg>)
> 注：![L_x](https://www.zhihu.com/equation?tex=L_x) 是 prompt 长度，![T](https://www.zhihu.com/equation?tex=T) 是生成回复长度（实际中常 padding 到固定 max\_len）。

核心计算逻辑

1. **生成轨迹**：对每个 prompt ![x](https://www.zhihu.com/equation?tex=x)，用当前策略生成完整回复 ![y = (a_1, ..., a_T)](https://www.zhihu.com/equation?tex=y+%3D+%28a_1%2C+...%2C+a_T%29)，形成状态序列：  
    ![s_0 = x,\quad s_1 = x \oplus a_1,\quad \dots,\quad s_T = x \oplus y \\](https://www.zhihu.com/equation?tex=s_0+%3D+x%2C%5Cquad+s_1+%3D+x+%5Coplus+a_1%2C%5Cquad+%5Cdots%2C%5Cquad+s_T+%3D+x+%5Coplus+y+%5C%5C)
2. **获取最终奖励**：调用冻结的 Reward Model：  
    ![R = r_\phi(x, y) \\](https://www.zhihu.com/equation?tex=R+%3D+r_%5Cphi%28x%2C+y%29+%5C%5C) （中间步骤无奖励，即 ![r_t = 0](https://www.zhihu.com/equation?tex=r_t+%3D+0) for ![t < T](https://www.zhihu.com/equation?tex=t+%3C+T)）
3. **计算回报（Return）**：  
    ![\hat{R}_t = \sum_{k=t}^{T} \gamma^{k-t} r_k = \gamma^{T - t} R \\](https://www.zhihu.com/equation?tex=%5Chat%7BR%7D_t+%3D+%5Csum_%7Bk%3Dt%7D%5E%7BT%7D+%5Cgamma%5E%7Bk-t%7D+r_k+%3D+%5Cgamma%5E%7BT+-+t%7D+R+%5C%5C) 因为只有最后一步有奖励。回报序列 ![\hat{R}_0, \hat{R}_1, ..., \hat{R}_T](https://www.zhihu.com/equation?tex=%5Chat%7BR%7D_0%2C+%5Chat%7BR%7D_1%2C+...%2C+%5Chat%7BR%7D_T) 构成目标值。
4. **计算优势（Advantage）**：  
    ![A_t = \hat{R}_t - V_\psi(s_t), \quad t = 0, 1, ..., T-1 \\](https://www.zhihu.com/equation?tex=A_t+%3D+%5Chat%7BR%7D_t+-+V_%5Cpsi%28s_t%29%2C+%5Cquad+t+%3D+0%2C+1%2C+...%2C+T-1+%5C%5C) 表示：**在状态 ![s_t](https://www.zhihu.com/equation?tex=s_t) 下执行动作 ![a_t](https://www.zhihu.com/equation?tex=a_t)，比“平均水平”好多少**。
5. **保存“旧”值**：将当前策略的 log-prob 和评论家的 value **detach**，作为阶段 2 的基准（即“old policy”和“old critic”）。

伪代码（阶段 1）

```
trajectories = []

for x in prompts:  # x: [L_x]
    # 1. 用当前策略生成回复 y 和 log-prob
    y, logprobs = policy_model.generate_with_logprobs(x)  # y: [T], logprobs: [T]

    # 2. 构建状态序列 s_0 ... s_T
    states = [torch.cat([x, y[:t]]) for t in range(len(y) + 1)]  # len = T+1

    # 3. 用当前评论家估计每个状态的价值
    values = torch.stack([critic_model(s) for s in states])  # [T+1]

    # 4. 奖励模型打分（仅最终奖励）
    R = reward_model(x, y)  # scalar

    # 5. 计算回报：R_t = γ^{T−t} * R
    T_len = len(y)
    returns = torch.zeros(T_len + 1)
    returns[T_len] = R
    for t in reversed(range(T_len)):
        returns[t] = gamma * returns[t + 1]

    # 6. 计算优势：A_t = R_t - V(s_t)，仅对 t=0..T-1 有效
    advantages = returns[:-1] - values[:-1]  # [T]

    # 7. 保存“旧”值（detach 阻断梯度）
    trajectories.append({
        'x': x,
        'y': y,
        'logprobs_old': logprobs.detach(),      # [T]
        'values_old': values.detach(),          # [T+1]
        'advantages': advantages.detach(),      # [T]
        'returns': returns.detach()             # [T+1]
    })
```

> ✅ 此阶段结束时，我们得到一个**固定的数据集**，后续训练将在此数据上多次迭代。

### 阶段 2：策略与评论家更新（Policy & Critic Learning）

目标:利用阶段 1 收集的固定轨迹数据，**更新策略模型（Policy）和评论家模型（Critic）**，使得：

* 策略更倾向于选择高优势的动作；
* 评论家更准确地预测未来回报；
* 同时通过 **PPO-clip** 和 **KL 正则**防止策略突变或偏离合理语言分布。

参与模型与接口

![](https://pic1.zhimg.com/v2-69fe4aa53ef578b8b94ee4163a93d737_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='613' height='178'></svg>)

核心计算逻辑

1. **策略损失（PPO-Clip）**  
   定义概率比：  
    ![r_t(\theta) = \frac{\pi_\theta(a_t | s_t)}{\pi_{\text{old}}(a_t | s_t)} = \exp\left( \log \pi_\theta(a_t|s_t) - \log \pi_{\text{old}}(a_t|s_t) \right) \\](https://www.zhihu.com/equation?tex=r_t%28%5Ctheta%29+%3D+%5Cfrac%7B%5Cpi_%5Ctheta%28a_t+%7C+s_t%29%7D%7B%5Cpi_%7B%5Ctext%7Bold%7D%7D%28a_t+%7C+s_t%29%7D+%3D+%5Cexp%5Cleft%28+%5Clog+%5Cpi_%5Ctheta%28a_t%7Cs_t%29+-+%5Clog+%5Cpi_%7B%5Ctext%7Bold%7D%7D%28a_t%7Cs_t%29+%5Cright%29+%5C%5C) PPO 损失为：  
    ![\mathcal{L}^{\text{PPO}} = \mathbb{E}_t \left[ \min\left( r_t(\theta) A_t,\ \text{clip}(r_t(\theta), 1-\epsilon, 1+\epsilon) A_t \right) \right] \\](https://www.zhihu.com/equation?tex=%5Cmathcal%7BL%7D%5E%7B%5Ctext%7BPPO%7D%7D+%3D+%5Cmathbb%7BE%7D_t+%5Cleft%5B+%5Cmin%5Cleft%28+r_t%28%5Ctheta%29+A_t%2C%5C+%5Ctext%7Bclip%7D%28r_t%28%5Ctheta%29%2C+1-%5Cepsilon%2C+1%2B%5Cepsilon%29+A_t+%5Cright%29+%5Cright%5D+%5C%5C)

* 若 ![A_t > 0](https://www.zhihu.com/equation?tex=A_t+%3E+0)：鼓励增加动作概率，但最多增加 ![(1+\epsilon)](https://www.zhihu.com/equation?tex=%281%2B%5Cepsilon%29) 倍；
* 若 ![A_t < 0](https://www.zhihu.com/equation?tex=A_t+%3C+0)：鼓励减少概率，但最多减少到 ![(1-\epsilon)](https://www.zhihu.com/equation?tex=%281-%5Cepsilon%29) 倍。

1. **KL 散度正则（防止语言退化）**  
    ![\mathcal{L}^{\text{KL}} = \beta \cdot \mathbb{E}_t \left[ \log \pi_\theta(a_t|s_t) - \log \pi_{\text{ref}}(a_t|s_t) \right] \\](https://www.zhihu.com/equation?tex=%5Cmathcal%7BL%7D%5E%7B%5Ctext%7BKL%7D%7D+%3D+%5Cbeta+%5Ccdot+%5Cmathbb%7BE%7D_t+%5Cleft%5B+%5Clog+%5Cpi_%5Ctheta%28a_t%7Cs_t%29+-+%5Clog+%5Cpi_%7B%5Ctext%7Bref%7D%7D%28a_t%7Cs_t%29+%5Cright%5D+%5C%5C)

* ![\pi_{\text{ref}}](https://www.zhihu.com/equation?tex=%5Cpi_%7B%5Ctext%7Bref%7D%7D) 是冻结的 SFT 模型；
* ![\beta](https://www.zhihu.com/equation?tex=%5Cbeta) 控制正则强度（如 0.01~0.1）。

1. **评论家损失（Value MSE）**  
    ![\mathcal{L}^{\text{value}} = \mathbb{E}_t \left[ \left( V_\psi(s_t) - \hat{R}_t \right)^2 \right] \\](https://www.zhihu.com/equation?tex=%5Cmathcal%7BL%7D%5E%7B%5Ctext%7Bvalue%7D%7D+%3D+%5Cmathbb%7BE%7D_t+%5Cleft%5B+%5Cleft%28+V_%5Cpsi%28s_t%29+-+%5Chat%7BR%7D_t+%5Cright%29%5E2+%5Cright%5D+%5C%5C)

* 目标是让评论家准确预测阶段 1 计算出的回报 ![\hat{R}_t](https://www.zhihu.com/equation?tex=%5Chat%7BR%7D_t)。

1. **总损失**：  
    ![\mathcal{L}_{\text{total}} = -\mathcal{L}^{\text{PPO}} + \beta \cdot \text{KL} + c_1 \cdot \mathcal{L}^{\text{value}} \\](https://www.zhihu.com/equation?tex=%5Cmathcal%7BL%7D_%7B%5Ctext%7Btotal%7D%7D+%3D+-%5Cmathcal%7BL%7D%5E%7B%5Ctext%7BPPO%7D%7D+%2B+%5Cbeta+%5Ccdot+%5Ctext%7BKL%7D+%2B+c_1+%5Ccdot+%5Cmathcal%7BL%7D%5E%7B%5Ctext%7Bvalue%7D%7D+%5C%5C)

伪代码（阶段 2）

```
for epoch in range(K):  # K=2~4，对同一数据集多轮优化
    for traj in trajectories:
        x, y = traj['x'], traj['y']                     # x: [L_x], y: [T]
        logprobs_old = traj['logprobs_old']             # [T]
        advantages = traj['advantages']                 # [T]
        returns = traj['returns']                       # [T+1]

        # --- 1. 策略损失 ---
        logprobs_curr = policy_model.get_logprobs(x, y)  # [T]
        ratio = torch.exp(logprobs_curr - logprobs_old)  # [T]

        surr1 = ratio * advantages
        surr2 = torch.clamp(ratio, 1 - eps, 1 + eps) * advantages
        ppo_loss = -torch.mean(torch.min(surr1, surr2))

        # KL 正则（ref_model 冻结）
        with torch.no_grad():
            logprobs_ref = ref_model.get_logprobs(x, y)  # [T]
        kl_loss = torch.mean(logprobs_curr - logprobs_ref)

        policy_loss = ppo_loss + beta * kl_loss

        # --- 2. 评论家损失 ---
        states = [torch.cat([x, y[:t]]) for t in range(len(y) + 1)]
        values_pred = torch.stack([critic_model(s) for s in states])  # [T+1]
        value_loss = F.mse_loss(values_pred, returns)

        # --- 3. 优化 ---
        total_loss = policy_loss + c1 * value_loss
        optimizer.zero_grad()
        total_loss.backward()
        optimizer.step()
```

## 总结：PPO 的设计哲学

* **阶段 1 是“探索”**：用当前策略生成多样回复，用外部信号（RM）和内部估计（Critic）打标签；
* **阶段 2 是“学习”**：在固定数据上保守更新，通过 clip 和 KL 防止“学歪”；
* **Reference Model 是安全网**：确保语言依然流畅、合理；
* **整个流程可迭代**：每轮 PPO 后，策略更强，下一轮采样质量更高。

这种“采样-学习”交替的模式，正是 PPO 能在 LLM 对齐中兼顾**效果、稳定性和安全性**的关键。

## 3. DPO：绕过 RL 的“聪明办法”

DPO（Direct Preference Optimization）发现：**其实不需要显式训练 Reward Model + PPO，可以直接从人类偏好数据中优化策略**。

### DPO 的核心洞察

人类偏好数据是成对的：![(x, y_w, y_l)](https://www.zhihu.com/equation?tex=%28x%2C+y_w%2C+y_l%29)，其中：

* ![x](https://www.zhihu.com/equation?tex=x)：用户输入（prompt）
* ![y_w](https://www.zhihu.com/equation?tex=y_w)：人类偏好的回复（win）
* ![y_l](https://www.zhihu.com/equation?tex=y_l)：较差的回复（lose）

DPO 证明：**最大化人类偏好等价于最小化下面这个损失**：

![\mathcal{L}_{\text{DPO}} = -\mathbb{E}_{(x,y_w,y_l)} \left[ \log \sigma \left( \beta \left( \log \frac{\pi_\theta(y_w|x)}{\pi_{\text{ref}}(y_w|x)} - \log \frac{\pi_\theta(y_l|x)}{\pi_{\text{ref}}(y_l|x)} \right) \right) \right] \\](https://www.zhihu.com/equation?tex=%5Cmathcal%7BL%7D_%7B%5Ctext%7BDPO%7D%7D+%3D+-%5Cmathbb%7BE%7D_%7B%28x%2Cy_w%2Cy_l%29%7D+%5Cleft%5B+%5Clog+%5Csigma+%5Cleft%28+%5Cbeta+%5Cleft%28+%5Clog+%5Cfrac%7B%5Cpi_%5Ctheta%28y_w%7Cx%29%7D%7B%5Cpi_%7B%5Ctext%7Bref%7D%7D%28y_w%7Cx%29%7D+-+%5Clog+%5Cfrac%7B%5Cpi_%5Ctheta%28y_l%7Cx%29%7D%7B%5Cpi_%7B%5Ctext%7Bref%7D%7D%28y_l%7Cx%29%7D+%5Cright%29+%5Cright%29+%5Cright%5D+%5C%5C)

### 这个公式到底在算什么？

* ![\pi_\theta(y|x)](https://www.zhihu.com/equation?tex=%5Cpi_%5Ctheta%28y%7Cx%29)：**当前训练模型在 prompt ![x](https://www.zhihu.com/equation?tex=x) 下生成完整回复 ![y](https://www.zhihu.com/equation?tex=y) 的概率**  
  → 实际计算时，是把 ![y](https://www.zhihu.com/equation?tex=y) 拆成 token 序列，求 $\prod\_t \pi\_\theta(y\_t | x, y\_{
* ![\pi_{\text{ref}}(y|x)](https://www.zhihu.com/equation?tex=%5Cpi_%7B%5Ctext%7Bref%7D%7D%28y%7Cx%29)：**参考模型（SFT 模型）生成 ![y](https://www.zhihu.com/equation?tex=y) 的概率**
* ![\beta](https://www.zhihu.com/equation?tex=%5Cbeta)：温度参数，控制优化强度（越大越激进）

> **通俗理解**：DPO 希望模型对“好回复”的相对概率（相比参考模型）比“坏回复”更高。

### DPO 伪代码

```
for batch in preference_data:
    x, y_w, y_l = batch
    
    # 计算当前模型和参考模型对两个回复的 log 概率
    logp_w = policy_model.log_prob(x, y_w)
    logp_l = policy_model.log_prob(x, y_l)
    ref_logp_w = ref_model.log_prob(x, y_w)
    ref_logp_l = ref_model.log_prob(x, y_l)
    
    # 计算 logits 差
    logits = beta * ((logp_w - ref_logp_w) - (logp_l - ref_logp_l))
    
    # 二分类损失：希望 logits 越大越好
    loss = -F.logsigmoid(logits).mean()
    optimizer.step(loss)
```

> **DPO 本质是一个带参考模型的对比学习（contrastive learning）**，**完全不需要 RL 循环**，所以训练快、稳定。

## 4. GRPO：在 PPO 和 DPO 之间找平衡

### PPO vs DPO：各自的痛

| 方法 | 优点 | 缺点 |
| --- | --- | --- |
| PPO | 支持 online learning（边生成边学），样本利用率高；可结合多种奖励（如安全性、事实性） | 需要训练 4 个模型（Policy, Critic, RM, Reference），流程复杂；RM 质量直接影响效果 |
| DPO | 训练简单，只需 2 个模型（Policy + Reference）；效果接近 PPO | 完全依赖离线（offline）偏好数据；容易过拟合（尤其数据少时）；无法引入动态奖励 |

### GRPO：群体相对优化

GRPO（Group Relative Policy Optimization）的思路是：

> **既然人类经常面对多个选项做判断（比如从 4 个回复中选最好的 2 个），那就直接建模这种“群体偏好”**。

GRPO 的做法

1. 对每个 prompt ![x](https://www.zhihu.com/equation?tex=x)，用当前策略生成 ![K](https://www.zhihu.com/equation?tex=K) 个回复（比如 ![K=4](https://www.zhihu.com/equation?tex=K%3D4)）
2. 根据 Reward Model（或人类）将这些回复分成“好组”和“坏组”
3. 优化目标：**拉大组间差异，缩小组内差异**

### GRPO 损失函数（简化版）

![\mathcal{L}_{\text{GRPO}} = -\mathbb{E}_x \left[ \log \frac{\sum_{y \in \text{good}} \exp(\beta \log \frac{\pi_\theta(y|x)}{\pi_{\text{ref}}(y|x)})}{\sum_{y \in \text{all}} \exp(\beta \log \frac{\pi_\theta(y|x)}{\pi_{\text{ref}}(y|x)})} \right] \\](https://www.zhihu.com/equation?tex=%5Cmathcal%7BL%7D_%7B%5Ctext%7BGRPO%7D%7D+%3D+-%5Cmathbb%7BE%7D_x+%5Cleft%5B+%5Clog+%5Cfrac%7B%5Csum_%7By+%5Cin+%5Ctext%7Bgood%7D%7D+%5Cexp%28%5Cbeta+%5Clog+%5Cfrac%7B%5Cpi_%5Ctheta%28y%7Cx%29%7D%7B%5Cpi_%7B%5Ctext%7Bref%7D%7D%28y%7Cx%29%7D%29%7D%7B%5Csum_%7By+%5Cin+%5Ctext%7Ball%7D%7D+%5Cexp%28%5Cbeta+%5Clog+%5Cfrac%7B%5Cpi_%5Ctheta%28y%7Cx%29%7D%7B%5Cpi_%7B%5Ctext%7Bref%7D%7D%28y%7Cx%29%7D%29%7D+%5Cright%5D+%5C%5C)

这其实是一个**带参考模型的 softmax 分类损失**：希望“好回复”的归一化概率更高。

### GRPO 伪代码

```
for x in prompts:
    # 1. 生成 K 个回复
    responses = [policy_model.generate(x) for _ in range(K)]
    
    # 2. 用 RM 打分并分组（比如 top-2 为 good）
    scores = [reward_model.score(x, y) for y in responses]
    good_mask = get_top_k_mask(scores, k=2)
    
    # 3. 计算每个回复的 log ratio
    ratios = []
    for y in responses:
        logp = policy_model.log_prob(x, y)
        ref_logp = ref_model.log_prob(x, y)
        ratios.append(beta * (logp - ref_logp))
    
    # 4. softmax 分类损失
    logits = torch.stack(ratios)
    loss = F.cross_entropy(logits.unsqueeze(0), target=good_mask)
    optimizer.step(loss)
```

**GRPO 的优势**：

* 保留了 PPO 的 online 生成能力（自己造数据）
* 像 DPO 一样只优化策略模型，无需 Critic
* 对 RM 的依赖比 PPO 弱（只需排序，不要求绝对分数准确）

## 5. 总结：选哪个？

| 方法 | 模型数量 | 是否需要 RM | 是否 RL | 适合场景 |
| --- | --- | --- | --- | --- |
| PPO | 4（Policy, Critic, RM, Ref） | ✅ | ✅ | 高质量对齐，多目标奖励 |
| DPO | 2（Policy, Ref） | ❌ | ❌ | 快速迭代，偏好数据充足 |
| GRPO | 3（Policy, RM, Ref） | ✅（弱依赖） | ⚠️（类 RL） | 平衡效率与效果，支持 online 学习 |

> 强化学习在 LLM 中，早已不是“必须用 PPO”的时代。**DPO 让对齐变得像 SFT 一样简单，GRPO 则试图把 PPO 的灵活性和 DPO 的简洁性结合起来**。

技术在进化，我们的工具箱也在变丰富。选对方法，比盲目堆资源更重要。


---

## 二叉树的前序遍历，中序遍历和后序遍历分别有什么作用？

`link: https://www.zhihu.com/question/22031935/answer/1963992121167028629 · created: 1761032210`


## 1. 前言吐槽

刷过 Leetcode 的牛马都知道二叉树是逃不过去的坎儿，尤其是遍历，修改等等。遍历又分成层序遍历，前序中序后序遍历，然后实现方法又分成迭代和递归，每次去敲代码都因为一些细节卡死，比如什么时候打印，什么时候修改，好不容易代码通过了，隔了一段时间，好家伙又忘记怎么写的了

本质上还是对于二叉树理解不够透彻，就比如很长一段时间后，很可能根本不记得前中后序的遍历规则是什么了。这篇文章就是基于刷过的各种文章来做个小结，以便未来忘记了再来快速回忆一下（希望不要再回忆了。。。）

## 2. “序”到底是什么

序 顾名思义就是顺序。而要有顺序，就得有参考坐标。一般来说，我们会把二叉树的根节点作为参考坐标，类似的每次递归子二叉树的时候，对应二叉树的根节点也就是当前递归轮次的参考坐标了。

参考坐标很好理解，那为什么分成前中后序呢？为什么不是先后（左右）序呢？

“中”序的中又是指什么呢？这些概念最近刷到文献[1]后才豁然开朗。

我们以下面二叉树的节点 2 为例。可以看到遍历节点 2 通常会有 3 次：

* 第一次是从根节点 1 到节点 2
* 第二次是节点 2 到节点 3，然后节点 3 **返回**到节点 2
* 第三次是节点 4 **返回** 到节点 2

![](https://picx.zhimg.com/v2-d2e0c14f5f8fa91e4c46316f55bfca74_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='722' height='800'></svg>)

对于每个节点都是会经过 3 次，即使是节点 7 也是如此，即使它的左右节点都是空，但是也可以看作从 左右空节点返回节点 7。

至此，其实就是前中后序的由来（或者一种方便理解的解释）。第一次进过节点就是该节点的前序，第二次就是中序，第三次就是后序。

> 一个比较有意思的说法：所以对于任意一个节点而言，后序包含的信息量是最大的，还是以节点 2 为例，它的前序只有节点 1 的信息，中序增加了节点 3 （及其子节点）的信息，后序增加了节点 4（及其子节点）的信息。

## 3. 递归遍历

了解了前中后序的含义后，那我们自然也就是到为什么前序遍历打印的结果是（根节点，左节点，右节点）了，因为打印操作是在第一次进入该节点执行的，对应到代码就是：

```
def traverse(root):
 if not root:
  return None
 
 # 第一次进入该节点
 print(root.val)
 traverse(root.left)
 traverse(root.right)
```

那中序呢？很简单，就是在第二次进入节点的时候执行的操作

```
def traverse(root):
 if not root:
  return None
 
 # 第一次进入该节点
 traverse(root.left)
 # 第二次进入该节点
 print(root.val)
 traverse(root.right)
```

后序同理

```
def traverse(root):
 if not root:
  return None
 
 # 第一次进入该节点
 traverse(root.left)
 # 第二次进入该节点
 traverse(root.right)
 # 第三次进入该节点
 print(root.val)
```

你可能会说这很简单啊，只要记住前中后序的对应递归代码就好了呀。但是对我而言，上面的逻辑能够帮助我跳脱出递归的代码逻辑，从一个更高的维度来写代码，逻辑会更加清晰，有一种呼吸道新鲜空气的感觉，而不是陷在递归的逻辑沼泽里难以呼吸（有同感的吗 hh）

## 4. 迭代遍历

除了递归遍历，另一种遍历方法是迭代遍历，就和 for 循环一样显式的写出来遍历过程，这种遍历方式更好理解，在求解二叉树的深度的时候会有奇效

```
from collections import deque
def iterative(root):
 Q = deque(root)
 depth = 0
 while Q:
  num = len(Q) # 当前层的队列长度
  for i in range(num):
   node = Q.popleft()
   if Q:
    # 下面两行会把左右节点都插入到队列，但有可能是空节点
    # 所以为了下一轮遍历，需要判断试一下是否为空节点
    Q.append(node.left)
    Q.append(node.right)
  depth += 1
 return depth
```

迭代遍历通常会用到 deque (double-ended queue 双端队列)，为了实现层序遍历，那逻辑很简单，就是先把第 i 层（从 0 开始）的所有节点插入到队列里，并记下数量 ![n_i](https://www.zhihu.com/equation?tex=n_i)，然后遍历这些数量的节点。 遍历第 i 层节点的同时继续把这些节点的左右节点插入到队列了，遍历完了就是就等价于把第![i+1](https://www.zhihu.com/equation?tex=i%2B1)层节点也都插入到队列里了，类似地也记录下这一层的节点数量，重复迭代就实现了层序遍历。

有个特别注意的点：`Q.append(node)`是往队列右侧增加新的节点，为了保证顺序一致，我们需要用`node = Q.popleft()`来从左边取节点，如果用`node = Q.pop()`就是从右边取节点，这样就会出现逻辑错误

至此，你了解了二叉树的递归遍历，迭代遍历，前中后序遍历。感兴趣的可以试试用迭代遍历实现前中后序遍历

## 参考：

[1] [https://labuladong.online/algo/essential-technique/binary-tree-summary-2/#%E4%BA%8C%E5%8F%89%E6%A0%91%E7%9A%84%E9%87%8D%E8%A6%81%E6%80%A7](https://link.zhihu.com/?target=https%3A//labuladong.online/algo/essential-technique/binary-tree-summary-2/%23%25E4%25BA%258C%25E5%258F%2589%25E6%25A0%2591%25E7%259A%2584%25E9%2587%258D%25E8%25A6%2581%25E6%2580%25A7)


---

## AI 赋能后科研模式发生了什么改变？

`link: https://www.zhihu.com/question/6486140721/answer/1962634110565618369 · created: 1760708435`


作为研究AI方向的牛马，日常就是和论文、模型、实验打交道。不得不吐槽，AI 领域的更新节奏实在是太快了，新架构、新算法、新 benchmark 几乎每天都有。过去还能靠精读几篇论文、手动复现一个模型来跟上节奏，如今这种方式几乎不可能持续，科研从“钻透一个方向”，变成了“尽快理解、实现、再表达”的循环。

问题是，这个过程现在也被各种 AI 工具拆得越来越碎。理解论文要用 PDF 阅读模型，写代码得换代码助手，画算法图又得调用生成模型。每个工具各有长处，但它们之间却不会没有语义和记忆延续。于是我变成了“上下文搬运工”：每切换一次，就得重新交代研究背景、变量定义和算法意图。久而久之，效率看似提高了，思维反而被割裂。AI 帮我产出了更多结果，却没真正理解我在研究什么。

所以我一直在想，科研+ AI 到底该是什么样？

**理想的状态，不该只是“能干更多事”，而是能在同一个语境里理解我——从论文到代码，再到图示，语义一致、逻辑连贯。**但用了国内外的一些AI，总是有些差强人意。某包能力全，但理解不行；某D理解强，但能力少。直到最近试到通义 AI 的新一批模型更新，我去试了一番，才第一次看到这个想法有被实现的可能。

通义 AI 背靠的Qwen系列模型一直是开源模型体系里最“科研友好”的一支。从早期版本开始就坚持开放权重和技术报告，在中文语义理解、多模态推理上表现突出，也广泛被学界用于算法验证和任务定制。这一轮更新后，它的定位更彻底地从“大语言模型”进化成了“全模态科研接口”。核心模型 Qwen3-Omni 能在同一语义空间理解文本、图像、音频、视频，做到真正的跨模态推理；Qwen-Image-Edit 能直接生成论文风格的算法示意图；通义万相 2.5 则能把算法逻辑变成动态讲解视频。

<https://xg.zhihu.com/plugin/cbc412c7d0ae0d73b52a5d23d3876f73?BIZ=ECOMMERCE>

对我而言，这种“语义整合”的变化比任何单一功能升级都更重要。它意味着科研的整个流程——理解、实现、表达——终于可以在一个系统里连贯地完成，而不必再在多个工具之间来回切换。

为了验证它在科研学习中的实用性，我选择了一个我最近在关注的主题：**speculative decoding**。

这是近一年来生成式模型领域的重要技术，它通过预测并行生成多个候选token，从而显著提升推理效率。

我想看看：如果让通义 AI一条龙服务式地来解释概念、实现代码、并可视化算法，会是怎样的效果。

---

## **一个没有期待的尝试，却实现了理想的解决**

**Prompt 1：概念性理解**

```
请详细解释 speculative decoding 的基本思想，
包括它与标准自回归生成的区别，
以及这种方法如何在不牺牲模型质量的情况下提升推理速度。
请使用科研者能快速理解的方式进行讲解，
同时补充一个简洁的数学形式描述。
```

首先，我让通义AI开始对speculative decoding进行理解，它从四个方面由浅入深地展开了介绍和解释分析，可以非常快速地给我一个概要性的理解。

![](https://picx.zhimg.com/v2-f1a20dc6c4993088390e015862bd479c_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='972' height='2506'></svg>)

纯文字不够直观，我希望能通过流程图的形式更加明了地理解算法步骤。并在这过程里，用同样的prompt测试了不同的主流 AI 工具，包括文心一言、豆包和 ChatGPT。具体效果可以看下面的截图。

```
请一次性给出 Speculative decoding 的概要性原理介绍，代码实现，算法示意图生成
```

通过对比，可以看到通义 AI生成的算法示意图更加丰富准确，不仅包含了丰富的步骤，还带有具体的示例。而其他的 AI 工具则是敷衍了事地绘制了非常简单的流程图，导致对帮助理解算法原理的作用只能说甚微。

* 通义 AI清晰明了的给出了详细的流程示意图，输入是“Today”，draft 模型和 target 模型分别有输出，并且有验证。最后也附上了示意图说明帮助理解。

![](https://picx.zhimg.com/v2-2b8d93d1f9fe8ba5e8ed91a4455eca67_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='627' height='778'></svg>)

* 豆包本身是会自动去渲染流程图的，但这次没渲染成功。另外生成的算法示意图是非常简单的，并没有清晰展示出算法的细节：

![](https://pic1.zhimg.com/v2-d48d13a4b88db8a9cb33f687ce4d46a7_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2676' height='898'></svg>)

* 文心一言，和豆包一样，多一个字都不想说：

![](https://picx.zhimg.com/v2-9cd128d769d688238a489a19eb8fee53_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1118' height='479'></svg>)

* ChatGPT给出了两个候选，心思很细腻啊，但是 mermaid 格式的流程图和豆包，文心一言一样都很简单，聊胜于无吧。方案 B 需要我额外再去输入指令生成图片：

![](https://picx.zhimg.com/v2-8b29f4aa48e2651d45e7958bfd63063a_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='941' height='801'></svg>)

从这次测试的结果来看，通义 AI 给出的流程示意是最清晰完整。它从输入序列开始，依次展示了草稿模型生成候选 token、主模型并行验证、接受与拒绝的决策逻辑，以及更新上下文的整个过程。相比之下，其他模型的输出往往只展示了两三个节点，忽略了验证和回退环节，这使得算法的核心机制难以被真正理解。

这种结构化的表达方式体现出通义 AI 对算法逻辑从理解到输出解释的专业性。**科研理解从来不只是“看懂定义”，而是要在脑中形成完整的运行路径。**通义 AI 在这一点上做得尤为自然——它不仅准确地捕捉了 speculative decoding 的推理节奏，还让语言描述、逻辑结构和算法流程保持一致。

这种一致性，也为后续的代码生成打下了基础。如果模型在解释阶段就能形成连贯的逻辑框架，那么在实现阶段，它就有机会让理论与代码同样连贯。这也是我继续测试下一个 prompt 的原因——让它直接生成一个最小可运行的 speculative decoding 实现。

---

## **实战检验：用speculative decoding验证一体化能力**

在理解了原理之后，我进一步想通过它能用示例让我实现一站式实现。

于是，我输入了第二个 prompt。

**Prompt 2：代码实现**

```
请使用 Python 实现一个简化版 speculative decoding 示例。
假设有一个主模型和一个 draft 模型，
主模型用于验证 draft 模型的候选 token，
示例中展示两者的交互逻辑即可，
不需要依赖真实的大语言模型 API。
请用注释解释每个关键步骤。
```

很多时候我们只知道要做什么东西，但是代码具体的架构设计不是很清楚。**通义AI很贴心地支持自动优化 prompt**，下面是优化前后的 prompt，可以看到它能直接定义清楚了代码的架构和模块等等，逻辑更加清晰了，而且我们也可以在这个基础上提前检查需求是否准确。

![](https://picx.zhimg.com/v2-a89eff4ff053ef6a46db62c44873d271_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='815' height='250'></svg>)![](https://picx.zhimg.com/v2-5d797d870ea058187f00edb717d50f00_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='893' height='276'></svg>)

下面是基于优化后的 prompt生成的代码，可以看到很准确地理解了指令，并且 prompt 中设计了 MainModel和 DraftModel，整个代码逻辑非常清晰：

```
"""
简化版 Speculative Decoding 示例

本示例模拟了 speculative decoding 的核心交互逻辑：
- DraftModel（草稿模型）快速生成候选 token。
- MainModel（主模型）验证这些候选 token 是否可接受。
- 每轮只生成一个 token（k=1），便于理解基本流程。
"""

import random


class MainModel:
    """
    主模型（Target Model）：负责高质量地验证 token。
    在真实场景中，该模型通常较大、较慢，但生成质量高。
    """

    def __init__(self, seed=42):
        # 设置随机种子以保证可复现性（仅用于演示）
        random.seed(seed)

    def validate_token(self, token, context):
        """
        验证草稿模型生成的 token 是否可被主模型接受。

        为简化，本示例采用概率性接受策略：
        - 如果 token 与主模型“期望”的 token 一致，则接受；
        - 否则以一定概率拒绝（模拟分布差异）。

        在真实 speculative decoding 中，此处会执行拒绝采样逻辑。

        参数:
            token (int): 待验证的候选 token ID。
            context (list): 当前已生成的 token 序列（上下文）。

        返回:
            bool: True 表示接受，False 表示拒绝。
        """
        # 模拟主模型对下一个 token 的“偏好”：
        # 为简单起见，我们假设主模型期望的 token 是 (sum(context) + 1) % 10
        expected_token = (sum(context) + 1) % 10

        # 如果草稿 token 与期望一致，直接接受
        if token == expected_token:
            return True

        # 否则，以较低概率接受（模拟拒绝采样中的“小概率接受”）
        # 这里仅为演示，实际中会基于 p(x)/q(x) 计算接受概率
        accept_prob = 0.2  # 20% 概率接受错误 token
        return random.random() < accept_prob


class DraftModel:
    """
    草稿模型（Draft Model）：快速生成候选 token。
    在真实场景中，该模型通常较小、较快，但质量略低。
    """

    def __init__(self, seed=123):
        random.seed(seed)

    def generate_tokens(self, context, num_tokens=1):
        """
        基于当前上下文生成若干候选 token。

        为简化，本示例每次只生成一个 token（num_tokens=1），
        且生成逻辑为：随机选择一个接近主模型期望的值。

        参数:
            context (list): 当前已生成的 token 序列。
            num_tokens (int): 要生成的 token 数量（本示例固定为 1）。

        返回:
            list: 生成的候选 token 列表（长度为 num_tokens）。
        """
        # 草稿模型“猜测”主模型可能喜欢的 token
        # 简单策略：基于上下文和一点噪声生成
        base = (sum(context) + 1) % 10 if context else 0
        # 加入 ±1 的扰动，模拟草稿模型的不完美
        candidate = (base + random.choice([-1, 0, 1])) % 10
        return [candidate]


def main():
    """
    主程序：演示 speculative decoding 的三轮交互过程。
    """
    # 初始化模型
    main_model = MainModel(seed=42)
    draft_model = DraftModel(seed=123)

    # 初始上下文（可视为 prompt）
    context = [0]  # 假设初始 token 为 0

    print("初始上下文:", context)
    print("-" * 50)

    # 执行三轮 speculative decoding
    for round_num in range(1, 4):
        print(f"第 {round_num} 轮:")

        # 步骤 1: 草稿模型生成一个候选 token
        candidate_tokens = draft_model.generate_tokens(context, num_tokens=1)
        candidate = candidate_tokens[0]
        print(f"  草稿模型生成候选 token: {candidate}")

        # 步骤 2: 主模型验证该候选 token
        is_accepted = main_model.validate_token(candidate, context)
        print(f"  主模型验证结果: {'接受' if is_accepted else '拒绝'}")

        # 步骤 3: 根据验证结果更新上下文
        if is_accepted:
            context.append(candidate)
            print(f"  接受 token，当前上下文更新为: {context}")
        else:
            # 在真实 speculative decoding 中，此时会从修正分布中重新采样一个 token
            # 为简化，这里我们直接使用主模型“期望”的 token
            fallback_token = (sum(context) + 1) % 10
            context.append(fallback_token)
            print(f"  拒绝候选，回退到主模型推荐 token: {fallback_token}")
            print(f"  当前上下文更新为: {context}")

        print("-" * 50)


if __name__ == "__main__":
    main()
```

生成的代码非常简洁，把一些主要模块抽象出来实现了，对于理解前面的公式和概念非常有帮助。我们可以让模型在此基础上提供基于 Huggingface 的可运行的版本，输入如下简短的 prompt即可：

```
基于 Huggingface 实现可运行的版本，选择合适的 MainModel 和 DraftModel
```

因为最终生成的回复内容解决了 prompt 的所有需求。不过因为回复较长，所以内容以截图或者文本形式分成了不同部分。

* 首先可以看到回复内容完成了基于 huggingface 实现的要求，还提供了依赖安装方法。而且还推荐使用了Gemma 系列主模型和 draft 模型。

![](https://pic1.zhimg.com/v2-55ce2c98b5e9cbc45e15cfdb6da7fcc6_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='742' height='385'></svg>)

* 完整代码

```
"""
基于 Hugging Face Transformers 的 Speculative Decoding 简化实现

说明：
- MainModel: google/gemma-2b-it（目标模型，高质量）
- DraftModel: TinyLlama/TinyLlama-1.1B-Chat-v1.0（草稿模型，快速）
- 每轮草稿模型生成 1 个候选 token，主模型验证是否接受
- 使用 logits 计算接受概率（简化版拒绝采样）
- 仅用于教学演示，未实现完整 speculative decoding（如多 token 并行验证）
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import random

# 设置设备（自动选择 GPU 或 CPU）
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"使用设备: {device}")

# ==============================
# 1. 加载主模型（Target Model）
# ==============================
print("正在加载主模型 (Gemma-2b) ...")
main_model_name = "google/gemma-2b-it"
main_tokenizer = AutoTokenizer.from_pretrained(main_model_name, trust_remote_code=True)
main_model = AutoModelForCausalLM.from_pretrained(
    main_model_name,
    torch_dtype=torch.float16 if device == "cuda" else torch.float32,
    low_cpu_mem_usage=True,
    trust_remote_code=True
).to(device).eval()

# ==============================
# 2. 加载草稿模型（Draft Model）
# ==============================
print("正在加载草稿模型 (TinyLlama) ...")
draft_model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
draft_tokenizer = AutoTokenizer.from_pretrained(draft_model_name, trust_remote_code=True)
# 确保草稿模型 tokenizer 与主模型兼容（此处仅用于生成候选，不严格对齐）
draft_model = AutoModelForCausalLM.from_pretrained(
    draft_model_name,
    torch_dtype=torch.float16 if device == "cuda" else torch.float32,
    low_cpu_mem_usage=True,
    trust_remote_code=True
).to(device).eval()

# 添加 pad_token（如果缺失）
if draft_tokenizer.pad_token is None:
    draft_tokenizer.pad_token = draft_tokenizer.eos_token
if main_tokenizer.pad_token is None:
    main_tokenizer.pad_token = main_tokenizer.eos_token

# ==============================
# 3. 辅助函数：从 logits 采样 token
# ==============================
def sample_token(logits, temperature=1.0):
    """从 logits 中采样一个 token ID"""
    probs = torch.softmax(logits / temperature, dim=-1)
    token_id = torch.multinomial(probs, num_samples=1).item()
    return token_id

# ==============================
# 4. Speculative Decoding 主循环
# ==============================
def speculative_decode(
    prompt: str,
    main_model, main_tokenizer,
    draft_model, draft_tokenizer,
    max_new_tokens: int = 10,
    draft_k: int = 1,  # 每轮草稿生成 token 数（简化为 1）
    temperature: float = 1.0
):
    """
    简化版 speculative decoding 实现（k=1）
    """
    # 编码初始 prompt
    input_ids = main_tokenizer.encode(prompt, return_tensors="pt").to(device)
    generated_ids = input_ids.clone()

    print(f"\n初始提示: {prompt}\n")
    print("生成过程:")

    for step in range(max_new_tokens):
        # --- 草稿阶段：用草稿模型生成 1 个候选 token ---
        with torch.no_grad():
            draft_outputs = draft_model(generated_ids)
            draft_logits = draft_outputs.logits[:, -1, :]  # 最后一个位置的 logits
            candidate_token = sample_token(draft_logits, temperature)
            candidate_tensor = torch.tensor([[candidate_token]], device=device)
            speculative_ids = torch.cat([generated_ids, candidate_tensor], dim=1)

        # --- 验证阶段：主模型并行计算 logits（当前 + 候选）---
        with torch.no_grad():
            main_outputs = main_model(speculative_ids)
            main_logits = main_outputs.logits[:, -2:, :]  # 倒数第2（当前）和最后（候选）位置

            # 主模型对“当前应生成位置”的 logits（即倒数第2个）
            main_logits_current = main_logits[:, 0, :]
            # 主模型对“候选 token 位置”的 logits（即最后一个）
            main_logits_candidate = main_logits[:, 1, :]

        # --- 拒绝采样：计算接受概率 ---
        # 获取主模型和草稿模型在候选 token 上的概率
        p = torch.softmax(main_logits_candidate, dim=-1)[0, candidate_token].item()
        q = torch.softmax(draft_logits, dim=-1)[0, candidate_token].item()

        # 避免除零
        if q == 0:
            accept_prob = 0.0
        else:
            accept_prob = min(1.0, p / q)

        accepted = random.random() < accept_prob

        if accepted:
            # 接受候选 token
            generated_ids = speculative_ids
            token_str = main_tokenizer.decode([candidate_token], skip_special_tokens=True)
            print(f"[接受] {token_str}")
        else:
            # 拒绝候选，从主模型重新采样
            fallback_token = sample_token(main_logits_current, temperature)
            generated_ids = torch.cat([generated_ids, torch.tensor([[fallback_token]], device=device)], dim=1)
            token_str = main_tokenizer.decode([fallback_token], skip_special_tokens=True)
            print(f"[拒绝 → 重采样] {token_str}")

        # 检查是否生成结束符
        if generated_ids[0, -1].item() == main_tokenizer.eos_token_id:
            print("遇到 EOS，提前结束。")
            break

    # 返回最终生成文本
    output_text = main_tokenizer.decode(generated_ids[0], skip_special_tokens=True)
    return output_text

# ==============================
# 5. 主程序
# ==============================
if __name__ == "__main__":
    prompt = "Once upon a time,"
    
    try:
        result = speculative_decode(
            prompt=prompt,
            main_model=main_model,
            main_tokenizer=main_tokenizer,
            draft_model=draft_model,
            draft_tokenizer=draft_tokenizer,
            max_new_tokens=15,
            draft_k=1,
            temperature=0.7
        )
        print("\n" + "="*50)
        print("最终生成结果:")
        print(result)
    except Exception as e:
        print(f"运行出错: {e}")
        print("可能原因：模型下载失败、显存不足、或网络问题。")
        print("建议：使用更小模型（如 'gpt2' 和 'distilgpt2'）进行本地测试。")
```

* 除了代码，回复内容还主动提供了注意事项。

![](https://pica.zhimg.com/v2-caa4d826d2060ac8827836a3f4501594_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='903' height='1169'></svg>)

我将上面的代码在 Colab 上去运行，的确遇到了回复内容中预先提到的问题，即 Gemma 没有权限访问。

![](https://pica.zhimg.com/v2-7b9276b671169032388f2c31c71d6336_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1446' height='798'></svg>)

我按照建议把模型换成 gpt2 系列后，代码便可正常运行了。

![](https://picx.zhimg.com/v2-76ab93ff7f8b9078fc8fb9ea17a18216_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='935' height='541'></svg>)

整个代码生成过程非常顺畅。**通义 AI 不仅写出了结构清晰、逻辑完整的实现示例，还贴心地提醒了可能遇到的问题和解决方案，感觉就像和一个真正懂算法的同事在讨论细节，既专业又高效。**生成的代码能够直接运行，逻辑和命名也延续了前面的解释，让整个过程保持了连贯的思维流，也省去了我反复切换和沟通。

<https://xg.zhihu.com/plugin/cbc412c7d0ae0d73b52a5d23d3876f73?BIZ=ECOMMERCE>

---

## 从文字到结构，科研的思维链能否完整闭环？

完成了实验代码后，我们还有很重要的一步就是画图，这在如今 LLM 时代尤为重要。某种程度上，好看的算法示意图就是代表一篇论文的颜值，论文审稿过程就像高考语文作文的字，字写得好看，直接就能在审稿人心里加分了，虽然有点讨巧，但是锦上添花也未尝不可。

接下来，我继续通过通义 AI从代码中提取逻辑关系，并自动生成系统结构图。prompt 也很简单，如下所示

**Prompt 3：可视化生成**

```
请根据上面生成的代码和参考图，绘制 speculative decoding 的系统流程图，
展示主模型与 draft 模型之间的交互关系、token 验证路径、以及最终输出的生成过程。
请在图中标出并行预测与验证的关键节点。
```

通义AI还支持支持上传参考图，我从网上搜了3张和 speculative decoding 相关的算法示意图丢给了通义 AI，如下所示

![](https://pic1.zhimg.com/v2-d9cb88ca9d28d0e59f0be7fe9b56bb2c_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1392' height='771'></svg>)

我们把文字 prompt 和三个参考图都丢给通义AI：

![](https://pica.zhimg.com/v2-556d466c1487e7232d1d17ff5cd39ecd_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1944' height='872'></svg>)

生成的图片效果如下， 可以看到这个生成的示意图很好的融合了不同参考图的特点，保留了参考图 1 的 Draft 和 Target Model，图 2 的 prompt（虽然部分文本没有渲染成功，但是不影响提供绘图灵感，这是更重要的点），还保留了图 3 的 parallel 验证示意。我经常会让大模型帮我生成图片给我图片布局的灵感，后续就会用 Drawio 或者 PPT 来细化。

![](https://pica.zhimg.com/v2-f6a640f15b8aae187c8deaa383e35618_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1952' height='544'></svg>)

我也试用了豆包，但是最终生成的效果我只能说它可能是个自由派画家，我给的参考图它是一个都没参考。

![](https://pic1.zhimg.com/v2-2bfeefa2c01de893124d807a7e0b1738_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1220' height='807'></svg>)

这个简单的画图测试再次验证了通义 AI 对于用户指令具有很强的理解和执行能力，实际应用中我们还可以通过细化 prompt 要求来进一步提高画图质量。**而且通义是完全免费的，可以重复画很多次。**我已经把ChatGPT 停掉续费了，省下的钱打算买点好吃的犒劳自己了～

---

## **总结：从碎片到一体，让科研回到连贯的思考**

过去使用 AI 工具辅助科研，最大的痛点是不得不在不同系统之间来回切换。

这并不是选择太多，而是**没有一个模型能同时理解科研的上下文，配合全链路的实现**。

有的擅长读论文、提炼概念，却无法把数学符号与推理过程对齐；有的能写代码，却不了解我想验证的假设；还有的生成图示不错，但根本不懂算法结构。

于是，我只能像管理一组不互通的助手一样，在不同模型之间搬运语义：告诉A模型我在研究什么，再告诉B模型要实现什么，最后还得提醒C模型别画错逻辑。

久而久之，我花在“让工具理解我”的时间，比花在“解决问题”的时间还多。

通义 AI 的更新，让这种碎片化的体验第一次变得连贯。

**它能在同一个语义空间中同时理解文字、公式、代码和结构化逻辑。**

**这意味着科研的三个核心环节——理解、实现、表达——终于可以在一个连续的语境中完成。**

我可以先让它讲清楚一个新技术的机制，再在同一上下文中生成代码原型、绘制结构示意，而不用每一步都从头解释。

这带来的变化并不只是“效率提升”，而是一种久违的顺畅感。

**思维可以从想法自然流向实现，中间不再被工具切断，也不需要反复重写 prompt 去解释研究意图。**

**我终于能把注意力放回问题本身，而不是耗在不同系统之间的语义搬运。**

从这次尝试里，我更确定一件事：

**真正好的科研 AI，不在于功能有多全，而在于它能否理解科研者的思维方式，让工作流保持连贯、减少切换带来的割裂感。**

也许每个人最终都会找到自己顺手的系统——关键在于，让它成为一个**连续的语义空间**，而不是一堆孤立的工具。对我来说，通义 AI 在这方面的体验是比较符合我预期的产品。

<https://xg.zhihu.com/plugin/cbc412c7d0ae0d73b52a5d23d3876f73?BIZ=ECOMMERCE>


---

## 从门户时代的信息互联，到移动时代的服务革命的飞跃，如今智能时代正在催生哪些新的产业浪潮呢？

`link: https://www.zhihu.com/question/1944814063214391851/answer/1945900306283078811 · created: 1756718786`


> 从信息互联到智能时代，大模型与Agent正重新定义企业的生产关系和产业运作逻辑。未来的竞争，不再是模型参数的较量，而是谁能率先把AI组织成可靠的智能体群体。

回望过去三十年，科技浪潮一波接一波。门户时代的信息互联，让信息第一次在大规模范围内自由流动；移动时代的服务革命，则把服务触达到每个人的指尖。而今天，我们正处在智能时代的起点。大模型、智能体（Agent）以及新的算力基础设施，正在重新定义企业的生产关系和产业的运作逻辑。

在刚刚召开的百度云智大会上，分享了很多方面的创新和产品，包括 **AI基础设施百舸、智能体平台千帆、Agent即服务、AI Coding。**我看到一个非常清晰的信号：**智能化正在从“模型能力”转向“Agent 化的产业共识”**。换句话说，未来的竞争，不是看谁的模型参数更多，而是谁能率先把 AI 组织成可靠的智能体群体。这一点，也和国务院近期发布的“AI+”行动指导意见高度契合——政策层面明确提出，要推动人工智能与经济社会各领域深度融合，加快形成新质生产力。

---

**从开幕式看趋势：百舸与千帆**  
在大会开幕式上，百度副总裁沈抖的演讲中着重介绍了两个平台：**百舸、千帆**。  
百舸是新的算力与系统基础设施。大会发布的百舸AI 计算平台 5.0，强化了高密度超节点、分布式 KV Cache、MoE 专家路由优化等能力。这些听上去偏技术，但背后的含义是：在智能时代，算力基础设施的使命不再只是“降本增效”，而是直接为 Agent 提供高效、可扩展的推理和协作支持。

![](https://pic1.zhimg.com/v2-f9444623a727e642506808a6fc62a6a3_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2544' height='918'></svg>)

千帆是大模型与 Agent 的开发平台。它把模型调用、精调、工具编排、数据治理打包成一站式服务，企业可以直接基于千帆来开发、部署和管理自己的智能体。这也是百度提出“Agent 即服务”的出发点。

![](https://pic1.zhimg.com/v2-594e5e758f84ac6639a05a32da4d56fa_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2708' height='1016'></svg>)

在我看来，这二者为 Agent 的发展提供了强有力的支撑：百舸是算力与系统层的底座，用来处理异构资源、推理并发、稳定性这些基础能力；千帆是一站式的开发与运营平台，从模型管理、数据治理到智能体编排、评测与上线，提供了一条贯通的工具链。它们的角色更像“公共基础设施”，不是叙事的终点，而是让后续“把任务交给 Agent”变得现实的前提。

---

**什么是 Agent 即服务（AaaS）？**

很多人可能会疑惑：既然大模型 API 已经很强了，为什么还要强调 Agent？我的理解是，区别在于 **API 给的是“答案”，而 Agent 给的是“结果”。**

举个例子，到了 Agent 阶段，企业希望的是把整个任务链交出去：营销不是只写广告词，而是要能生成多个版本、自动投放、实时监测与复盘；客服不是只回复一句话，而是要能联动工单系统，关单才算结束；研发流程也不只是检索论文，还要能发起计算任务、收集结果并沉淀知识。  
**Agent 即服务（AaaS）**要做的，是把这种“从触发到闭环”的工作方式标准化。企业在千帆上用角色模板和组件组合自己的智能体，把业务数据、工具和权限接进去，得到的是一个可以长期运行、可观察、可治理、能迭代的服务，而不是一次性的展示。平台负责把稳定性、并发、权限、审计这些“难且隐身”的问题收进去，使用方聚焦在业务约束与目标。  
正因如此，Agent 被认为是大模型的下一个应用形态。它不再只是一个“聪明的搜索框”，而是可以直接嵌入企业的运营流程，成为真正的生产力。  
如果说大模型是智能的“大脑”，那么 Agent 就是“有手有脚的数字员工”。它不仅能理解自然语言，还能调用工具、做计划、与其他 Agent 协作，从而完成一项复杂任务。  
“Agent 即服务”并不是指单一的产品，而是一种全新的服务模式。它的核心逻辑是：**企业不再购买单一模型 API，而是直接购买或定制“能够完成某类任务的 Agent 服务”。**  
在大会上展示的一个医疗场景让我印象很深。比如“灵医智惠”，它的定位不是再做一个医疗问答机器人，而是让智能体去帮患者、医生和医院真正衔接起原本割裂的流程。

![](https://picx.zhimg.com/v2-b4898a1f9599dceaa994f588d59c9a28_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2216' height='630'></svg>)

诊前，患者往往最困惑的是“该挂哪一科、找哪位医生”。灵医智惠的智能体可以根据病情描述，结合既往就诊记录和医院科室分布，给出合理的挂号建议。对患者来说，这比单纯的“抢号入口”有价值得多——它减少了跑错科室、来回折腾的情况。  
到了诊中，医生面临的负担是信息太碎。病历在一个系统，检验报告在另一个系统，影像还得单独调。灵医智惠会在后台自动整合这些资料，生成结构化的摘要推送到医生工作台，医生不必再切换多个界面去找信息。更进一步，它还能根据指南知识库，提示可能的临床路径，帮助医生避免遗漏。这里体现的不是“替代医生判断”，而是让医生少花时间在机械的录入和翻找上。  
诊后，智能体的作用同样关键。它可以基于诊断结果自动生成随访计划，提醒患者按时复诊和用药；对于慢病患者，比如糖尿病、高血压，它还能发起定期的健康咨询，收集监测数据并反馈给医生团队。很多医院都有随访部门，但人员有限、覆盖率低，智能体在这里显然能把“长期照护”从口号变成可执行的服务。  
对医院来说，灵医智惠的价值不仅仅是改善患者体验。每一次就诊、随访产生的数据都会沉淀下来，经过脱敏和治理后可以用于科研与质量评估，形成医院自己的知识资产。这对推动科研和优化管理流程，都是长期有利的。  
我觉得这个案例特别能说明 **Agent 即服务**的意义：它不是让模型回答一个问题，而是把一件事从头到尾衔接起来，并且能长期运行。医疗是对可靠性和合规性要求最高的行业之一，能在这里跑通，说明智能体确实具备了“从 demo 走向生产”的能力。  
这也让我更确信，未来产业的竞争点不在于谁的模型答得更漂亮，而在于谁能用智能体稳定、安全地把复杂任务办成事。医疗场景是一个很好的例子：它证明了智能体并不是炫酷的展示，而是真正能够嵌入关键流程，成为生产力的一部分。

---

**我的理解：Agent 服务背后的系统挑战**  
作为一名长期从事 AI 研究的科研人员，我在工作中主要研究大模型推理优化、Mixture-of-Experts (MoE) 的路由机制以及模型架构设计等。站在这个背景下，我特别想强调一点：**Agent 即服务表面上看是应用层的创新，本质上对应着底层系统工程的挑战。**  
为什么这么说？  
当一个企业要运行几十个、上百个 Agent 并发服务时，看似是在解决客服、营销、研发等业务问题，实际上考验的是：

* **算力调度**：如何在 GPU、CPU、边缘节点之间高效分配任务；
* **模型路由**：如何让不同任务调用最合适的基础模型或专精模型，避免成本浪费；
* **缓存与并发**：如何通过 KV Cache 复用、模型驻留和预取机制，降低切换开销；
* **多智能体协作**：如何在保证吞吐量的同时，避免不同 Agent 的逻辑冲突或幻觉放大。

这些问题如果解决不好，Agent 服务很可能只能停留在炫酷的 demo 阶段，难以真正成为企业的生产力。而百度在大会上提出“百舸+千帆”的组合，某种意义上正是想用基础设施和平台层来兜底，让 Agent 能够跑在可控、可扩展的环境里。

---

**国家战略与产业共识：AI+ 的呼应**

![](https://picx.zhimg.com/v2-e06f4851eb6f534ca82a66c919515a0c_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2478' height='954'></svg>)

就在不久前，国务院发布了关于“AI+”的指导意见，提出要推动人工智能赋能经济社会发展各个领域。文件中特别强调了“打造 AI 驱动的新质生产力”，并鼓励企业加快 AI 技术在科技、产业、消费、民生、治理、全球合作等领域的深度应用。  
这与百度在云智大会上展示的 Agent 服务案例高度一致。换句话说，Agent 即服务不仅仅是企业的选择题，更是政策鼓励的方向。在这种背景下，企业如果能率先形成“Agent 化的组织共识”，将可能在未来率先进入新的增长周期。

---

**案例与产品的延伸：从“秒哒”到数字员工**  
除了面向大型企业的行业 Agent，大会还发布了一些面向大众和中小企业的工具。例如“秒哒”，就是一个无代码的应用开发平台。用户只需要一句自然语言描述，比如“请生成一份客户调查问卷”或者“设计一个抽奖系统”，秒哒就能自动生成应用。  
这类工具的价值在于降低了门槛，把“人人都是开发者”从口号变成现实。对于企业来说，它意味着可以快速响应长尾需求；对于个人来说，它则让创意有机会落地为真实可用的应用。

![](https://pic1.zhimg.com/v2-b0063567f1ab13f9aaf600ff1e94099e_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1332' height='1572'></svg>)

我自己也测试了一下，使用起来非常简单，只需要用百度账号登录后，用文字输入自己的需求，秒哒就会自动解析我的需求，生成一个 markdown 文件。

![](https://pic1.zhimg.com/v2-fc3ce8195977f44c710f020f1840c9d7_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2760' height='1548'></svg>)

之后，直接点击【生成应用】就会开始进行应用搭建，整个过程不需要手写一个代码

![](https://picx.zhimg.com/v2-6464254ea3c54d8a7556114d0edc338b_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2474' height='1446'></svg>)

待结束之后就可以直接体验并且发布，而且秒哒非常好的一个功能是可以在微信小程序上也能使用你创建的应用，大家也可以去体验一下我创建的 ToDo 应用。[https://app-5u8rg2ro6neq.appmiaoda.com/](https://link.zhihu.com/?target=https%3A//app-5u8rg2ro6neq.appmiaoda.com/)

![](https://pica.zhimg.com/v2-920acbc667da407b5b04d4aede59d7eb_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2742' height='1548'></svg>)

生成应用的网页界面

![](https://picx.zhimg.com/v2-0bb9060d24124a6fda7cbf6e858fd05a_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2312' height='1594'></svg>)

你也可以通过访问微信小程序使用秒哒生成的应用，这个体验真的就很流畅了

![](https://pic1.zhimg.com/v2-248ddf2795886623566ce8c9dd9c9f0d_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1280' height='2800'></svg>)

如果你觉得创建的应用有什么需要改进的地方也可以继续输入自己的需求，秒哒也可以按照需求进行修改。这是真的人人都能当产品经理了

---

**展望未来：未来的商业格局**  
回到知乎提问的原点：智能时代正在催生怎样的新产业浪潮？  
我的想法是：**未来的竞争不再取决于谁的模型参数更多，而是取决于谁能更快把 AI 组织成可靠的 Agent 群体。** 企业如果仍然停留在“采购 API”的阶段，未来可能会落后；而那些率先完成 Agent 化转型的企业，则会在供应链、营销、研发等环节全面释放新质生产力。  
百度云智大会上提出的“Agent 即服务”，正是这一趋势的缩影。它既回应了国家“AI+”战略的号召，也给出了企业可落地的路径。从算力基础设施（百舸）、到模型平台（千帆）、再到应用层的 Agent 产品，构成了一个相对完整的生态闭环。  
对我个人而言，作为一个研究算力调度和大模型系统优化的科研人员，这次大会让我看到研究与产业之间的契合点：我们在实验室里讨论的 KV Cache 复用、MoE 路由优化、模型预取策略，其实都直接关系到 Agent 服务能否真正跑起来、跑稳、跑快。这让我更确信，未来将是科研与产业深度共振的时代。  
所以，用一句话来总结：**Agent 即服务是智能时代的“电力公司”，它让智能像电一样，随取随用，推动整个社会的生产力跃迁。**


---

## 小红书笔记怎么写？

`link: https://www.zhihu.com/question/322024414/answer/1896974868148368591 · created: 1745054052`


在撰写笔记、教程或技术总结时，我们常常使用 Markdown 来写作，并希望将其发布到社交平台，如小红书、公众号、知乎等。但这些平台往往不支持直接粘贴 Markdown，因此将 Markdown 渲染为图片成为一种通用且视觉友好的方式。

本文介绍一种基于 `Node.js` 的自动化方案：**将 Markdown 转换成 HTML，再用浏览器截图为多张图片，适配小红书的阅读体验。**

### ✨ 应用场景

* 在本地撰写 Markdown，输出高质量截图用于小红书/知乎/公众号；
* 保留公式、代码块、标题等 Markdown 特性；
* 支持语法高亮（highlight.js）和数学公式（KaTeX）；
* 自动分段截图，适配移动端阅读体验。

### 技术方案简介

整个流程包括：

1. 使用 `marked` 将 Markdown 转为 HTML；
2. 使用 `highlight.js` 实现代码高亮；
3. 使用 `KaTeX` 渲染数学公式；
4. 使用 `puppeteer` 启动 Chromium，加载 HTML 并截图；
5. 自动将长文分割成多段图片，适配小红书标准尺寸（如 1250px 高度）。

### ⚙️ 依赖项

请确保你已安装：

* Node.js（推荐版本 ≥ 16）
* npm（Node.js 自带）
* macOS/Linux 系统（Windows 需要额外处理字体路径）

### 项目使用的 NPM 库：

```
npm install marked puppeteer highlight.js katex minimist
```

快速开始

1. 克隆项目

```
git clone https://github.com/marsggbo/markdown2rednote.git
cd markdown2rednote
```

1. 准备你的 Markdown 文件

例如：`how_to_markdown2rednote.md`

1. 运行转换脚本

赋予脚本权限并执行：

```
chmod +x ./md2xhs.sh
./md2xhs.sh how_to_markdown2rednote.md
```

1. 输出结果

脚本会自动：

- 分析并分段渲染 Markdown 内容；

- 在 how\_to\_markdown2rednote./ 目录下生成截图：

- 01.png, 02.png, …, 每段对应一张图；

- 每张图高度自动适配，默认最大为 1250px（小红书推荐尺寸）；

- 最终显示完成提示 ✅。

输出示例

你的输出目录结构类似：

```
how_to_markdown2rednote./
├── 01.png
├── 02.png
├── 03.png
```

Markdown 中使用的图片、代码块、公式都将被正确渲染。

常见问题

1. 没有显示代码高亮？

请确保你已正确引入 highlight.js 样式： - 示例用的是 monokai-sublime 主题； - 可以替换为其他风格（如 atom-one-dark, github, 等）。

1. 数学公式不显示？

确保你写的是 $E = mc^2$ 或 ![f(x) = \int_{a}^{b} x^2dx](https://www.zhihu.com/equation?tex=f%28x%29+%3D+%5Cint_%7Ba%7D%5E%7Bb%7D+x%5E2dx) 这类标准格式，并启用了 KaTeX。

✅ 总结

这种基于 Puppeteer 的截图方案，可以无缝地将 Markdown 转换成清晰、高质量、排版友好的图文内容。尤其适合将技术类笔记、写作内容发布到图文平台，避免重新排版或丢失语义结构。

推荐扩展 - 支持图片圆角和水印； - 多语言语法高亮支持； - 微信公众号图文样式模板； - zip 打包生成所有图片一键分享。

项目地址

GitHub：marsggbo/markdown2rednote

欢迎 Star / Fork / 提 Issue / PR


---

## overleaf 无法编译出 PDF 怎么办？

`link: https://www.zhihu.com/question/592117099/answer/1896934511100536794 · created: 1745044430`


在写科研文稿时，我们经常需要插入结构图、模型图等 PDF 格式的矢量图。但在 Overleaf 中，我遇到了一个较难定位的问题：使用 `\includegraphics` 插入 PDF 图片时，**编译无报错，但无法显示图片甚至生成 PDF 文件失败**。提示如下信息

```
No PDF
This compile didn’t produce a PDF. This can happen if:
There is an unrecoverable LaTeX error. If there are LaTeX errors shown below or in the raw logs, please try to fix them and compile again.
The document environment contains no content. If it’s empty, please add some content and compile again.
This project contains a file called output.pdf. If that file exists, please rename it and compile again.
```

本文记录这一问题的背景、排查过程与最终解决方案，希望对遇到类似问题的用户有所帮助。

## 1. 问题背景

文档中使用如下方式插入图像：

```
\usepackage{graphicx}
\graphicspath{{figures/.../}}

...

\begin{figure}
    \centering
    \includegraphics[width=\linewidth]{prune_structure.pdf}
    \caption{结构化剪枝示意图}
    \label{fig:pruning}
\end{figure}
```

其中 prune\_structure.pdf 是一张矢量格式的图像，在本地查看没有问题,并没有损坏。

## 2. 问题现象

在 Overleaf 中： • 使用 Fast Compile 模式时，文档可以编译成功，但图片显示为空白； • 使用 Normal Compile 模式时，编译直接失败，并提示：

This compile didn’t produce a PDF.

日志中没有明确的错误信息，定位困难。

## 3. 排查过程

以下是我尝试过的排插步骤：

1. 确认路径正确：

* 日志显示图像被正确找到：`File: figures/.../prune_structure.pdf Graphic file (type pdf)`

2. 注释图像代码：

+ 注释掉 figure 环节后，PDF 成功生成，说明问题出在图像本身。

3. 确认 PDF 未损坏：

+ 图片可以在本地打开，也可以在 Overleaf 文件预览中正常显示，说明文件不是损坏的。

4. 加入调试信息：

+ 添加 \listfiles，确认使用的是 XeLaTeX，图像类型正确，依然无法定位问题。

**原因分析**

最后问 chatgpt 和上网查资料，终于找到这个诡异的问题的原因了，就是因为Overleaf 使用 XeLaTeX 编译时，某些 PDF 图像的边界框信息（bounding box / crop box）不规范，可能会导致渲染器加载失败。特别是使用某些工具导出的图（如绘图工具、Python 库等）经常出现这种兼容性问题。这个问题光靠肉眼去检查 PDF 根本不可能看出来。折腾了我一上午这破玩意。

## 4. 解决方案：使用 pdfcrop 清理边界信息

我用的是Macbook，所以好像自带 pdfcrop命令。使用如下命令重新生成裁剪后的 PDF：

```
pdfcrop -xetex prune_structure.pdf
mv prune_structure-crop.pdf prune_structure.pdf
```

这样处理后，重新上传至 Overleaf，即可成功插入图像并正常编译生成 PDF。

每次都这么敲键盘怪累的，我们可以自动化命令简化操作。只需要把下面的代码添加到 .bashrc 或 .zshrc，我用的是后者：

```
# ~/.zshrc
pdfclean() {
    if [ $# -ne 1 ]; then
        echo "Usage: pdfclean <filename.pdf>"
        return 1
    fi
    local input="$1"
    local base="${input%.pdf}"
    pdfcrop -xetex "$input" "${base}-crop.pdf" && mv "${base}-crop.pdf" "$input"
}
```

然后使用：

```
pdfclean prune_structure.pdf
```

即可一键清理图像并替换原文件。

## 5. 总结

当 Overleaf 中插入 PDF 图片后出现“无错误但无法显示”或“编译失败”的现象时，建议优先考虑图片的边界信息问题。使用 pdfcrop -xetex 是一个有效且高效的解决方案，能显著提高在线 LaTeX 平台对 PDF 图像的兼容性。

## 参考

* [https://www.cnblogs.com/Undefined443/p/18191274](https://link.zhihu.com/?target=https%3A//www.cnblogs.com/Undefined443/p/18191274)

### 微信公众号：AutoML机器学习

![](https://picx.zhimg.com/50/v2-87083e55cd41dbef83cc840c142df48a_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='0' height='0'></svg>)

**MARSGGBO♥原创**  
如有意合作或学术讨论欢迎私戳联系~  
邮箱:marsggbo@foxmail.com


---

## 你有什么好书推荐给想要提升自己的人？

`link: https://www.zhihu.com/question/10847707489/answer/106205047404 · created: 1740060304`


### 当大模型成为全民谈资：一本「硬核技术手册」如何成为普通人逆袭的阶梯？

最近，朋友圈被**DeepSeek - R1**强势刷屏。这个号称“让大模型听懂人话”的AI助手，成功让**强化学习（Reinforcement Learning）**，这个曾经高冷的学术名词，摇身一变，成了全民热议的科技热词。

但很多人可能没意识到，这场AI狂欢背后真正的技术推手，正是强化学习（RL）。从AlphaGo以绝对优势碾压人类棋手，到ChatGPT对对话进行微调，再到如今各类大模型展现出“智慧涌现”的现象，RL始终是推动AI进化的核心引擎，在AI的发展进程中扮演着无可替代的关键角色。

普通人难道只能眼巴巴地当这场技术革命的旁观者？答案其实藏在一本被AI圈奉为“中文RL圣经”的神作里——**《动手学强化学习》**。

![](https://picx.zhimg.com/v2-8d1b9c01127287518fe6019e271c593b_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1280' height='2276'></svg>)

### 为什么说这本书能让你「摸透大模型的底层逻辑」？

1. **从「马尔可夫决策过程」到「深度Q网络」——一套打通任督二脉的知识框架**  
   与零散的技术博客不同，这本书以“工程师思维”重新构建知识体系。从最基础的贝尔曼方程推演开始，逐步深入到PPO、SAC等前沿算法，所有章节统一采用标准数学符号，这就避免了初学者陷入“符号地狱”，让学习过程更加顺畅、高效，能够系统地掌握强化学习的知识脉络 。
2. **GitHub星标破万的开源代码库**：每个算法都配备了可一键运行的PyTorch/TensorFlow实现。

[GitHub - boyu-ai/Hands-on-RL: https://hrl.boyuai.com/](https://link.zhihu.com/?target=https%3A//github.com/boyu-ai/Hands-on-RL)

学习者能快速将理论知识转化为实际操作，切实感受算法的运行效果 。

**3. 白嫖党的终极福利**：作者团队相当慷慨，直接放出全书网页版

[初探强化学习](https://link.zhihu.com/?target=https%3A//hrl.boyuai.com/chapter/1/%25E5%2588%259D%25E6%258E%25A2%25E5%25BC%25BA%25E5%258C%2596%25E5%25AD%25A6%25E4%25B9%25A0)

还提供配套PPT/PDF课件，甚至贴心地准备了Jupyter Notebook交互式学习环境。在知识付费盛行的时代，这样的操作宛如一股清流，为学习者提供了极大的便利 。

### 这本书狠在哪？看互联网大厂怎么「用脚投票」

* **阿里达摩院**将其作为内部培训指定教材，足以证明这本书在专业知识和实践指导方面的权威性和实用性，能为专业人员提供有价值的学习内容。
* **字节跳动RL团队**把它列为新人onboarding必读书目，说明这本书对于新入行的人员快速了解和掌握RL知识体系，融入团队工作有着重要的作用。
* 知乎上某微软研究院大佬直言：“国内RL领域，暂时找不到比它更系统的中文教程”。这从侧面反映出这本书在国内RL领域的领先地位，得到了业内资深人士的高度认可。

### 一个「反常识」的真相：RL才是普通人弯道超车的蓝海赛道

当全民都扎堆涌入深度学习领域时，RL领域却存在着巨大的人才断层。根据猎聘数据显示，RL工程师的薪资比普通算法岗高出30%，而岗位竞争比仅为1:5。这意味着在RL领域，不仅就业机会多，而且薪资待遇优厚，竞争压力相对较小 。

这本书最具颠覆性的地方在于，它证明了RL并非数学天才的专属领域。通过“代码驱动理论”的独特设计（比如用蒙特卡洛树搜索讲解AlphaGo原理），哪怕是文科生，也能借助Python代码直观地理解那些最艰深的算法，极大地降低了学习门槛 。

### 为什么我劝你「白嫖之后还是买本纸质书」？

说实话，这可能是出版界最“卑微”的操作了。作者把整本书免费开放给大家阅读，还附赠价值上万元的配套资源。

在这个知识付费疯狂割韭菜的时代，这种“以开源精神做教育”的初心，显得尤为珍贵，值得每个真正想提升技术认知的人用实际行动支持。毕竟，在AI世界这片混沌深海中，我们永远需要这样的“傻瓜式灯塔”，为我们照亮前行的道路 。

**最后说句大实话**：当大模型开始接管重复劳动，人类最后的优势正是“掌握AI进化方法论”的能力。而这本书，或许就是你参与未来智能世界构建的第一张船票，带你开启探索AI世界的大门，掌握核心技术，在未来的智能时代占据一席之地 。


---

## 普通人如何抓住AI这个风口?

`link: https://www.zhihu.com/question/591256543/answer/106181582754 · created: 1740058188`


随着大语言模型（LLM）持续进化，不少人害怕被其取代，实则不必焦虑，新工具诞生总会引发此类担忧，我们要做的是紧跟时代、持续学习，提升自身竞争力。当下大模型推理能力强大，如何借其助力自我提升至关重要，接下来就以 Kimi K1.5 为例探讨。

Kimi K1.5 支持长思考模式，能够更加精准的理解和分析问题，给出更优质的回答。 而且这一功能可以免费无限制体验。本文将结合实际场景，介绍它在学术研究、健康管理两大场景的应用价值，大家可前往网页端和手机 app 端体验使用。

![](https://picx.zhimg.com/v2-a67f02682657b9d00fca648005ac1895_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2136' height='1148'></svg>)

电脑端

![](https://pica.zhimg.com/v2-2cdb395bd40c6918ea2e04f4b7e2f2fd_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1280' height='2800'></svg>)

手机 APP

## 1. 助力学术研究

在学术研究中，我们常常需要阅读和比较多篇论文，以掌握某个领域的技术脉络。然而，面对海量文献，逐一阅读既耗时又费力。Kimi K1.5 的强大之处在于，它可以一次性接收多个论文链接，自动读取并智能解析内容，帮助用户快速掌握核心信息。  
  
例如，现在人人讨论的大语言模型的核心模块就是注意力机制。为了提高效率，出现了很多创新的注意力机制算法，例如原始的 **多头注意力机制（MHA）、和后续改进的MQA 和 GQA** 。下图是三个工作的论文截图。

![](https://pic1.zhimg.com/v2-08a62c0ee920905d4d57ec7b1f3c1c0a_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='4096' height='5458'></svg>)

为了理解这三种不同注意力机制的区别以及各自是如何实现的，只需将对应的论文链接输入 Kimi K1.5即可

![](https://picx.zhimg.com/v2-1d502616b45df77002c73a66fbce1d50_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1348' height='1550'></svg>)

可以看到，Kimi K1.5会从以下几个方面给出详尽的解析：

1. **理解问题需求**：首先准确理解用户的研究目的，并针对性地确定解析方向。
2. **逻辑关系分析**：清晰梳理 MHA、MQA、GQA 三者之间的逻辑关系，指出 MHA 是基础机制，MQA 在此基础上进行改进，而 GQA 则是进一步优化。
3. **代码实现指导**：不仅详细解释算法原理，还提供完整的代码实现，并指出关键注意事项。

通过这样的多维度分析，科研人员可以快速了解不同算法的优缺点，并将其应用于自己的研究中。  
下面是生成的<answer>部分的内容，三种注意力机制的代码实现都完整的展示出来了。回复内容很长，所以拆成三个截图作为展示：

* MHA 代码实现部分：

![](https://pic1.zhimg.com/v2-95dbd3f464042854b20955db135b6f3f_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='643' height='1250'></svg>)

* MQA 代码实现部分：

![](https://pic1.zhimg.com/v2-44634a6cf7a4f6286ee56c3624cb1587_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='649' height='1319'></svg>)

* GQA 代码实现部分：

![](https://pic1.zhimg.com/v2-9585894050f5d8253caed3a0ed73c37d_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1319' height='4222'></svg>)

## 2. 辅助课程学习

除了通过看论文掌握学术前沿，老师授课也是重要的知识来源。不同老师授课风格各异，有的用PPT，有的用黑板板书。但因上课节奏快，学生常来不及消化内容就进入下一章节，所以大家习惯用手机拍很多照片。  
  
但是通常这些知识点也就仅仅以照片形式存在于相册，难以真正被记住。Kimi k.15能够自动识别并提取核心知识点，生成结构化笔记，助力学生快速回顾课程，提升复习效率。   
  
以 B 站热门课程《机器学习-白板推导系列》为例，当学生拍摄下“指数分布”这一小节的板书内容后，Kimi K1.5 不仅能准确识别出标题如“概率知识补充”，还能够将指数族分布的数学形式、推导过程和相关公式清晰地总结出来，形成逻辑严谨、层次分明的复习笔记，帮助学生更好地理解课程内容。

![](https://picx.zhimg.com/v2-c30adde0275515641455f42285b475ac_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1754' height='998'></svg>)

下面是 Kimi k1.5的生成结果。可以看到思考过程很详实，能够准确定位板书内容。例如明确指出了板书标题是“概率知识补充。也准确识别出了左上角的指数族分布的数学形式。

![](https://pic1.zhimg.com/v2-e72161e2f795de9ab55d09b8d82de03f_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1114' height='2278'></svg>)

板书右边的内容也能准确定位和识别

![](https://picx.zhimg.com/v2-216fe1a5ada6eabe38d013da3ac7641f_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='718' height='1080'></svg>)

## 3. 日常健康管理

除了学术研究，Kimi K1.5 在日常生活中也能提供智能支持。例如，体检报告往往包含多份复杂的数据和健康指标，普通人难以快速理解并做出相应决策。Kimi K1.5 支持多张图片和文件上传，能够自动识别体检报告中的关键健康指标，并结合专业知识，提供简明的解读和合理的改善建议。

下面截图示例中，我提供了图片形式的体检报告以及电子版截图，Kimi K1.5 都能准确读取，并以清晰的语言解释各项健康指标的含义，帮助用户快速掌握自身健康状况，做出更科学的生活方式调整。

![](https://picx.zhimg.com/v2-3c361940ec45352033f0cbb0fccf44ba_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1280' height='11334'></svg>)

对于普通人来说，Kimi K1.5 这类先进的 AI 工具是抓住 AI 风口的好帮手。它能长思考，还免费无限制。不管是学习、研究还是健康管理，都很有用。  
  
上文只是我的一些使用场景分享，AI 还有更大潜力。大家要主动探索 Kimi K1.5 等工具的新用法，把它们融入生活，借助 AI 提高效率、解决问题。这样才能借 AI 提升竞争力，搭上发展快车，抓住风口，实现自我提升。赶紧用起来吧！


---

## 有哪些好用的 AI 学术研究工具和科研工具？

`link: https://www.zhihu.com/question/606932275/answer/3622089219 · created: 1726020245`


各位学术打工人们，被文献和论文支配，写报告是不是感觉要秃头？现在很多 AI 工具有帮助阅读 pdf 的，有翻译的，有搜索的，但是大都是单独的功能，来回切换不同的工具还挺麻烦的。今天给大家安利一个神器：灵办 AI 插件。

为什么说它是神器？因为它真的懂你！不管是阅读文献、翻译理解、查文献，还是那让人头疼的论文写作，这款 AI 工具通通搞定。更妙的是，直接在你常用的浏览器里用，Edge、Chrome 都支持，Windows、MacOS 也不挑，简直是学术界的瑞士军刀啊。我个人比较喜欢浏览器插件，不用下载，微信二维码扫一下就能注册登录了，非常方便

[灵办AI插件：免费学习办公助手，一站式提升效率](https://link.zhihu.com/?target=https%3A//ilingban.com/browser_extension%3Ffrom%3Dmarsggbo)

如果喜欢本地客户端的也可以从这个链接去下载

[灵办AI：免费学习办公神器，工作学习效率双倍提升](https://link.zhihu.com/?target=https%3A//ilingban.com/web%3Ffrom%3Dmarsggbo)

**AI 翻译功能**

你是不是也经常被一坨英文文献压得喘不过气？没事，丢给灵办 AI，搞定！它不仅帮你把文献翻译得清楚明白，还贴心到能给你联想出相关问题，真是把学术饭嚼碎了喂到你嘴里。

![](https://pica.zhimg.com/v2-a9ca0ce37213eee54c9478273b4f1dd5_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='790' height='398'></svg>)

**AI 搜索和总结**

灵办 AI 还有一个特别牛的地方——它会嵌入到不同的网页里，自动给你总结结果。比如，我测试了一下在谷歌搜索“大模型越狱攻击”，灵办 AI 会立马在右侧给你总结精华信息。再也不用一个个网页慢慢啃了，效率蹭蹭往上涨！

![](https://picx.zhimg.com/v2-222a60a2318142ab85dd83d71c1dd853_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1960' height='1430'></svg>)

甚至在 GitHub 这样的技术网站，它还能直接总结 repo 里干了啥，帮你快速判断这个代码库是不是你要的。是不是觉得瞬间变身科研效率王？（下面的 repo 非常推荐，可以直接把 数学公式截图转换成 latex，写论文就方便多了）

![](https://picx.zhimg.com/v2-835f49be8330d9e7c33ce2b26f9460a3_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='936' height='614'></svg>)

我也尝试了用灵办 AI 来总结这问题下其他答主的回答，总结得也比较准确。不过 很多介绍的工具可能只负责某一部分的功能，灵办 AI 基本上是把这些功能做了整合，用起来会更加全面。

![](https://pic1.zhimg.com/v2-144c57a03ea111c5e098b59495ebf216_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='748' height='624'></svg>)

**AI教学助手**

不管是当助教的各位博士牛马们（尤其是海外的留子们，据我了解大家都是要做助教的），还是国内小初高中的园丁教师们，上课的课件肯定是个头疼的事情。也不是说课件有多难做，但是这是一个辛苦活，我发现灵办 AI 有 AI 教学助手，它可以直接帮助大家针对不同的课程自动生成教案，这可以很方便地帮助我们整理思路和课程安排。

下面是一个示例，假如你需要准备一个关于人教版牛顿三定律的课程教案，然后你可以自定义一些要求，同时有必要的话你也可以把一些参考资料上传上去作为参考。

![](https://picx.zhimg.com/v2-0668fce37fb021dde58183b1f9a06201_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1974' height='1390'></svg>)

最后，灵办 AI 会生成一个 word 版本的教案，下面是教案的部分截图示例。我这里只是给出了一个非常简单的示例。在实际上，你可以指定更加详细的要求生成不同的教学资料。

![](https://pic1.zhimg.com/v2-f1c385b5fd3e0e4bdbd8e1889255e011_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1636' height='1052'></svg>)![](https://pic1.zhimg.com/v2-451911738ef0ece2b2a136b924f50496_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1722' height='1086'></svg>)![](https://picx.zhimg.com/v2-2f081865745f5aaedb0ab5bcc368c15a_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1450' height='1484'></svg>)

可以看到，生成的教案会自动判断每个知识点需要分配的时间和教学内容，这对于新手教师来说还是很有帮助的。当然，对于有经验的老师其实也是会有很大的帮助，例如通过这么一个 AI 工具，可以得到一些新的教学思路，进一步提高教学水平。

**AI 扩写**

AI 扩写在写论文的时候经常用到。比如在写论文摘要的时候，你可能心里有一个大概的思路，甚至是只有一些关键词，这个时候灵办AI提供的扩写功能就能很好地帮你整理出一个更加完善的表达。下面给了一个简单的关于大模型论文的摘要扩写的例子，提示词非常简单，灵办 AI 就能自动地给出扩写后的摘要。这里给的例子很简单，你可以通过给出更多关键词从而让扩写后的内容更加符合你的要求。

![](https://picx.zhimg.com/v2-981b14d16a3b24f32cc6c7f1b5d86033_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='818' height='604'></svg>)

另外，大家经常写的总结报告也可以用灵办 AI 来完成。这里我 Cosplay 了一下高三的物理老师，只需要指定一下字数就可以了，效率直接拉满。

![](https://picx.zhimg.com/v2-fb99264ed0b158fec98d74af57400643_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='830' height='532'></svg>)


---

## 知乎移动端推出 AI 搜索功能，你的使用感受如何？

`link: https://www.zhihu.com/question/652463265/answer/3462618837 · created: 1712837122`


知乎移动端终于上线 AI 功能了，我当然是立马搜一下我自己啦

嗯，很好，吹捧我的样子，我很喜欢。关注我的朋友应该知道我还发过很多其他论文的技术分享，知乎 AI 搜索的确去除了那些回答和文章的干扰，把我发表的工作提炼出来了，还挺准确的。

![](https://picx.zhimg.com/v2-f5fd4dd0bb49b11b7da0a89793da7522_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1260' height='2720'></svg>)

既然说了我主要的研究方向是 AutoML，那我就很好奇，在知乎AI 搜索眼里，我到底做了那些事情呢？

![](https://pica.zhimg.com/v2-9add89e9cbeeb769b743cab0e332efa5_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1260' height='4968'></svg>)

看完回答，我只能说知乎这个 AI 是个人简历包装的神奇，能把你做过的一些小事情包装的特别伟大。比如，我只不过弄了个 AutoML 相关的公众号，它浓缩成了“推广和教育”，很不错，我坦然接受 hhh，今后继续努力

接着，我测试了一下搜索时效性，以英伟达最新发布的 GPU 为例，可以看到知乎 AI 搜索时效性还是不错的

![](https://picx.zhimg.com/v2-4787e036882636a6468af7cb639c66e7_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1423' height='600'></svg>)

知乎 AI 搜索的一个比较好的地方是除了回答问题外，还提供了和你的问题相关的其他答主的回答供参考。比如，读博因为科研进度 emo 了，可以看看别人的建议，这个还是很不错的

![](https://pic1.zhimg.com/v2-4b23e1a6e955140424a765c6ae23b79b_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1260' height='2720'></svg>)

知乎的特点是专业性强，所以涉及到一些需要专业指导的东西，除了给出 AI 生成的回答外，还要有很多其他专业答主的回答供参考。比如要减肥的朋友也可以看看食谱咋弄

![](https://pica.zhimg.com/v2-6a6c727c15245157f8c4f818b2866e03_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1260' height='2720'></svg>)

总的来说，知乎 AI 搜索很简洁，未来应该再丰富一点，支持上传图片等其他 AI 工具都已具备的功能。另外，AI 生成的回答目前来说还比较简洁，不过好在有嵌入其他答主的回答。但是这对用户来说多少还是有点麻烦，如果能更好地对所有人的回答取其精华的总结就更好了


---

## 华为将于 4 月 11 日在鸿蒙春季沟通会上发布车和 PC 类产品，你有哪些期待？

`link: https://www.zhihu.com/question/652055768/answer/3457832163 · created: 1712503656`


对于华为的这个鸿蒙沟通会，我其实对 PC 类产品很期待，尤其是好奇华为会如何把 AI 玩出花，巧妙的和 PC 结合。最早让我感到眼前一亮的是华为手机的隔空手势功能，你可以说它实用性不强（对手持 Mate60Pro的我来说真的不强），但是第一看到的时候还是觉得蛮有意思的。

随着人工智能技术的飞速发展，大模型AI已经成为我们生活中不可或缺的一部分。特别是类似于ChatGPT这样的对话智能AI，它们不仅能够提供流畅的对话体验，还在各个领域展现出了巨大的潜力。这些AI工具通过深度学习和大量数据的训练，已经能够理解和生成自然语言，为用户提供信息查询、问题解答、甚至是情感交流等多种服务。

在未来，我们可以期待这些对话AI工具进一步扩展到更多的场景中，尤其是与我们日常工作密切相关的PC产品。我比较期待以下几个场景：

1. 首先，我们可以想象一个系统级别的AI办公辅助，提高搬砖效率。目前 word 自带纠正语法、ppt 也自带模板生成，但是总还是差点火候，希望 AI 能够添一把大火，把大家的办公效率提上去。例如，在Word写作时，AI可以提供写作建议、自动校对语法错误、甚至帮助用户进行内容的结构化整理。在PPT制作中，AI可以根据用户输入的主题和内容，自动生成合适的模板和布局。而在Excel处理数据时，AI不仅能够帮助用户进行数据分析，还能提供预测和可视化的建议。另外，像程序员写代码、建筑师画图等都还是有很大的需求的

2. 其次，系统级别的翻译接口也将是一个重要的发展方向。随着全球化的推进，跨国界的沟通变得越来越频繁，一个能够实时翻译多种语言的系统工具将极大地提高工作效率。用户在编辑文档或者观看视频时，AI可以即时提供翻译，打破语言障碍，让信息交流变得更加畅通。

3. 另一个是智能搜索，或者说模糊搜索。有的时候我们只知道要找一个东西，但是那个东西叫什么、在什么地方，甚至有没有这个东西都不知道。所以希望能够提供一个更加智能化的搜索和文件管理方案，通过理解文件的内容、上下文以及用户的搜索意图，提供更为精确和个性化的搜索结果。此外，AI还可以自动分类和整理文件，甚至基于内容预测和推荐相关文件。

4. 最后，通过自然语言转义的用户需求实现，将使得操作系统变得更加直观和易用。用户不再需要通过复杂的菜单和选项来设置电脑，而是可以直接通过语音或文字输入命令，如“将音量降低到25%”，或者“再把音量降低一点点”。AI系统将能够理解这些指令，并自动调节到用户满意的设置。

综上所述，未来的PC产品将会更加智能化，AI技术将在其中扮演关键的角色。期待华为能够在即将到来的沟通会上，展示更多创新的AI应用，推动整个行业向前发展。


---

## 人工智能工具聚合网站有哪些？

`link: https://www.zhihu.com/question/589358880/answer/3443176524 · created: 1711370711`


自从ChatGPT引领大模型浪潮以来，市面上涌现出了众多AI工具，它们覆盖了从翻译、文案创作到绘图、编程等多个领域。北京智谱华章科技有限公司（以下简称“智谱AI”）提供的免费 AI 大模型工具-- **智谱清言**-- 便是这波浪潮中的佼佼者。

智谱清言不仅提供了基础的对话问答功能，更引入了既实用又能满足个性化需求的“**智能体**”功能。这些智能体可以理解成具有不同功能的 app，用户可以在智谱清言的官方网站上根据自己的具体需求轻松创建，完全不需要任何编程知识。我体验了很多智能体，给我的感受就一句话，“智谱清言就是智能体，智能体就是智谱清言”。下面我会先介绍一下让我印象比较深的两个智能体，然后再介绍一下如何创建自己的智能体。

<https://xg.zhihu.com/plugin/96814df366e10710b1cdfaabc3839f43?BIZ=ECOMMERCE>

## 1. 体验智能体

目前网站上已经开放出来了很多官方和其他用户创建的智能体。

![](https://picx.zhimg.com/v2-2cc8c27aa7def0860d85ca96dac42158_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2140' height='1598'></svg>)

### 1.1 实用性：AI 搜索智能体

我自己比较常用的智能体是AI 搜索，它可以帮助我们联网搜索给出最新的信息，省去了一个一个网页去阅读的时间。  
比如英伟达刚刚（2024 年 3 月）发布了新的 GPU，我测试了一下，可以看到智谱清言爬取了 10 个相关网页，最后的回答显示最新的 GPU 是 Blackwell 平台，这个效率杠杠的。

![](https://picx.zhimg.com/v2-011435ae50e5e3fe7c992b7397460188_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2350' height='1420'></svg>)

对比一下 kimichat 和 GPT-4，可以看到kimi 回答的 H100 是 2022 年 3 月发布的。

![](https://pica.zhimg.com/v2-f0161c7f0aa55b87fac6a53211b379b4_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1566' height='1228'></svg>)

GPT-4搜索到的最新 GPU 是 RTX 40 SUPER，这个是 2024 年 1 月发布的。

![](https://picx.zhimg.com/v2-810404be24a99ecacfbd9204ea9dfa77_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1504' height='1034'></svg>)

在时效性这方面，智谱清言值得信赖，非常可靠

![](https://picx.zhimg.com/50/v2-d2468eecb91cb1ce72555c65aa458ae4_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='124' height='118'></svg>)

### 1.2 娱乐性：打败容嬷嬷智能体

除了这种实用性强的智能体，还有很多平时可以用来休闲娱乐的。我最近一直在玩那种有剧情走向的智能体，比如“穿越之打败容嬷嬷”

![](https://picx.zhimg.com/v2-fafc816b43a9e12afa4570fc6f30b7f3_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1384' height='532'></svg>)

做人讲究 peace and love,所以第一步当然是和容嬷嬷讲道理，以德服人。咱们就是说上来先动之以情，毕竟都是宫里的人，素质应该大概多少还是有点的。

![](https://pica.zhimg.com/v2-37a08d97503e65d6f971b6ff9cc17c74_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1346' height='1420'></svg>)

但是剧情走向是容嬷嬷还是犹豫不决。动情没用，咱们就晓之以理，选择策略 3

![](https://pic1.zhimg.com/v2-4d9ed8c010b04c3d3eb033c9de7382a8_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1326' height='762'></svg>)

容嬷嬷简直是个滚刀肉，动之以情，晓之以理感觉都没用，既然如此，咱们就来硬的，直接改变策略，利诱！！提出交换条件，在利益面前肯定没人能 hold 住的

![](https://pica.zhimg.com/v2-3ce4a001619c09e5b3001ce305e01b02_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1322' height='882'></svg>)

看，在利益面前终于松口了，预知后面的剧情走向，且听下回分解

![](https://pica.zhimg.com/v2-13feca51f137aa688fed6eb6be4fb042_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='580' height='336'></svg>)

## 2. 自定义智能体

除了使用现成的智能体，我们也可以根据需求创建自定义的智能体。创建智能体非常简单，你只需要把你的需求写清楚，系统会自动将你的需求转换成合适的配置。

<https://xg.zhihu.com/plugin/96814df366e10710b1cdfaabc3839f43?BIZ=ECOMMERCE>

### 2.1 文献追踪

比如，我平时经常需要跟进某个领域的最新文献，我就创建了这么一个智能体。只要给出智能体的描述就好了

![](https://pic1.zhimg.com/v2-3bb74b3bfbcd0d1dbdd0fa836a8f34d6_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2148' height='1342'></svg>)

点击【生成配置】后，会将描述自动转换成具体的配置信息，如下图，不仅给出了 logo 和智能体名字，还润色和丰富了智能体的描述。我们也可以根据需求再做修改。我这里根据需求选择开启了联网、绘画和代码能力。当然我们甚至还可以上传文件作为知识库，智谱清言会结合提供的内容提供更加个性化的回答。

![](https://picx.zhimg.com/v2-86c421298e6af109d1db941b6e3a7dd6_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1602' height='793'></svg>)

下面是具体的使用体验，可以看到我的问题是搜索最新的大模型推理优化相关的论文，返回的结果的确是 2024 年较新的大模型推理方向的论文，对比过给出的网页链接也是正确的，靠谱！

![](https://pica.zhimg.com/v2-8badd0dda6f4d077a3f2cd2dd882b1db_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1620' height='1350'></svg>)

每个人创建的智能体也可以选择开放出来让别的人使用。你在智谱清言的智能体页面搜索“智慧搜索者”应该就能找到我创建的智能体了。

### 2.2 论文精读

前面这个“智慧搜寻者”智能体是主要是用来粗读论文，帮助我快速筛选相关的论文。我还创建了用于精读的智能体，只需要传入 pdf 链接即可自动根据指定的要求总结论文

![](https://pic1.zhimg.com/v2-20288bb205cd009a843fed5353a14975_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1172' height='788'></svg>)

我用我之前 2021 年发表在 AAAI （Association for the Advancement of Artificial Intelligence）上的一篇论文做了测试，总结的很准确,清楚的总结了研究的问题、方法、实验结果和结论等信息。

![](https://picx.zhimg.com/v2-05fa98e5c437dd755bdb0b8f97ba285f_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2912' height='1428'></svg>)

我又进一步问了一下最终模型准确率，智谱清言准确总结了在三个不同数据集上的实验结果，牛！

![](https://pic1.zhimg.com/v2-7aadf85007c40d7a94bf7d5b53e9f85b_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1080' height='654'></svg>)<https://xg.zhihu.com/plugin/96814df366e10710b1cdfaabc3839f43?BIZ=ECOMMERCE>

总的来说，智谱AI无疑在国内大模型服务领域中带来了一阵清新的气息。他们推出的大模型解决方案横跨了从代码新手到技术专家的广泛用户群体，每个人都能找到适合自己的高效工具。对于那些编程知识有限的用户来说，免费的智谱清言提供了一个极佳的平台，无需编程就能够显著提升工作和学习的效率；而对于开发者而言，智谱AI的开源GLM系列模型提供了强大的自定义和微调能力，以适应具体的应用需求。智谱清言的用户体验极其出色，其简洁直观的界面让人仿佛在使用聊天软件，却能完成让人惊叹的复杂任务。智谱AI为了使AI技术更加易于理解和广泛应用，确实投入了巨大的努力和资源。这种精神和成果，值得我们每一个人的尊敬和赞扬。


---

## 基于 RISC-V 开源架构笔记本「如意BOOK」发布，首次打通软硬一体全链路，有哪些意义？

`link: https://www.zhihu.com/question/648406367/answer/3431084304 · created: 1710465838`


## **引言**

感谢阿里达摩院邀请，有幸以媒体人的方式参加了由阿里达摩院举办的 2024 年 RISC-V 生态大会。

人在现场，见到了好多大佬和媒体同行（假装自己是个媒体人）。

* 倪光南院士,第一次这么近距离看见新闻上的大人物。倪院士在大会致辞环节简单树立了 RISC-V 的发展和前景，深入浅出，娓娓道来。

![](https://picx.zhimg.com/v2-f5c764b004bdd923f3acef24aba540d1_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='832' height='478'></svg>)

倪光南院士

* 硅仙人：Jim Keller。简单科普一下，这个大哥是芯片界的传说，他基本上在硅谷各大芯片厂商都待过，并且在每个公司都创下了不可磨灭的功绩。比如，在 AMD 期间先后参与和领导设计了 K7,K8 处理器，开启了 AMD 对英特尔的反击。后面又去了苹果，带领团队开拓了苹果A系列处理器中的开山之作A4和下一代的A5。老哥曾经放言：“**我这个人没什么太大成就，你们用过最好的CPU，都是我设计的。**”狂的有底气，大佬就是大佬。这次没能亲临现场，但是录制的 VCR 很大篇幅在介绍 RISC-V 在 AI 领域的应用前景，我只能说相信大佬的眼光准没错，all in 就完事了！

![](https://picx.zhimg.com/v2-326e549af1cb9e14f1182c5b73e3e7a1_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='832' height='470'></svg>)

Jim Keller

回到「如意BOOK」的发布，还是挺激动的，因为它不仅仅是一款新的笔记本电脑，它标志着全球首台RISC-V架构的开源笔记本电脑的诞生，其意义非凡。要深入理解这个意义，我们首先得探讨一下RISC-V本身。

![](https://picx.zhimg.com/v2-9297ebce27679f8c675b54c19b50092f_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='686' height='572'></svg>)

## **RISC-V是什么？**

在介绍RISC-V 之前，我们首先得了解 **ISA（Instruction Set Architecture，指令集架构）**是什么。

简单理解，ISA 就像是一本规则书，而这本书并不直接涉及编程代码的编写，也不介入电子电路的具体设计。它在计算机的世界中起着指挥棒的作用，告诉CPU它能理解和执行哪些指令。这不仅涉及CPU内部的“小盒子”（寄存器），还包括如何寻址、处理的数据类型等一系列基本规则。

举个例子，当我们谈论数据类型时，我们可以根据需求选择使用整型、fp16、bf16、fp8等特定的格式规范。确定了这些基础规则后，我们就能根据它们来设计电路、编写相应的软件代码。

**那么，RISC-V究竟是什么？**

简单来说，RISC-V 是一个具体的 ISA 实例，代表着“精简指令集计算 （**Reduced** Instruction Computer）”的第五代，这里的“V”就是罗马数字5的意思。这个“精简”意味着它采用的是一种尽可能简化指令的方式来设计指令集，以优化性能、降低实现复杂性。这与以 X86 为代表的复杂指令集计算（**Complex** Reduced Instruction Computer, CISC）形成对比，CISC是另一种设计哲学，强调通过复杂的指令来减少程序执行的指令数量，以试图直接提高执行效率。

下图简单总结了RISC 和 CISC衍生出的不同计算机体系结构和操作系统等，我们可以看到目前主流的架构还是那两个老朋友 X86 和 ARM，而RISC-V 异军突起，占据一席之地。

![](https://picx.zhimg.com/v2-66d4aa89f0dd962d5aa8316ea98373fb_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='832' height='468'></svg>)

RISC vs. CISC

## **RISC-V 商用化挑战和机遇**

要聊聊RISC-V商用化的挑战，我们首先回顾一下处理器的发展历程和现状。借用倪院士的几张PPT。

首先随着处理器不断发展，摩尔定律和登纳德定律逐渐失效，换言之，硬件工艺制造已经接近物理瓶颈，虽然可以通过堆叠更多晶体管数量来弥补，但是同时也带来了更大功耗。

![](https://picx.zhimg.com/v2-7a657e7f94f574288f2693c5a89213b3_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='832' height='390'></svg>)

根据倪光南院士的演讲，我们可以看到早期的 CISC 处理器每年的计算速度增速为 22%，随后 RISC 将年增速提高到了52%。但是到了近几年，处理器年增速却维持在了 3% 左右而已。因此，处理器的发展急需更大的创新。

![](https://picx.zhimg.com/v2-6b9b8cc0edd058a132a27b03c29a2c6d_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='832' height='400'></svg>)

除了处理器存在挑战外，在商用化的路上， RISC-V 还面临着其他不小的挑战。

l **工具和软件，还得再磨磨**：先说开发环境。想让开发者拥抱RISC-V，就得给他们好用的工具。但现状是，跟ARM和x86这俩老江湖比，RISC-V的软件生态还需要时间长大。没那些成熟的编译器、调试器，开发起来能顺畅吗？

l **硬件，这块拼图游戏不好玩**：RISC-V给设计师很大自由，听着不错，实则这意味着不同的实现之间可能互不兼容，软件得为各种硬件配置特别优化，增加了开发难度。

l **市场，不是说“我来了”就有人买账**： RISC-V虽然吸引了不少大公司的目光，但让整个行业都跟着你转，还得需要时间。不仅是硬件厂商，软件开发者、消费者都得接受，才能真正说构建了一个生态系统。

l **IP和法律，不是谁都能随便玩的沙盘**：虽然RISC-V自己是开源的，但实际商用可能涉及到的一些专利技术，那就是另一回事了。避免侵权，处理好知识产权的问题，也是走向商用化必须要过的一关。

## **如意BOOK的产品亮点**

RISC-V商用化的道路荆棘密布。但正是因为有这些挑战，才更凸显这个开源项目的价值和潜力。毕竟，没有哪个技术是一帆风顺就能成功的，**不是吗？**

RISC-V的旅程，才刚刚开始。在这个旅途中，出现了一个让人眼前一亮的新星——「如意BOOK」，这可以说是全球首款打通软硬一体全链路的RISC-V开源笔记本。这个笔记本的发布，标志着上面提到的问题得到极大改善，RISC-V 的商业化道路迈出了坚实一步。

### **设计与外观**

我们首先看看一个产品给人最直观的东西，那就是外观。

先看看官方渲染图

![](https://picx.zhimg.com/v2-df23a7400af60cd50a4c46e6c899b92b_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='832' height='446'></svg>)

再看看实拍图

![](https://pic1.zhimg.com/v2-903d2a92863bb674d4812c52aee1942b_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='604' height='786'></svg>)

如意 Book 实拍图

看看黑白键盘、银色机身,是不是很像一位故人啊？弄一个刘海可能就更像了，只能说优秀的设计是相通的（逃。

电脑的其他配置可以看看下图的总结。总的来说，这款笔记本整体的风格设计属于轻薄便携，适合商务办公场景。

![](https://picx.zhimg.com/v2-5e2b5c0bd09b7df95d0b9002476a0ac4_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='616' height='532'></svg>)

如意 Book 参数配置

听展台的工作人员介绍，在应用生态方面，「如意BOOK」搭载的OpenEuler操作系统，不仅能够流畅运行钉钉、Libre Office、福昕PDF、搜狗输入法等办公软件，还具备长达12小时的综合续航能力，快速启动系统，一键休眠功能，以及网页浏览、4K高清视频播放等强大功能。在会上，达摩院院长张建峰特别提到基于 RISC-V 实现的玄铁架构和多个 Linux 系统平台也有了不同程度的合作和尝试。

![](https://pica.zhimg.com/v2-96b0c2d76263e34fe9cbe39b8676bdda_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='832' height='440'></svg>)

### 性能

性能方面，如意BOOK搭载玄铁C910处理器，具备GPU、VPU加速单元，片上拥有4TOPS@INT8通用AI算力，融入TEE等可信计算特性，实现了低功耗、高安全、AI本地算力支持等特点。展台工作人员表示正在适配将大模型部署在笔记本本地，也就是说可以在没有网络的情况下也能够借助大模型的手提高办公、代码等工作的效率。

## RISC-V 披荆斩棘之路

「如意BOOK」这款备受瞩目的新品的发布得益于阿里巴巴和中科院已经在RISC-V的赛道上默默耕耘。

自2018年起，阿里巴巴就开始了对RISC-V架构的深入探索，从最初的IoT小溪流，逐渐汇成了涵盖高性能应用的宽广河流。2019年，玄铁C910的问世，不仅标志着RISC-V在高性能计算领域的突破，也为后续的技术创新奠定了坚实的基础。六年磨一剑，阿里巴巴达摩院不仅推出了多款覆盖低功耗到高性能的RISC-V处理器，更是将这些处理器的应用领域扩展到了30多个，包括边缘计算、无线通信等，出货量更是达到了惊人的40亿颗，让玄铁成为了国内RISC-V领域的佼佼者。

![](https://pic1.zhimg.com/v2-719f68713cc76af0c698c6dd99552421_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='654' height='352'></svg>)

在全栈技术能力方面，达摩院的探索从未停歇。XT-Link的推出，无剑芯片设计平台的高性能异构特性，以及剑池编译及开发工具的全面优化，这些技术的进步不仅降低了开发门槛，缩短了产品研发周期，更是大幅提升了开发效率，为RISC-V生态的蓬勃发展注入了新的活力。在大会上还正式成立了 RISC-V 无剑联盟，首批成员包括达摩院、中国电信研究员、新思、芯昇科技、Imagination 和 ARTERIS等。

![](https://picx.zhimg.com/v2-69a189c8aeeaf39f0901105955249abc_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='832' height='694'></svg>)

RISC-V 无剑联盟

另外，今年的玄铁RISC-V生态大会上，玄铁处理器家族的全面升级成为了焦点。玄铁C907的矩阵运算扩展为AI加速计算带来了新的可能，而且张建峰院长表示旗舰处理器C930的即将在 2024 年下半年发布，性能将得到更进一步的提升，这让人们对RISC-V的未来充满了期待。

![](https://picx.zhimg.com/v2-b5f8980f9d2c0d0864dcee60b8af4d06_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='666' height='382'></svg>)

阿里巴巴通过玄铁系列处理器的持续创新和全栈技术的深度融合，不仅在国内RISC-V领域占据了领先地位，更为RISC-V生态的未来发展打下了坚实的基础。目前，国内外很多厂商也都基于 RISC-V 推出了不同程度的产品和应用。比如：

* 中科蓝讯为耳机专门制作了基于 RISC-V 的耳机芯片，每年出货量超过 8 亿颗，成功在科创板上市。

![](https://pica.zhimg.com/v2-fe105794604e7ddf6db22444b452c8a9_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='676' height='410'></svg>)

* 著名的 GPU IP公司 Imagination 基于 RISC-V 迭代出了多款性能出色的 GPU。

![](https://picx.zhimg.com/v2-531bc79f69d8cbbc9284c2bd5cadb556_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='832' height='486'></svg>)

随着技术的不断进步，我们有理由相信，RISC-V的应用前景将更加广阔，其影响力将更加深远。


---

## 在有机器学习和深度学习的基础上，如何自学AutoML算法？

`link: https://www.zhihu.com/question/334021426/answer/3420498126 · created: 1709699230`


> 论文: [AutoML: A Survey of the State-of-the-Art](https://link.zhihu.com/?target=https%3A//arxiv.org/abs/1908.00709)  
>  下面这个网站会不断更新AutoML相关的论文，当然如果你的论文未被收录，你也可以手动上传你的论文让更多人看到(建议电脑端查看）：  
>  [https://marsggbo.github.io/automl\_a\_survey\_of\_state\_of\_the\_art/](https://link.zhihu.com/?target=https%3A//marsggbo.github.io/automl_a_survey_of_state_of_the_art/)

## **1、文章结构**

![](https://picx.zhimg.com/v2-2e6f8a4002bf21ee2346c387fdcf988f_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='484' height='666'></svg>)

下面是整个AutoML的pipeline，全文也是围绕这个pipeline对AutoML技术做了回顾和总结。

![](https://picx.zhimg.com/v2-84a19096d309068057adc1074a5b7c0a_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1419' height='734'></svg>)

下表总结了目前现有的AutoML相关的综述，我们的survey涵盖了更广的范围，并且将2020年已发表在会议或期刊上的很多论文都整理在内。其他综述写的都很棒，都有很高的参考价值。

![](https://picx.zhimg.com/v2-cf1e5440bf9a7064465f086ccc5c6631_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='696' height='445'></svg>)

下面的内容会对论文做一个简单的总结，不会涉及到太多的细节，感兴趣的朋友可以移步最上面的链接阅读原文。

## **2、Data preparation**

![](https://pic1.zhimg.com/v2-7b575d4631d0d484cad5371a36dcfa79_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='728' height='643'></svg>)

上图是数据准备的流程图，涉及到的技术有：

* data searching
* data synthesis
* data cleaning
* data augmentation

+ 这里介绍了一些**自动数据增强**的算法，即不需要人工设计，而是通过算法为特定任务设计一套数据增强操作。

具体细节可参阅原文。

## **3、Neural architecture search (NAS)**

由前面的pipeline可以看到NAS技术主要有三个部分组成：

* **search space**：定义了网络结构的范式。我们论文主要关注神经网络架构，因此像SVM这种传统机器学习模型的search space我们没有做过多介绍。
* **architecture optimization (AO)**： 定义了如何搜索网络结构。在一些论文里也称作search strategy或search policy等，也有不少论文称之为architecture optimization，本文选择这个的原因也是为了和hyperparameter optimization (HPO) 统一起来，即二者都是优化算法，只不过HPO一般是指优化像学习率或者batch size这样的超参数，而AO则是优化网络结构。
* **model estimation**：找到一个模型后，我们需要评估它以此来判断模型的好坏。

> 在之前版本里，我们将architecture也视为了超参数的一种，这个可能会引起歧义，而且目前NAS社区大多数论文都将architecture和hyperparameter区分开来的，所以为了方便理解，该版本也对architecture和hyperparameter做了区分。

## **3.1 Search space**

主要有如下四种search space：

* entire-structured search space

直接设计出一个完整的网络结构，即每一层代表一个操作，该操作是从预设定的search space里选择的；然后层与层之间可以跳跃连接。这样设计的主要问题是设计出来的模型缺乏可迁移性，不太好扩展。

![](https://pica.zhimg.com/v2-9fbdb068a55ee2b49bb9d8113890479d_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='689' height='875'></svg>)

* Cell-based search space

为了解决上个方式的问题，Cell-based，顾名思义，就是先搜索出一个表现最好的cell结构，然后堆叠cell来得到最终的模型。

![](https://picx.zhimg.com/v2-21468beec007658473d05f57baa5e4d2_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='690' height='850'></svg>)

* Hierarchical search space

cell-based 有个缺点就是cell 结构其实是人为固定好的，比如你需要提前设置好一个cell是由几个node组成的。而且最后只是简单地堆叠重复的cell得到最终模型，这样的设计范式也是存在局限性的。下面两种搜索空间使得cell结构的可能性更多。

第一种是将cell分成若干个level，高level的cell由低level的cell组成

![](https://pic1.zhimg.com/v2-befd5e10cf2af68182cf0e6d1ce1aa71_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='717' height='628'></svg>)

另一种是以MnasNet为代表的方法，即每一层是一个cell，每个cell由若干个block组成，block的数量是可以搜索的。另外每个cell内部的block结构是一样的，但是不同的cell之间的block是不一样的。

![](https://picx.zhimg.com/v2-12a4041644f80df43214dc29b5ec108d_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='690' height='788'></svg>)

* Morphism-based search space

这种方式简单理解就是可以基于现有的模型进行扩展，比如模型加宽、加深，或者把某一个操作替换成其他操作等。

![](https://pic1.zhimg.com/v2-9c631259bfcbbeb5980a6aa12801cdcb_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='747' height='561'></svg>)

## **3.2 Architecture Optimization**

* Evolutionary Algorithm

进化算法其实就是借鉴的生物进化，主要包括四步：

* selection：选择父母网络，用于生成子网络
* crossover：可以简单理解成子网络获取父母网络的信息
* mutation：子网络的部分信息发生突变，这样可以得到更多种类的网络结构
* update：更新网络数量，因为生成的网络越多，消耗的资源也越多。而资源是有限的，所以需要控制网络总数，一般可以通过淘汰表现差的或老的来控制模型的数量。

![](https://picx.zhimg.com/v2-f422c9f459a6971aa7e747c728f9a327_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='571' height='570'></svg>)

* Reinforcement Learning

如果对这类方法还不熟悉的，建议阅读ENAS论文或之前的文章[论文笔记系列-Efficient Neural Architecture Search via Parameter Sharing](https://link.zhihu.com/?target=https%3A//www.cnblogs.com/marsggbo/p/9435954.html)，这里不做过多介绍。

![](https://picx.zhimg.com/v2-6ee97724b43ac742f0cf36905392f6c9_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='707' height='447'></svg>)

* Surrogate model-based optimization (SMBO)

SMBO简单理解就使用一个代理模型（比如Gaussian process）来预测生成的模型的性能，进而加快搜索效率。

![](https://pic1.zhimg.com/v2-5e6c08a36f8fd003a39b0a7797b3b421_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='718' height='342'></svg>)

* Random & Grid search

random search被好几个论文证明了它也是非常有效的，有的时候甚至超过了一些“花里胡哨”的方法。 （真.玄.学）

* Gradient descent-based method

DARTS应该是最早提出连续化搜索的方法之一，但是他有一个很大的问题就是内存消耗大，因为它构建了一个supernet，而且每次计算都需要更新这个supernet。因此后续有很多方法来改进。比如GDAS将Gumbel-softmax应用到DARTS上，每次只需要更新supernet的一个子网络即可，因此对内存消耗减少了很多。还有其他很多改进算法详见论文。

![](https://picx.zhimg.com/v2-20b1ea879ebafff9fcd4e969e26f1c9c_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='715' height='579'></svg>)

## **3.3 Model estimation**

搜索到一个模型后，我们需要对一个模型做评估。最朴素的想法就是训练这个模型直到收敛，然后在验证集上看他的结果怎么样，但是这样既耗时又耗资源。所以需要一些提高效率的方法，下面只是做简单的总结，具体细节详见论文。

### **1） 低保真度评估**

* 使用分辨率更小的图片（比如ImageNet原图一般是224\*224，那我们可以用64\*64的变体数据集）
* 使用训练集的子集来训练，减少训练时间
* 使用多个低保真的评估，然后将这些评估结果做一个ensemble

### **2）weight sharing**

ENAS 和DARTS都采用了类似的方式，即所有可能的模型都是一个supernet的子模型。这些子模型互相共享权重，因此就不需要每次都重新对子模型进行训练了。

### **3）Surrogate**

我不再去训练模型了，相反我可以使用代理模型来预测模型的性能。但是如何确保代理模型能准确预测是一个需要解决的问题。

### **4）资源感知**

早期NAS工作更多关注在最终的accuracy，而忽略了生成的模型的大小。比如有的模型虽然表现不错，但是模型非常大，换言之这种模型的实用性是有局限的。所以很多论文开始探索如何找到参数不是太多而且表现还不错的模型。

## **4、NAS讨论**

## **4.1 Performance Comparison**

![](https://picx.zhimg.com/v2-620433d696018bf5dcc647ccc6039136_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='916' height='1080'></svg>)![](https://picx.zhimg.com/v2-1d0979925687c40d79b35b1a427627e5_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='940' height='1053'></svg>)

上面两个表格总结了NAS算法在CIFAR-10和ImageNet上的结果。虽然每个论文使用的硬件设备都不太一样，但是大致上我们还是能看到Gradient descent-based methods是非常高效的，不仅使用的资源少，而且效果还很不错，这也是为什么很多后续NAS工作都是沿着这个思路做的。

但是我们也可以看到随机搜索也是一个非常不错的方法，不仅简单，而且结果也可和其他方法相媲美。

### **1） Kendall Tau**

但是上面的都是基于accuracy和搜索时间上做的对比。有不少方法开始寻找其他的NAS算法评价指标，。我们知道大多数NAS其实分成两个步骤，一是搜索最有潜力的模型（搜索阶段）；二是验证该模型的表现（评估阶段）。但是很多时候搜索阶段表现最好的，在评估阶段并不是最好的，甚至可能表现很差。 因此一种用的比较多的就是**Kendall Tau metric**，它会评估两个阶段模型性能的相关性，相关性越高则表示算法越有效，它的计算公式如下：

![\tau=\frac{N_{C}-N_{D}}{N_{C}+N_{D}} \\](https://www.zhihu.com/equation?tex=%5Ctau%3D%5Cfrac%7BN_%7BC%7D-N_%7BD%7D%7D%7BN_%7BC%7D%2BN_%7BD%7D%7D+%5C%5C)

其中![N_C,N_D](https://www.zhihu.com/equation?tex=N_C%2CN_D)分别表示 concordant and discordant pairs。![\tau](https://www.zhihu.com/equation?tex=%5Ctau)的大小在-1到1之间：

* ![\tau=1](https://www.zhihu.com/equation?tex=%5Ctau%3D1)：算法**能**很好地找到表现好的模型，即搜索阶段表现最好的模型在评估阶段也是最好的。
* ![\tau=1](https://www.zhihu.com/equation?tex=%5Ctau%3D1): 算法**不**能很好地找到表现好的模型，即搜索阶段表现最好的模型在评估阶段反而是最差的。
* ![\tau=0](https://www.zhihu.com/equation?tex=%5Ctau%3D0)：搜索阶段和评估阶段之间完全没有关系，基本上是随机搜索。

### **2） NAS-Bench**

最近有好几个NAS相关的数据集，如NAS-Bench-101、NAS-Bench-201和NAS-Bench-NLP。简单理解就是这些数据集的每个样本的数据就是某种网络结构和模型大小等信息，对应的标签就是该网络结构的准确率。很多NAS算法都基于这些数据集来验证他们算法的有效性，而且使用这些数据集不需要我们在训练和评估搜索到的网络结构了，效率也更高了。

## **4.2 Two-stage vs. One-stage NAS**

![](https://picx.zhimg.com/v2-dc8f638476f127bcff3e3cfcd40b985f_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='708' height='810'></svg>)

一般的NAS算法都是Two-stage的，即先找到一个比较有潜力的模型，之后在deploy之前基本上还得retrain或者finetune一遍。而one-stage NAS则不需要，即找到模型后即可直接用这个模型来做预测了，这方面的方法有Once-for-all NAS, AutoHAS, FBNetv3等。

## **4.3 One-shot NAS**

![](https://pic1.zhimg.com/v2-909c3d4955617c353226c87c8ea09221_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='711' height='434'></svg>)

在介绍之前需要说明下：One-shot NAS和One-stage NAS是两回事，二者可能会有重叠的地方，但是分类的方法是不一样的。One-stage NAS强调的是一步到位，即搜索完之后模型可以直接使用，而不再需要retrain等操作；而One-shot NAS指的是那些将search space构造成一个supernet的方法，即对网络结构的搜索其实就是对supernet内部路径的搜索。

我们把 One-shot NAS又进一步划分成了两类：coupled optimization（耦合优化）和decoupled optimization（解耦优化）。

### **1）耦合优化**

耦合优化的包含两个方面的耦合：

* 网络结构和权重的耦合。比如DARTS采用的是bilevel的方式来优化架构和对应权重
* 子网络之间权重耦合。由于子网络之间互相共享权重，更新某一个子网络的权重必然会影响其他子网络的性能

像DARTS、ENAS就是属于耦合优化。

### **2）解耦优化**

解耦优化，就是把架构优化和权重优化分开成两个步骤，即先只训练supernet，之后从supernet中按照设计的优化算法选择和评估。

Understanding and Simplifying One-Shot Architecture Search和Single Path One-Shot Neural Architecture Search with Uniform Sampling这两篇论文是比较经典的解耦优化算法。

## **4.4 Joint Hyperparameter and Architecture Optimization**

文章最前面提到我们将hyperparameter和architecture做了区分，但是究其本质，其实二者是一样的，而且使用的优化算法也很多是通用的，比如随机搜索，SMBO，基于梯度的优化算法等都可以用来优化hyperparameters和architecture。因此为什么不同时优化二者呢？像AutoHAS这些方法在这一方向上做了探索，也取得了不错的效果（详见原论文）。

## **5、Open problems and Future work**

* Flexible search space

目前大多数NAS的search space基本上都是基于人类经验设计的，比如使用卷积操作、假如skip-connection等，虽然效果不错，但是或多或少都引入了人类偏见，或者说仍旧没有跳脱出人类的设计范畴。所以如何设计出不受人类偏见影响的search space是一个值得探索的方向。Auto-Zero在这方向上做出了探索，它只使用一些非常基础的数学计算式子，例如加、减sin，cos，高斯分布等从0开始成功地找到了2层的神经网络结构。

* 可解释性
* 可复现性
* 鲁棒性

目前NAS更多应用在科研性质的数据集上，而我们都知道现实世界中的数据是有很多噪声的，比如标签错误或者信息不完整等，甚至有的数据加入了人为制造的噪声（如Adversarial data），这些都会影响模型的性能。虽然已经有不少方法可以提高模型的对抗噪声鲁棒性，但是他们都是算是一个后处理的方法，一个理想的方法是在搜索过程我就能搜索到鲁棒性很强的模型，这样就不用再做一些后处理操作了。目前将NAS和鲁棒性结合的论文还不是很多（好像只有三四篇论文），因此还是一个初步探索阶段。

* 将NAS应用到更多领域

下表统计了除了图像分类外，目前NAS所应用的领域

![](https://picx.zhimg.com/v2-175358cc5aba4f6ab4413e580264c191_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1370' height='791'></svg>)

* 完整的AutoML pipeline系统

目前有不少AutoML的开源库了，但是大都只实现了pipeline的一部分。

比如TPOT，Auto-Weka，Auto-Sklearn都是基于传统机器学习模型设计的。Auto-keras则主要侧重NAS。不过微软的NNI和华为最近开源的Vega都提供了非常强大的功能，例如NAS、模型压缩、超参数搜索。NNI最近更新了对Sklearn的支持，Vega还提供了自动化data augmentation功能，很是强大了，因此完全傻瓜式的多模块AutoML系统指日可待了。

* lifelong learning

一个优秀的AutoML系统还应该能够lifelong learning，因为在现实场景中会源源不断的产生新数据，所以换句话说就是**能不断学习新数据，同时还能记住旧知识**。

对于学习新数据，有两个问题：一是新数据的数量可能会很少，这就涉及到meta-learning技术。最近有不少论文将NAS和meta-learning做了结合，也都取得了不错的效果；二是新数据的标签不完整，这就涉及非监督学习，何凯明团队最新研究成果UnNAS发现非监督NAS也能取得不错甚至比监督NAS更好的结果。

记住旧知识比较经典的算法是*learning without forgetting （LwF）* 和 *iCaRL*。

### **微信公众号：AutoML机器学习**

![](https://picx.zhimg.com/50/v2-87083e55cd41dbef83cc840c142df48a_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='0' height='0'></svg>)

**MARSGGBO♥原创**  
**如有意合作或学术讨论欢迎私戳联系~**  
**邮箱:marsggbo@foxmail.com**   
**2020-07-09 11:06:31**


---

## 为什么 OpenAI 可以跑通所有 AGI 技术栈？

`link: https://www.zhihu.com/question/644486081/answer/3412773666 · created: 1709126373`


这个问题蛮有意思的，我也来分享下自己的看法吧。

首先，让我们聊聊那种“光脚不怕穿鞋”的精神。OpenAI作为一个相对年轻的初创公司，真的是敢打敢拼，全力以赴地投入到了一些超前的、实验性的想法中。这与像微软、谷歌这样的科技巨头形成了鲜明对比，因为后者虽然资源丰富，但同时也背负着巨大的业务包袱，他们可能不太会，也不太愿意为了探索性的项目而冒太大的风险。

接着谈谈领导力。OpenAI的领导人真的很有远见，勇气和执行力。他们不仅能够准确地把握技术发展的脉络，还能够大胆地做出决策，并且迅速执行。这种领导力是OpenAI能够在AGI领域取得领先的关键因素之一。

然后是技术的坚持和深化。OpenAI选择了decoder-only架构，而不是那种更传统的encoder-decoder架构。这个选择在当时可能看起来颇具争议，但OpenAI通过持续的深入研究和不断的实践，证明了他们的选择是正确的。他们在这一领域的深耕细作，让他们能够在AGI技术栈的各个方面都保持领先。

最后，我认为OpenAI从一开始就把数据放在了优先的位置，这和传统的架构优先的观点形成了对比。前几年我就看到吴恩达老师有公开提过数据的重要性，还开设了 data science 之类的课程。那个时候我会觉得说数据很重要没错，但是模型架构不行的话数据再好可能也学不了。不过目前看来，GPT 系列模型天赋异禀，学习能力的天花板还没突破，未来仍然可期。

ChatGPT的成功不仅仅是技术上的胜利，更是数据处理能力的胜利。它的成功为Sora等后续项目积累了巨大的数据优势，这种从数据优先转变的战略视角，让OpenAI在数据获取、清洗以及利用方面拥有了超越其他团队的能力。这其中可能包括了自动爬虫、OCR、物理引擎等先进的数据获取手段，以及基础格式整理、二次校对等深度的数据清洗工作。

真的，当你深入思考OpenAI如何能够在这么短的时间内，从零到一，再到领先全球的AGI技术水平，你会发现这背后的不仅仅是技术实力的展现。更重要的是，它们展现了一种独特的组织文化和价值观——一种对未知领域的无畏探索，对技术深度和广度的不懈追求，以及对社会进步贡献的长远考虑。

另一个角度来看，OpenAI的成功也反映了整个行业对于创新和实验性项目的渴望。在这个快速发展的时代，那些能够快速适应变化，敢于冒险尝试新思路的组织，往往能够在竞争中脱颖而出。OpenAI就是这样的一个典范，它们不仅推动了AI技术的边界，也为整个科技界提供了宝贵的经验和启示。

总的来说，OpenAI之所以能在AGI技术栈上取得如此惊人的成就，不仅仅是因为他们敢于冒险和创新，更因为他们在领导力、技术坚持以及数据处理能力上的出色表现。


---

## 能否图文结合详细介绍vLLM Decoding阶段手写Kernel的执行逻辑？

`link: https://www.zhihu.com/question/633412311/answer/3387111566 · created: 1707041319`


## **1. Quick Start**

创建如下代码，命名为 `run.py`

```
from vllm import LLM, SamplingParams

prompts = [
 "Have you followed marsggbo in Zhihu?",
 "你一键三连了吗？"
] # 输入prompts
sampling_params = SamplingParams(temperature=0.8, top_k=50) # 采样策略
llm = LLM(model="facebook/opt-125m", tensor_parallel_size=2) # 初始化 LLM
outputs = llm.generate(prompts, sampling_params) # 完成推理
for output in outputs:
 prompt = output.prompt
    generated_text = output.outputs[0].text
    print(f"Prompt: {prompt!r}, Generated text: {generated_text!r}")
```

执行命令：`python run.py`。该脚本会自动将模型以张量并行的方式在两个 GPU 上进行推理计算。

整个推理过程大大致流程如下图所示，即 1 给定一定数量的 prompts（字符串数组） 2. vllm 会使用 Scheduler 模块自动对需要推理句子进行调度 3. 根据调度的结果，使用 tokenizer 将字符串转换成 prompt id，然后喂给 model 进行计算得到 logits 预测结果 4. 根据 logits 预测结果和提前设置好的采样策略对结果进行采样得到新的 token id 5. 将采样结果保存到 output

![](https://pica.zhimg.com/v2-c1cc9475fc25d13583f7af950481542b_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1720' height='312'></svg>)

inferencce pipeline

## **2. 整体核心模块**

![](https://pica.zhimg.com/v2-d692937551e96c74b2e7dd508fa2120b_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='823' height='871'></svg>)

上图给出了 vLLM 核心模块之间的结构关系。接下来我们从简单的模块（即输入、采样和输出）开始介绍，最后详细介绍 LLM 模块。

## **3. Sequence**

![](https://picx.zhimg.com/50/v2-7f158b90189375fe99cbdd76a90d2d39_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='193' height='390'></svg>)

如上图我们可以看到 vLLM 为输入的句子设计了很多子模块，这些模块的用处各不相同，但是有彼此之间有关系，下面分别详细介绍一下。

## **3.1 SequenceStatus**

首先看到 `SequenceStatus`，其源代码如下：

```
class SequenceStatus(enum.Enum):
    """Status of a sequence."""
    WAITING = enum.auto() # 等待中，句子还没开始推理，或者推理还未结束
    RUNNING = enum.auto() # 运行中
    SWAPPED = enum.auto() # 已交换
    FINISHED_STOPPED = enum.auto() # 已停止
    FINISHED_LENGTH_CAPPED = enum.auto() # 已长度限制
    FINISHED_ABORTED = enum.auto() # 已中止
    FINISHED_IGNORED = enum.auto() # 已忽略

    @staticmethod
    def is_finished(status: "SequenceStatus") -> bool:
        # 判断状态是否为已停止、已长度限制、已中止或已忽略
        return status in [
            SequenceStatus.FINISHED_STOPPED,
            SequenceStatus.FINISHED_LENGTH_CAPPED,
            SequenceStatus.FINISHED_ABORTED,
            SequenceStatus.FINISHED_IGNORED,
        ]
```

## **3.2 SequenceData**

`SequenceData` 用于存储与序列相关的数据。这个类有三个属性：`prompt_token_ids`（提示词的标记ID）、`output_token_ids`（生成文本的标记ID）和`cumulative_logprob`（累计对数概率）。

```
class SequenceData:
    def __init__(
        self,
        prompt_token_ids: List[int],
    ) -> None:
        self.prompt_token_ids = prompt_token_ids
        self.output_token_ids: List[int] = []
        self.cumulative_logprob = 0.0
```

## **3.3 Sequence**

`Sequence` 用于存储序列的数据、状态和块信息,且每个序列有唯一标识，即`seq_id`。注意看下面的代码：

* **数据**其实是通过上面的 `SequenceData` 保存的
* 默认初始化状态，所有句子序列的**状态**都是 `SequenceStatus.WAITING`
* 所谓**块信息**，其实就是 vLLM 会在初始化阶段预留出一定数量的CPU 和 GPU 内存，一般是以 token 为单位的，例如在初始化的时候会使用值全为 0，大小为 (256, 128)的 prompt\_ids做 warm up。每个序列会按照实际大小申请 block 来记录内存使用情况，即序列 token 数越多，属性`logical_token_blocks`包含的 block 个数也就越多。

```
class Sequence:
    def __init__(
        self,
        seq_id: int,
        prompt: str,
        prompt_token_ids: List[int],
        block_size: int,
    ) -> None:
        self.seq_id = seq_id
        self.prompt = prompt
        self.block_size = block_size

        self.data = SequenceData(prompt_token_ids) # 数据

        self.logical_token_blocks: List[LogicalTokenBlock] = []
        # Initialize the logical token blocks with the prompt token ids.
        self._append_tokens_to_blocks(prompt_token_ids) # 块信息
        self.status = SequenceStatus.WAITING # 状态
  ...
```

## **3.3 SequenceGroup**

`Sequence`只是单个序列的表示方式,`seq_id`是它的唯一标识。`SequenceGroup`则是为了表示多个序列，`request_id`是它的唯一标识，表示是第几个请求。

具体而言，可以看到`__init__`函数有个参数是 `seqs: List[Sequence]`，它表示由一个或多个 Sequence 组成的列表，然后会通过`self.seqs_dict = {seq.seq_id: seq for seq in seqs}`转化成字典方便管理，这个字典的 key 是每个 Sequence 的唯一标识`seq_id`。

```
class SequenceGroup:
    def __init__(
        self,
        request_id: str,
        seqs: List[Sequence],
        sampling_params: SamplingParams,
        arrival_time: float,
        lora_request: Optional[LoRARequest] = None,
        prefix: Optional[Prefix] = None,
    ) -> None:
        self.request_id = request_id
        self.seqs_dict = {seq.seq_id: seq for seq in seqs}
        self.sampling_params = sampling_params
        self.arrival_time = arrival_time
  ...
```

下面是 vLLm 中 LLMEngine 使用 Sequence 和 SequenceGroup 的场景示例：

```
class LLMEngine:
    def add_request(
        self,
        request_id: str,
        prompt: Optional[str],
        sampling_params: SamplingParams,
        prompt_token_ids: Optional[List[int]] = None,
        arrival_time: Optional[float] = None,
        lora_request: Optional[LoRARequest] = None,
        prefix_pos: Optional[int] = None,
    ) -> None:
        prompt_token_ids = self.encode_request(
            request_id=request_id,
            prompt=prompt,
            prompt_token_ids=prompt_token_ids,
            lora_request=lora_request) # 将字符串序列转换成 id

        # Create the sequences.
        block_size = self.cache_config.block_size
        seq_id = next(self.seq_counter)
        seq = Sequence(seq_id, prompt, prompt_token_ids, block_size,
                       lora_request)

        # Create the sequence group.
        seq_group = SequenceGroup(request_id, [seq], sampling_params,
                                  arrival_time)

        # Add the sequence group to the scheduler.
        self.scheduler.add_seq_group(seq_group)
```

可以看到`SequenceGroup`的`seqs`参数在最初阶段其实只是单个序列 ，即`[seq]`。但是我们知道其实一个 prompt 可以有多个输出结果，所以`SequenceGroup`的目的是管理一个输入 prompt的多个生成序列信息。如果我们设置`SamplingParams.n=2`（第 4 节会介绍），那么在推理过程中，`SequenceGroup`会新增一个 Sequence，这个新增的 Sequence 的 seq\_id 和原来的那个 Sequence 不一样，具体的代码细节会在下一篇文章中介绍。

## **3.5 SequenceGroupMetadata**

```
class SequenceGroupMetadata:
    def __init__(
        self,
        request_id: str,
        is_prompt: bool,
        seq_data: Dict[int, SequenceData],
        sampling_params: SamplingParams,
        block_tables: Dict[int, List[int]],
    ) -> None:
        self.request_id = request_id
        self.is_prompt = is_prompt
        self.seq_data = seq_data
        self.sampling_params = sampling_params
        self.block_tables = block_tables
  ...
```

SequenceGroupMetadata 记录了一些元信息，下面代码展示了 Scheduler 模块是如何生成这些信息的：

* `request_id` 就是 SequenceGroup的 request\_id
* `seq_data` 是一个字典，key 是每个 Sequence的 seq\_id，value 则是对应的 data （即 SequenceData）
* `block_tables`也是一个字典，key 也是每个 Sequence的 seq\_id，value 这是对应 Sequence 申请的 block

```
class Scheduler:
    def schedule(self) -> Tuple[List[SequenceGroupMetadata], SchedulerOutputs]:
        scheduler_outputs = self._schedule()

        # Create input data structures.
        seq_group_metadata_list: List[SequenceGroupMetadata] = []
        for seq_group in scheduler_outputs.scheduled_seq_groups:
            seq_data: Dict[int, SequenceData] = {}
            block_tables: Dict[int, List[int]] = {}
            for seq in seq_group.get_seqs(status=SequenceStatus.RUNNING):
                seq_id = seq.seq_id
                seq_data[seq_id] = seq.data # 单个 SequenceData
                block_tables[seq_id] = self.block_manager.get_block_table(seq) # 对应Sequence的block信息

            seq_group_metadata = SequenceGroupMetadata(
                request_id=seq_group.request_id,
                is_prompt=scheduler_outputs.prompt_run,
                seq_data=seq_data,
                sampling_params=seq_group.sampling_params,
                block_tables=block_tables,
                lora_request=seq_group.lora_request,
                prefix=seq_group.prefix,
            )
            seq_group_metadata_list.append(seq_group_metadata)
        return seq_group_metadata_list, scheduler_outputs
```

## **3.6 SequenceOutput 和 SequenceGroupOutput**

SequenceOutput 和 SequenceGroupOutput的关系就类似 Sequence 和 SequenceGroup。SequenceOutput其实就是记录了上一个 输入 token id 以及对应输出的 token id。

```
class SequenceOutput:
    def __init__(
        self,
        parent_seq_id: int,
        output_token: int,
        logprobs: Dict[int, float],
    ) -> None:
        self.parent_seq_id = parent_seq_id
        self.output_token = output_token
        self.logprobs = logprobs

class SequenceGroupOutput:
    def __init__(
        self,
        samples: List[SequenceOutput],
        prompt_logprobs: Optional[PromptLogprobs],
    ) -> None:
        self.samples = samples
        self.prompt_logprobs = prompt_logprobs
```

## **4. SamplingParams**

![](https://picx.zhimg.com/50/v2-18236626ba33edfb0386073548ceb970_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='244' height='467'></svg>)

SamplingParams 包含以下参数：

* `n`：要生成的序列的数量，默认为 1。
* `best_of`：从多少个序列中选择最佳序列，需要大于 n，默认等于 n。
* `temperature`：用于控制生成结果的随机性，较低的温度会使生成结果更确定性，较高的温度会使生成结果更随机。
* `top_p`：用于过滤掉生成词汇表中概率低于给定阈值的词汇，控制随机性。
* `top_k`：选择前 k 个候选 token，控制多样性。
* `presence_penalty`：用于控制生成结果中特定词汇的出现频率。
* `frequency_penalty`：用于控制生成结果中词汇的频率分布。
* `repetition_penalty`：用于控制生成结果中的词汇重复程度。
* `use_beam_search`：是否使用束搜索来生成序列。
* `length_penalty`：用于控制生成结果的长度分布。
* `early_stopping`：是否在生成过程中提前停止。
* `stop`：要停止生成的词汇列表。
* `stop_token_ids`：要停止生成的词汇的ID列表。
* `include_stop_str_in_output`：是否在输出结果中包含停止字符串。
* `ignore_eos`：在生成过程中是否忽略结束符号。
* `max_tokens`：生成序列的最大长度。
* `logprobs`：用于记录生成过程的概率信息。
* `prompt_logprobs`：用于记录生成过程的概率信息，用于特定提示。
* `skip_special_tokens`：是否跳过特殊符号。
* `spaces_between_special_tokens`：是否在特殊符号之间添加空格。

这些参数的设置通常取决于具体需求和模型性能。以下是一些常见的设置指导方法：

* `temperature`：较低的温度（如0.2）会产生更确定性的结果，而较高的温度（如0.8）会产生更随机的结果。您可以根据您的需求进行调整。
* `presence_penalty、frequency_penalty 和 repetition_penalty`：这些参数可以用于控制生成结果中的词汇分布和重复程度。您可以根据您的需求进行调整。
* `use_beam_search`：束搜索通常用于生成更高质量的结果，但可能会降低生成速度。您可以根据您的需求进行调整。
* `length_penalty`：这个参数可以用于控制生成结果的长度。较高的值会产生更长的结果，而较低的值会产生更短的结果。您可以根据您的需求进行调整。
* `early_stopping`：如果您不希望生成过长的结果，可以设置此参数为True。
* `stop 和 stop_token_ids`：您可以使用这些参数来指定生成结果的结束条件。

## **5. Output 模块**

![](https://picx.zhimg.com/50/v2-067aa13f79c213df18df86f50ae2f7c8_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='233' height='382'></svg>)

Output 主要用于表示语言模型（LLM）的生成结果，包含如下两个模块：

* `CompletionOutput`
* `RequestOutput`

通过上面的介绍我们知道一个 request 可能包含多个序列，`CompletionOutput` 用来表示一个 request 中某个序列的完整输出的数据，其中下面的`index`就表示该序列在 request 中的索引位置

```
class CompletionOutput:
    def __init__(
        self,
        index: int, # 输出结果在请求中的索引
        text: str, # 生成的文本
        token_ids: List[int], # 生成的文本对应的 token ID 列表
        cumulative_logprob: float,
        logprobs: Optional[SampleLogprobs],
        finish_reason: Optional[str] = None, # 序列完成的原因（SequenceStatus）
        lora_request: Optional[LoRARequest] = None,
    ) -> None:
        self.index = index
        self.text = text
        self.token_ids = token_ids
        self.finish_reason = finish_reason
```

`RequestOutput`则表示 request 所有序列的输出结果，有它的初始化函数可以看到它记录了对应的 `request_id`。

```
class RequestOutput:
    def __init__(
        self,
        request_id: str,
        prompt: str,
        prompt_token_ids: List[int],
        prompt_logprobs: Optional[PromptLogprobs],
        outputs: List[CompletionOutput],
        finished: bool,
        lora_request: Optional[LoRARequest] = None,
    ) -> None:
        self.request_id = request_id
        self.prompt = prompt
        self.prompt_token_ids = prompt_token_ids
        self.outputs = outputs
        self.finished = finished
```

我们看看RequestOutput的from\_seq\_group就能很好理解`CompletionOutput`和 `RequestOutput`是如何使用的了。为方便理解，代码有删减，但是不影响最终结果：

```
class RequestOutput:
    @classmethod
    def from_seq_group(cls, seq_group: SequenceGroup) -> "RequestOutput":
        # 1. Get the top-n sequences.
        n = seq_group.sampling_params.n # 每个序列返回的生成序列数量
        seqs = seq_group.get_seqs()
  # 根据累积 logprob 值来选择出前 n 个生成序列
  sorting_key = lambda seq: seq.get_cumulative_logprob()
        sorted_seqs = sorted(seqs, key=sorting_key, reverse=True)
        top_n_seqs = sorted_seqs[:n]

        # 2. Create the outputs.
        outputs: List[CompletionOutput] = []
        for seq in top_n_seqs:
            logprobs = seq.output_logprobs
            finshed_reason = SequenceStatus.get_finished_reason(seq.status)
            output = CompletionOutput(seqs.index(seq), seq.output_text,
                                      seq.get_output_token_ids(),
                                      seq.get_cumulative_logprob(), logprobs,
                                      finshed_reason)
            outputs.append(output)

        # Every sequence in the sequence group should have the same prompt.
        prompt = seq_group.prompt
        prompt_token_ids = seq_group.prompt_token_ids
        prompt_logprobs = seq_group.prompt_logprobs
        finished = seq_group.is_finished()
        return cls(seq_group.request_id,
                   prompt,
                   prompt_token_ids,
                   prompt_logprobs,
                   outputs,
                   finished,
                   lora_request=seq_group.lora_request)
```

`RequestOutput`是通过对传入的`seq_group: SequenceGroup`进行解析后得到的。解析过程主要有两个阶段：

1. Get the top-n sequences：这一阶段就是对生成序列按照 cumulative\_logprob 进行排序，最后选择出top-n 序列。
2. Create the outputs：将所有top-n生成序列分别转换成 `CompletionOutput`列表，并作为`RequestOutput`的初始化参数。

### **微信公众号：AutoML机器学习**

**![](https://pic1.zhimg.com/50/v2-87083e55cd41dbef83cc840c142df48a_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='0' height='0'></svg>)**

**MARSGGBO♥原创**  
**如有意合作或学术讨论欢迎私戳联系~**  
**邮箱:marsggbo@foxmail.com**


---

## GPT，Generative 自回归生成，其原理是什么？

`link: https://www.zhihu.com/question/597267302/answer/3303292551 · created: 1700997892`


GPT 训练和推理过程示意图，如有理解错误欢迎指正

![](https://picx.zhimg.com/v2-c3fbe9a5275277ddb7ce0f20a37e8865_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1336' height='1000'></svg>)


---

## 粤港澳多地暴雨持续，深圳水库排洪，香港深夜一小时雨量创 139 年来最高，目前各地情况如何？

`link: https://www.zhihu.com/question/621046941/answer/3206334404 · created: 1694412790`


我住在国贸旁边的公寓，暴雨当晚停电，直到两天后才用发电机供上电，但是还是限时的而且不稳定。住10楼，电梯没供电，每天上下爬十楼就当锻炼了。老街，国贸，罗湖地铁直到今天(2023/09/11)都还没通，而且有的商铺和居民楼也没来电，下面是暴雨第二天晚上在金光华拍的照片，金光华黯淡无光

![](https://picx.zhimg.com/v2-2dbacfee09071c2f1cd6a2fe5b65a5ad_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2276' height='1280'></svg>)![](https://picx.zhimg.com/v2-3d2f55d1f293c140c66ae7016b567225_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2276' height='1280'></svg>)![](https://picx.zhimg.com/v2-a52cd6d7ec427d5bc92f3f451eed75e9_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2276' height='1280'></svg>)![](https://pic1.zhimg.com/v2-aba5c41d3e37f6191d126b58dc2e8b18_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2276' height='1280'></svg>)

现在在香港，又开始下暴雨，不知道还能不能回去了。。。

![](https://picx.zhimg.com/v2-17a520749e04292f750f4035ee07677f_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1280' height='2844'></svg>)![](https://pic1.zhimg.com/v2-c8e7315a263de67594dcfc95a7f3d888_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1280' height='2844'></svg>)![](https://picx.zhimg.com/v2-cff0d3e0c38b80183bf05a5b10490041_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1280' height='2844'></svg>)![](https://pic1.zhimg.com/v2-2e87fddd644aa1492349fce977e518cd_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1280' height='2844'></svg>)![](https://pica.zhimg.com/v2-da6bb9fc9ded29e3bfdeed5edaa6bcb5_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1280' height='2844'></svg>)

真的不想过没电没网，水压还不稳的生活了。。真是一夜回到解放前了


---

## FlashAttention 的速度优化原理是怎样的？

`link: https://www.zhihu.com/question/611236756/answer/3128719955 · created: 1689921775`


[https://arxiv.org/pdf/2205.14135.pdf](https://link.zhihu.com/?target=https%3A//arxiv.org/pdf/2205.14135.pdf)

![](https://pica.zhimg.com/v2-66f1e5829c79eefe92d5b78a7c8a0af4_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2220' height='844'></svg>)

https://arxiv.org/pdf/2205.14135.pdf

## **1. Motivation**

不同硬件模块之间的带宽和存储空间有明显差异，例如下图中左边的三角图，最顶端的是GPU种的SRAM，它的容量非常小但是带宽非常大，以A100 GPU为例，它有108个流式多核处理器，每个处理器上的片上SRAM大小只有192KB，因此A100总共的SRAM大小是192KB![\times](https://www.zhihu.com/equation?tex=%5Ctimes)108![\approx](https://www.zhihu.com/equation?tex=%5Capprox)20MB，但是其吞吐量能高达19TB/s。而A100 GPU HBM（High Bandwidth Memory也就是我们常说的GPU显存大小）大小在40GB~80GB左右，但是带宽只与1.5TB/s。

![](https://picx.zhimg.com/v2-c7e2ecc450e405170eb0128a9455f9cf_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1938' height='830'></svg>)

下图给出了标准的注意力机制的实现流程，可以看到因为HBM的大小更大，我们平时写pytorch代码的时候最常用到的就是HBM，所以对于HBM的读写操作非常频繁，而SRAM利用率反而不高。

![](https://picx.zhimg.com/v2-a9d55ec5b6e8dadbb378e004bcab33c9_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1652' height='402'></svg>)

FlashAttention的主要动机就是希望把SRAM利用起来，但是难点就在于SRAM太小了，一个普通的矩阵乘法都放不下去。FlashAttention的解决思路就是将计算模块进行分解，拆成一个个小的计算任务。

## **2. Softmax Tiling**

在介绍具体的计算算法前，我们首先需要了解一下Softmax Tiling。

1. 数值稳定： Softmax包含指数函数，所以为了避免数值溢出问题，可以将每个元素都减去最大值，如下图示，最后计算结果和原来的Softmax是一致的。

![](https://picx.zhimg.com/v2-b49a95b04d4881a0400701edefe9550b_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2028' height='180'></svg>)

2. 分块计算Softmax

因为Softmax都是按行计算的，所以我们考虑一行切分成两部分的情况，即原本的一行数据![x\in\mathbb{R}^{2B}=[x^{(1)},x^{(2)}]](https://www.zhihu.com/equation?tex=x%5Cin%5Cmathbb%7BR%7D%5E%7B2B%7D%3D%5Bx%5E%7B%281%29%7D%2Cx%5E%7B%282%29%7D%5D)。

![](https://pic1.zhimg.com/v2-c579a346d995abe09df82199bec1ee4b_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2152' height='358'></svg>)

可以看到计算不同块的f(x)值时，乘上的系数是不同的，但是最后化简后的结果都是指数函数减去了整行的最大值。以![x^{(1)}](https://www.zhihu.com/equation?tex=x%5E%7B%281%29%7D)为例，

![\begin{align} e^{m(x^{(1)})-m(x)}f(x^{(1)})&=e^{m(x^{(1)})-m(x)}[e^{x^{(1)}_1-m(x^{(1)})},...,e^{x^{(1)}_B-m(x^{(1)})}] \notag \\ &=[e^{x^{(1)}_1-m(x)},...,e^{x^{(1)}_B-m(x)}]  \end{align}\\](https://www.zhihu.com/equation?tex=%5Cbegin%7Balign%7D+e%5E%7Bm%28x%5E%7B%281%29%7D%29-m%28x%29%7Df%28x%5E%7B%281%29%7D%29%26%3De%5E%7Bm%28x%5E%7B%281%29%7D%29-m%28x%29%7D%5Be%5E%7Bx%5E%7B%281%29%7D_1-m%28x%5E%7B%281%29%7D%29%7D%2C...%2Ce%5E%7Bx%5E%7B%281%29%7D_B-m%28x%5E%7B%281%29%7D%29%7D%5D+%5Cnotag+%5C%5C+%26%3D%5Be%5E%7Bx%5E%7B%281%29%7D_1-m%28x%29%7D%2C...%2Ce%5E%7Bx%5E%7B%281%29%7D_B-m%28x%29%7D%5D++%5Cend%7Balign%7D%5C%5C)

## **3. FlashAttention算法流程**

FlashAttention算法流程如下图所示

![](https://pic1.zhimg.com/v2-79134704eac6f10245086a216c5b271b_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2248' height='1304'></svg>)

为方便理解，下图将FlashAttention的计算流程可视化出来了，简单理解就是每一次只计算一个block的值，通过多轮的双for循环完成整个注意力的计算。

![](https://picx.zhimg.com/v2-45534db483a314bbc23a6aa59c5f2c8d_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='999' height='1158'></svg>)

下面是FlashAttention的代码实现，参考自[https://github.com/shreyansh26/FlashAttention-PyTorch/tree/master](https://link.zhihu.com/?target=https%3A//github.com/shreyansh26/FlashAttention-PyTorch/tree/master)

```
import torch
import torch.nn as nn
import numpy as np
import sys
import time
from einops import rearrange

BLOCK_SIZE = 1024
NEG_INF = -1e10 # -infinity
EPSILON = 1e-10

def normal_attention_causal(Q, K, V):
    scale = 1 / np.sqrt(Q.shape[-1])
    Q = Q * scale
    QKt = torch.einsum('... i d, ... j d -> ... i j', Q, K)

    Q_LEN = Q.shape[2]
    K_LEN = K.shape[2]

    causal_mask = torch.triu(torch.ones((Q_LEN, K_LEN)), K_LEN - Q_LEN + 1)
    causal_mask = causal_mask.to(device='cuda')
    QKt = torch.where(causal_mask > 0, NEG_INF, QKt)

    attn = nn.functional.softmax(QKt, dim=-1)
    return attn @ V

def flash_attention_causal_forward(Q, K, V):
    O = torch.zeros_like(Q, requires_grad=True)
    l = torch.zeros(Q.shape[:-1])[...,None]
    m = torch.ones(Q.shape[:-1])[...,None] * NEG_INF

    O = O.to(device='cuda')
    l = l.to(device='cuda')
    m = m.to(device='cuda')

    Q_BLOCK_SIZE = min(BLOCK_SIZE, Q.shape[-1])
    KV_BLOCK_SIZE = BLOCK_SIZE

    Q_BLOCKS = torch.split(Q, Q_BLOCK_SIZE, dim=2)
    K_BLOCKS = torch.split(K, KV_BLOCK_SIZE, dim=2)
    V_BLOCKS = torch.split(V, KV_BLOCK_SIZE, dim=2)

    Tr = len(Q_BLOCKS)
    Tc = len(K_BLOCKS)

    O_BLOCKS = list(torch.split(O, Q_BLOCK_SIZE, dim=2))
    l_BLOCKS = list(torch.split(l, Q_BLOCK_SIZE, dim=2))
    m_BLOCKS = list(torch.split(m, Q_BLOCK_SIZE, dim=2))

    Q_LEN = Q.shape[2]
    K_LEN = K.shape[2]

    Q_RANGE = torch.arange(Q_LEN)[:,None] + (K_LEN - Q_LEN)
    K_RANGE = torch.arange(K_LEN)[None,:]

    Q_RANGE = Q_RANGE.to(device='cuda')
    K_RANGE = K_RANGE.to(device='cuda')

    Q_RANGE_BLOCKS = torch.split(Q_RANGE, Q_BLOCK_SIZE, dim=0)
    K_RANGE_BLOCKS = torch.split(K_RANGE, KV_BLOCK_SIZE, dim=1)

    for j in range(Tc):
        Kj = K_BLOCKS[j]
        Vj = V_BLOCKS[j]
        K_RANGE_BLOCKSj = K_RANGE_BLOCKS[j]

        for i in range(Tr):
            Qi = Q_BLOCKS[i]
            Oi = O_BLOCKS[i]
            li = l_BLOCKS[i]
            mi = m_BLOCKS[i]
            Q_RANGE_BLOCKSi = Q_RANGE_BLOCKS[i]

            scale = 1 / np.sqrt(Q.shape[-1])
            Qi_scaled  = Qi * scale

            S_ij = torch.einsum('... i d, ... j d -> ... i j', Qi_scaled, Kj)
            
            # Masking
            causal_mask = Q_RANGE_BLOCKSi >= K_RANGE_BLOCKSj
            S_ij = torch.where(causal_mask > 0, S_ij, NEG_INF)

            m_block_ij, _ = torch.max(S_ij, dim=-1, keepdims=True)
            P_ij = torch.exp(S_ij - m_block_ij)
            # Masking
            P_ij = torch.where(causal_mask > 0, P_ij, 0)

            l_block_ij = torch.sum(P_ij, dim=-1, keepdims=True) + EPSILON

            P_ij_Vj = torch.einsum('... i j, ... j d -> ... i d', P_ij, Vj)

            mi_new = torch.maximum(m_block_ij, mi)
            li_new = torch.exp(mi - mi_new) * li + torch.exp(m_block_ij - mi_new) * l_block_ij
            
            O_BLOCKS[i] = (li/li_new) * torch.exp(mi - mi_new) * Oi + (torch.exp(m_block_ij - mi_new) / li_new) * P_ij_Vj
            l_BLOCKS[i] = li_new
            m_BLOCKS[i] = mi_new
        
    O = torch.cat(O_BLOCKS, dim=2)
    l = torch.cat(l_BLOCKS, dim=2)
    m = torch.cat(m_BLOCKS, dim=2)
    return O, l, m

def flash_attention_causal_backward(Q, K, V, O, l, m, dO):
    Q_BLOCK_SIZE = min(BLOCK_SIZE, Q.shape[-1])
    KV_BLOCK_SIZE = BLOCK_SIZE

    Q_BLOCKS = torch.split(Q, Q_BLOCK_SIZE, dim=2)
    K_BLOCKS = torch.split(K, KV_BLOCK_SIZE, dim=2)
    V_BLOCKS = torch.split(V, KV_BLOCK_SIZE, dim=2)

    Tr = len(Q_BLOCKS)
    Tc = len(K_BLOCKS)

    O_BLOCKS = list(torch.split(O, Q_BLOCK_SIZE, dim=2))
    dO_BLOCKS = list(torch.split(dO, Q_BLOCK_SIZE, dim=2))
    l_BLOCKS = list(torch.split(l, Q_BLOCK_SIZE, dim=2))
    m_BLOCKS = list(torch.split(m, Q_BLOCK_SIZE, dim=2))

    dQ = torch.zeros_like(Q, requires_grad=True).to(device='cuda')
    dK = torch.zeros_like(K, requires_grad=True).to(device='cuda')
    dV = torch.zeros_like(V, requires_grad=True).to(device='cuda')

    dQ_BLOCKS = list(torch.split(dQ, Q_BLOCK_SIZE, dim=2))
    dK_BLOCKS = list(torch.split(dK, KV_BLOCK_SIZE, dim=2))
    dV_BLOCKS = list(torch.split(dV, KV_BLOCK_SIZE, dim=2))

    Q_LEN = Q.shape[2]
    K_LEN = K.shape[2]

    Q_RANGE = torch.arange(Q_LEN)[:,None] + (K_LEN - Q_LEN)
    K_RANGE = torch.arange(K_LEN)[None,:]

    Q_RANGE = Q_RANGE.to(device='cuda')
    K_RANGE = K_RANGE.to(device='cuda')

    Q_RANGE_BLOCKS = torch.split(Q_RANGE, Q_BLOCK_SIZE, dim=0)
    K_RANGE_BLOCKS = torch.split(K_RANGE, KV_BLOCK_SIZE, dim=1)

    for j in range(Tc):
        Kj = K_BLOCKS[j]
        Vj = V_BLOCKS[j]
        K_RANGE_BLOCKSj = K_RANGE_BLOCKS[j]

        dKj_block = torch.zeros_like(dK_BLOCKS[j], requires_grad=True).to(device='cuda')
        dVj_block = torch.zeros_like(dV_BLOCKS[j], requires_grad=True).to(device='cuda')

        for i in range(Tr):
            Qi = Q_BLOCKS[i]
            Oi = O_BLOCKS[i]
            dOi = dO_BLOCKS[i]
            li = l_BLOCKS[i]
            mi = m_BLOCKS[i]
            Q_RANGE_BLOCKSi = Q_RANGE_BLOCKS[i]

            scale = 1 / np.sqrt(Q.shape[-1])
            Qi_scaled  = Qi * scale

            S_ij = torch.einsum('... i d, ... j d -> ... i j', Qi_scaled, Kj)
            
            # Masking
            causal_mask = Q_RANGE_BLOCKSi >= K_RANGE_BLOCKSj
            S_ij = torch.where(causal_mask > 0, S_ij, NEG_INF)

            P_ij = (1/li) * torch.exp(S_ij - mi)
            # Masking
            P_ij = torch.where(causal_mask > 0, P_ij, 0)

            dVj_block = dVj_block + torch.einsum('... r c, ... r d -> ... c d', P_ij, dOi)
            dP_ij = torch.einsum('... r d, ... c d -> ... r c', dOi, Vj)

            Di = torch.sum(dOi * Oi, dim=-1, keepdims=True)
            dS_ij = P_ij * (dP_ij - Di)

            dQ_BLOCKS[i] = dQ_BLOCKS[i] + scale * torch.einsum('... r c, ... c d -> ... r d', dS_ij, Kj)

            dKj_block = dKj_block + scale * torch.einsum('... r c, ... r d -> ... c d', dS_ij, Qi)
        
        dK_BLOCKS[j] = dKj_block
        dV_BLOCKS[j] = dVj_block
    
    dQ = torch.cat(dQ_BLOCKS, dim=2)
    dK = torch.cat(dK_BLOCKS, dim=2)
    dV = torch.cat(dV_BLOCKS, dim=2)
    return dQ, dK, dV

def flash_attention_causal(Q, K, V):
    out = flash_attention_causal_forward(Q, K, V)
    return out[0]

if __name__ == "__main__":
    Q = torch.randn(1, 2, 4096, 1024, requires_grad=True).to(device='cuda')
    K = torch.randn(1, 2, 4096, 1024, requires_grad=True).to(device='cuda')
    V = torch.randn(1, 2, 4096, 1024, requires_grad=True).to(device='cuda')

    for i in range(10):
        start1 = time.time_ns()
        out1 = flash_attention_causal(Q, K, V)
        end1 = time.time_ns()

        start2 = time.time_ns()
        out2 = normal_attention_causal(Q, K, V)
        end2 = time.time_ns()

        t1 = (end1 - start1) / 1000000
        t2 = (end2 - start2) / 1000000

        print(f'{t1}ms, {t2}ms')
        print(torch.allclose(out1, out2, atol=1e-5))
```

---

### **微信公众号：AutoML机器学习**

**![](https://pica.zhimg.com/50/v2-87083e55cd41dbef83cc840c142df48a_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='0' height='0'></svg>)**

**MARSGGBO♥原创**  
**如有意合作或学术讨论欢迎私戳联系~**  
**邮箱:marsggbo@foxmail.com**


---

## 如何优化transformer的attention?

`link: https://www.zhihu.com/question/602057035/answer/3087265062 · created: 1687570960`


论文:Transformer Quality in Linear Time

会议/期刊: ICML 年份: 2022

## **1. Vanilla Transformer Block（MHSA+FFN）**

原本的Transformer的Block遵循如下的设计范式：MHSA（多头自注意力）+ 一层或者两层的FFN（全连接层），如下图所示。我们只考虑FFN的话，其数学表达式如下：T表示句子长度，d表示词向量维度（也表示模型隐藏层维度），e表示expanded intermediate 特征大小。

![{\cal O}=\phi(X W_{u})W_{o}\mathrm{~Where~}\,\, X\in\mathbb{R}^{T\times d}, W _{u}\in\mathbb{R}^{d\times e},W_{o}\in\mathbb{R}^{e\times d} \\](https://www.zhihu.com/equation?tex=%7B%5Ccal+O%7D%3D%5Cphi%28X+W_%7Bu%7D%29W_%7Bo%7D%5Cmathrm%7B~Where~%7D%5C%2C%5C%2C+X%5Cin%5Cmathbb%7BR%7D%5E%7BT%5Ctimes+d%7D%2C+W+_%7Bu%7D%5Cin%5Cmathbb%7BR%7D%5E%7Bd%5Ctimes+e%7D%2CW_%7Bo%7D%5Cin%5Cmathbb%7BR%7D%5E%7Be%5Ctimes+d%7D+%5C%5C)

![](https://pica.zhimg.com/50/v2-5f50654e12df0193e552dcaab1e22e29_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='242' height='337'></svg>)

图1 多头注意力

## **2. 改进Transformer Block （MHSA+GLU）**

后面有工作对FFN做了改进，提出了[GLU（Gated Linear Unit）结构](https://link.zhihu.com/?target=https%3A//www.notion.so/GLU-Variants-Improve-Transformer-8651dcfc5b444fa3ba379ce50624584d%3Fpvs%3D21)，并且发现能有效提升模型性能。GLU结构大致如下图。简单理解就是有两个支路，两条支路都是全连接层加激活函数。两条支路的激活函数可以不同。最后两路的结果会做element-wise相乘，得到的结果会再经过一个全连接层进行处理。

![](https://picx.zhimg.com/v2-d7eee1de2fe52666de4b673e48c6962f_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1578' height='985'></svg>)

图2 GLU+MHSA

上图左边的GLU结构的数学表达式如下：

![\begin{array}{l l}{{U=\phi_{u}(X W_{u}),}}&{{V=\phi_{v}(X W_{v})}}\\ {{{O}=\left(U \odot V\right)W_{o}}}\tag{1}\end{array} ](https://www.zhihu.com/equation?tex=%5Cbegin%7Barray%7D%7Bl+l%7D%7B%7BU%3D%5Cphi_%7Bu%7D%28X+W_%7Bu%7D%29%2C%7D%7D%26%7B%7BV%3D%5Cphi_%7Bv%7D%28X+W_%7Bv%7D%29%7D%7D%5C%5C+%7B%7B%7BO%7D%3D%5Cleft%28U+%5Codot+V%5Cright%29W_%7Bo%7D%7D%7D%5Ctag%7B1%7D%5Cend%7Barray%7D+)

其中![U,V\in\mathbb{R}^{T\times e}，O\in\mathbb{R}^{T\times d}](https://www.zhihu.com/equation?tex=U%2CV%5Cin%5Cmathbb%7BR%7D%5E%7BT%5Ctimes+e%7D%EF%BC%8CO%5Cin%5Cmathbb%7BR%7D%5E%7BT%5Ctimes+d%7D)

## **3. GAU（Gated Attention Unit）**

上面的GLU和注意力模块是独立开的，GAU做了一个很巧的构思把二者融合到了一个模块，其结构和伪代码如下图所示

![](https://pic1.zhimg.com/v2-dab2f95cd0224dcfd8c8dc84048b4ff9_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2162' height='1125'></svg>)

图3 GAU示意图和伪代码

GAU的数学表达式如下：

![{O}=(U\odot\hat{V})W_{o}\quad\mathrm{where}\quad\hat{V}=A V \tag{2} ](https://www.zhihu.com/equation?tex=%7BO%7D%3D%28U%5Codot%5Chat%7BV%7D%29W_%7Bo%7D%5Cquad%5Cmathrm%7Bwhere%7D%5Cquad%5Chat%7BV%7D%3DA+V+%5Ctag%7B2%7D+)

其中

![\begin{array}{l l}{{Z=\phi_{z}(X W_{z})}}&{{\qquad\in\mathbb{R}^{T\times s} }}\\ {{A=\operatorname{relu}^{2}\left(\mathcal{Q}(Z)\mathcal{K}(Z)^{\top}+b\right)}}&{{\qquad\in\mathbb{R}^{T\times T} }}\tag{3}\end{array} ](https://www.zhihu.com/equation?tex=%5Cbegin%7Barray%7D%7Bl+l%7D%7B%7BZ%3D%5Cphi_%7Bz%7D%28X+W_%7Bz%7D%29%7D%7D%26%7B%7B%5Cqquad%5Cin%5Cmathbb%7BR%7D%5E%7BT%5Ctimes+s%7D+%7D%7D%5C%5C+%7B%7BA%3D%5Coperatorname%7Brelu%7D%5E%7B2%7D%5Cleft%28%5Cmathcal%7BQ%7D%28Z%29%5Cmathcal%7BK%7D%28Z%29%5E%7B%5Ctop%7D%2Bb%5Cright%29%7D%7D%26%7B%7B%5Cqquad%5Cin%5Cmathbb%7BR%7D%5E%7BT%5Ctimes+T%7D+%7D%7D%5Ctag%7B3%7D%5Cend%7Barray%7D+)

可以看到在计算注意力矩阵A用到的Q和K是基于共享的矩阵Z计算得到的，![\mathcal{Q}(Z), \mathcal{K}(Z)](https://www.zhihu.com/equation?tex=%5Cmathcal%7BQ%7D%28Z%29%2C+%5Cmathcal%7BK%7D%28Z%29)都是对矩阵Z做per-dim的归一化，类似于LayerNorm。得到注意力A后，还要经过ReLU激活函数，然后取二次方，即![relu^2](https://www.zhihu.com/equation?tex=relu%5E2)，这个是在《[Primer: Searching for Efficient Transformers for Language Modeling](https://link.zhihu.com/?target=https%3A//arxiv.org/abs/2109.08668)》论文中用NAS搜索出来的。

## **3.1 参数量比较**

下面我们比较一下 MHSA +MLP/GLU与 GAU 结构的参数量：

* MHSA+MLP/GLU

+ MHSA: Q, K, V对应的映射模块权重均为 ![h\times d\times d/h=d^2](https://www.zhihu.com/equation?tex=h%5Ctimes+d%5Ctimes+d%2Fh%3Dd%5E2) *,最后MHSA的Dense层的权重参数量也是* ![d^2 ](https://www.zhihu.com/equation?tex=d%5E2+) ，所以MHSA的参数量为4![d^2 ](https://www.zhihu.com/equation?tex=d%5E2+)
+ MLP: 通常是两个全连接层，每个的权重参数量为d*e,一般e=4d，所以MLP模块的权重参数量为* ![2(d*e)=2 (d*4d)=8d^2](https://www.zhihu.com/equation?tex=2%28d%2Ae%29%3D2+%28d%2A4d%29%3D8d%5E2)
+ GLU: 如果采用GLU结构，那么权重参数量则为 ![3*d*e=12d^2](https://www.zhihu.com/equation?tex=3%2Ad%2Ae%3D12d%5E2)
+ 总结：如果采用MHSA+MLP，则参数量是12*d*d；如果采用MHSA+GLU，则参数量是16*d*d

* GAU参数量为3*d*e+d*s。通常s会远远小于d,所以参数量近似为3*d*e。改论文中，作者设置e=2d,那么GAU模块的参数量则为* ![6d^2](https://www.zhihu.com/equation?tex=6d%5E2) 。换言之两个GAU级联后的参数量等价于MHSA+MLP。

## **3.2 计算复杂度比较**

对比GLU+MHSA和GAU，我们可以看到GAU只有一个head，而且去掉了Softmax，而且实验结果显示GAU的表现和原来的MHSA+MLP也不分伯仲，甚至更好

![](https://picx.zhimg.com/v2-dd1f44079d5522f7c687f34285bd0493_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='998' height='352'></svg>)

图4 GAU和Transformer实验结果对比

但是，仔细分析一下，我们会发现GAU的计算复杂度和原本的自注意力机制一样，仍旧是句子长度的二次方，即![O(T^2)](https://www.zhihu.com/equation?tex=O%28T%5E2%29)。

下面我们分析一下二次复杂度的来源，GAU和原始的自注意力机制的计算都可以用如下的数学公式表示：

![A=\phi(QK^T)V \\](https://www.zhihu.com/equation?tex=A%3D%5Cphi%28QK%5ET%29V+%5C%5C)

在原始的自注意力机制中，激活函数![\phi](https://www.zhihu.com/equation?tex=%5Cphi)是softmax，而在GAU中是![ReLU^2](https://www.zhihu.com/equation?tex=ReLU%5E2)。矩阵![Q, K\in\mathbb{R}^{T\times d}](https://www.zhihu.com/equation?tex=Q%2C+K%5Cin%5Cmathbb%7BR%7D%5E%7BT%5Ctimes+d%7D)，二者矩阵乘法的复杂度为![O(T\times d \times T)](https://www.zhihu.com/equation?tex=O%28T%5Ctimes+d+%5Ctimes+T%29),如果只考虑句子长度，我们可以将d忽视，所以复杂度为![O(T^2)](https://www.zhihu.com/equation?tex=O%28T%5E2%29).

后续的一些尝试将复杂度降低至线性复杂度的方法的思路如下所示：

![\phi(QK^T)V\rightarrow(\phi_q(Q)\phi_k(K)^T)V=\phi_q(Q)(\phi_k(K)^TV) \\](https://www.zhihu.com/equation?tex=%5Cphi%28QK%5ET%29V%5Crightarrow%28%5Cphi_q%28Q%29%5Cphi_k%28K%29%5ET%29V%3D%5Cphi_q%28Q%29%28%5Cphi_k%28K%29%5ETV%29+%5C%5C)

简而言之就是尝试将矩阵![K^T](https://www.zhihu.com/equation?tex=K%5ET)和![V](https://www.zhihu.com/equation?tex=V)先做矩阵乘法，这样一来它们的复杂度则为![O(d\times T \times d)](https://www.zhihu.com/equation?tex=O%28d%5Ctimes+T+%5Ctimes+d%29)，得到大小为![\mathbb{R}^{d\times d}](https://www.zhihu.com/equation?tex=%5Cmathbb%7BR%7D%5E%7Bd%5Ctimes+d%7D)的矩阵，该矩阵再和![Q](https://www.zhihu.com/equation?tex=Q)相乘，计算复杂度同样是![O(d\times T \times d)](https://www.zhihu.com/equation?tex=O%28d%5Ctimes+T+%5Ctimes+d%29)。

## **3.3 推理阶段的复杂度**

我们接下来考虑推理时GAU的复杂度。

我们知道GAU会先算![M=K^TV](https://www.zhihu.com/equation?tex=M%3DK%5ETV)，然后再计算![QM](https://www.zhihu.com/equation?tex=QM)，所以我们先着重分析一下矩阵![M](https://www.zhihu.com/equation?tex=M)的计算。

由于推理阶段采用的是自回归的解码方式，也就是说K和V的长度（即词数量）是从1逐渐增加到T的。考虑t时刻的情况，要得到矩阵![M_t](https://www.zhihu.com/equation?tex=M_t), 我们需要![O(d*t*d)](https://www.zhihu.com/equation?tex=O%28d%2At%2Ad%29)的计算复杂度，随着t逐渐从1增加到T，计算复杂度是不断增加的，换言之计算复杂度是![O(Td^2)](https://www.zhihu.com/equation?tex=O%28Td%5E2%29)。

这里其实有一个计算上的技巧，即我们需要先存储上一次的结果![M_{t-1}](https://www.zhihu.com/equation?tex=M_%7Bt-1%7D)。当到t时刻的时候，我们计算出新词的![K_t,V_t\in\mathbb{R}^{1\times d}](https://www.zhihu.com/equation?tex=K_t%2CV_t%5Cin%5Cmathbb%7BR%7D%5E%7B1%5Ctimes+d%7D)向量，然后计算![K_t^TV_t\in\mathbb{R}^{d\times d}](https://www.zhihu.com/equation?tex=K_t%5ETV_t%5Cin%5Cmathbb%7BR%7D%5E%7Bd%5Ctimes+d%7D)，最后将这个值和![M_{t-1}](https://www.zhihu.com/equation?tex=M_%7Bt-1%7D)累加即可得到![M_t](https://www.zhihu.com/equation?tex=M_t)，即

![M_t=M_{t-1}+K_t^TV_t \tag{4} ](https://www.zhihu.com/equation?tex=M_t%3DM_%7Bt-1%7D%2BK_t%5ETV_t+%5Ctag%7B4%7D+)

简而言之，每个时刻（即有新的词输入的时候），只需要计算新词的![K_t^TV_t](https://www.zhihu.com/equation?tex=K_t%5ETV_t)即可，因此空间复杂度是![O(d^2)](https://www.zhihu.com/equation?tex=O%28d%5E2%29)，计算复杂度始终保持为![O(d^2)](https://www.zhihu.com/equation?tex=O%28d%5E2%29)，相比于原来的![O(Td^2)](https://www.zhihu.com/equation?tex=O%28Td%5E2%29)计算复杂度有了明显改进。

上述这种计算技巧在推理阶段非常有效，可以很巧妙地降低计算复杂度。但是，在训练阶段就会有问题了，因为这个技巧是基于自回归的特点设计的，也就是说推理阶段就像RNN一样，每次只新增一个单词，无需考虑并行性。训练阶段输入的数据一般是大小为![b\times T\times d](https://www.zhihu.com/equation?tex=b%5Ctimes+T%5Ctimes+d)的张量，如果想采用上面的计算技巧，那么训练阶段的输入就需要像推理阶段一样，显然这会得不偿失，因为这样无法并行计算了。

## **4. Mixed Chunk Attention**

为了解决上面提到的推理计算技巧无法应用到训练阶段，本文作者提出了Mixed Chunk Attention方法，该方法将Partial Attention（简单理解就是只计算更重要部分的注意力，但是实际上这类方法的计算效率不高，因为计算是不规则和碎片化的）和Linear Attention的优点进行了结合。

![](https://picx.zhimg.com/v2-f974b9762f3e01c0d7c644e2e98a8c10_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1348' height='1250'></svg>)

图5 三种不同注意力计算方法

上面图中每个圆圈代表一个单词的词向量，中间的正方形表示![M_t=M_{t-1}+K_t^TV_t](https://www.zhihu.com/equation?tex=M_t%3DM_%7Bt-1%7D%2BK_t%5ETV_t)。

图（top）表示原始的注意力机制计算方法，每次计算注意力矩阵的复杂度是![O(T^2d)](https://www.zhihu.com/equation?tex=O%28T%5E2d%29)。

图（middle）即表示通过公式(4)可以复用前一时刻的结果，将计算复杂度降低至![O(d^2)](https://www.zhihu.com/equation?tex=O%28d%5E2%29)，但是在这种类似RNN的计算方式缺乏并行性，很难在训练阶段使用

图（bottom）则做了这种，所以称作mixed chunk attention （MCA）。假设输入序列维度是![b\times T\times d](https://www.zhihu.com/equation?tex=b%5Ctimes+T%5Ctimes+d)，后面为避免符号太多，我们省略batch size，即![b](https://www.zhihu.com/equation?tex=b)。由图（bottom）可以看到，MCA其实就是将原来的一个句子划分成![G](https://www.zhihu.com/equation?tex=G)个chunk，每个chunk包含![C](https://www.zhihu.com/equation?tex=C)个单词（该论文取![C=256](https://www.zhihu.com/equation?tex=C%3D256)），也就是说原来的句子长度![T=G\times C](https://www.zhihu.com/equation?tex=T%3DG%5Ctimes+C)。所以原本的输入序列![T\times d\rightarrow G\times C\times d](https://www.zhihu.com/equation?tex=T%5Ctimes+d%5Crightarrow+G%5Ctimes+C%5Ctimes+d)。原本的GAU模块转变成了如下图：

![](https://picx.zhimg.com/v2-13ecdaee74494dc151e589e5ea06e018_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='430' height='464'></svg>)

图6 Mixed Chunk Attention

为方便理解，我们只考虑单个chunk，那么对于第![g](https://www.zhihu.com/equation?tex=g)个chunk，则中间结果![U_g\in\mathbb{R}^{C\times e},V_g\in\mathbb{R}^{C\times e},Z_g\in\mathbb{R}^{C\times s},](https://www.zhihu.com/equation?tex=U_g%5Cin%5Cmathbb%7BR%7D%5E%7BC%5Ctimes+e%7D%2CV_g%5Cin%5Cmathbb%7BR%7D%5E%7BC%5Ctimes+e%7D%2CZ_g%5Cin%5Cmathbb%7BR%7D%5E%7BC%5Ctimes+s%7D%2C)其中Q，K矩阵是基于共享的![Z_g](https://www.zhihu.com/equation?tex=Z_g)采用不同的放射变化得到的，具体而言会有两套Q，K矩阵：

* 一套用于计算local Attention的复杂度为二次方的![Q_g^{quad},K_g^{quad}\in\mathbb{R}^{C\times s}](https://www.zhihu.com/equation?tex=Q_g%5E%7Bquad%7D%2CK_g%5E%7Bquad%7D%5Cin%5Cmathbb%7BR%7D%5E%7BC%5Ctimes+s%7D)。如图5（bottom）最下面那一行圆圈所示，每两个圆圈之间会计算彼此之间的注意力矩阵，这其实可以理解成一种稀疏的注意力，其计算公式如下

![\hat{V}_g^{quad}=relu^2(Q_g^{quad}K_g^{quad}+B)V_g \tag{5} ](https://www.zhihu.com/equation?tex=%5Chat%7BV%7D_g%5E%7Bquad%7D%3Drelu%5E2%28Q_g%5E%7Bquad%7DK_g%5E%7Bquad%7D%2BB%29V_g+%5Ctag%7B5%7D+)

单个chunk的local Attention的计算中的![Q_g^{quad}K_g^{quad}](https://www.zhihu.com/equation?tex=Q_g%5E%7Bquad%7DK_g%5E%7Bquad%7D)计算复杂度为![O(C^2s)](https://www.zhihu.com/equation?tex=O%28C%5E2s%29)，计算得到的结果与矩阵![V_g](https://www.zhihu.com/equation?tex=V_g)相乘的计算复杂度为![O(C^2e)](https://www.zhihu.com/equation?tex=O%28C%5E2e%29)，因为$s<

* 另一套是用于计算global Attention的复杂度为线性的![Q_g^{lin},K_g^{lin}\in\mathbb{R}^{C\times s}](https://www.zhihu.com/equation?tex=Q_g%5E%7Blin%7D%2CK_g%5E%7Blin%7D%5Cin%5Cmathbb%7BR%7D%5E%7BC%5Ctimes+s%7D)。我们其实可以将图5（bottom）最下面每两个圆圈视为一个圆圈，就像图5（middle）一样。此时计算global Attention可以分成两种情况：训练和推理，或者也可以称作Non-Causal和Causal。Causal表示因果，即下一个单词的预测依赖前面的输入，这就对应推理。两种情况的具体计算公式如下：

1. Non-Causal (适用于非自回归任务，比如完形填空、情感分类等):

![\hat{V}_g^{lin}=Q_g^{lin}(\sum_{h=1}^G{K_h^{lin}}^TV_h) \tag{6} ](https://www.zhihu.com/equation?tex=%5Chat%7BV%7D_g%5E%7Blin%7D%3DQ_g%5E%7Blin%7D%28%5Csum_%7Bh%3D1%7D%5EG%7BK_h%5E%7Blin%7D%7D%5ETV_h%29+%5Ctag%7B6%7D+)

训练阶段其实可以不用像公式(6)那样分chunk的去计算，我们其实可以直接用完整的矩阵![Q^{lin},K^{lin}\in\mathbb{R}^{T\times s}](https://www.zhihu.com/equation?tex=Q%5E%7Blin%7D%2CK%5E%7Blin%7D%5Cin%5Cmathbb%7BR%7D%5E%7BT%5Ctimes+s%7D)直接计算得到公式(6)右边的累加项。

我们再看看计算复杂度，![{K_h^{lin}}^TV_h](https://www.zhihu.com/equation?tex=%7BK_h%5E%7Blin%7D%7D%5ETV_h)的计算复杂度为![O(Cse)](https://www.zhihu.com/equation?tex=O%28Cse%29)，累加G个chunk，那么复杂度就是![O(GCse)=O(Tse)=O(Tsd)](https://www.zhihu.com/equation?tex=O%28GCse%29%3DO%28Tse%29%3DO%28Tsd%29)。矩阵Q与KV计算的到矩阵相乘的复杂度为![O(Cse)=O(Csd)](https://www.zhihu.com/equation?tex=O%28Cse%29%3DO%28Csd%29)。所以公式(6)的计算复杂度近似为![O(Tsd)](https://www.zhihu.com/equation?tex=O%28Tsd%29)。

2. Causal (适用于自回归任务，如语言翻译、语言模型、文本生产等)：

![\hat{V}_g^{lin}=Q_g^{lin}(\sum_{h=1}^{g-1}{K_h^{lin}}^TV_h) \tag{7} ](https://www.zhihu.com/equation?tex=%5Chat%7BV%7D_g%5E%7Blin%7D%3DQ_g%5E%7Blin%7D%28%5Csum_%7Bh%3D1%7D%5E%7Bg-1%7D%7BK_h%5E%7Blin%7D%7D%5ETV_h%29+%5Ctag%7B7%7D+)

根据两套Q，K矩阵，我们可以分别求得![\hat{V}_g^{quad},\hat{V}_g^{lin}](https://www.zhihu.com/equation?tex=%5Chat%7BV%7D_g%5E%7Bquad%7D%2C%5Chat%7BV%7D_g%5E%7Blin%7D)，最后我们将二者相加得到混合注意力，最终第![g](https://www.zhihu.com/equation?tex=g)个chunk的输出计算公式如下

![O_g=[U_g\odot(\hat{V}_g^{quad}+\hat{V}_g^{lin})]W_o \tag{8} ](https://www.zhihu.com/equation?tex=O_g%3D%5BU_g%5Codot%28%5Chat%7BV%7D_g%5E%7Bquad%7D%2B%5Chat%7BV%7D_g%5E%7Blin%7D%29%5DW_o+%5Ctag%7B8%7D+)

Mixed Chunk Attention伪代码如下：

![](https://picx.zhimg.com/v2-e30f982099bab6c24598eebe547b47a5_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1408' height='1054'></svg>)

## **5. 论文中的一些讨论**

## **5.1 Chunk是否需要overlap**

前面提到将输入序列划分成多干个chunk，这些chunk彼此之间是没有overlap的。比如说这句话“今天我吃了好多好吃的，有龙虾、鲍鱼、海参和饺子。”，以non-overlap的划分方式将这个句子（总共24个字符）划分成三个chunk，则得到

* [今天我吃了好多好]
* [吃的，有龙虾、鲍]
* [鱼、海参和饺子。]

那么，一个很自然的问题是如果overlap会怎么样呢？结果是否会更好？作者对这个做了测试，实验结果表明overlap的划分chunk的方式的确能够提升模型性能，但是引入了额外的计算成本。与其使用overlap 的chunk划分方式，还不如直接多加几层non-overlapping GAU模块。

## **5.2 局部和全局注意力的Ablation Study**

原论文还做了消融实验，显示相对来说局部注意力比全局注意力更重要，而混合式的效果最好。下面实验中的MC-TFM++是指将Mixed Chunk Attention运用到Transformer++。MC-TFM++和FLASH一样都是线性复杂度，但是用的FFN。可以看到使用GAU的FLASH要明显优于MC-TFM++。

![](https://picx.zhimg.com/v2-d016ae48fb6c350f6a951602d890cba6_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2057' height='587'></svg>)

## **5.3 Chunk大小该如何选择**

* 当C和句子长度一样时，此时等价于FLASH-Quad，即计算复杂度为二次方
* 当C=1时，则等价于Linear Attention，但是在做auto-regressive training的时候不够高效，缺少并行性
* 下图给出了在不同句子长度下，C取不同值「128, 256, 512, 1024」的效果，彼此差距不是很大，最终作者选取了256

![](https://picx.zhimg.com/v2-716f88d672d41f933e38084c93d299bd_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2376' height='728'></svg>)


---

## 高中同学29岁就成了顶尖985的副教授，看看普通的自己，会有什么想法？

`link: https://www.zhihu.com/question/586589709/answer/3083166940 · created: 1687309195`


如果我说本科同学 [@Gaoning](https://www.zhihu.com/people/c325bebfb60bb9a62a33b31f23d36c08) 27岁成了教授，阁下又当如何应对

![](https://pica.zhimg.com/v2-a6cf744309e1d0186f5f1a49045c54ef_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='512' height='512'></svg>)


---

## 你在出差过程中有总结了哪些经验值得借鉴？

`link: https://www.zhihu.com/question/27583640/answer/3052569919 · created: 1685504036`


我目前在香港读博，因此有的时候需要出国参加学术会议。很不幸的是碰上了疫情，只去过新加坡。所以这里给未来可能要来香港或者去新加坡参加学术会议的同学一些有用的出差经验。

**行李攻略**

首先最重要的肯定是准备行李了，行李准备好了，后续才不会忙手忙脚。行李主要可以参考下面几点：

* 证件：护照、签证、港澳通行证。这些玩意都忘记带的话，就泰裤辣！！！
* 衣物&生活用品：香港和新加坡都慢热的，所以有必要带上防风防晒薄衫、防晒霜之类的东东。不过，如果你是12月或者1月左右来香港，这个时候其实还是有可能会冷的，所以有必要带一件长袖外套和长裤子，免得冻感冒。再加上众所周知，香港和新加坡的电是”不要钱”的，所以室内一般也都是比较冷的，所以长袖真的很有必要。另外也可以带上一次性的拖鞋、毛巾、袜子、内裤，行李箱可以越用越空、回来的时候也更加轻松不是吗~~ 0~0
* 身体好：U型枕、眼罩、耳塞（也可以用降噪耳机代替）、零食、常用药（例如止泻等肠胃药，出去难免会吃点好吃的，万一吃坏肚子还能拯救一下）
* 工作好：平板、笔记本、充电宝、转接口。如果你东西多也可以买一个像我这样的排插，既有USB插口，又支持不同的插口，美滋滋

![](https://picx.zhimg.com/50/v2-59b8b0182b657294ad027846757b4b94_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='383' height='672'></svg>)

**出行攻略**

香港：在香港出行有八达通就行了，这个可以在淘宝或者在7-11商店购买。另外出行一般坐地铁就完事了，香港的地铁虽然贵。但是真的很方便，不少换乘站只需要下车走到对面就可以了，例如旺角站、太子站。对了，现在香港地铁已经支持支付宝和微信扫码进展了。微信搜索【乘车码】小程序，城市切换至香港就ok了。除了地铁，还可以选择做大巴和小巴。大巴可以下载 APP 1933-KMB软件，他会提示你大巴还有多久到站。小巴的话，如果你是社恐人士，能不坐就不坐了吧hhh。打车的话，香港用Uber会比较多一点

新加坡：新加坡的地铁也提供方便的，在7-11购买Ez-link交通卡就可以了，这个卡坐公交或者地铁都是可以的。打车的话，新加坡常用的打车软件挺多的，实测Go-Jek比较便宜，Grab和ComfortDelgro也挺好用的。这边的打车软件不用登记身份信息，只需要绑定信用卡就完事了，当然你也可以选择现金或者支付宝付钱。司机很多都是华人，所以没什么沟通问题。

**电话卡攻略**

现在手机上一般都有那种全球流量包可以购买，但是如果你对流量需求挺大的话建议购买一张临时电话卡，这样会更划算。

在香港，你可以在7-11购买一张临时电话卡。当然也可以找一下附近的屈臣氏或者百佳超市，它们会有那种月租36港币左右的电话卡，这不需要实名登记，流量够你出差用的了。

在新加坡，你同样可以在7-11购买一张临时电话卡，我记得价格是在15新币一个余月，流量够够的，我记得第一个星期给你有100G。

**学术会议攻略**

现在万事具备，只差开会了。学术会议一般有三种场景：

* 聆听大佬们现场激情的演讲
* 聆听未能亲自参会的大佬们的录播视频
* 和其他学者面对面交流

会议期间一般会有很多分会场，所以去参会之前一定要提前做好计划，找出感兴趣的环节，标记好时间安排，避免不同场次的时间冲突。

计划都做好了，接下来就是要如何提高会议的效率了。因为现如今的会议大多都是用英文交流的，加上有的时候现场环境嘈杂或者走神，很可能就会错过一些重要内容。所以一种办法是用录音笔或者手机录音，会议结束后再去从录音里回顾会议内容。但是，很显然这种办法很累，因为一般开完会后是没有精力再去整理的。这里推荐一个神器，iFLYBUDS Nano+耳机。真的，这玩意儿绝了，除了颜值不错，它还把蓝牙耳机玩出花了，商务人士或者学生党真的可以入手一个。

<https://xg.zhihu.com/plugin/4889b3ba3f5cabaf2be5313ab08e9f2f?BIZ=ECOMMERCE>![](https://picx.zhimg.com/v2-85e20bc8a7ecb2a47c58438d59fd38dd_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1379' height='776'></svg>)

iFLYBUDS Nano+是一个具有主动降噪和录音功能的耳机。一听是不是觉得，不就是降噪加录音嘛，我用手机不也一样可以录音。是的！我第一次看到这耳机的时候我也是这么想的。但是，它不仅仅能做到录音转写还做了很多后续场景的优化。

首先这耳机搭配充电盒有40小时的长续航，单独使用也有12小时，所以不用担心录音录到一半没电了。左右耳机可以分别保存2小时的录音内容，也就是总共可以录4个小时，这个时长完全足够了。启动录音的方式有两种：

* 一种方式是用IFLYBUDS app（长这个样子）

![](https://pic1.zhimg.com/50/v2-626c5cf31be06c0266131449ee588e04_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='109' height='126'></svg>)

应用用商店可以直接搜索下载。手机端提供了提供三种场景的录音：现场录音、网络电话录音（比如微信、zoom、腾讯会议等）、音视频录音（例如看B站视频或者听广播）。

![](https://pica.zhimg.com/50/v2-674aa9791f8ae41f7a75c0cd9bc09482_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='261' height='580'></svg>)

手机APP端提供三种录音方式

* 另一种方式是“**闪录**”，即只需要长按耳机即可开启录音功能。闪录的重点在“闪”，即不需要复杂的操作，不需要打开手机，你只需要随便选择一个耳机长按就可以启动录音功能。每次只需要选择一个耳机录音就可以了，两个耳机都自带存储空间。每次录完之后，可以把信息同步到手机上，然后就可以把耳机上的录音删除了，避免存储空间占满的情况。

![](https://picx.zhimg.com/50/v2-cd557b29fe58f9ac16550248f1169def_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='322' height='550'></svg>)

耳机端长按后开启闪录

闪录功能非常适合紧急来电的情况，比如导师或者老板突然要安排个事情，比如交代一下论文有啥问题，项目有啥新需求等等，直接长按耳机即可开启录音，再也不用担心小小的脑袋装不下大大的修改意见了。

语音上传到手机后，等个一两分钟就能自动将语音信息转换成文字，目前支持9种语言：普通话（中英混合）、英语、日语、韩语、俄语、法语、西班牙语、德语、意大利语。12种方言： 河南话、河北话、四川话、云南话、贵州话、重庆话、天津话、东北话、山东话、甘肃话、太原话、粤语。所以在大多数地区出差，会议记录应该是不成问题了。不仅如此，讯飞会议耳机还支持通用、法律、教育、金融、医疗、科技、政府、企业、电商、生活等10大行业术语识别转写，转写前选择合适的领域可以提高转写的准确度，识别出一些专业术语。

下面是我通过将闪录功能录下的会议内容同步到手机APP后的结果，可以看到不仅能转化成文字，还能自动识别说话人，这个简直不要太方便，我们可以快速定位所关注的人说的内容。我用过手机自带的录音软件，不仅识别率低，而且最后给一坨密密麻麻的文字，反而增加了工作量。

![](https://picx.zhimg.com/v2-91bba5aa18ca05c34aa80fe93d9099ff_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='425' height='945'></svg>)

选择【区分说话人】

![](https://pic1.zhimg.com/50/v2-4d74b33ba17713657c2adb21bfe735b6_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='417' height='926'></svg>)

录音转化为文本后，会自动按照说话人进行文本区分

对了，讯飞会议耳机还支持中英混合的语音转换，我实测了一下一个非常international和drama的视频，转换效果非常good，and非常令人amazing

[![](https://picx.zhimg.com/v2-6175b05e8ace3b5df169d08a07163038.jpg?source=382ee89a)比如说铆钉亮片或者是绑带bandaghttps://www.zhihu.com/video/1643370218947768320](https://link.zhihu.com/?target=https%3A//www.zhihu.com/video/1643370218947768320)

另外录音内容还支持智能播放，比如它会根据算法自动把一些空白或者杂声给去掉，这可以极大节省时间。

![](https://pica.zhimg.com/v2-f3878e3d623016670f2384fb30300274_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='540' height='1199'></svg>)

只是简单把录音转成文字肯定是不够的。iFLYBUDS 手机app里提供了生成式VIAIM AI会议助理，它能够基于人工智能（AI）技术自动对录音信息做处理。比如，如果你嫌文字内容太多，讯飞会议耳机甚至还可以贴心提供了【摘要】功能，它能自动将文字内容里提取出重要信息，转换成摘要。像一些会议开头的“喂，听得到吗”，“诶，听得到”，“hello, can you hear me”这些戏份一键删除。不仅如此，VIAIM AI会议助理还能够自动生成待办事项，一切安排的明明白白，属实是被拿捏住了。讯飞会议耳机它真的，我哭死。

![](https://picx.zhimg.com/50/v2-9f1c6ee671b10c2d20e472900a196694_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='250' height='196'></svg>)![](https://pic1.zhimg.com/50/v2-e0178db5b047f85fea7949e21cc283a2_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='163' height='156'></svg>)

还有还有啊，先留点眼泪别哭死，关键的是语音转文字功能永久免费！！！是的，永久免费！！！来，1,2,3，给我哭！！！

![](https://picx.zhimg.com/50/v2-433510e350a6bfb640988a49fe86bf78_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='173' height='138'></svg>)![](https://pic1.zhimg.com/50/v2-8a5a9557b23536e296aa478d139522a5_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='222' height='227'></svg>)![](https://pic1.zhimg.com/50/v2-e8ee834d76657f1346def6a2bc0982ce_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='229' height='220'></svg>)

我还发现了这个耳机一个好用的地方，就是可以用来学习。真的，我说的是真的学习。他可以用来啃生肉，它能够实时地生成字幕。如果想通过广播学英语就不用担心没有文本材料了。

[![](https://picx.zhimg.com/v2-3914422baaf3278285ba3e62f3aae575.jpeg)https://www.zhihu.com/video/1643370752639467521](https://link.zhihu.com/?target=https%3A//www.zhihu.com/video/1643370752639467521)

最后再看看使用动画演示，把上面提到的功能都直观展现出来了

[![](https://picx.zhimg.com/v2-0cbc5ed1563253ca0b45ff82f7f6e59e.jpg?source=382ee89a)iFLYBUDS Nano+耳机https://www.zhihu.com/video/1647161621918216192](https://link.zhihu.com/?target=https%3A//www.zhihu.com/video/1647161621918216192)<https://xg.zhihu.com/plugin/4889b3ba3f5cabaf2be5313ab08e9f2f?BIZ=ECOMMERCE>


---

## 科技部启动「人工智能驱动的科学研究」专项部署工作，释放了哪些信号？

`link: https://www.zhihu.com/question/592157178/answer/2956246891 · created: 1679920446`


科技部牵头的这个人工智能发展规划意义深刻，未来我国必定会有大量人力物力投入到人工智能发展中去。

规划特别强调了AI For Science (AI4Science)，这个其实学术界很早就开始有研究了，比较著名的就是Alphafold,它能够用AI技术自动预测蛋白质的三维结构，即蛋白质中每个氨基酸在空间中的具体位置。ChatGPT等大模型的涌现已经让很多low-hanging fruit无法采摘了，科研民工只能朝着更高级别的任务去卷，AI For Science将成为下一个研究热潮，这也是喜闻乐见的，毕竟这些做出来是真的有帮助的。 这里有个AI4Science的学习网站：[https://ai4science-amsterdam.github.io/](https://link.zhihu.com/?target=https%3A//ai4science-amsterdam.github.io/)

![](https://pic1.zhimg.com/v2-03888e06a709d136c2389628487e89d8_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1024' height='768'></svg>)

ChatGPT等一众大模型已经成为人工智能领域的重要研究成果之一，而科技部启动“人工智能驱动的科学研究”专项部署工作，也意味着大模型将有可能成为新的基础设施，这将开启一种全新的编程范式。

什么意思呢？我的猜想是，在将来，对于大多数用户而言，编程语言也许不再是Python、C++等传统编程语言，而是我们平时说出来的话，如何有效地与机器进行沟通将成为一门新的研究课题，甚至会单独开设一门课程也不一定哈哈 再夸张一点，也许大模型接触的用户多了，可能也会出现“心理问题”，到时候说不定还需要转为大模型服务的心理医生干预

最后，想谈谈AI对各行各业发展的影响。我认为AI大模型将会大幅降低许多行业门槛，推动普罗大众参与现在看起来成本很大的领域。就以最近Epic发布的虚幻引擎5为例，在AI辅助下仅使用iphone便可完成录制视频用于后期的动作捕捉处理，不再需要那些昂贵的动捕设备。技术成熟后，更多人可以参与到这个行业中去，实现自己的创意和想法。推广到其他行业亦是如此。与其担心失业，不如想想如何快速使用“新世界”。

不过，以上种种畅想都需要极大地投入才能变成现实，这个规划虽迟但到，一起期待吧


---

## OceanBase开发者大会，CTO杨传辉表示「单机分布式一体化是数据库的未来」，如何看待此观点？

`link: https://www.zhihu.com/question/591814962/answer/2954600141 · created: 1679830577`


这次大会提到了很多对于开发者来说很现实的问题。

比如开发者最担心的兼容性，MySQL 5.7今年10月底生命周期结束，迁移到你这个数据库是不是真的能解决兼容性问题，要不要额外做很多麻烦看起不必要的调整。

比如来自PostgreSQL中文社区的张文升提到一个问题，当他们把一个分布式系统当做一个单机系统去用，部署到一个机器上面去后，它的性能会有很大幅度的降低。这是一个很现实的问题。OceanBase 单机分布式一体化，就可以解决这个单机性能问题，甚至在同等硬件在很多场景下，可以做比传统的NewSQL性能更好。

同样这个问题OceanBase CTO 杨传辉也分享了很多NewSQL的案例。NewSQL是一种新兴的数据库技术，它是传统关系型数据库和分布式NoSQL数据库之间的一种融合。NewSQL旨在克服传统关系型数据库的扩展性问题，同时也避免了分布式NoSQL数据库的一些缺点，如数据一致性、可靠性和安全性等问题。他们在实际应用中发现NewSQL，单机性能就会掉到原来的1/5甚至1/10，这是不可接受的。在我看来，这也是为什么这么多年来，NewSQL只是被大家记住NewSQL的名字，但没有办法成为数据库主流。

这种情况在现在的很多企业中是一个刚需。

但是随着业务量持续增长，原有的单机数据库会无法满足需求，这时企业会面临着以下问题：一是单机数据库的性能瓶颈，无法承载大量的并发访问；二是数据存储容量有限，无法满足海量据存储的需求；三是数据库的高可用性问题，如果出现故障将对业务产生巨大的影响。

为了解决上述问题，企业将不得不从单机数据库转向使用分布式数据库。

然而，从单机数据库转变为分布式数据库是一项复杂的任务，上面提到的问题也是我们这些开发者最为重视的。

例如:

如何在数据迁移和同步过程中，我们如何得确保数据不会丢失和损坏。

单机数据库与分布式数据库的架构设计不同，因此在转变过程中需要重新设计数据库的架构。需要考虑到数据分片、数据复制、负载均衡等因素，以确保系统的高可用性和性能。

还有个问题是原数据库代码改造和优化的难度较大，工作量也大。

一个实际的例子，文章开头里提到的杨传辉提到从分布式到单机的性能损耗有一个主要来源是因为分布式要做到高可用，所以有强同步的容灾开销。早期支付宝使用分布式数据库，在开启强同步时，性能会降低35%。

为了解决这一问题，一种可行的方案是异步log模式，能将强同步的性能损失控制在8%以内。另外为了保持单机数据库的性能，我们还需要避免一些分布式的IO开销。

可以看得出来无论是从单机到分布式，是有挑战性的。这些技术难题包括分片数据、实现负载均衡、保证数据一致性、保证数据可靠性，以及处理数据合并和同步等。

这些问题需要特别的技术手段和算法来解决，并需要大量的精力和时间进行研究和实现。

总的来说，单机分布式一体化是实现数据库发展的趋势，它专注于从单机到分布式的扩展性，并为开发人员提供更好的数据处理解决方案。

开发人员可以开始使用单机数据库，然后在需要时平滑地扩展到分布式数据库，要做到整个过程中对应用绝对的无感，并满足更高的性能和可靠性要求。此外，单机分布式一体数据库可以极大地降低部署的难度和开发者的工作量，通过配置来指定不同节点的角色和任务，使得部署过程更加简单和快捷。

为了实现单机分布式一体化，除了技术方面的改进外，技术文档和API架构设置也需要相应地进行改进和完善。技术文档应该详细介绍数据库的功能和使用方法，业内很多的文档，看似字数不少，但就是没有说清楚细节，开发者对照文档就是没法用的起来，走一步卡一步。API架构也应该易于使用和理解，以便开发者更好地理解和应用单机分布式一体化。此外，安全性和可靠性也是单机分布式一体数据库需要关注的重要方面。为了保证数据在传输和存储过程中的安全性和可靠性，可以采取多种措施，例如加密数据、备份数据等。总之，实现单机分布式一体化需要技术手段、算法和时间的投入，但是，它对于数据库的发展和数据处理的优化具有重要的意义，我觉得这不但是一个历史性的技术进步，而且是分布式数据库对开发者友好的一个巨大进步。


---

## 百度正式推出「文心一言」，然而港股股价已暴跌近 10%，客观来说其能力与 ChatGPT 相较如何？

`link: https://www.zhihu.com/question/589941496/answer/2939373954 · created: 1678962772`


李彦宏在台上展介绍文心一言的样子像极了我们写一篇paper来展示自己的研究成果，例如

1. 都有deadline，时间到了，不管论文写的什么屎样都得交了
2. Motivation是因为国内用户有这方面的需求，且对应产品空缺 <-> 这个方法在我们关注的领域暂时没人去做
3. 都需要竭尽全力挖掘一些可能并不是亮点的“亮点”
4. 大谈特谈商业模式 <-> 用future impact来增加论文卖点
5. 用户看低股票 <-> 审稿人点击reject
6. 目前只支持中文语种 <-> 目前只在一个数据集上做了验证测试
7. 没有现场演示且还需要公测一段时间 <-> 代码会在论文接收后开源

但是问题的关键在于他展示的不是论文，更像是research proposal

尬，太尬了，任重道远

![](https://pic1.zhimg.com/v2-bb9ac994471e4a453c9adf511a4d66b4_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='960' height='960'></svg>)


---

## NAS神经网络架构搜索通常怎么评判效果？常用什么benchmark？

`link: https://www.zhihu.com/question/529736951/answer/2934761498 · created: 1678713482`


现有NAS Benchmark 数据集汇总[1] , 如下表示。

NAS Benchmark dataset提供了查询式的数据库，每个模型都有对应的性能指标和结构信息，无需训练模型权重。可以帮助更快探索不同搜索算法的效率。

家里或者组里没有矿的同学可以基于这些数据集做一些研究工作。

![](https://pica.zhimg.com/v2-b85c9c8e2bb710b27ecc8d1318d366cf_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='888' height='1152'></svg>)


---

## windows系统如何通过ssh远程连接linux？

`link: https://www.zhihu.com/question/51669913/answer/2900095351 · created: 1676738604`


## **1. 背景**

我学校有一台Windows电脑 (`x@a.b.c.d`)，里面安装了一个Ubuntu虚拟机（用户名为`y`），虚拟机里连着VPN。并且虚拟机的22端口映射到了主机的22端口。通过这个VPN我可以访问另一个远程的服务器（`z@e.f.g.h`）用于炼丹。

我现在在家，无法直接访问远程服务器，只能把学校电脑作为跳板才可以。下面是示意图

![](https://pic1.zhimg.com/v2-dc2037d66275dc67e867f98776591ad7_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1758' height='904'></svg>)

image

## **2. 在Windows上安装OpenSSH并配置服务器**

## **2.1 安装SSH Server**

假如你在机器A上安装SSH，一般情况下只有客户端，也就是说你只能去ssh到其它远端机器。但是你如果想在机器B上ssh到机器A是不行的，因为机器A并没有SSH服务器（Server）。SSH Server安装方式如下

![](https://pic1.zhimg.com/v2-0620cbe2077c85073a98c960569d7178_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2026' height='1384'></svg>)

image

## **2.2 SSH Server配置**

1. 打开SSH Server

首先按下快捷键 `Win + R`，然后输入`services.msc`，之后会进入到windows的服务管理界面。往下滑你可以找到OpenSSH SSH Server选项，双击它后点击`启动`，并将启动类型选项改为`自动`。

![](https://picx.zhimg.com/v2-9ccc5b75448634084d8dc11ad9d0921d_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1278' height='612'></svg>)

image

1. 防火墙增加入站规则，添加22端口

![](https://pica.zhimg.com/v2-0ff22a96072c9de83dc80bc44247e239_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1910' height='696'></svg>)

image

你可以通过如下命令查看22端口是否成功监听

```
netstat -an | findstr :22
```

![](https://picx.zhimg.com/v2-7ade80fac238ded854dab8459d198d42_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='560' height='55'></svg>)

image

1. 修改`sshd_config`文件 `sshd_config`路径一般在`C:\ProgramData\ssh`文件夹里，其中`ProgramData`是隐藏文件夹，你需要在文件管理器里设置显示隐藏文件夹后就能看到了。之后用管理员权限打开`sshd_config`文件，你需要修改两个地方：

* 一个是把原本是注释状态的端口取消，即把#删掉即可

```
Port 22
```

* 另一个则是把最后两行注释掉，如下。这个耽误了我最长时间，之间一直无法成功ssh，直到把这个做了之后就可以了。

```
#Match Group administrators
#       AuthorizedKeysFile __PROGRAMDATA__/ssh/administrators_authorized_keys
```

如果你修改了上面提到的路径的`sshd_config`还是没用，你也可以试着把`C:\Windows\System32\OpenSSH`路径下的`sshd_config_default`仿照上面的方法修改一下。

## **开始SSH**

假设你远程Windows的用户名是x,IP是a.b.c.d；虚拟机的用户名是y，并且你已经将虚拟机的22端口映射到了Windows的22端口，那么你可以直接通过如下方式就可以ssh到虚拟机了

```
ssh -J x@a.b.c.d,y@127.0.0.1 z@e.f.g.h
```

## **参考**

* [https://www.cnblogs.com/sparkdev/p/10166061.html](https://link.zhihu.com/?target=https%3A//www.cnblogs.com/sparkdev/p/10166061.html)


---

## ChatGpt能成为恋爱大师吗？

`link: https://www.zhihu.com/question/583833801/answer/2896493131 · created: 1676543374`


人和机器人之间的情感是一个热门的主题，有很多影视作品和书籍涉及这个主题。以下是一些相关的例子：

1. 电影《她》(Her, 2013)：讲述了一个男人和一款操作系统之间的情感故事，探讨了人和机器之间的关系和可能性。
2. 电影《机械姬》(Ex Machina, 2014)：描绘了一名程序员与他的人工智能机器人之间的关系和情感互动，同时也探讨了人工智能的伦理和道德问题。
3. 小说《机器人系列》(The Robot Series)：艾萨克·阿西莫夫创作的系列小说，探讨了机器人的智能和情感问题。
4. 电影《银翼杀手》(Blade Runner, 1982)：讲述了一个杀手与一群人工智能机器人之间的故事，探讨了人工智能的意识和情感问题。
5. 电影《A.I.人工智能》(A.I. Artificial Intelligence, 2001)：讲述了一个机器儿童与人类之间的故事，探讨了人工智能的情感和意识问题。

这些作品都探讨了人类和机器之间的情感问题，但是它们的情节都是虚构的，并不能直接应用于现实。目前的ChatGPT作为一个自然语言处理模型，虽然可以生成人类类似的自然语言输出，但是它没有情感或感情，无法理解人类的情感和情感体验。因此，ChatGPT不能成为真正的恋人。

但是，至于恋爱大师，ChatGPT可以提供一些恋爱方面的话题或对话建议。下面是一些测试例子：

![](https://pica.zhimg.com/v2-92e45e416ea63f37c28d580e37734e03_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1528' height='1066'></svg>)

但是ChatGPT只能基于输入数据和预训练模型的模式匹配和生成，不具备深刻的情感分析和情感支持能力。从上面的例子我们也可以看到，他更多的地知识给了一个机械概括性的建议，目前而言它还类专业心理医生和恋爱专家的角色。

但是，如果我想如果模型小到可以部署到手机端的话，那么用户可以日积月累地和它交流，这样每个用户都可以有一个定制化的ChatGPT。另一种思路，也许就是用联邦学习的思路来训练一个特定的ChatGPT。联邦学习算法可以在不将数据集从客户端传输到服务器的情况下，让多个客户端在本地训练模型，然后将本地模型的权重汇总到全局模型中，从而使得全局模型的性能可以逐步提升。

需要注意的是，为每个用户训练一个定制的ChatGPT模型的实现难度很大，例如每个用户需要拥有足够的数据，且数据质量要高，否则训练出来的模型性能可能不尽如人意。另外需要花费大量的时间和计算资源来训练模型，尤其是当用户数量很多时，可能需要分批次或增加并行计算来加速模型训练和聚合。最重要的问题是需要解决用户数据隐私和数据泄露，采用一定的数据加密和安全措施来保障用户数据的安全和隐私。


---

## ChatGPT 结合工业机器人，将锁死发展中国家的崛起？

`link: https://www.zhihu.com/question/583128160/answer/2886163463 · created: 1676008151`


近年来，人工智能（AI）的应用在制造业中出现了激增。最有前途的基于人工智能的技术之一是ChatGPT，它是一种自然语言处理（NLP）技术。这项技术有可能使工业机器人能够理解人类的命令，并以更自然的方式与人互动。因此，它可能对发展中国家的增长和社会的未来产生重大影响。本文将讨论ChatGPT与工业机器人相结合，对发展中国家的崛起是阻碍还是帮助。

### 潜在的好处

毫无疑问，ChatGPT和工业机器人的潜在好处对发展中国家有很大好处。首先，这些技术可以帮助降低劳动力成本，因为机器人需要最少的人力投入和监督。此外，ChatGPT可以使工业机器人理解来自人类的复杂指令，使其更加高效。这可以帮助发展中国家的工厂降低生产成本，提高产量。此外，它可以帮助提高这些国家的整体生产力，从而促进经济增长。

第二，ChatGPT和工业机器人可以帮助提高发展中国家制造的产品质量。这些技术将使工业机器人能够以比人类更高的精度和准确度来生产物品，从而获得更高质量的产品。这可以提高发展中国家在全球市场上的声誉，从而带来更高的利润和更好的经济增长。此外，它可以导致在这些国家的更多投资，帮助他们进一步发展和成长。

### 潜在的弊端

尽管有潜在的好处，在发展中国家使用ChatGPT和工业机器人也有一些潜在的弊端。

首先，这些技术有可能取代人类劳动，导致一些国家的工作岗位流失和失业率上升。这可能导致更高的贫困率和更大的贫富不均。

第二，ChatGPT和工业机器人的使用也可能导致发展中国家的工作质量下降。由于工业机器人能够完成大部分工作，因此需要更少的人从事体力劳动或操作机器。这可能导致工人的生活质量下降，因为他们将被迫从事收入较低、福利较少的工作。

最后，这些技术的引进也可能导致那些就业竞争力低的人的工资下降，因为雇主不再需要支付那么多钱。

### 结论

总之，ChatGPT 结合工业机器人对发展中国家的影响是复杂的，不能简单地认为它会锁死发展中国家的崛起。ChatGPT和工业机器人可以为发展中国家带来好处，因为它们可以帮助降低劳动力成本，提高产量，并改善产品的质量。然而，也有一些潜在的缺点，如就业机会的丧失和工作质量的下降，以及那些就业竞争力低的人的工资可能下降。因此，发展中国家在实施ChatGPT和工业机器人之前，必须仔细考虑其潜在的好处和弊端。如果操作得当，这些技术可以成为发展中国家发展的一大助力，帮助他们实现金融稳定和繁荣。

为了使ChatGPT和工业机器人在发展中国家的潜在利益最大化，必须考虑几个关键因素。重要的是要确保技术的使用不会对现有工作产生负面影响，并确保为工人提供必要的培训和支持，以适应任何变化。此外，重要的是要评估对工资的潜在影响，并确保任何工资的减少都能通过额外的福利或其他形式的补偿得到补偿。最后，重要的是要考虑对环境的潜在影响，并确保任何负面影响被最小化或避免。

同样重要的是，要确保有足够的安全法规，以保护工人免受与使用基于人工智能的技术和工业机器人有关的潜在危险。此外，必须评估这些技术的潜在经济和社会影响，如对收入不平等和工人的生活质量的影响。最后，必须考虑这些技术可能导致某些行业的迁移，如与体力劳动相关的行业。


---

## 谷歌 AI 犯错致市值一夜蒸发 1056 亿美元，谷歌 Bard 是否暴露了类似的人工智能系统的缺陷？

`link: https://www.zhihu.com/question/582930903/answer/2884842350 · created: 1675936164`


![](https://picx.zhimg.com/v2-a7cb052c4cb72eac8ee78c86c56d4b44_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='794' height='742'></svg>)

1. Bard出错的原因可能是什么？

首先，值得注意的是，AI 并不是十全十美的，它仍然有缺陷。在这种情况下，Bard 可能出错的原因有很多，例如：

* 数据偏差：如果训练数据不全面、不具有代表性，AI 系统很容易出错。
* 模型复杂度：如果模型过于复杂，很容易过拟合，也就是说，在训练数据上表现良好，但在新数据上表现不佳。
* 技术落后：随着 AI 技术的不断发展，某些方法在短期内就会过时，导致 AI 系统出错。

2. 如何避免 AI 出错，有哪些可行的措施？

AI 出错的根源可以归结为数据偏差、模型偏差和欠拟合/过拟合等。为了避免 AI 出错，业界通常推荐一些可行的措施，包括：

* 数据多样性：在训练 AI 模型时，应该尽量保证数据多样性，以防模型陷入单一类型数据的偏见。
* 数据验证：在训练和测试 AI 模型时，应该对数据进行严格的验证，以确保数据的质量和准确性。
* 模型监测：在 AI 模型部署后，应该实施监测，以确保模型的表现是否符合预期。
* 模型评估：在 AI 模型部署前，应该进行全面的评估，以确保模型的质量和可靠性。

当然，这些措施并不是万无一失的，但如果正确实施，可以大大减少 AI 出错的风险。

3. 如何看待 AI 出错？

AI 出错时，我们应该保持冷静和客观，从多个角度对 AI 出错进行分析。

平衡风险与机会：首先，我们要看待 AI 出错是一个普遍存在的问题，人工智能是一项前沿技术，其发展和应用还处于初期阶段。在这个过程中，AI出错是难免的，但也带来了巨大的机会。因此，对于AI出错，我们需要平衡风险和机会，合理评估AI的风险，在继续推广和改进AI的同时避免不必要的风险。

追求完善：AI出错是一种技术漏洞，也是技术提高的机会。对于AI出错，我们需要对其进行详细的分析，揭示其中的问题，从而不断完善和改进AI。

加强监管：随着AI在社会的广泛应用，其出错带来的影响越来越大。因此，我们需要加强对AI的监管，确保AI的安全性和合法性。

总体来说，对于AI出错，我们需要积极看待，并从多个方面对其进行评估和探讨，从而推动AI的更好发展。

---

*以上回答由ChatGPT提供。*


---

## 2023年 AAAI 计算机视觉领域有哪些值得关注的论文？

`link: https://www.zhihu.com/question/571725734/answer/2797186492 · created: 1670758601`


> 打个广告：最近我们实验室的一篇文章“**[NAS-LID: Efficient Neural Architecture Search with Local Intrinsic Dimension](https://link.zhihu.com/?target=https%3A//arxiv.org/abs/2211.12759)**”被AAAI2023主会录取，该文提出了一种基于局部本征维度(local intrinsic dimension, LID)的神经架构搜索算法，提高对候选模型的性能排序相关性，从而帮助找到优秀的模型结构。

## 1. 摘要

One-NAS通过训练一个超网来估计每个可能的子网的性能，从而显着提高搜索效率。然而，子网之间特征的不一致对优化产生了严重的干扰，导致子网的性能排名相关性差。随后的一些工作尝试通过特定准则（例如梯度匹配）分解超网权重以减少干扰；然而，这些方法的问题在于计算成本高和空间可分性低。在这项工作中，我们提出了一种轻量级且有效的基于局部本征维度（LID）的方法 ，叫做NAS-LID。NAS-LID 通过对子网逐层计算低成本 的LID 特征来评估架构的几何特性。我们发现LID 表征的相似性与梯度相比具有更好的可分离性，从而有效地降低了子网之间的干扰。在 NASBench-201 上进行的大量实验表明，NAS-LID 以更高的效率实现了卓越的性能。具体来说，与梯度驱动方法相比，NAS-LID 在 NASBench-201 上搜索时可以节省高达 86% 的 GPU 内存开销。我们在 ProxylessNAS 和 OFA 空间上也验证了NAS-LID的有效性，实验结果显示NAS-LID搜索到的模型在ImageNet数据集上取得了与之前工作相似甚至更好的结果。

## 2. 背景和研究动机

神经架构搜索（Neural Architecture Search, NAS）旨在自动搜索模型结构，该方法已经被应用到多种任务，并且实验表明其搜索到的模型已经可以与人工设计的模型相媲美，甚至表现更好。早期的普通NAS算法（也叫Vanilla NAS）是每次从搜索空间中采样一个模型并将其训练至收敛，然后在验证集上得到验证性能（如validation accuracy），之后不断重复采样新的模型，最后挑选出验证性能最高的作为最终模型结构。所以NAS也可以理解成是对模型性能进行排序，排序的准确性决定了能否找到最优模型结构。  
不过很显然，Vanilla NAS方法会耗费大量计算资源和时间，因此后续有工作提出权重共享策略来提高效率，这类方法叫One-shot NAS。下图给出了Vanilla NAS和One-shot NAS的区别，每一个圆圈代表一个模型结构。

![](https://pic1.zhimg.com/v2-2478b4d9099a20e2cdc2dc7f599185b4_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='865' height='354'></svg>)

图片来源于 AutoML: A Survey of State-of-the-art [1].

可以看到One-shot NAS的候选模型之间会有部分重叠区域，这就表示权重共享。换句话说，整个搜索空间可以看成是一个巨大的模型结构（叫超网，Supernet），而每个候选模型则是这个超网的子网（subnet）。One-shot NAS中模型之间共享权重，所以共享部分的权重可以直接继承过来，而不用每次重复训练了。  
虽然权重共享让One-shot NAS有效提高了搜索效率，但是它也是问题所在。为方便理解，我们以上图（右）中的最小同心圆为例进行说明。可以看到它是很多模型共享权重的部分，假设它的权重更新了，有可能它会让一部分模型性能得到提升，但也有可能会使得另一部分模型性能降低。换句话说，权重共享方式下每一次更新对于不同模型会带来不同的影响，而这最终会导致我们对模型性能产生误判，导致没法找到真正好的模型。而Vanilla NAS因为是独立地训练每个模型所以不存在这个问题。

已经有不少工作尝试去解决One-shot NAS评估模型性能不准确的问题，其中一种思路就是把互相产生负面干扰的模型划分开来。最早的工作是Few-shot NAS [2]，该论文作者将一个Supernet以穷尽地方式随机划分成指定个数的sub-Supernet,这样一来其实是减少了每个sub-Supernet中包含的模型数量，从而间接地减少模型之间的干扰。简单理解Few-shot NAS就是介于Vanilla NAS和One-shot NAS的方法，前者每一个模型都视为一个sub-Supernet，而后者就只有一个Supernet。Few-shot NAS有一个比较明显的缺点就是划分方式存在随机性，效率不高。所以后面一个发表在ICLR2022的工作，GM-NAS [3]提出根据模型梯度相似性来划分Supernet，其实验结果表明这种划分方式的确能进一步提高NAS对模型性能的排序相关性，一般用Kendall tau或Spearman系数作为评价指标，和两个指标范围都介于-1到1。-1表示相关性完全相反，即实际上最好的模型被预测成最差的；1则表示相关性最强，即能准确预测每一个模型的相对好坏。

我们对GM-NAS做进一步分析发现它仍然有一些地方可以改进。首先，GM-NAS因为需要额外计算梯度，所以整个过程对GPU内存开销有较高要求。另外，GM-NAS是根据梯度cosine相似度对模型进行划分的，而我们知道深度神经网络的梯度是处于非常高维的空间。而高维空间有维数灾难问题，计算cosine距离并不能真实反映相似度。我们的实验也证实模型之间梯度的cosine相似度都很接近，因此很难基于梯度对模型进行划分。

## 3. 方法

为了解决GM-NAS的两个缺点，我们使用了一个新的指标，即局部本征维度（LID）。LID衡量的是能够用于表征数据的最小维度，比如很多工作用它来衡量数据集的难易程度等。这里，我们尝试用LID来对模型结构进行表征。我们首先对NAS-Bench201搜索空间随机采样并独立训练了多个模型，之后我们根据如下公式计算了每个模型逐层特征的LID值。

![](https://picx.zhimg.com/v2-aa489e40c741545e32cb37df333b78cc_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='663' height='237'></svg>)

最后我们将采样的模型的逐层LID可视化如下图，图中每个曲线代表一个模型，横坐标表示模型的相对深度，纵坐标表示对应层数的LID值。

![](https://pic1.zhimg.com/v2-d2a54db8636de8186ea3eff494fb84a3_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='909' height='771'></svg>)

图中红色曲线为准确度高的模型，可以看到它们的LID都呈现拱形。我们认为红色曲线的LID先增趋势表示模型首先浅层将输入数据逐渐映射到更高维的流形空间，这一过程模型在学习数据的特征，而后面LID值不断下降表示模型此时在剪枝那些冗余的信息；而蓝色曲线代表准确率偏低的模型，它们的LID呈现递减趋势，这可能表示模型在浅层并未能有效学习到数据的特征。基于上面的分析，我们认为模型逐层的LID值分布能够表征模型结构的几何特性，而该特性在一定程度上决定了模型的training dynamics。换句话说，逐层LID值分布相似的模型在训练过程中可能有相似的偏好。作为一个概念验证性的工作，我们提出了NAS-LID方法，即基于逐层LID值分布相似性来对模型进行划分。具体来说，NAS-LID将每个模型表征成一组LID值，其长度即为模型的深度。很显然，相比于基于梯度的方法，我们将每个模型的表征维度大大降低了，这有效缓解了维数灾难问题。

下图显示了基于LID和梯度对NAS-Bench201空间可分性得分对比。每条边上有5个候选操作，选择不同额操作会得到不同的模型结构。每条边上的分数表示空间可分性得分，分数越低表示不同模型之间相似度方差越小，即很难将它们区分开来。可以看到NAS-LID能更有效地区分不同模型，而GM-NAS反之。

![](https://pica.zhimg.com/v2-db84ce883645b02cc4550fd9213702d7_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='902' height='268'></svg>)

下图是基于LID相似度对Supernet划分的示意图，Supernet每层有若干个候选操作。通过连接不同节点而得到的路径可以看成是一个子模型。下面是Supernet划分步骤，为方便理解我们考虑第一层：

1. 把第一层中的4个候选操作划分开来，这样可以将原来的Supernet划分得到4个sub-Supernet。
2. 对生成的4个sub-Supernet分别计算它们逐层的LID值分布
3. 计算sub-Supernet彼此之间LID分布相似度
4. 基于min-cut算法找到对sub-Supernet最合理的划分方式，即尽可能保证相似的sub-Supernet归为同一类。属于同一类的会进行合并得到最终的sub-Supernet，如下图（左）所示。
5. 划分完sub-Supernet之后分别finetune若干个epoch，最后每个模型通过继承对应sub-Supernet的权重直接进行性能评估。我们采用了进化算法进行搜索。

![](https://picx.zhimg.com/v2-9c94751fe99639ea58221c8b83a1c3b5_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1703' height='690'></svg>)

## 4. 实验结果

* GPU内存开销对比  
  下表显示了GM-NAS和NAS-LID在不同搜索空间和输入数据大下GPU内存开销对比。可以看到，在四种情况下，NAS-LID的GPU内存开销都明显小于GM-NAS，尤其是当时输入数据大小为32×3×224×224和搜索空间为NASBench-201时，GPU内存开销能降低86%。

![](https://pic1.zhimg.com/v2-4908946c27e470250a32d339388a6d51_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='629' height='269'></svg>)

* 模型性能排序相关性实验

下表对比了SPOS、GM-NAS和我们的NAS-LID在NAS-Bench201数据集上对模型性能排序相关性。可以看到NAS-LID有效提升了排名靠前的模型之间的性能排序。

![](https://picx.zhimg.com/v2-c117613731ecc3d925c852ec0035d20d_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1240' height='249'></svg>)

* 相似度衡量指标对性能排序影响  
  我们对比了基于欧氏距离和Pearson距离指标对最终性能排序相关性的影响。其中Pearson只衡量不同模型的LID的相对关系，例如假设两个模型的LID分布分别是[1,2,3]和[10,20,30]，那么Pearson指标会认为二者完全相似，而欧氏距离则关注的是绝对关系。  
  下表结果显示基于欧氏距离计算LID相似度取得了更高的性能排序相关性，这意味着LID值的绝对大小对于表征高维空间中不同结构的几何特性至关重要。

![](https://pica.zhimg.com/v2-134a9e1a56a76e016cf3e2677cb8d869_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='597' height='219'></svg>)

* 在OFA和ProxylessNAS搜索空间上的表现

我们进一步在 OFA和ProxylessNAS搜索空间验证了NAS-LID的有效性，下表显示了搜索到的模型在ImageNet上的表现，可以看到NAS-LID能够有效找到优秀的模型结构。

![](https://pica.zhimg.com/v2-8bb5f01f2c53f4256eaaf95cdcf0078c_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1234' height='873'></svg>)

## 5. 总结

我们的实验表明，逐层LID是一个能有效表征模型架构的指标。作为一个概念验证，我们提出了NAS-LID 来证明LID在划分超网中的潜在应用。与梯度相比，LID有效地解决了维度的诅咒，用于计算相似度的计算开销可以忽略不计，并且NAS-LID实现了更好的空间可分离性和更高的子网排名相关性。我们发现，LID值的大小在基于LID的模型架构表征中起着至关重要的作用，我们认为逐层的LID描绘了高维数据在模型中是如何变化的。

不过在这项工作中，我们只探讨了图像分类模型。我们认为有必要对大型语言模型也做类似的LID分析，也许能够帮助我们对大模型有更深入的了解。

## 6. 参考文献

[1] He X, Zhao K, Chu X. AutoML: A survey of the state-of-the-art[J]. Knowledge-Based Systems, 2021, 212: 106622.

[2] Zhao Y, Wang L, Tian Y, et al. Few-shot neural architecture search[C]//International Conference on Machine Learning. PMLR, 2021: 12707-12718.

[3] Hu S, Wang R, Hong L, et al. Generalizing Few-Shot NAS with Gradient Matching[J]. arXiv preprint arXiv:2203.15207, 2022.


---

## 如何评价Hinton提出的Forward-Forward方法？

`link: https://www.zhihu.com/question/570153849/answer/2787253215 · created: 1670161706`


我惊讶的是论文只有老爷子一个人的署名，致敬

![](https://picx.zhimg.com/v2-0fbd5dd2495e321a13b75495106235a8_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='691' height='599'></svg>)


---

## 你在发表理科学术文章过程中有哪些经验值得借鉴？

`link: https://www.zhihu.com/question/26729854/answer/2783365087 · created: 1669904455`


> 差生文具多，这里推荐我常用的一些对写文章有帮助的工具

### 写作

* Grammarly: 改语法错误。安装浏览器插件后会自动识别你输入的英文内容并提出修改建议

[Write your best with Grammarly.](https://link.zhihu.com/?target=https%3A//www.grammarly.com/)![](https://picx.zhimg.com/v2-c79d2fa2006af3d6f0443cba82c77125_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='524' height='407'></svg>)

* Quillbot：同义词替换，改变句式

![](https://picx.zhimg.com/v2-0aac35163cd649edef51817a74bd37de_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1307' height='210'></svg>)

* EasyEssay

输入一句话，可以自动根据话的意思生成一个段落。比如这里我让它写一下AutoML的历史，下面方框中的内容就是生成的。不过不是免费的，每天就有几次的额度而已

![](https://pic1.zhimg.com/v2-4b617a5b835f22c637bf5b4785c5bbca_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='664' height='493'></svg>)

我把生成的内容复制过来，客官们可以看看效果如何：

> Automated Machine Learning (AutoML) has a long history, beginning in the 1950s with the introduction of the first automated systems for optimizing industrial processes. The goal of AutoML is to automate the process of designing, building, and deploying machine learning models. Since then, AutoML has made great strides in helping organizations automate the process of creating machine learning models, making it easier and faster to build and deploy models. Recent advances in AutoML have enabled organizations to build and deploy machine learning models with minimal manual effort, saving time and resources. AutoML has become a key component of many machine learning systems and continues to play a vital role in the development of intelligent systems.

* Linggle：模糊查找英文单词用法

[https://linggle.com/help/](https://link.zhihu.com/?target=https%3A//linggle.com/help/)![](https://pic1.zhimg.com/v2-876a8a5b197fcabc3ee8e7f33d208b4b_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='807' height='783'></svg>)

### 翻译

* DeepL

翻译效果公认的好

* 沙拉查词：同时用多个翻译软件翻译，支持浏览器插件，滑词滑句子就能实时翻译，还免费

货比三家才是真正好

![](https://pica.zhimg.com/v2-368cadb4221485c84a843bb21db75018_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='593' height='634'></svg>)

### 画图

无他，Drawio足矣，而且还开源。之前坚果云就基于这个提供了画图功能，但是阉割了导出pdf，改成了收费模式，-\_-

[https://github.com/jgraph/drawio-desktop/releases](https://link.zhihu.com/?target=https%3A//github.com/jgraph/drawio-desktop/releases)

要是在墙外，可以直接用网页版，方便到不行

[Flowchart Maker & Online Diagram Software](https://link.zhihu.com/?target=https%3A//app.diagrams.net/)![](https://picx.zhimg.com/v2-fedb7560e47811dba8fc0266d8355da4_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='906' height='772'></svg>)

### Latex工具

* Detexify：记不住符号命令没关系，有手就行。

[Detexify LaTeX handwritten symbol recognition](https://link.zhihu.com/?target=http%3A//detexify.kirelabs.org/classify.html)

下图左边是我用鼠标画的，虽然很丑，但是不影响识别

![](https://picx.zhimg.com/v2-f5e140a5392851d11d1c843a224e1078_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='662' height='564'></svg>)

* Tables generator：表格转换器

[Create LaTeX tables online](https://link.zhihu.com/?target=https%3A//www.tablesgenerator.com/)

支持Excel、markdown，HTML，Latex等格式的表格转换，latex新手推荐使用

![](https://picx.zhimg.com/v2-5611997eb1ac610d0a5c68386a752b16_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='968' height='682'></svg>)

* Online Bibtext Tidy：在线整理bib文件

[Online BibTeX Tidy - Clean up BibTeX files](https://link.zhihu.com/?target=https%3A//flamingtempura.github.io/bibtex-tidy/)

写论文的时候一般引用很多论文，例如这个例子中原bib文件长这样，格式乱七八糟，非常不美观

![](https://pic1.zhimg.com/v2-82e8af869c815b2a43cd1c7bd511ed42_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='623' height='421'></svg>)

一键清洗后长这样，是不是清爽多了

![](https://pica.zhimg.com/v2-26790320d8398f3018f6674cf1824c75_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='720' height='355'></svg>)

另外该网页还支持很多其他的功能，例如去重，去除空字符等等，还能够批量修改。对bib文件有其他需求的也可试试这个网页看能不能解决你的问题

### 语料库

* PhraseBank

[Reporting results - Academic Phrasebank](https://link.zhihu.com/?target=https%3A//www.phrasebank.manchester.ac.uk/reporting-results/)

学术论文说简单点有点像八股文，其实都大同小异，无非是摘要，介绍，方法，实验和结果，相关工作，总结等部分组成，这个网站提供了论文各个部分的模板句式。

以对实验结果章节为例，假如你要描述某个图片或表格的结果，你可以这样写

![](https://picx.zhimg.com/v2-7c812cb5e46b226e496678b423d37b00_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='693' height='605'></svg>)

如果你想强调你从实验结果发现了一些有趣的现象，你可以这样写

![](https://pic1.zhimg.com/v2-523ddee7781b9b44ff21328eb15ce24e_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='615' height='465'></svg>)

### 追踪感兴趣的学者/工作

* ResearchGate: 学术版facebook

首页会推送与你相关领域的研究工作，另外你关注的学者的最新动态也会实时更新

[https://www.researchgate.net/profile/Xin-He-105](https://link.zhihu.com/?target=https%3A//www.researchgate.net/profile/Xin-He-105)![](https://pic1.zhimg.com/v2-976c97990c711c791573b2881cdfe217_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1473' height='907'></svg>)


---

## 如何看待 Meta 新 AI 在战略桌游上表现突出，可用话语进行谈判和欺骗？此类 AI 技术难点在哪？

`link: https://www.zhihu.com/question/569924273/answer/2783305069 · created: 1669901144`


## 1. 简介

馒头给这个AI取名为 Cicero（西塞罗），其实借用了罗马共和国晚期的哲学家、政治家、律师、作家、雄辩家的名字。因为其演说和文学作品，西塞罗被广泛地认为是古罗马最伟大的演说家和最具影响力的散文作家之一。

之前的阿法狗或者是王者荣耀AI都是基于规则和算力，以一种理性的方式打败人类。而Cicero AI则是通过对话的方式感性地（也有理性成分）说服人类。具体来说，馒头选择了外交作为测试，因为几十年来，外交一直被视为人工智能中几乎不可能的重大挑战，因为它要求AI能够掌握理解他人动机和观点，制定复杂的计划并调整策略，然后使用自然语言与其他人达成协议，说服他们建立伙伴关系和联盟等等。是不是听起来就很复杂

![](https://pic1.zhimg.com/v2-411bea782c81b682401b89830ef09382_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1920' height='1080'></svg>)

Cicero AI在（[Home - webDiplomacy](https://link.zhihu.com/?target=https%3A//webdiplomacy.net/)）上进行了测试，这是一个提供了很多游戏的网站，其中网络外交就是其中一个。

代码已开源：[GitHub - facebookresearch/diplomacy\_cicero: Code for Cicero, an AI agent that plays the game of Diplomacy with open-domain natural language negotiation.](https://link.zhihu.com/?target=https%3A//github.com/facebookresearch/diplomacy_cicero)

相关工作也已经发表在 Science2022和 投稿至ICLR2023上：

* ["Human-Level Play in the Game of Diplomacy by Combining Language Models with Strategic Reasoning"](https://link.zhihu.com/?target=https%3A//www.science.org/doi/10.1126/science.ade9097) Science, November 2022.
* ["Mastering the Game of No-Press Diplomacy via Human-Regularized Reinforcement Learning and Planning"](https://link.zhihu.com/?target=https%3A//arxiv.org/abs/2210.05492) ICLR 2023. （这会影响双盲吗）

## 2. “网络外交”是什么游戏？

在了解CiceroAI之前，我们先简单了解一下这个网络外交游戏到底是个啥？

![](https://pic1.zhimg.com/v2-e51c2713329df367192a96759222380b_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='630' height='546'></svg>)

外交游戏模拟的是一战期间七大强国瓜分欧陆的情形，，七名玩家中的每一个都控制着 1901 年欧洲的一个大国,其核心规则是玩家通过交流（即外交）争夺资源点，最终率先拿下一半欧洲领土的即为赢家。

整个游戏过程中，玩家可以在棋盘上移动你的单位，争取将其他玩家的补给中心据为己有。游戏初始状态下每个玩家都有3个军队单位，每个单位战斗力相同。所以刚开始1v1谁也赢不了对方，这个时候就需要找人联盟帮忙，游戏中需要通过对话框来与其他游戏玩家交流来达到结盟等目的。

![](https://pic1.zhimg.com/v2-21fb77c6ea3786ddc01a95d7847ef515_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1536' height='864'></svg>)

* CICERO打了40场比赛，对阵82名匿名人类竞争对手。

• 在每场比赛中，CICERO平均向其他六名球员发送130条消息。

• CICERO的平均得分是对手的2倍以上。

• CICERO在玩过不止一款游戏的参与者中排名前10%\*\*。

下图是CICERO在实际游戏过程中的对话信息,其代理国家是是奥地利，通过对话可以看到它正在和代理俄罗斯的玩家进行着某种不可言说的交易

![](https://pic1.zhimg.com/v2-da175d35f438b02f5bd243b2fe2b234f_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1851' height='1015'></svg>)

这就很像图灵测试，真实的游戏玩家在和CICERO交流时甚至都没有发觉对方是个机器人。和小爱小冰的区别在于，CICERO 更倾向掌握对话主动权，着实有点意思。也许以后在面对甲方的无理要求时，CICERO也许是个不错的帮手。

## 3. AI技术

### 可控对话

基于上面对游戏的简介我们知道CiceroAI的一个核心就是可控对话模型。要训练这个模型最重要的就是数据集。相比于以往的NLP模型，这里需要的数据集更侧重于对话，而且对话之间有真有假，逻辑性很强。为了解决这一问题，meta使用了27亿参数量的类似BART【1】的语言模型，该模型先基于互联网上的文本数据进行预训练，然后再基于[http://webDiplomacy.net](https://link.zhihu.com/?target=http%3A//webDiplomacy.net)上40,000个人类游戏数据进行微调。

另外，facebook上本身就含有大量对话信息，我猜测这上面用户之间的聊天数据可能也有部分作为训练集参与了训练，当然也只是猜测。

Meta团队开发了自动将训练数据中的消息与游戏中相应的计划动作进行注释的技术，以便在推理时可以控制对话生成，以讨论代理及其对话伙伴的特定期望操作。比如说当CiceroAI设定为奥地利时，那么上面图中红色文本就是需要预测的内容，就像是高阶版本的完形填空。

CiceroAI采用强化学习来更新模型，每次会生成多个文本，然后通过设计好的过滤器筛掉那些废话多，信息量低的句子，已达到最大化value的目的。

![](https://picx.zhimg.com/v2-b6860ed12fd0b970745c885175155673_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='747' height='414'></svg>)

### 目的一致性、有对话意识

单纯生成对话文本还不行，因为游戏中有不同的玩家。比如我们是英格兰，其他游戏玩家可能是法国、德国和俄罗斯等等。只要我们想，我们可以在对话框中对任意游戏玩家发送私信进行聊天。那么需要保证的与不同玩家说话，所要传达的最终目的需要保持一致，不能前后对话自相矛盾。比如我们的最终目的是要找到联盟拿下德国，那么我们肯定不希望AI一边跟法国说结盟打德国，另一边又跟俄罗斯说结盟打俄罗斯。

下图展示了AI机器人作为英格兰玩家的时候对法国、德国和俄罗斯发送的对话信息。CICERO试图通过向三个不同的玩家提出行动来执行其战略。在第二个对话框中，AI能够告诉其他玩家为什么他们应该合作以及如何互惠互利。第三，CICERO既在征求信息，又为未来的行动奠定基础。

![](https://pica.zhimg.com/v2-cd566dfd2dc55cac830512f7396ab4af_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1916' height='970'></svg>)

## 4. 未来

我到时希望国内如果有研究团队想跟进这类项目的话可以考虑把甄嬛传拿来作为训练数据，这个可能对于编剧行业会产生不小的冲击

## 参考

【1】BART: Denoising Sequence-to-Sequence Pre-training for Natural Language Generation, Translation, and Comprehension

【2】[https://ai.facebook.com/blog/cicero-ai-negotiates-persuades-and-cooperates-with-people/](https://link.zhihu.com/?target=https%3A//ai.facebook.com/blog/cicero-ai-negotiates-persuades-and-cooperates-with-people/)


---

## 自动机器学习（AutoML）领域有哪些优秀的算法？

`link: https://www.zhihu.com/question/470440334/answer/2768804331 · created: 1669044489`


## 王婆卖瓜，自卖自夸，给自己的框架带个广告

[https://github.com/marsggbo/hyperbox](https://link.zhihu.com/?target=https%3A//github.com/marsggbo/hyperbox)

## **1. 简介**

Hyperbox目前支持：

* 神经架构搜索（Neural Architecture Search, NAS）：基于微软的NNI框架设计并做了改进，涉及的核心模块包括`hyperbox.mutables`和`hyperbox.mutator`。另外`hyperbox.networks`重新实现了很多NAS论文中的搜索空间。
* 超参优化（Hyperparameters Optimization, HPO）：基于`hydra`和`optuna`库实现
* 自动数据增强（Auto Data Augmentation, ADA）：基于`Kornia`库实现

完整的搜索和训练方法基于Pytorch-lightning封装实现，所以像多GPU，混合精度计算等细节的东西我们可以不用担心了。

## **2. 安装**

安装方式有两种：

* 第一种是pip安装

```
pip install hyperbox
```

* 第二种是源码安装

```
git clone https://github.com/marsggbo/hyperbox.git
cd hyperbox
python setup.py develop # 建议已开发者模式安装
python install -r requirements.txt
```

## **3. 神经架构搜索（NAS）**

## **3.1 可搜索模块 (`hyperbox.mutables`)**

![](https://picx.zhimg.com/v2-89e82d474f558b96fd0ae340f31a10fc_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1440' height='591'></svg>)

目前hyperbox支持实现上面三种搜索模块，这已经能够覆盖现有的大多数模型结构了。`hyperbox.networks`中十几个常见的NAS搜索空间。下面我们可以看看图中三种不同搜索空间的代码实现示例

* 图左代码实现示例：候选操作搜索

这个其实就是相当于在某一层中我们有若干个候选操作，我们想从中选择出最适合的一个，`OperationSpace`就是这个用途

```
import torch.nn as nn
from hyperbox . mutables . spaces import OperationSpace
op1 = nn.Conv2d(in_channels=3, out_channels=16, kernel_size=3, stride =1, padding=1)
op2 = nn.Conv2d(in_channels=3, out_channels=16, kernel_size=5, stride =1, padding=2)
op3 = nn.Conv2d(in_channels=3, out_channels=16, kernel_size=7, stride =1, padding=3)
ops = OperationSpace(candidates=[op1, op2, op3], key=’conv_op’, mask=[1, 0, 0])
```

可以看到`OperationSpace`有三个重要的参数：

* `candidates`：很显然就是一个list，每个元素是一个Pytorch的`nn.Module`
* `key`：可以理解成是一个唯一识别码，如果两个可搜索模块重名了，那么它们二者的搜索结果会一样，这个需要特别注意
* `mask`: 默认为None，表示当前模块需要搜索；否则，可以传入list或者dict来之指明选择哪一个操作

+ one-hot格式的list，长度需要和`candidates`一样。上面`mask=[1, 0, 0]`表示选择第一个操作，即3x3卷积
+ dict（字典），即`{key: value}`，其中的key和value可以有很多组，并且value也必须是list。不过其中必须包含一组`{'conv_op': [0, 1, 0]}`。

如无特殊说明，后面两种模块也遵循这种设计。

* 图中代码实现示例：输入节点搜索

除了从多个候选操作中选择一个，很多情况我们也想从模型前面几层的输出中选择一个或者若干作为当前层的输入，这个时候可以用`InputSpace`

```
import torch
from hyperbox.mutables.spaces import InputSpace
in1 = torch.rand(2, 64)
in2 = torch.rand(2, 32)
in3 = torch.rand(2, 16)
inputs = [in1, in2, in3]
skipconnect = InputSpace(n_candidates=3, n_chosen=1, key=’sc’, mask=[0, 1, 0])
out = skipconnect([ in1 , in2 , in3 ]) 
assert out is in2
>>> True
```

* 图右代码实现示例：细腻度（Finegrained）操作搜索

以上两个模块都是参考的微软NNI框架实现的，不过他们仅支持搜索完整的操作，很多时候我们也许像搜索更加细腻度的操作，就像图右所示，我们想搜索不同卷积核大小，不过它们就像人生无常，大肠包小肠一样地重叠在一起了，现有的框架大都不支持这个。Hyperbox实现了`ValueSpace`，然后override了pytorch的所有卷积操作（Conv1d/2d/3d）、线性层（Linear）和batchnorm。只要传入的参数是`ValueSpace`，hyperbox就能够对这个参数进行搜索，我们看看下面的例子

```
from hyperbox.mutables.spaces import ValueSpace
from hyperbox.mutables.ops import Conv2d, Linear 

# convolution
ks = ValueSpace([3, 5, 7], key=’kernelSize’, mask=[0, 1, 0])
cout = ValueSpace([16, 32, 64], key=’channelOut’, mask=[0, 1, 0])
conv = Conv2d(3 , cout , ks , stride =1, padding=2, bias=False)
print([x.shape for x in conv.parameters()])
>>> [torch.Size([32, 3, 5, 5])]

# linear
cout = ValueSpace([10, 100], key=’channelOut1’)
isBias = ValueSpace([0, 1], key=’bias’) # 0: False, 1: True 
linear = Linear(10, cout , bias=isBias)
print([x.shape for x in linear.parameters()])
>>> [ torch.Size ([100 , 10]) , torch.Size ([100]) ]
```

## **3.2 搜索算法 (`hyperbox.mutator`)**

* Random Search Algorithm `RandomMutator` 前面介绍`hyperbox.mutables`时，我们可以看到都有显式地指明一个参数，即`mask=...`。但很多时候其实我们不知道模型应该长什么样，所以保持默认值`mask=None`即可。

之后，可以用到`hyperbox.mutator`来对设计的搜索空间进行搜索。可以看看下面的代码示例：

```
from hyperbox.mutator import RandomMutator
from hyperbox.networks.ofa import OFAMobileNetV3

net = OFAMobileNetV3(mask=None)
rm = RandomMutator(net)
rm.reset() # search a subnet
arch: dict = rm._cache # arch of a subnet
print(arch)

subnet1 = OFAMobileNetV3(mask=arch) # initialize a subnet, which has smaller parameters than `net`
subnet2 = net.build_subnet(mask_arch)
```

* `OFAMobileNetV3`是Once-for-all （OFA）论文中用到的搜索空间,此时`mask=None`表示模型处于待搜索状态
* 第5行，模型`net`作为参数传给了`RandomMutator`,在`RandomMutator`初始化的时候它会对`net`中所有的模块遍历一遍，如果发现了`hyperbox.mutables`模块就会记录下。每次模型forward的时候，正常的`nn.Module`模块没有变化，而`hyperbox.mutables`的forward会受到Mutator的控制。比如一个`OperationSpace`的mask搜索结构是[0,1,0]，那么Mutator会自动激活第二个操作参与到的forward计算，另外两个不会参与运算。
* 第6行：`.reset()`是调用搜索算法，看看`RandomMutator`源码应该就能知道是什么作用了
* 第7行：每次调用`reset()`就会采样得到一个新的子网，该子网的结构用字典表示，存储在`_cache`这个属性中
* 第10行和11行：这两行显示了两种生成子模型的方法，建议使用第二种，因为它能够自动继承Supernet的权重到子网的对应位置。第一种会随机初始化权重。

```
class RandomMutator(Mutator):
    def __init__(self, model, *args, **kwargs):
        super().__init__(model)

 def reset(self):
  ... # 一些预处理操作
  self._cache = self.sample_search()
  return self._cache

    def sample_search(self):
        result = dict()
        for mutable in self.mutables:
            if isinstance(mutable, OperationSpace):
                gen_index = torch.randint(high=mutable.length, size=(1, ))
                result[mutable.key] = F.one_hot(gen_index, num_classes=mutable.length).view(-1).bool()
                mutable.mask = result[mutable.key].detach()
            elif isinstance(mutable, InputSpace):
                if mutable.n_chosen is None:
                    result[mutable.key] = torch.randint(high=2, size=(mutable.n_candidates,)).view(-1).bool()
                else:
                    perm = torch.randperm(mutable.n_candidates)
                    mask = [i in perm[:mutable.n_chosen] for i in range(mutable.n_candidates)]
                    result[mutable.key] = torch.tensor(mask, dtype=torch.bool)  # pylint: disable=not-callable
                mutable.mask = result[mutable.key].detach()
            elif isinstance(mutable, ValueSpace):
                gen_index = torch.randint(high=mutable.length, size=(1, ))
                result[mutable.key] = F.one_hot(gen_index, num_classes=mutable.length).view(-1).bool()
                mutable.mask = F.one_hot(gen_index, num_classes=mutable.length).view(-1).bool()
        return result
```

未完待续。。。

超参调优和自动数据增强见下一篇文章介绍

Hyperbox框架还有很多可以完善的地方，对框架开发感兴趣的小伙伴可以扫码入群，有问题也可以在群里讨论。

![](https://picx.zhimg.com/v2-a0ad462e687c9bf67c2f85503b077b76_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='910' height='1264'></svg>)

### **微信公众号：AutoML机器学习**

![](https://picx.zhimg.com/50/v2-87083e55cd41dbef83cc840c142df48a_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='0' height='0'></svg>)

**MARSGGBO♥原创**  
**如有意合作或学术讨论欢迎私戳联系~**  
**邮箱:marsggbo@foxmail.com**


---

## 如何看待与评价 AAAI 2023 的录用结果？

`link: https://www.zhihu.com/question/566823653/answer/2765541195 · created: 1668845273`


只有导师收到邮件了，accept，但是cmt系统被挤爆了，现在进不去

![](https://pic1.zhimg.com/v2-fea49654a1a2cf5ed730ca1973b99612_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1280' height='2844'></svg>)

给自己的automl框架打个广告，是基于nni设计的，有设计新的搜索API，文档说明还有待完善，有兴趣参与框架设计的欢迎私戳讨论，也欢迎提issue

传送门:

[https://github.com/marsggbo/hyperbox](https://link.zhihu.com/?target=https%3A//github.com/marsggbo/hyperbox)

更多细节可查阅源代码或看看这篇文章

[自动机器学习框架Hyperbox：妈妈再也不用担心我不会设计模型和调参啦](https://zhuanlan.zhihu.com/p/585073718)

本次中的论文中文介绍：

[marsggbo：AAAI2023论文 | 基于局部本征维度的高效神经架构搜索算法](https://zhuanlan.zhihu.com/p/591027254)


---

## 如何评价某211本科课程只能用LaTeX提交作业？

`link: https://www.zhihu.com/question/564679301/answer/2753760825 · created: 1668138984`


问题描述是 “都是才来大学不到三个月的高中生啊，我觉得这是否有点揠苗助长”

咋的，是latex的使用有年龄限制吗？还是说你想把作业写在答题纸上？

让你用latex是拔苗助长？助长了你啥？矫情吗？？？

花个几天时间（快的几个小时）就能上手的事情还特地跑知乎来找骂，B站肯定也一大堆视频教程，亏你还特意在问题上写了211，这点学习能力都没有吗，纯纯来找骂

好好利用知乎，遇到不爽的事平时自己发个微博，发个朋友圈吐槽一下就够了

别老想着在知乎上借大家的嘴帮你泄愤，输出情绪后仍然解决不了问题

要是嫌装latex环境太复杂了，你大可问问知乎的人er们有没有什么简单好用的latex工具，网上也有一大堆本地环境安装教程

另外 [overleaf.com](https://link.zhihu.com/?target=http%3A//overleaf.com/) 这个网站不需要自己配置，选择好模板后，就和word差不多是了，而且还不用管排版


---

## 硕士研究生如何入AutoML(自动机器学习)?

`link: https://www.zhihu.com/question/554255720/answer/2750670583 · created: 1667960577`


> 自引一下之前的回答

只谈谈个人的学习方法，希望对想学习AutoML的同学有帮助

## 综述

第一步当然是得看综述，这样你能有一个全局的概念，不至于看一大堆NAS论文的时候不知道他们的区别是什么，而迷失在技术细节里。

谈到综述，那必然首推NAS综述鼻祖： **Neural Architecture Search: A Survey**

[a](https://link.zhihu.com/?target=https%3A//arxiv.org/abs/1808.05377)![](https://picx.zhimg.com/v2-3739d240368534f5477c3cc47ef8deb9_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='780' height='306'></svg>)

NAS流程图

这篇综述将NAS划分成三个组成部分：搜索空间，搜索策略和性能评估策略。后续基本所有NAS论文也都遵循这个框架设计思路，或者在这个框架下改进。

接下来推荐你看看我们实验室的AutoML综述：**AutoML: A Survey of the State-of-the-Art**

[a](https://link.zhihu.com/?target=https%3A//arxiv.org/abs/1908.00709)

我们的综述清晰地给出了一个完整的AutoML的pipeline框架，如下图示。

![](https://pic1.zhimg.com/v2-b7d685e80d1ba1e7699b22a1df5a295b_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1292' height='629'></svg>)

AutoML Pipeline

可以看到我们把传统的机器学习模型和深度神经网络都统一到了一个框架下，NAS（虚线框里面的部分）也在这个AutoML pipeline中。我们还总结了现有的搜索空间和搜索策略等技术细节，详情可以看原论文或者之前的文章

[a](https://zhuanlan.zhihu.com/p/158162306)

NAS和AutoML的综述有不少，你精度几篇之后，另外几篇可以作为补充阅读，这样你就对AutoML能有一个大题的了解了。

## 阅读经典

阅读论文的时候可能很多技术细节你读的云里雾里，没关系，你这个时候只需要知道它属于哪一类，大概用了某一种方法就可以了。接下来你就需要阅读一些经典的NAS论文，因为后续很多论文都是基于早期的工作做改进或者魔改，又或者是一些rethinking的工作。

这里推荐你阅读一下论文：

### 强化学习

* 最早的NAS：B. Zoph, Q. V. Le, Neural architecture search with reinforcement learning, in: 5th International Conference on Learning Representations, ICLR 2017
* [ENAS：Efficient Neural Architecture Search via Parameters Sharing](https://link.zhihu.com/?target=http%3A//proceedings.mlr.press/v80/pham18a.html) ENAS是较早提出权重共享（weight-sharing）的搜索策略，这个也让NAS的搜索从最初成千上百的GPU消耗降到了只需要一个GPU。技术细节可以看看我之前的博客

[a](https://link.zhihu.com/?target=https%3A//www.cnblogs.com/marsggbo/p/9435954.html)

### 进化算法

* 这里只推荐一篇论文，华为的CARS：**Z. Yang, Y. Wang, X. Chen, B. Shi, C. Xu, C. Xu, Q. Tian,C. Xu, CARS: continuous evolution for efficient neural architecture search, CVPR 2020**。早期的进化算法资源消耗的多，而且时间还长（比如AmoebaNet用了450 K40搜索了3150个GPU days），因为不同子网络是互相独立搜索的。不过CARS将进化算法和权重共享做了结合，效率大大提升，源码也开源了，感兴趣地可以了解一下,里面部分代码我也有贡献hhh

[a](https://link.zhihu.com/?target=https%3A//github.com/huawei-noah/vega/blob/master/docs/en/algorithms/cars.md)

### 梯度下降

* 提到梯度下降，那肯定就是鼻祖工作 DARTS了：**H. Liu, K. Simonyan, Y. Yang, DARTS: differentiable architecture search, ICLR 2020.**  后面几乎所有基于梯度下降的都是基于它的思路做的改进
* 强烈推荐看看这篇论文 Once for All: Train One Network and Specialize it for Efficient Deployment。这个是韩松老师团队的工作，他们可以在完成搜索后，可以直接导出模型，而且模型不需要重头训练就能有很好的效果。我有在自己的框架实现这个，发现的确是可以不用train from scratch，导出的任意一个子模型效果都还不错，我们只需要finetune一下下就能进一步提高模型性能。这种训练范式可以理解成 one-shot NAS。类似的工作还有

[a](https://link.zhihu.com/?target=https%3A//arxiv.org/abs/1904.00420)

## 阅读原论文代码

算法知道了，下一步要啃的硬骨头就是代码了，以下推荐的代码真的要认真去跑一下，并且理解它的设计思路

### DARTS

* 这个是原作者开源的代码

[a](https://link.zhihu.com/?target=https%3A//github.com/quark0/darts)

* 这个是更好理解的代码版本，推荐看这个

[a](https://link.zhihu.com/?target=https%3A//github.com/khanrc/pt.darts)

### ENAS

* 原论文是基于TensorFlow写的，emm不做过多评价

[a](https://link.zhihu.com/?target=https%3A//github.com/melodyguan/enas)

* 如果你更加钟意pytorch，可以看看这个代码

[a](https://link.zhihu.com/?target=https%3A//github.com/carpedm20/ENAS-pytorch)

### Once-for-all

这个前面提到的韩松老师他们的工作，代码写的很清晰

[a](https://link.zhihu.com/?target=https%3A//github.com/mit-han-lab/once-for-all)

## NAS大一统

如果前面的代码你都体验过后，你会发现，不同框架实现起来千差万别，你想在你的数据集上尝试不同算法得花大把时间做代码迁移（魔改），而且往往还不一定成功。这个时候你需要一个NAS框架来帮助你。目前已经有不少开源的NAS框架，这里我只推荐两个吧，这两个我真的推荐好多次了哈哈哈哈

* 华为的Vega
* [marsggbo：华为诺亚实验室AutoML框架-Vega：(1) 介绍](https://zhuanlan.zhihu.com/p/258362976)
* [marsggbo：华为诺亚AutoML框架-Vega：(2) 代码结构](https://zhuanlan.zhihu.com/p/306462348)
* 微软的NNI
* [marsggbo：Retiarii：微软在NAS框架上的新动作，已被顶会OSDI2020接收](https://zhuanlan.zhihu.com/p/372128920)
* 我自己开发的AutoML框架：[https://github.com/marsggbo/hyperbox](https://link.zhihu.com/?target=https%3A//github.com/marsggbo/hyperbox) 还在不断更新开发中，感兴趣的可以私信我一起开发

### 微信公众号：AutoML机器学习

![](https://picx.zhimg.com/50/v2-87083e55cd41dbef83cc840c142df48a_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='0' height='0'></svg>)

**MARSGGBO♥原创**

如有意合作或学术讨论欢迎私戳联系~

邮箱:marsggbo@foxmail.com


---

## 深度强化学习是如何利用GPU进行并行计算的？

`link: https://www.zhihu.com/question/308716947/answer/2750345563 · created: 1667925386`


> “ 本文主要参考ColossalAI论文 《Colossal-AI: A Unified Deep Learning System For Large-Scale Parallel Training》  
>  ColossalAI框架开源提供了本文介绍的所有并行训练: [https://github.com/hpcaitech/ColossalAI](https://link.zhihu.com/?target=https%3A//github.com/hpcaitech/ColossalAI)  
>  ”

## **前言**

本文会介绍几种流行的深度学习并行方法，包括

* 数据并行（data parallel）
* 模型并行（model parallel）

+ tensor并行
+ pipeline并行
+ Sequence并行

* Zero Redundancy Data Parallelism （ZeRO）

下图给出了这些并行方法的示意图，非常直观好懂。

![](https://picx.zhimg.com/v2-7946bc1070d007f8409f4bce00fe1731_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1916' height='700'></svg>)

不过在介绍各种并行训练方法之前，我们首先对一些概念做一个声明，方便后面理解

模型训练过程中涉及到的参数主要包含两大类，*model data* 和 *non-model data*，具体表示如下：

* model data

+ 模型权重
+ 模型权重的梯度
+ 优化器的状态

* non-model data

+ 模型逐层的特征向量（也叫作activations）

## **1. Data parallelism (DP)**

经典的数据并行算法是在多个设备上都拷贝一份完整的模型参数，彼此之间可以独立计算，所以每个设备传入的输入数据不一样​，这也是为什么叫数据并行。只不过，每隔一段时间（比如一个batch或者若干个batch）后需要彼此之间同步模型权重的梯度​。随着模型大小不断增大，单个GPU的内存已经无法容纳现如今的大模型，所以便有了后面会介绍的模型并行​。

DP下有很多优化算法，具体的可以看看我优秀师弟 [@二猹树](https://www.zhihu.com/people/f97528ae4a73b5bf0504a7123453a37e) 的相关综述

* 《[Communication-Efficient Distributed Deep Learning: A Comprehensive Survey](https://link.zhihu.com/?target=https%3A//arxiv.org/abs/2003.06307)》
* 《[A Quantitative Survey of Communication Optimizations in Distributed Deep Learning](https://link.zhihu.com/?target=https%3A//ieeexplore.ieee.org/abstract/document/9275615/)》

## **2. Model Parallelism (MP)**

### **2.1 Pipeline Parallelism (PP)**

pipeline parallelism是比较常见的模型并行算法，它是模型做层间划分，即inter-layer parallelism。以下图为例，如果模型原本有6层，你想在2个GPU之间运行pipeline，那么每个GPU只要按照先后顺序存3层模型即可。

![](https://picx.zhimg.com/v2-bfeea6ddcc2e60511652d10f4da7acb2_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='544' height='546'></svg>)

已经有很多Pipeline相关的研究工作了，例如PipeDream，GPipe，和Chimera。它们的主要目的都是降低bubble time。这里不做过多介绍。

### **2.2 Tensor Parallelism (TP)**

前面介绍的Pipeline Parallelism是对模型层间做划分，叫inter-layer parallelism。那么另一种方式则是对模型层内做划分，即intra-layer Parallelism，也叫Tensor Parallelism。

![](https://picx.zhimg.com/v2-2befe468a1450ee315c7672c0e40594b_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1640' height='570'></svg>)

Tensor Parallelism

**2.2.1 1D Tensor Parallelism**

Megatron-LM [1]是最早提出1D Tensor并行的工作。该工作主要是为了优化transformer训练效率，把线性层按照行或者列维度对权重进行划分。如下图所示，原本线性层为![Y=W_1W_2X](https://www.zhihu.com/equation?tex=Y%3DW_1W_2X) ，这里将![W_1](https://www.zhihu.com/equation?tex=W_1)按列进行划分，将![W_2](https://www.zhihu.com/equation?tex=W_2)按行进行划分。这样，每个GPU只需要存一半的权重即可，最后通过All-reduce操作来同步Y的结果。当GPU数量为![N](https://www.zhihu.com/equation?tex=N)时，每个GPU只需要存![\frac{1}{N}](https://www.zhihu.com/equation?tex=%5Cfrac%7B1%7D%7BN%7D)的权重即可，只不过每层输出需要用All-reduce来补全结果之后才能继续下一层的计算。

![](https://picx.zhimg.com/v2-692d0821e4bad2eceaec24dbf3fe24dd_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='870' height='436'></svg>)

对于土豪公司，可以使用NVLink来连接GPU（如下图a），从而提供高带宽来降低通信开销。但是土豪终归是少数的，大部分公司和个人是没法承担这昂贵的硬件费用，因此比较常见的GPU连接方式是下图b，即节点内花点钱实现NVLink连接，节点之间通过PCIe连接。

![](https://picx.zhimg.com/v2-2b2f460cb3d80a78dbb939b57119f6a8_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='928' height='688'></svg>)

1D Tensor并行对通信速度要求较高，不过1D在每层的输入和输出都有冗余的内存开销。以Fig.4为例，我们可以看到虽然模型权重被划分了，但是每个GPU都有重复的输入![X](https://www.zhihu.com/equation?tex=X),另外All-reduce之后每个GPU也会有重复的输出![Y](https://www.zhihu.com/equation?tex=Y)，所以后续一些工作尝试从这里做进一步改进,包括2D, 2.5D,和3D tensor并行。

**2.2.2 2D Tensor Parallelism**

2D Tensor Parallel [2] 基于SUMMA和Cannon矩阵相乘算法沿着两个不同的维度对 *输入数据*，*模型权重*，*每层的输出* 进行划分。给定![N](https://www.zhihu.com/equation?tex=N)个GPU，tensor会被划分成![N](https://www.zhihu.com/equation?tex=N)个chunk（使用`torch.chunk`），每个GPU保存一个chunk。这![N](https://www.zhihu.com/equation?tex=N)个GPU呈方形网络拓扑结构，即每行每列均为![\sqrt{N}](https://www.zhihu.com/equation?tex=%5Csqrt%7BN%7D)个GPU。假设tensor的维度大小是![[P,Q]](https://www.zhihu.com/equation?tex=%5BP%2CQ%5D)，那么划分后每个GPU上存的chunk大小即为![[P/\sqrt{N},Q/\sqrt{N}]](https://www.zhihu.com/equation?tex=%5BP%2F%5Csqrt%7BN%7D%2CQ%2F%5Csqrt%7BN%7D%5D)。至此，每个GPU都只会保存部分的输入输出以及部分的权重。虽然相比于1D Tensor并行，2D额外增加了模型权重的通信，但是需要注意的是当GPU数量很多的时候，每个GPU上分配的模型权重就会小很多，而且因为使用的All-reduce通信方式，所以2D也还是要比1D更高效的。

**2.2.3 2.5D Tensor Parallelism**

2.5D Tensor Parallel [3] 是受2.5D矩阵乘法算法 [4] 启发进一步对2D Tensor并行的优化。具体来说2.5D增加了 *depth* 维度。当 *depth=1* 时等价于2D；当 *depth>1* 时，

同样假设有![N](https://www.zhihu.com/equation?tex=N)个GPU，其中![N=S^2*D](https://www.zhihu.com/equation?tex=N%3DS%5E2%2AD)，![S](https://www.zhihu.com/equation?tex=S)类似于原来2D正方形拓扑结构的边长，而![D](https://www.zhihu.com/equation?tex=D) 则是新增加的维度 *depth* 。![D](https://www.zhihu.com/equation?tex=D)可以由用户指定，![S](https://www.zhihu.com/equation?tex=S) 则会自动计算出来了。所以一般来说至少需要8个GPU才能运行2.5D算法，即![S=2,D=2](https://www.zhihu.com/equation?tex=S%3D2%2CD%3D2)。

**2.2.4 3D Tensor Parallelism**

3D Tensor Parallel [5]是基于3D矩阵乘法算法 [6]实现的。假设有 ![N](https://www.zhihu.com/equation?tex=N)个 GPU，tensor维度大小为![[P, Q, K]](https://www.zhihu.com/equation?tex=%5BP%2C+Q%2C+K%5D)，那么每个chunk的大小即为 ![[P/\sqrt[3]{N},Q/\sqrt[3]{N},K/\sqrt[3]{N}]](https://www.zhihu.com/equation?tex=%5BP%2F%5Csqrt%5B3%5D%7BN%7D%2CQ%2F%5Csqrt%5B3%5D%7BN%7D%2CK%2F%5Csqrt%5B3%5D%7BN%7D%5D)。当tensor维度小于3时，以全连接层为例，假设权重维度大小为 ![[P, Q]](https://www.zhihu.com/equation?tex=%5BP%2C+Q%5D) ,那么可以对第一个维度划分两次，即每个chunk的维度大小为 ![[P/(\sqrt[3]{N})^2,Q/\sqrt[3]{N}]](https://www.zhihu.com/equation?tex=%5BP%2F%28%5Csqrt%5B3%5D%7BN%7D%29%5E2%2CQ%2F%5Csqrt%5B3%5D%7BN%7D%5D) 。3D Tensor并行的通信开销复杂度是 ![O(N^{1/3})](https://www.zhihu.com/equation?tex=O%28N%5E%7B1%2F3%7D%29) ，计算和内存开销都均摊在所有GPU上。

**2.2.5 小结**

1D Tensor并行每一层的输出是不完整的，所以在传入下一层之前都需要做一次All-gather操作，从而使得每个GPU都有完整的输入，如下图a所示。

2D/2.5D/3D Tensor 并行算法因为在一开始就对输入进行了划分， 所以中间层不需要做通信，只需要在最后做一次通信即可。在扩展到大量设备（如GPU）时，通信开销可以降到很小。这3个改进的Tensor并行算法可以很好地和Pipeline并行方法兼容。

![](https://pica.zhimg.com/v2-13c9d48af74271cc29da70c5faed1bb4_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='906' height='652'></svg>)

### **2.3 Sequential Parallelism**

Tensor parallelism主要是为了解决由 model data （模型权重，梯度和优化器状态）导致的内存瓶颈，但是 non-model data也可能成为性能瓶颈。比如像AlphaFold和NAS任务中会存在很多中间特征值（也叫activations）。

以DARTS算法为例，它的模型参数量其实并不多，但是它有很多分支，所以activations会消耗大量GPU内存，这也是为什么很多NAS算法只能在CIFAR-10上搜索到合适的模型结构后，再做人工扩展，最后应用到ImageNet上做性能验证。

同样地，在使用Transformer训练语言模型时，由于Transformer层中的Self-attention机制的复杂度是![O(n^2)](https://www.zhihu.com/equation?tex=O%28n%5E2%29)，其中 ![n](https://www.zhihu.com/equation?tex=n) 是序列长度。换言之，长序列数据将增加中间activation内存使用量，从而限制设备的训练能力。

Sequential Parallelism （SP）就为了解决non-model data导致的性能瓶颈而提出的。下图给出了SP在Transform并行训练上的应用，具体的原理可以查看原论文[7]。

![](https://picx.zhimg.com/v2-30b1dfa8d4feb973615920de0034aa47_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1726' height='920'></svg>)

## **3. Zero Redundancy Data Parallelism (ZeRO)**

训练过程中GPU内存开销主要包含以下几个方面：

* 模型状态内存（Model State Memory）：

+ 梯度
+ 模型参数
+ 优化器状态：当使用像Adam这样的优化器时，优化器的状态会成为GPU内存开销的大头。前面介绍的DP，TP， PP算法并没有考虑这个问题。

* 激活内存（Activation Memory）：在优化了模型状态内存之后，人们发现激活函数也会导致瓶颈。激活函数计算位于前向传播之中，用于支持后向传播。
* 碎片内存（Fragmented Memory）：深度学习模型的低效有时是由于内存碎片所导致的。在模型之中，每个张量的生命周期不同，由于不同张量寿命的变化而会导致一些内存碎片。由于这些碎片的存在，会导致即使有足够的可用内存，也会因为缺少连续内存而使得内存分配失败。ZeRO 根据张量的不同寿命主动管理内存，防止内存碎片。

ZeRO针对模型状态的三部分都做了对应的内存改进方法：

* ZeRO1：只划分优化器状态(optimizer states, os)，即![P_{os}](https://www.zhihu.com/equation?tex=P_%7Bos%7D)
* ZeRO2：划分优化器状态和梯度(gradient, g)，即![P_{os+g}](https://www.zhihu.com/equation?tex=P_%7Bos%2Bg%7D)
* ZeRO3：划分优化器状态和梯度和模型参数(parameters, p)，即![P_{os+g+p}](https://www.zhihu.com/equation?tex=P_%7Bos%2Bg%2Bp%7D)

下图给出了三种方法带来的内存开销收益

![](https://pic1.zhimg.com/v2-58035d8b766089601b679d799d5e0aad_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1488' height='934'></svg>)

不管采用三种方法的哪一种，ZeRO简单理解就是给定![N](https://www.zhihu.com/equation?tex=N)个设备，然后把一堆data等分到这些设备上，每个设备只存![1/N](https://www.zhihu.com/equation?tex=1%2FN)的数据量，并且每次也只负责更新这![1/N](https://www.zhihu.com/equation?tex=1%2FN)的数据。

因为对数据做了划分，ZeRO在每一层都需要有通信操作。我们考虑ZeRO在某一层的具体操作：

* 在forward的时候，会首先使用all-gather让每个设备拥有该层完整的模型权重，然后计算得到输出，最后每个设备会只保留原来的权重，即把all-gather过来的权重扔掉，这样可以节省开销。
* 在backward的时候，同样会先all-gather该层的所有权重，然后计算梯度，最后也会把梯度进行划分，每个设备上只会存1/N对应的梯度数据。

注意ZeRO对数据划分方式并没有什么具体的要求，可以是随意划分，因为最后反正会用all-gather使得所有设备商都有用完整的数据；当然，也可以使用前面提到的Tensor Parallelism的划分方式，这样一来可以有效降低通信开销，进一步提高效率。

> “ 关于ZeRO更详细的介绍可以查看原论文或者看看[这篇博客](https://link.zhihu.com/?target=https%3A//www.cnblogs.com/rossiXYZ/p/15782054.html) ”

未完待续。。。

### **微信公众号：AutoML机器学习**

![](https://pic1.zhimg.com/50/v2-87083e55cd41dbef83cc840c142df48a_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='0' height='0'></svg>)

**MARSGGBO♥原创**  
**如有意合作或学术讨论欢迎私戳联系~**  
**邮箱:marsggbo@foxmail.com**


---

## 大家能分享一下当前博士就业的情况吗？

`link: https://www.zhihu.com/question/559157484/answer/2734110170 · created: 1666937661`


近年来，博士毕业生的就业形势和过去相比变化其实挺大的。特别是在面临科研与就业、创业与大厂这些多重选择时，感觉每种选择好像都很不错，但是每种选择的缺点也有不少。不过根据我和几个博士同学现在的情况来看，博士毕业之后选择大厂或者研究所相对更加稳妥，我博士毕业之后去了新加坡，希望通过分享一些我的经历，可以和大家一起探讨各种不同选择的优劣势，并且我找了一个近期上线的企业招聘计划，和大家说说在选择企业时应该关注哪些方面。

**1. 继续科研**

博士期间，周围有些大佬是真的很爱学术。这样的大佬留在学术界继续搞科研和教学其实就很不错，可以专心探索自己感兴趣的领域。但实话实说，现在国内的学术圈竞争非常激烈，尤其是C9和985、211的学校，想要拿到一个稳定的教职，难度相当大。再加上晋升压力和科研经费的申请，我觉得除非是对科研很感兴趣，并且在博士和硕士期间已经有足够文章的加持，否则不是很建议选择学校。  
当然，我不否认普通院校或者大专会轻松很多，但问题在于，普通院校的项目申请和经费难度也非常大，而且待遇相对一般，只能说很“稳定”，而且我老家那边的大专院校招的老师只要是硕士以上就可以，博士毕业去这些地方，个人感觉性价比太低。  
相比之下，研究所其实是个不错的选择，我目前在新加坡的A\*STAR。选研究所主要看它的待遇和近些年的研发成果，如果和自己的方向比较吻合，而且不想过于卷的话，可以考虑国内和国外的研究所。

![](https://picx.zhimg.com/v2-c1ab8e90b892ac4f938f87ba157e54af_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='554' height='274'></svg>)

**2. 进入企业**

**（1）创业**  
①自己创业  
确实，自己创业听起来非常 “酷”，有一种开疆拓土的感觉。然而，其中蕴含的风险却不可小觑。刚毕业的博士们在自身学术领域方面确实可以算得上 “小牛”，如果将一些项目变成产品的话商业价值也不低。但毕竟刚从学校出来，很多同学对商业环境往往比较陌生。商业经验的匮乏是创业的第一大短板，毕竟学术和商业是不同的赛道，术业有专攻。而且当下的市场环境不确定性和资金压力都比较高，如果没有充足的资源储备和丰富的经验，自己创业这条路对多数刚毕业的博士而言性价比着实不高。当然，这只是从普遍情况来看，毕竟在各个领域都不乏奇才，但问题在于我们不一定是那个奇才哈哈~。  
②加入创业公司  
相比自己创业，加入创业公司可能相对好一些。在这里，博士们有机会参与到公司从无到有、从初具规模到发展壮大的过程，能够充分发挥自己的专业知识，将一些自己的想法融入到公司的产品里。但在我看来，创业公司本身就处于发展的不稳定阶段，它可能会面临资金链紧张、业务方向调整等问题。与成熟企业相比，它的资源相对有限，如果遇到瓶颈，反而会在一定程度上限制博士们进一步深入研究和发展的空间，同时也可能带来职业发展的不确定性。  
**（2）加入大厂**  
相比创业，加入大厂是一个相对稳妥的选择。大厂现在已经发展的比较成熟了，基础设施也很完善，可以支持各种研发项目的落地。而且，人工智能本身就是现在的热门，各个公司在资源上的倾斜和投入也会大很多。  
做人工智能和大模型的硕士和博士在很多大厂眼中都是“香饽饽”，提供的待遇和资源也更多。而且从我过去的实习情况来看，现在很多大厂的研发部门氛围其实非常像学校，和同事之间的关系也没有那么复杂，在大厂工作，大家在一起交流、激发灵感，共同解决问题，这种学习和成长的环境对个人发展非常有帮助，这对刚毕业的硕士和博士来说无疑是一个不错的平台。同时，大厂一般都有明确的职业发展通道，有很多不同的岗位选择和晋升机会。而且公司提供的培训和支持也很完善，可以帮助员工不断提升技能。

![](https://picx.zhimg.com/v2-e5f12ada4b9cbc8b1740cf5f5bd0191f_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='554' height='368'></svg>)

上面我对比了博士毕业后的几种选择，实际上每种选择都有优势和缺点，每种选择也都有适合的人，只不过对大多数应届生来说，我觉得进研究所和进大厂对博士来说性价比相对更高。  
最近我也在和进入大厂的几个朋友聊过这个问题，他们说现在大厂提供的人才计划非常多，不论是资源的倾斜还是工资待遇都很不错。但如果说针对AI大模型领域博士生的头部人才计划，目前了解到只有字节的Top Seed，我看完以后对这个计划还挺感兴趣。  
豆包现在的发展我觉得是国内大模型里面比较好的，不仅豆包 APP 的下载量在 AIGC 类应用中排名第一，而且截至 9 月，豆包语言模型的日均 tokens 处理量超过 1.3 万亿，相比 5 月1200 亿 的处理量猛增十倍。  
字节跳动对大模型非常重视，投入力度也很大。团队里有很多顶尖的人才，像TikTok产品技术负责人朱文佳、豆包大语言模型研究团队负责人王明轩以及Foundation团队负责人项亮等技术大牛都在其中，他们都是技术出身，相比从行政上来的领导会更加务实，而且聚焦的也都是最新的技术热点。前段时间我听说他们在做Transformer架构在语言模型中的优化，提升豆包在处理复杂语义和长文本理解方面的能力。这种对前沿技术的积极探索，能让团队始终站在行业技术发展的前沿。跟着这样的leader，也能对自己的技术能力和研究思路带来快速的提升。

![](https://pic1.zhimg.com/v2-54b7ddc58b60e5096f6beda2c4bb6aa6_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='554' height='678'></svg>)

我也和在字节工作的朋友了解了一下，有一位在字节算法优化相关的团队。他们当时主要解决的是一个原有算法效率太低的问题，他们从数据结构分析入手，重新设计了部分算法逻辑，最终使算法效率提升了 30%。新人就直接参与到重要项目实际工作中的情况，在字节很常见。我朋友刚进去的时候还不太适应，好的是带他的mentor不光带他熟悉业务，还辅助他一起解决了很多技术问题，一起讨论有价值的研究课题。最近，朋友组里也在招聘实习生，感兴趣的可以私信我。  
另外看到网上的信息，猜测Top Seed年薪大概在200左右，甚至更高。外加字节的期权，确实相当有吸引力，字节在17年开始每年有两次回购机会，而且字节期权回购价格一路飙升，已经从21年的126刀涨到了今年的180刀左右。单从三年总共43%左右的上涨幅度来看，这也已经比绝大多数我们能买到的金融产品强很多了。

![](https://picx.zhimg.com/v2-bc6f2cb2df119e1d75d185f8013d4900_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='554' height='243'></svg>)

除了字节以外，我看到阿里、腾讯和美团等几个头部的企业也都推出了一些人才计划，不过不是针对AI大模型方向的，身边在这几家公司的朋友比较少，就不展开分享了，大家感兴趣也可以去了解一下。  
最后还是那句话，每个人的情况不一样，大家还是要根据自己的实际情况，选择适合自己的道路。对研究本身感兴趣且不想太卷的话可以去研究所，如果希望既有资源做研究，也想看到技术成果落地，同时对高回报有需求，进大厂更合适些。


---

## 如何看待与评价AAAI2023第二轮审稿结果？

`link: https://www.zhihu.com/question/549071929/answer/2732065927 · created: 1666827851`


![](https://picx.zhimg.com/v2-69054686062cbd1114d96c025bb34964_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1170' height='2532'></svg>)

今年又将是腥风血雨，群嘲而至的AAAI

省流:

审稿人能看见其他审稿人名字

审稿人能看见meta审稿人名字

meta审稿人能看见其余审稿人名字

往年彼此之间都是匿名的，今年开诚布公

已经有作者联系到审稿人希望能提高分数了


---

## 新加坡都有哪些值得一去的城市？

`link: https://www.zhihu.com/question/559523252/answer/2719481502 · created: 1666018624`


新加坡这个国家太大了，下面包含很多附属国，够你逛了，比如

牛车水(中国城)

荷兰村

小印度


---

## 除了NAS，AutoML对深度学习模型优化还有了哪些贡献？

`link: https://www.zhihu.com/question/358840958/answer/2697082599 · created: 1664592396`


AutoML（Automated Machine Learning，自动机器学习）大火应该是从2016年谷歌的一篇NAS工作开始的，到今天AutoML也到了一个阶段性的成果收获季节了，因为陆续有这个方向的博士毕业了，下面总结了AutoML方向的博士毕业论文，仅供参考。

* [Efficient Neural Networks](https://link.zhihu.com/?target=https%3A//era.ed.ac.uk/bitstream/handle/1842/39326/TurnerJ_2022.pdf%3Fsequence%3D1%26isAllowed%3Dy)
* [Parallel and Distributed Methods for Autonomous Design of Artificial Neural Networks](https://link.zhihu.com/?target=https%3A//dspace.lib.uom.gr/bitstream/2159/27216/5/KyriakidesGeorgePhD2022.pdf)
* [Efficient neural architectures for edge devices Supervisors](https://link.zhihu.com/?target=https%3A//dare.uva.nl/search%3Fidentifier%3D03eff2c1-b5ab-4fc8-bfe6-046c0a92941b)
* [Evolving Deep Neural Network Architectures for Time Series Data](https://link.zhihu.com/?target=https%3A//ir.lib.uwo.ca/etd/8555/)
* [Automated Machine Learning Under Resource Constraints](https://link.zhihu.com/?target=https%3A//people.ece.cornell.edu/cy/_papers/chengrun_phd_thesis.pdf)
* [Towards Efficient Deep Neural Networks](https://link.zhihu.com/?target=https%3A//dx.doi.org/10.3929/ethz-b-000540498)
* [Automated Deep Learning: Principles and Practice](https://link.zhihu.com/?target=https%3A//tel.archives-ouvertes.fr/tel-03464519/document)
* [From Human-Designed Convolutional Neural Networks Towards Robust Neural Architecture Search](https://link.zhihu.com/?target=https%3A//dx.doi.org/%252010.5075/epfl-thesis-8035)
* [The Nonlinearity Coefficient - A Practical Guide to Neural Architecture Design](https://link.zhihu.com/?target=http%3A//reports-archive.adm.cs.cmu.edu/anon/anon/home/ftp/usr/ftp/2021/abstracts/21-110.html)
* [Efficient Neural Architecture Search for Automated Deep Learning](https://link.zhihu.com/?target=https%3A//oaktrust.library.tamu.edu/bitstream/handle/1969.1/193093/JIN-DISSERTATION-2021.pdf%3Fsequence%3D1%26isAllowed%3Dy)
* [Efficient and Generalizable Neural Architecture Search for Visual Recognition](https://link.zhihu.com/?target=https%3A//dukespace.lib.duke.edu/dspace/bitstream/handle/10161/23808/Cheng_duke_0066D_16412.pdf)
* [Relaxation and Optimization for Automated Learning of Neural Network Architectures](https://link.zhihu.com/?target=https%3A//escholarship.org/content/qt3wt239sm/qt3wt239sm.pdf)

> 资料参考自 [https://www.ml4aad.org/automl/literature-on-neural-architecture-search/](https://link.zhihu.com/?target=https%3A//www.ml4aad.org/automl/literature-on-neural-architecture-search/)


---

## LATEX排版表格太宽显示不全怎么办？左边还有空间，MDPI的模板？

`link: https://www.zhihu.com/question/471658198/answer/2695127042 · created: 1664452313`


```
\begin{sidewaystable}[!tbp]
    \caption{Example of SideWaysTable}
    \centering
    \begin{tabular}{c|c|c|c|c|c|c|c|c|c|c|c|c}
        \hline
        AAAAA & BBBB & CCCC & DDDD & EEEE & FFFF & GGGG & HHHH & IIII & JJJJ & KKKK & LLLL & MMMM \\
        AAAAA & BBBB & CCCC & DDDD & EEEE & FFFF & GGGG & HHHH & IIII & JJJJ & KKKK & LLLL & MMMM \\
        AAAAA & BBBB & CCCC & DDDD & EEEE & FFFF & GGGG & HHHH & IIII & JJJJ & KKKK & LLLL & MMMM \\
        \hline
    \end{tabular}
    \label{table3:sidewaystable_example}
\end{sidewaystable}
```

效果图如下：

![](https://pica.zhimg.com/v2-5cc18cd7971f3aed51072c0141901ab5_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='502' height='648'></svg>)


---

## Latex绘制表格内容太长如何解决？

`link: https://www.zhihu.com/question/429388452/answer/2694932510 · created: 1664442575`


```
\usepackage{longtable}


\begin{longtable}{l|c|c}
% \centering
\caption[Short Caption]{Full Caption Content.}
\label{table:longtable_example} \\

% 下面是表头
\hline Col1 & Col2 & Col3 \\  \hline 
\endfirsthead

% 下面数字3的意思是表格的列数
\multicolumn{3}{c}%
{{\bfseries \tablename\ \thetable{} -- continued from previous page}} \\
\hline Col1 & Col2 & Col3 \\  \hline  
% 注意这里把表头复制了一遍，因为在新的页面也会展示一下表头，不然表格不方便阅读
\endhead

\hline \multicolumn{3}{r}{{Continued on next page}} \\ \hline
\endfoot

\hline \hline
\endlastfoot

% 下面就是真正的表格数据了，注意不用再写表头了
d1 & d2 & d3 \\
d1 & d2 & d3 \\
d1 & d2 & d3 \\
d1 & d2 & d3 \\
d1 & d2 & d3 \\
d1 & d2 & d3 \\
d1 & d2 & d3 \\
d1 & d2 & d3 \\
d1 & d2 & d3 \\
d1 & d2 & d3 \\
d1 & d2 & d3 \\
d1 & d2 & d3 \\
d1 & d2 & d3 \\
d1 & d2 & d3 \\
d1 & d2 & d3 \\
d1 & d2 & d3 \\
d1 & d2 & d3 \\
d1 & d2 & d3 \\
d1 & d2 & d3 \\
d1 & d2 & d3 \\
d1 & d2 & d3 \\
d1 & d2 & d3 
\end{longtable}
```

效果如下图，可以看到表格被换分到了两页，当然如果你的表格特别特别长，也会默认划分到多个连续的页面

![](https://picx.zhimg.com/50/v2-212e409298c14e07c7a5a17fcd2cc371_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='379' height='754'></svg>)


---

## 武大华科西交哈工大和新加坡国立、南洋理工谁比较厉害？

`link: https://www.zhihu.com/question/550405496/answer/2650313678 · created: 1661741774`


华科>武大>新国立≈南洋理工

新加坡top2傻子才想去(真香

![](https://picx.zhimg.com/v2-02fdec8ba0f6b5d8e04e03da6053d663_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2276' height='1280'></svg>)

好家伙，没完没了了，还把西交和哈工大加进来。。。

![](https://pic1.zhimg.com/v2-e680528565cadf5059a21f27839d091d_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1280' height='2844'></svg>)


---

## 如何看待如今AI顶会审稿（如，某群明码标价审稿bid）？

`link: https://www.zhihu.com/question/548211913/answer/2628097632 · created: 1660560306`


假装互相bid，套取信息后直接举报

这招怎么样


---

## 如何评价中国国民对911喜闻乐见的态度？

`link: https://www.zhihu.com/question/28042919/answer/2603362773 · created: 1659334218`


![](https://picx.zhimg.com/v2-12427fdb35cbbf350896df829b28bfcc_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1440' height='1284'></svg>)


---

## 如何看待ICML2022的结果？

`link: https://www.zhihu.com/question/524486916/answer/2603144068 · created: 1659325842`


恭喜师弟 [@二猹树](https://www.zhihu.com/people/f97528ae4a73b5bf0504a7123453a37e) 喜提ICML，宣传文稿来一波，欢迎大家讨论关注。

ICML 2022 “Virtual Homogeneity Learning: Defending against Data Heterogeneity in Federated Learning” 提出了一种利用虚拟同构数据集来抵御联邦学习中的数据异构性的技术，显著地提高了联邦学习的泛化性能及收敛速度。

![](https://pic1.zhimg.com/v2-48018b6a247539b96d3a98b954499469_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1000' height='326'></svg>)

**摘要**

联邦学习可以实现对去中心化的数据收集和模型训练，已成为一种重要的模型训练并同时保护数据隐私的技术。在联邦学习场景中，大量客户端在不共享其私有数据的情况下协作更新机器学习模型。

在联邦学习中，模型性能通常会受到数据异构性而引起的客户端漂移的影响，主流工作侧重于纠正客户端漂移。 我们提出了一种名为虚拟同构性学习（VHL）的不同方法来直接“纠正”数据异构性。 VHL 使用虚拟同构数据集进行联邦学习，该数据集旨在满足两个条件：完全不包含任何隐私信息并且是可分的。虚拟数据集可以从客户端共享的纯噪声中生成，旨在校准来自异构客户端的特征。 理论上，我们证明了 VHL 可以在原数据分布上实现可保证的泛化性能。 实验上，我们验证了 VHL 赋予联邦学习显著提高的收敛速度和泛化性能。 VHL 是首次尝试使用虚拟数据集来解决数据异构性问题的工作，为联邦学习提供了新的有效工具。

**背景与挑战**

联邦学习面临着来自不同客户端的non-IID数据分布以及其计算和通信能力的多样性带来的异构挑战。严重的数据异构性很容易导致客户端漂移，导致不稳定的收敛和较差的模型性能。

为了解决计算以及通信异构性问题，第一个联邦学习算法FedAvg，提出在训练期间进行更多的局部计算和更少的通信。虽然FedAvg解决了计算和通信的异构性问题，但non-IID数据分布（数据异构性）引起的客户端漂移对FedAvg有显著的负面影响。为了解决客户端漂移问题，许多工作都致力于设计新的学习范式，例如在客户端的本地训练策略，或是在服务器端的模型聚合策略。然而，最近的一项基准测试工作表明，FedAvg在许多实验环境中都优于其变体。这表明，单一方法在多个场景中解决客户端漂移问题具有挑战性。因此，解决客户漂移仍然是联邦学习的一个基本挑战。

另一个令人振奋的方向是直接“纠正”客户端漂移的原因，即数据异构性。具体来说，共享一小部分私有数据或私有统计信息可以使位于不同客户端的数据异构性降低。然而，数据共享方法使联邦学习面临隐私泄露的危险。虽然差分隐私是避免隐私泄漏的一个竞争候选方案，但使用差分隐私可能会导致性能下降。所有这些挑战激发了一个基本问题：“通过共享完全不包含私有信息的数据，可以克服联邦学习系统中的数据异构挑战吗？”

在这项工作中，我们提出了一种新的方法，称为虚拟同构性学习（VHL），为这个问题提供了肯定的答案。VHL通过在所有客户端之间共享一个独立于私有数据集的虚拟同构数据集，为每个客户端矫正私有数据的异构性。

**方法**

VHL的关键挑战是如何生成虚拟数据集以提高模型性能。通常来说，将不同分布的新数据集与原始数据相结合可能会在不同方面牺牲泛化性能，例如分布漂移，带噪标签，和垃圾数据等问题。在实践中，从自然数据中采样数据以构建虚拟数据集是一个重要挑战。因此，引入来自不同分布的大量虚拟数据将导致训练分布不同于测试分布，即分布漂移，导致测试集的泛化性能较差。因此，分布漂移是引入虚拟数据集的一个关键不利影响。

幸运的是，我们可以访问有标签的虚拟数据集（即源域）和自然数据集（即目标域），因此我们可以通过域适应（DA）来缓解分布漂移。具体地说，我们可以匹配源域和目标域的条件分布。我们的理论分析表明，匹配基于标签信息的虚拟分布和自然分布可以实现可保证的泛化性能。这一匹配可以通过将同一类中的自然和虚拟数据特征拉到一起来实现，如图1所示。

![](https://pica.zhimg.com/v2-d994b99159cc0837a447eb70ccf55462_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1383' height='554'></svg>)

图1 不同客户端的特征分布。圆形和三角形分别表示客户端A和B上的数据。由虚线圆框包围的点表示虚拟数据。不同的颜色代表不同标签的数据。经过本地训练后，同一标签在不同客户端上的私有自然数据的特征相距较远，但同一标签的共享虚拟数据的特征相距较近（左图）。

图2显示了训练后特征分布的T-SNE可视化。这些数据表明，同一类的私有数据在客户端之间具有不同的特征分布。但同一类的共享噪声数据在客户端之间具有相似的特征分布。

![](https://picx.zhimg.com/v2-fbd79ee9a0cb0a2ea3c3c1a9b3b74830_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1774' height='591'></svg>)

图2 使用FedAvg训练的3个不同客户端模型上的数据特征的t-SNE可视化。不同的颜色代表不同的数据类别，不同的形状代表不同的客户端，虚线圆圈表示虚拟数据。Naive VHL意味着使用私有自然数据和共享虚拟数据进行训练，而不进行特征校准。

基于这种现象，我们建议将同一标签的样本拉到一起，以便减少私有数据的特征漂移。在这里，我们给虚拟数据分配与私有数据相同的伪标签，使得虚拟标签与自然标签有一对一的映射，以便于进行特征校准。在具体实现中，我们只需要在虚拟特征与其相应的自然特征之间添加一个新的距离损失。与FedAvg相比，我们只需对噪声数据进行额外采样，并添加新的损失计算。因此，VHL可以与其他联邦学习算法无缝结合。

**实验结果**

为了证明VHL的有效性，我们在广泛使用的联邦学习模拟数据集上进行了实验，并测试了不同数量的客户端、不同的non-IID程度、不同的本地更新轮次。我们在四个数据集上将VHL应用于几种流行的FL算法，包括FedAvg、FedProx、SCAFFOLD和FedNova。实验结果表明，VHL可以提高泛化能力和收敛速度。对于大多数实验，VHL可以获得最佳泛化性能和以最少的目标通信轮来获得目标精度。

![](https://picx.zhimg.com/v2-aa04ed8f5906431ddf44db6d0ea9daba_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='731' height='890'></svg>)![](https://picx.zhimg.com/v2-be2bf66396fc0d73bb88532e62c93f8b_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='726' height='906'></svg>)

另外，我们验证了不同消融算法和超参数对VHL的影响。第一种算法是虚拟特征转移学习（VFTL）。在该算法中，服务器将在噪声数据集上预训练全局模型，之后正常执行联邦学习算法。该算法没有表现出任何明显的改进，表明噪声预训练对联邦学习没有好处。第二种算法被命名为Naive VHL，其中，联邦学习同时对私有数据和噪声数据进行学习但不进行特征校准。有趣的是，结果表明，Naive VHL也可以改善训练，尽管其性能不如VHL。这一有趣的现象将激发更多的研究工作。第三种是虚拟特征对齐。它仅基于一些随机特征校准私有特征。这个简单的算法还改进了联邦学习。这表明了客户端之间相同标签的一致表示的重要性。我们还修改了VHL的不同超参数以进行敏感性测试。结果表明，VHL对这些因素不敏感

![](https://picx.zhimg.com/v2-42f01384569495c0e321a606cc531cc4_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='588' height='896'></svg>)

**总结与展望**

在本文中，我们发现联邦学习可以显著受益于不包含隐私信息的虚拟数据集，从而从虚拟数据的角度缓解了数据异构性。通过基于同质虚拟数据的异构特征校准，联邦学习可以显著提高性能，减少客户端漂移。我们的贡献不仅在于改进了联邦学习中的模型性能，而且带给人们对联邦学习更多的认识以及许多有趣的实验现象。我们希望未来的工作能够发掘更多关于VHL的理论与新算法，并利用它来增强联邦学习或其他机器学习任务。

更多的文章细节请阅读我们的文章，十分感谢大家。

**资源**

论文链接：[https://arxiv.org/abs/2206.02465](https://link.zhihu.com/?target=https%3A//arxiv.org/abs/2206.02465)

代码链接：[https://github.com/wizard1203/VHL](https://link.zhihu.com/?target=https%3A//github.com/wizard1203/VHL)


---

## 机器学习之高斯过程回归的原理是什么？

`link: https://www.zhihu.com/question/529465541/answer/2600313072 · created: 1659162398`


> 本回答是转载自网上已有的博文，目前搜索到的最早的出处应该是这篇[浅谈高斯过程回归 - 加拿大小哥哥 - 博客园](https://link.zhihu.com/?target=https%3A//www.cnblogs.com/hxsyl/p/5229746.html)，但是原链接图片都失效了，转载过来仅供参考，以下是正文。  
>  网上讲高斯过程回归的文章很少，且往往从高斯过程讲起，我比较不以为然：高斯过程回归（GPR）， 终究是个离散的事情，用连续的高斯过程( GP) 来阐述，简直是杀鸡用牛刀。所以我们这次直接从离散的问题搞起，然后把高斯过程逆推出来。 这篇博客有两个彩蛋，一个是揭示了高斯过程回归和Ridge回归的联系，另一个是介绍了贝叶斯优化具体是怎么搞的。后者其实值得单独写一篇博客，我在这里就是做一个简单介绍好了，但没准就不写了，想想就累。

## **高斯过程回归 的 Intuition**

![](https://picx.zhimg.com/v2-cf98cb297fabf6578440c8280ceb546b_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='843' height='536'></svg>)

　　假设有一个未知的函数f : R–> R ，

　　在训练集中，我们有3个点 x\_1, x\_2, x\_3, 以及这3个点对应的结果，f1,f2,f3. (如图) 这三个返回值可以有噪声，也可以没有。我们先假设没有。

　　so far so good. 没什么惊讶的事情。

　　高斯过程回归的关键假设是：

> 给定 一些 X 的值，我们对 Y 建模，并假设 对应的这些 Y 值 服从 联合正态分布！

（更正式的定义后面会说到）

　　换言之，对于上面的例子，我们的假设是：

![](https://picx.zhimg.com/v2-d0ef1e8f65f0f3e09be81d4da214297e_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1024' height='202'></svg>)

　　一般来说，这个联合正态分布的均值向量不用操心，假设成0 就蛮好。（讲到后面你就知道为什么了）

　　所以关键是，这个模型的 协方差矩阵K 从哪儿来。

　　为了解答这个问题，我们进行了另一个重要假设：

　　如果两个x 比较相似（eg, 离得比较近），那么对应的y值的相关性也就较高。换言之，协方差矩阵是 X 的函数。（而不是y的函数）

　　具体而言，对于上面的例子，由于x3和x2离得比较近，所以我们假设 f3和f2 的correlation 要比 f3和f1的correlation 高。

　　话句话说，我们可以假设协方差矩阵的每个元素为对应的两个x值的一个相似性度量：

![](https://pic1.zhimg.com/v2-423b23763476b3e1d75a070cf399d771_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1024' height='364'></svg>)
> 那么问题来了，这个相似性怎么算？如何保证这个相似性度量所产生的矩阵是一个合法的协方差矩阵？   
> 好，现在不要往下看了，你自己想3分钟。你也能想出来的。 提示：合法的协方差矩阵就是 (symmetric) Positive Semi-definite Matrix （。。。。。。。。。。。。思考中） 好了时间到。

　　答案： Kernel functions !

　　矩阵A正定是指,对任意的X≠0恒有X^TAX＞0。 　　矩阵A半正定是指,对任意的X≠0恒有X^TAX≥0。

　　判定A是半正定矩阵的充要条件是：A的所有顺序主子式大于或等于零。

　　如果你了解SVM的话，就会接触过一个著名的Mercer Theorem，（当然如果你了解泛函分析的话也会接触过 ），这个M定理是在说：一个矩阵是Positive Semi-definite Matrix当且仅当该矩阵是一个Mercer Kernel .

　　所以我们在svm里用过的任何Kernel都能拿过来用！

　　举个栗子，在高斯过程回归里，一种非常常见的Kernel就是SVM里面著名的高斯核（但是为了让命名不是那么混淆，文献中一般把这个Kernel称作 squared exponential kernel.

　　具体而言就是

![](https://picx.zhimg.com/v2-84c91180dc314f95fd6a036da2a9ecd4_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1024' height='652'></svg>)

## **回归分析**

　　好了，现在可以做回归分析了：

　　如果我们现在又有了一个新的点 x\*

　　这个新的点对应的f\* 怎么求？（如下图）

![](https://picx.zhimg.com/v2-6259e5bc8d72f82f16f9f65301aa90d2_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='806' height='515'></svg>)
> 根据假设，我们假设 f\* 和 训练集里的 f1, f2, f3 同属于一个 （4维的）联合正态分布！

也就是说，不仅 f1,f2,f3属于 一个3 维的联合正态分布（参数可以算出来），而且 f\* 和 f1,f2,f3属于（另一个）4维的联合正态分布，用数学的语言来表达就是：

![](https://pic1.zhimg.com/v2-f4514359ebaaa9d0db1191453d972ce1_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1024' height='564'></svg>)

　　首先我们来看一看，这个4 x 4 的 矩阵能不能算出来：

黄色的大K，是依据训练集的3维联合分布算出来的，绿色的K\*, 是测试点x\* 分别和每一个训练集的x 求出来的。所以整个联合分布我们都知道了。

　　接下来的事情就好办了，我们既然已经知道（f,f\*)的联合分布P(f, f\*)的所有参数, 如何求p(f\*) ？好消息是这个联合分布是正态的，我们直接用公式就能搞出来下面的结果（using the marginalization property）：

　　不难求出f\* 隶属于一个1维的正态分布， 参数是：

![](https://picx.zhimg.com/v2-7e38e2c7e64e89fa8a159b9118610749_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1024' height='416'></svg>)

　　所以这是一种贝叶斯方法，和OLS回归不同，这个方法给出了预测值所隶属的整个（后验）概率分布的。再强调一下，我们得到的是f\* 的整个分布！不是一个点估计，而是整个分布啊同志们。

> In addition, 不仅可以得到 f\*这一个点的分布，我们对这个未知的 函数 也可以进行推断！换言之，如果把一个函数想成一个变量，那么高斯过程回归可以求出这个函数的分布来。(distribution over functions)不幸的是，我们的计算机只能存储离散的数据，怎么表示一个连续的函数呢？

　　好办，我们对一个区间里面均匀地硬造出来1万个测试点x\*, 然后求出这些测试点和训练集所对应的y（一个巨高维的向量）的联合分布，然后在这个巨高维的联合分布里采样一次，就得到了函数的（近似的）一个样本。

![](https://pica.zhimg.com/v2-59bf584cb249cb70036711fd2f2dabe6_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1024' height='723'></svg>)

　　比如训练集就三个点，测试集1万个x，图中的每一个红点就分别是这些点f\* 的均值，（当点很多的时候，就可以假设是一个“连续”的函数了）而蓝色的线代表一个或两个标准差的bound.

　　我们如果从这个分布中采样10次，就可以得到10个巨高维的向量，也就是从这个后验概率中sample出来的10个函数的sample. plot出来长这个样子：

![](https://picx.zhimg.com/50/v2-801165c5a3950b1afee1d40d50505c47_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='379' height='309'></svg>)

　　含有已知数据（训练集）的地方，这些函数都离的很近（variance很低），没有数据的时候，这个spread就比较大。

　　也许你会问：我为毛要搞出来函数的分布？我为毛要关心这个variance. 在很多问题中，我们不仅仅需要知道预测值的点估计，而且要知道这个估计有多少信心在里面（这也是贝叶斯方法的好处之一）

> 举个例子：Multiple Bandit Problem假设 我们已经有了几个油井，每个油井的价值不一样，我们在这个二维平面上，利用高斯过程回归，对每一个地理位置估计一个该位置对应的出油量。而开发每一口井是有成本的，在预算有限的情况下，如果想尽可能少地花钱，我们就需要定义一个效益函数，同高斯过程回归的预测结果相结合，来指导我们下一次在哪儿打井。这个效益函数往往是 预测值 和 方差 的一个函数。以上这个例子，就是高斯过程回归在贝叶斯优化中的一个典型应用。有时间专门写一篇。  
>  高斯过程 好了，现在终于可以讲一讲高斯过程了。 高斯过程是在函数上的正态分布。（Gaussian distribution over functions)具体而言就是

![](https://pica.zhimg.com/v2-335fb8407e94db9a7d647949a9f13590_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1024' height='384'></svg>)

　　我们具体用的时候，模型假设是酱紫的：

　　我们观察到一个训练集 D

![](https://picx.zhimg.com/v2-fee5e3f03dfde2ce9a50372cf5ff5558_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1024' height='386'></svg>)

　　给定一个测试集 X\* （ X\* 是一个 N\* x D 的矩阵， D是每一个点的维度）我们希望得到 一个 N\* 维的预测向量 f\*. 高斯过程回归的模型假设是

![](https://picx.zhimg.com/v2-8cea79bfd6e16cb1560f403b8c6156f4_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1024' height='511'></svg>)

　　然后根据贝叶斯回归的方法，我们可以求出来 f\*的后验概率：

![](https://picx.zhimg.com/v2-27d23d8a600cd882866ba0bce6ba5efc_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1024' height='349'></svg>)

　　This is it. 要啥有啥了。

## **有噪声的高斯过程**

　　下面着重说一下有噪声情况下的结果，以及此情况下和Ridge Regression的神秘联系。

当观测点有噪声时候，即， y = f(x) + noise, where noise ~N(0, sigma^2)

我们有

![](https://picx.zhimg.com/v2-b2819585a2c43b46fe3a46f8a53d5aeb_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1024' height='493'></svg>)

　　发现没，唯一区别就是 K 变成 了 Ky，也就是多加了一个sigma。

　　这个很像是一种regularization. 确实如此。

* 好了，下面就说说这个 GPR的 insight，这个模型到底想干什么

　　如果只有一个测试点，那么输出的f\* 就是隶属于一个1维的正态分布了，具体而言：

![](https://picx.zhimg.com/v2-909b09b2d60ec50580eac68035673137_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1024' height='475'></svg>)

　　再看，我们回想一下Ridge Regression （*小编注：下图argmax应为argmin*）

![](https://pic1.zhimg.com/v2-04113df3485c0b585a3e5f26e6358768_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1620' height='564'></svg>)

　　我们仔细观察一下上面那个蓝色的框框

![](https://pic1.zhimg.com/v2-9cf108ff11df202432bd2ead0712afbb_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1024' height='423'></svg>)

　　所以说，ridge回归是一种最最最最简单的高斯过程回归，核函数就是简单的点积！

而高斯过程的核函数可以有很多，除了上面提到的squared exponential, 有整整一本书都在讲各种kernel和对应的随机过程

　　所以高斯过程是一个非常包罗万象的根基，类似于小无相功。

　　高斯过程回归(GPR)和贝叶斯线性回归类似，区别在于高斯过程回归中用核函数代替了贝叶斯线性回归中的基函数（其实也是核函数，线性核）。

　　来看看多维高斯分布的一些重要性质，第一个性质为两个相互独立的多维高斯分布A和B的和也是一个多维高斯分布C，且C的均值和方差都为A和B均值方差的和。第二个性质为：两个多维高斯分布之和构成的分布C而言，在已知一部分观察值C1的条件下，另一部分观察值C2的概率分布是一个多维高斯分布，且可以用A和B中对应的信息来表示。

如下：

![](https://picx.zhimg.com/v2-457bbb3dd2c46358cda0e8ba1f121898_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='440' height='149'></svg>)

　　由贝叶斯线性回归和高斯过程回归的对比可知，贝叶斯线性回归是高斯过程回归中的一个子集，只是它用的是线性核而已，通过两者的公式就可以看出它们之间的关系：

![](https://pic1.zhimg.com/50/v2-68ee305f1cff737a9df80cc1af046336_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='182' height='101'></svg>)

　　上面是贝叶斯线性回归，下面是高斯过程回归。

**简单例子：**

　　假设现在已经观察到了6个样本点，x为样本点特征（一维的），y为样本输出值。现在新来了一个样本点，要求是用高斯回归过程来预测新来样本点的输出值。这些样本点显示如下;

![](https://pic1.zhimg.com/v2-4f3e98885a08a9b5577a32904ea80724_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='429' height='328'></svg>)

　　其中前面6个点是已知输出值的训练样本，其值为：

![](https://pic1.zhimg.com/50/v2-6ca16df95c17152514a74e9a05d96662_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='378' height='28'></svg>)

　　第7个点是需要预测的样本，红色的垂直条形线表示观察输出值的误差，绿色的垂直条形线为用高斯过程回归的误差。

　　用GPR解该问题的流程大概如下（对应前面讲的一些基础知识）：

　　1. 选择适当的u（均值函数）和k（核函数），以及噪声变量σ，其中核函数的选择尤其重要，因为它体现了需处理问题的先验知识，应根据不同的应用而选择不同的核。

　　2. 计算出训练样本的核矩阵（6\*6），如下：

![](https://picx.zhimg.com/50/v2-389a510368fe0ac77f8c10961927fd57_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='331' height='135'></svg>)

　　3. 计算需预测的点

![](https://picx.zhimg.com/50/v2-5b3d5128ac97c5edb32f6cc78b191c1a_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='77' height='23'></svg>)

与训练样本6个点的核值向量，如下：

![](https://picx.zhimg.com/50/v2-316e96b7f125982c89a56f5570a4fab6_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='388' height='39'></svg>)

　　4. 自己和自己的核值为

![](https://pic1.zhimg.com/50/v2-a70d0ee2d44a00e6da8afc535fe3491c_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='103' height='29'></svg>)

且此时整个样本的多维高斯分布表达式为：

![](https://picx.zhimg.com/50/v2-a3b99c0dcd8197766a023a2a6579aa23_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='247' height='65'></svg>)

　　5. 通过前面m和D的公式，求得m=0.95，D=0.21.

　　6. 画出最终结果如下：

![](https://picx.zhimg.com/50/v2-62ac084e6c0986eb432b221254e732b9_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='386' height='268'></svg>)

　　这个例子来源于论文Gaussian Processes for Regression A Quick Introduction中，它的核函数等参数选择和基础知识部分的不同，但这里主要是对GPR的应用有个简单的宏观上的理解，让大脑对GPR应用有个初步的印象，否则有了那么多的公式推导但不会应用又有什么用呢？

[http://www.cnblogs.com/tornadomeet/archive/2013/06/14/3135380.html](https://link.zhihu.com/?target=http%3A//www.cnblogs.com/tornadomeet/archive/2013/06/14/3135380.html)

[http://dataunion.org/17089.html](https://link.zhihu.com/?target=http%3A//dataunion.org/17089.html)

[http://www.cnblogs.com/tornadomeet/archive/2013/06/15/3137239.html](https://link.zhihu.com/?target=http%3A//www.cnblogs.com/tornadomeet/archive/2013/06/15/3137239.html)


---

## 为什么远程控制Ubuntu服务器里的jupyter notebook始终打不开网页？

`link: https://www.zhihu.com/question/418317875/answer/2596736853 · created: 1658981703`


## **背景**

Slurm集群一般是由一个主节点（master）和各个带有GPU资源的子节点组成的，每次要想使用GPU需要通过主节点跳转到子节点。那么如果我们想使用jupyter使用子节点的GPU应该怎么做呢？

我有试过连接子节点后直接运行`jupyter`命令，然后再本地电脑上打开`127.0.0.1:8888/token?=***`，但是总是失败。其实，原因是因为我们本地电脑监听的是master节点的端口，并不能监听到子节点的端口，所以我们还需要将本地电脑和子节点的端口做映射之后才可访问jupyter。废话不多说，直接看如下教程：

## **方法**

1. 新建一个终端连接集群中的某个节点,假设节点名是`v100`

假设你已经远程连接到你的集群的master节点，然后执行以下命令进入某个指定的带有GPU资源的节点

```
srun -N 1 -p v100 -t 1440 --pty "bash";
```

* `-p v100`表示连接名为`v100`的节点
* `-t 1440`表示1440分钟，1440=24\*60，即一天
* `--pty "bash"`表示进入交互界面

1. 查看节点IP

```
cat /etc/hosts
```

运行上述命令后会打印出主节点和所有子节点的IP，输出大概长这样

```
127.0.0.1               localhost.localdomain localhost localhost4.localdomain4 localhost4
::1                     localhost.localdomain localhost localhost6.localdomain6 localhost6
10.31.29.16           psgcluster.cm.cluster ** master.cm.cluster master localmaster.cm.cluster localmaster

10.31.11.21    wwmaster        wwmaster.psg.**.zone
10.10.0.1       hydra

# PSG Cluster
10.31.225.88    v99
10.31.225.89    v100
```

在这个例子中我们需要找到`v100`节点的ip，可以看到是`10.31.225.89`。记住这个IP，后面会用到。

1. 运行jupyter-lab

第一步运行后会进入`v100`节点，之后我们需要运行jupyter环境,指定一下端口号，这里以8889为例，你也可以设置其他端口

```
jupyter-lab --port 8889

...
 LabApp] JupyterLab application directory is /datasets/xihe/miniconda3/envs/hyperbox/share/jupyter/lab
[I 2022-07-27 20:49:19.295 ServerApp] jupyterlab | extension was successfully loaded.
[I 2022-07-27 20:49:19.296 ServerApp] Serving notebooks from local directory: /home/xihe
[I 2022-07-27 20:49:19.296 ServerApp] Jupyter Server 1.11.0 is running at:
[I 2022-07-27 20:49:19.296 ServerApp] http://cluster:8889/lab?token=0be46135c38dfaa32e6c9257d00cbcb1d19ec3cc5d93f548
[I 2022-07-27 20:49:19.296 ServerApp]  or http://127.0.0.1:8889/lab?token=0be46135c38dfaa32e6c9257d00cbcb1d19ec3cc5d93f548
```

1. 实现本地和子节点的端口映射

创建一个新的终端，使用ssh命令进行映射

```
ssh -L8889:10.31.225.89:8889 username@cluster.**.com
```

这样就完成了本地电脑和`v100`子节点在8889端口的映射，此时你在打开第3步输出的ip地址就可以访问jupyter啦，即`http://127.0.0.1:8889/lab?token=0be46135c38dfaa32e6c9257d00cbcb1d19ec3cc5d93f548`

### **微信公众号：AutoML机器学习**

**![](https://picx.zhimg.com/50/v2-87083e55cd41dbef83cc840c142df48a_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='0' height='0'></svg>)**

**MARSGGBO♥原创**  
**如有意合作或学术讨论欢迎私戳联系~**  
**邮箱:marsggbo@foxmail.com**   
**2022-06-27 13:59:51**


---

## 如何看待香港城市大学(CityU)发布改名意见调查？如果改名，推荐改成什么比较好呢？

`link: https://www.zhihu.com/question/486600499/answer/2586049618 · created: 1658400987`


可以考虑城市大学和浸会大学合并成香港九龙大学(Hong Kong Kowloon University, HKKU)

城市大学校区命名为 香港九龙大学九龙塘校区

浸会大学校区命名为 香港九龙大学狮子山校区

城大和浸大都有光明的未来

![](https://picx.zhimg.com/v2-656d98b28fb1b0175bf08e5274f3cfc7_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2276' height='1280'></svg>)


---

## 如何看待邵阳学院送 20 多名教师到菲律宾亚当森大学读哲学博士，毕业后再以每人 80 多万费用引进？

`link: https://www.zhihu.com/question/543739791/answer/2580587439 · created: 1658132219`


没想到邵阳学院引起了大新闻，高中的时候经常出现在班主任嘴里:“平时不努力，高考后就只能到邵阳学院去”

我还听闻有的学校会安排已入职的老师公派出去拿个博士学位，有的去了印度尼西亚，菲律宾。总之，又一大波钱被浪费了

![](https://picx.zhimg.com/50/v2-608c536f09054282bb01ad2148064a3f_720w.gif?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'></svg>)


---

## 如何看待与评价ECCV2022的审稿结果？

`link: https://www.zhihu.com/question/516128811/answer/2576479219 · created: 1657894295`


最近我们的工作“EAGAN: Efficient Two-stage Evolutionary Architecture Search for GAN”被ECCV2022主会录取。本文提出了一个高效的由两阶段组成的基于进化算法的神经架构搜索（Neural Architecture Search，NAS）框架，用于搜索生成对抗网络（Generative Adversarial Network, GAN）的结构，有效解决了在搜索GAN的过程中的训练不稳定问题。

![](https://pic1.zhimg.com/v2-618b46c67d69dae063462bb08bc4ce2f_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1500' height='499'></svg>)

ECCV的全称是European Conference on Computer Vision(欧洲计算机视觉国际会议) ，两年一次，是计算机视觉三大会议（另外两个是[ICCV](https://link.zhihu.com/?target=https%3A//baike.baidu.com/item/ICCV%2522%2520%255Ct%2520%2522_blank)和[CVPR](https://link.zhihu.com/?target=https%3A//baike.baidu.com/item/CVPR%2522%2520%255Ct%2520%2522_blank)）之一。ECCV2022将于2022年10月23日至27日在以色列特拉维夫国际会展中心举行，会议共收到有效投稿5,803篇，接收1650篇论文，接受率在28%左右。

## **1. 摘要**

生成性对抗网络（GAN）在图像生成任务中已被证明是成功的。然而，GAN训练本身是不稳定的。尽管许多工作试图通过手动修改GAN架构来稳定它，但这需要很多专业知识。神经结构搜索（NAS）已成为自动搜索GAN的一个有吸引力的解决方案。早期的NAS-GAN只搜索生成器以降低搜索复杂度，但会导致次优GAN。最近的一些工作试图同时搜索生成器（G）和鉴别器（D），但它们受到GAN训练的不稳定性的影响。为了缓解这种不稳定性，我们提出了一种高效的基于两阶段进化算法的NAS框架来搜索GAN，即EAGAN。我们将G和D的搜索解耦为两个阶段，其中第1阶段使用固定D搜索G并采用多对一训练策略，第2阶段使用在第1阶段中找到的最优G搜索D并采用一对一训练和权重重置策略以增强GAN训练的稳定性。这两个阶段都使用非支配排序方法在多个目标（例如模型大小、初始分数（IS）和初始距离（FID））下生成帕累托前沿结构。EAGAN应用于无条件图像生成任务，可以在1.2 GPU天内高效地完成对CIFAR-10数据集的搜索。我们搜索的GAN在CIFAR-10数据集上获得了有竞争力的结果（IS=8.81±0.10，FID=9.91），并超过了STL-10数据集上先前的NAS GAN（IS=10.44±0.087，FID=22.18）。

**2. 难点**

NAS在图像分类任务上已经取得了非常不错的成绩了，用NAS搜到的模型能取得比人工设计的模型还要高的分类准确率。鉴于NAS的成功，有工作也尝试将NAS去搜索GAN模型结构。下表总结了现有的NAS-GAN工作。

我们知道GAN是由一个生成器（Generator, 简称G）和一个判别器（Discriminator,简称D）组成的。GAN的训练原理简单理解就是G和D这两个网络之间做零和博弈的优化，理想状态是最终达到纳什均衡。而这一过程并非易事，GAN本身的训练就是很容易崩溃的，经常会出现模式崩塌以及梯度消失等问题。一旦再使用NAS去搜索GAN，这一不稳定问题就更加严重了。而为了缓解不稳定问题，现有的很多NAS-GAN工作都只是去搜索G网络，而把D网络固定住。后续的一些工作尝试了去搜索G和D，但是他们仍遇到了一些问题，例如AdversarialNAS和AlphaGAN是将G和D耦合在一起同时进行搜索，AlphaGAN的实验结果表明这样的耦合搜索方式会加剧差的判别器结构对搜索过程造成的负面影响，即使得搜索过程不稳定。

另外，由下表也可以看到大多数的NAS-GAN在搜索过程中都只使用了单个的指标，而目前而言何种指标能最好的表示GAN模型性能还没有共识，这也是为什么有很多不同的指标被提出，例如Inception Score (IS)、Fr´echet Inception Distance (FID)等等。因此，单个指标并不能有效地衡量一个GAN模型的好坏。基于梯度的NAS-GAN为了保证搜索过程是可导的，倾向于选择loss作为优化指标；基于强化学习(Reinforcement Learning, RL)的工作只有E2GAN使用IS和FID的线性加权求和作为评价指标，但是两个指标需要额外引入权重超参，增加了训练难度；进化算法(Evolutionary Algorithm, EA)非常适合多目标下的搜索任务，但是现有的基于进化算法的NAS-GAN为了节省时间开销，都只使用了单个指标，其中COEGAN为G和D网络使用了不同的指标。

综上，我们主要想解决以下两个问题：

1. 解决GAN搜索过程中的不稳定性问题
2. 满足多目标搜索GAN，并提高搜索效率

![](https://picx.zhimg.com/v2-7ae635b5fe3f0af2cc228b99d1791db6_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='964' height='466'></svg>)

## **3. 方案**

### 3.1 搜索空间

为和之前的工作做一个公平对比，我们使用了AdversarialNAS相似的搜索空间，如下图所示

![](https://picx.zhimg.com/v2-aeb268efdd7124904f88d1da7cf6e30f_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1107' height='648'></svg>)

### 3.2 解决GAN搜索不稳定性问题

正如前面介绍的，AlphaGAN和AdversarialNAS是将生成器（G）和判别器（D）的结构进行耦合搜索的，那么很自然的想法是将二者解耦。下图是我们的方法的示意图：

![](https://picx.zhimg.com/v2-6f0b2a6c546d9cfcda35650cf75838d0_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1452' height='657'></svg>)

我们将G和D的搜索划分成两个独立的阶段：

在第一阶段我们固定判别器，然后执行多轮的生成器搜索。如上图（左）所示，每一轮我们会生成P个不同的生成器，这些生成器彼此之间共享权重，即他们都是一个生成器超网（Supernet-G）的子网。每次我们会从P个生成器中随机采样一个，然后将被采样的生成器和固定的判别器匹配进行训练，这种训练方式称为 many-to-one。这样带来的好处是，判别器与多个生成器匹配训练，某种程度上可以理解成是集成训练（ensemble training），这可以有效避免判别器过强导致梯度消失。

在第二阶段，我们设计了one-to-one的训练策略。之所以没有采用第一阶段中的many-to-one训练策略是因为对判别器性能的评估比较特殊。具体而言，我们在评估GAN的性能的好坏时，其实是评估生成器的好坏。换言之，判别器作为一个分类器，他取得或高或低的准确率都不能代表GAN的好坏。所以，一种可行的方式是我们使用生成器的好坏来间接评估判别器。很显然，如果使用many-to-one的训练策略，那么所有判别器都是和同一个生成器匹配，那么得到的性能评估是一样的，所以我们做了改进，提出了one-to-one的训练策略，这样一来每个判别器都匹配了一个独立的生成器，这些生成器采用的结构都是第一阶段搜索得到的最好的生成器的结构。

不过第二阶段的one-to-one训练策略仍然存在一个问题，即每一轮训练结束后，P个不同的生成器虽然结构相同，但是权重不一样了。当进入到下一轮对判别器的搜索时，上一轮表现差的生成器可能依旧表现差，但是这不一定是新生成的判别器导致的，因为也有可能是其已经发生了模式崩塌。换言之，one-to-one训练策略可能会导致不同判别器之间的比较不公平，所以我们进一步提出了权重重置（weight-resetting）策略，这个策略很简单，但是也非常有效。简单而言就是在开始新一轮对判别器搜索之前，我们将上一轮表现最好的生成器的权重进行拷贝，并将其作为下一轮所有生成器的初始权重，这样一来，所有判别器就能进行公平地比较。

### 3.3 高效地多目标搜索GAN

在两个阶段我们采用了相同的进化算法来指导对模型结构的采样。进化算法由选择、交叉和变异等步骤组成。具体而言，我们使用非支配排序（non-dominated sorting）算法来选择满足多目标下的模型结构。交叉和变异步骤是用来产生新的模型结构，避免搜索过程陷入局部最优。我们使用权重共享策略，这极大提升了搜索效率，因为每次采样得到的GAN模型可以直接从超网中继承权重进行性能评估，而不用每次都从头训练。一般而言，我们计算IS和FID指标需要生成器随机生成50,000张图像，我们将这一数量降低到5,000。实验结果显示这不仅能有效提高搜索效率，而且对模型性能的评估也能保持相对准确性。

## **4. 结果**

下表展示了人工设计的GAN模型和之前的NAS-GAN工作在CIFAR-10和STL-10的实验结果，实验指标使用了IS（越大越好）和FID（越小越好）。

![](https://picx.zhimg.com/v2-b81830ed016356f1f52113c6371c2996_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='747' height='606'></svg>)

对于NAS-GAN方法，我们划分了两种实验设置：

* 设置(a)是固定判别器，只搜索生成器，即对应我们的第一阶段（EAGAN-G）。
* 设置(b)是搜索生成器和判别器，即对应我们的两阶段搜索（EAGAN-GD1）。

通过对比NAS-GAN，我们可以看到AdversarialNAS在设置(a)中的效果较差，而AlphaGAN在设置(b)中实验结果明显变差，其是在CIFAR-10数据集上的FID指标从原来的10.35变成了15.56，而且在STL-10上搜索发生了崩溃，未给出最终实验结果。我们的算法在上述两个实验设置上都能取得不错的结果，而且两阶段的搜索能进一步提高最终的性能表现。

EAGAN-G/GD1的第一阶段使用的是预先定义好的D结构。我们想探索一下不同的初始化D结构对EAGAN的影响。我们设置了两个实验：

* EAGAN-GD2：初始化D是一个简单的分类器，由5层卷积核一个线性层组成的。实验结果是执行两阶段搜索后得到的。
* EAGAN-GD3：初始化D是使用EAGAN-GD2搜索到的D，然后重复执行两阶段搜索。

由上表我们可以得到以下三点：

* EAGAN对于不同的初始D结构具有加强的鲁棒性，因为最终都取得了具有竞争力的性能结果。
* 好的初始D结构对搜索过程有明显的促进作用，即EAGAN-GD1结果明显好于EAGAN-GD2
* 对比EAGAN-GD3和EAGAN-GD2的结果，我们会发现即使给定了一个较差的初始D结构，只要搜索时间足够大概率能找到更好的模型结构。

## **展望**

本文提出了一种高效的基于两阶段进化算法的NAS框架来搜索GAN，即EAGAN。我们证明，将生成器和鉴别器的搜索解耦为两个阶段可以通过为这两个阶段量身定制的GAN训练策略（多对一和一对一）和权重重置策略显著提高搜索GAN的稳定性。EAGAN非常高效，只需要1.2个GPU天就能完成在CIFAR-10上的搜索。我们搜索的GAN在CIFAR-10数据集上实现了有竞争力的性能（IS和FID），并且在STL-10数据集上优于以前的NAS GAN。

我们相信我们的工作值得更深入的研究，并可能有益于其他潜在领域。例如，当模型需要对抗性训练时，我们的解耦范式和定制的训练策略非常适合大规模并行搜索。此外，我们将研究减少搜索中权重共享的干扰，并探索高分辨率的生成任务。

## **资源**

论文：[https://arxiv.org/abs/2111.15097](https://link.zhihu.com/?target=https%3A//arxiv.org/abs/2111.15097)

代码：[https://github.com/marsggbo/EAGAN](https://link.zhihu.com/?target=https%3A//github.com/marsggbo/EAGAN)


---

## 如何评价华中科技大学教授质疑博士补助太高？并称情怀要高于助学金？

`link: https://www.zhihu.com/question/543409190/answer/2576328019 · created: 1657887319`


高情怀是配得上高助学金的，这两个不应该是负相关的。


---

## 如何评价北大教授温儒敏回应语文教材相关质疑时称「把火烧到语文教材别有用心」「选编课文没有夹带私货」？

`link: https://www.zhihu.com/question/535623510/answer/2511824415 · created: 1654140340`


为教材选课文经过层层把关，二三十轮审查，不可能一个人说了算，无所谓“夹带私货”。

翻译一下就是:你有本事把二三十轮参与的人全抓起来


---

## Pytorch如何局部更新模型权重？

`link: https://www.zhihu.com/question/533751625/answer/2494841758 · created: 1653098260`


forward之前把不想更新参数部分的参数的require\_grad设置为False即可


---

## CVPR21（2021）有什么值得关注的投稿？

`link: https://www.zhihu.com/question/430116346/answer/2458860021 · created: 1650976018`


介绍一篇NAS相关的论文:AttentiveNAS

## **1. 背景（Two-stage NAS）**

该篇论文（AttentiveNAS）聚焦的是Two-stage NAS，比较出名的算法有 BigNAS，Once-for-all NAS (OFA)， SPOS等等，不过他们都采用的uniform的采样去训练Supernet，即把所有的子网一视同仁，尽可能分配相等的采样机会。Two-stage NAS算法通常包含如下两个步骤：

## **1.1 Constraint-free pre-training**

第一步是训练Supernet，数学化公式如下：

![\min _{W} \mathbb{E}_{\alpha \in \mathcal{A}}\left[\mathcal{L}\left(W_{\alpha} ; \mathcal{D}^{t r n}\right)\right]+\gamma \mathcal{R}(W) \\](https://www.zhihu.com/equation?tex=%5Cmin+_%7BW%7D+%5Cmathbb%7BE%7D_%7B%5Calpha+%5Cin+%5Cmathcal%7BA%7D%7D%5Cleft%5B%5Cmathcal%7BL%7D%5Cleft%28W_%7B%5Calpha%7D+%3B+%5Cmathcal%7BD%7D%5E%7Bt+r+n%7D%5Cright%29%5Cright%5D%2B%5Cgamma+%5Cmathcal%7BR%7D%28W%29+%5C%5C)

* 第一项是所有子网loss的期望，这些子网共享权重
* 第二项是对共享权重的约束

## **1.2 Resource-constrained searching**

第二步是基于训练好的Supernet去评估子网络，然后选出Pareto-front模型。数学公式可表示成如下形式：

![\begin{aligned} &\left\{\alpha_{i}^{*}\right\}=\underset{\alpha_{i} \in \mathcal{A}}{\arg \min } \mathcal{L}\left(W_{\alpha_{i}}^{*} ; \mathcal{D}^{v a l}\right), \\ &\text { s.t. } \operatorname{FLOPS}\left(\alpha_{i}\right)<\tau_{i}, \quad \forall i \end{aligned} \\](https://www.zhihu.com/equation?tex=%5Cbegin%7Baligned%7D+%26%5Cleft%5C%7B%5Calpha_%7Bi%7D%5E%7B%2A%7D%5Cright%5C%7D%3D%5Cunderset%7B%5Calpha_%7Bi%7D+%5Cin+%5Cmathcal%7BA%7D%7D%7B%5Carg+%5Cmin+%7D+%5Cmathcal%7BL%7D%5Cleft%28W_%7B%5Calpha_%7Bi%7D%7D%5E%7B%2A%7D+%3B+%5Cmathcal%7BD%7D%5E%7Bv+a+l%7D%5Cright%29%2C+%5C%5C+%26%5Ctext+%7B+s.t.+%7D+%5Coperatorname%7BFLOPS%7D%5Cleft%28%5Calpha_%7Bi%7D%5Cright%29%3C%5Ctau_%7Bi%7D%2C+%5Cquad+%5Cforall+i+%5Cend%7Baligned%7D+%5C%5C)

一般常用的搜索算法是进化算法或者Monte Carlo tree search算法。

## **2. AttentiveNAS**

## **2.1 Mathematics**

AttentiveNAS想做的是把两个步骤融合成一步，可表示成如下数学公式：

![\begin{align} &\min _{W} \mathbb{E}_{\pi(\tau)} \mathbb{E}_{\pi(\alpha \mid \tau)}\left[\mathcal{L}\left(W_{\alpha} ; \mathcal{D}^{t r n}\right)\right], \\ =&\min _{W} \mathbb{E}_{\pi(\tau)} \sum_{\pi(\alpha \mid \tau)}\left[\gamma(\alpha) \mathcal{L}\left(W_{\alpha} ; \mathcal{D}^{t r n}\right)\right], \\ =&\min _{W} \frac{1}{n} \sum_{\tau_{o} \sim \pi(\tau)}^{n}\left[\sum_{\alpha_{i} \sim \pi\left(\alpha \mid \tau_{o}\right)}^{k} \gamma\left(\alpha_{i}\right) \mathcal{L}\left(W_{\alpha_{i}} ; \mathcal{D}^{t r n}\right)\right] \end{align} \\](https://www.zhihu.com/equation?tex=%5Cbegin%7Balign%7D+%26%5Cmin+_%7BW%7D+%5Cmathbb%7BE%7D_%7B%5Cpi%28%5Ctau%29%7D+%5Cmathbb%7BE%7D_%7B%5Cpi%28%5Calpha+%5Cmid+%5Ctau%29%7D%5Cleft%5B%5Cmathcal%7BL%7D%5Cleft%28W_%7B%5Calpha%7D+%3B+%5Cmathcal%7BD%7D%5E%7Bt+r+n%7D%5Cright%29%5Cright%5D%2C+%5C%5C+%3D%26%5Cmin+_%7BW%7D+%5Cmathbb%7BE%7D_%7B%5Cpi%28%5Ctau%29%7D+%5Csum_%7B%5Cpi%28%5Calpha+%5Cmid+%5Ctau%29%7D%5Cleft%5B%5Cgamma%28%5Calpha%29+%5Cmathcal%7BL%7D%5Cleft%28W_%7B%5Calpha%7D+%3B+%5Cmathcal%7BD%7D%5E%7Bt+r+n%7D%5Cright%29%5Cright%5D%2C+%5C%5C+%3D%26%5Cmin+_%7BW%7D+%5Cfrac%7B1%7D%7Bn%7D+%5Csum_%7B%5Ctau_%7Bo%7D+%5Csim+%5Cpi%28%5Ctau%29%7D%5E%7Bn%7D%5Cleft%5B%5Csum_%7B%5Calpha_%7Bi%7D+%5Csim+%5Cpi%5Cleft%28%5Calpha+%5Cmid+%5Ctau_%7Bo%7D%5Cright%29%7D%5E%7Bk%7D+%5Cgamma%5Cleft%28%5Calpha_%7Bi%7D%5Cright%29+%5Cmathcal%7BL%7D%5Cleft%28W_%7B%5Calpha_%7Bi%7D%7D+%3B+%5Cmathcal%7BD%7D%5E%7Bt+r+n%7D%5Cright%29%5Cright%5D+%5Cend%7Balign%7D+%5C%5C)

* 公式(1)中的![\tau](https://www.zhihu.com/equation?tex=%5Ctau)表示候选网络的FLOPs，最优的![W^*](https://www.zhihu.com/equation?tex=W%5E%2A)简单理解就是 使得 不同FLOPs下(![\mathbb{E}_{\pi(\tau)}](https://www.zhihu.com/equation?tex=%5Cmathbb%7BE%7D_%7B%5Cpi%28%5Ctau%29%7D)) 所有子模型的loss期望 (![\mathbb{E}_{\pi(\alpha \mid \tau)}](https://www.zhihu.com/equation?tex=%5Cmathbb%7BE%7D_%7B%5Cpi%28%5Calpha+%5Cmid+%5Ctau%29%7D)) 最小的解。
* 公式(2)和(3)都是分别使用Monte Carlo采样做近似计算。比如 ![n](https://www.zhihu.com/equation?tex=n)表示将整个搜索空间划分成![n](https://www.zhihu.com/equation?tex=n)个FLOPs区间，![k](https://www.zhihu.com/equation?tex=k)表示每个FLOPs区间内每次采样更新的模型数量,![\gamma(\alpha)](https://www.zhihu.com/equation?tex=%5Cgamma%28%5Calpha%29)是indicator函数，即如果模型结构![\alpha](https://www.zhihu.com/equation?tex=%5Calpha)满足指定条件，则![\gamma(\alpha)](https://www.zhihu.com/equation?tex=%5Cgamma%28%5Calpha%29)等于1，反之为0。

## **2.2 Pseudo Algorithm**

![](https://picx.zhimg.com/v2-4bd17be6720d4d535d9b65e8f29a9cea_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='647' height='647'></svg>)

上面数学公式中提到的![\gamma(\alpha)](https://www.zhihu.com/equation?tex=%5Cgamma%28%5Calpha%29)是一个指示函数，其条件是![\alpha](https://www.zhihu.com/equation?tex=%5Calpha)是否属于 best或worst Pareto-front，分别记为BestUp-k和WorstUp-k

![](https://picx.zhimg.com/v2-9fc249660ed8f69da1e3ed16c8dbc125_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='637' height='480'></svg>)

它的这种优化策略类似于BigNAS里的Sandwich策略，即把最好的和最差的都优化好了，那么就认为中间的也一定程度上被优化好了。

## **3. Experimental Results**

训练好了Supernet，接下来就是去做实验验证这种训练方式的稳定性和有效性。

## **3.1 Prediction**

对于任意一个子模型，我们可以得到它的评估性能（直接从Supernet中继承对应模块的权重）和真实性能（test acc），一般来说如果足够数量模型的评估性能和预测性能之间存在强相关性，则说明训练好的Supernet能够有效地知道后面对模型的搜索。

评估性能有两种策略可以获取：

* 1. 基于训练好的Supernet去初始化自网络，然后在验证集上去评估模型性能；
* 2. 上面的方法耗时比较长，所以另一种策略是训练一个预测器来预测每个模型的性能。本文的做法是先跑1024个子模型得到他们的真实性能，然后基于这1024个模型组成的数据对（模型结构编码，test acc）训练得到一个随机森林回归树。

下图是AttentiveNAS基于第二种策略得到的实验结果， 其中![s0,s1](https://www.zhihu.com/equation?tex=s0%2Cs1)分别表示在两个不同种子下跑的实验结果，ep30/ep360表示在训练30个epoch和360个epoch下的结果。可以看到预测的ACC和真实的ACC之间的相关系数Kendall tau（其范围是-1~1）还是比较大的。这表明预测器还是能有效预测出模型的ACC的。

![](https://pica.zhimg.com/v2-fcb46da5a08cbfbdf8ea751c13f2e889_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='932' height='399'></svg>)

## **3.2 Sampling Results**

![](https://picx.zhimg.com/v2-1f4346e6804378f8cf13decc11395166_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='931' height='400'></svg>)

不同采样训练的结果如上图所示，BestUp-50表示从best Pareto front set中每个sampling step采样50个模型做评估。根据上面的结果可以观察到训练WorstUp要比BestUp效果更好，这个常规的想法不太一致。

最终在ImageNet上的结果如下表所示

![](https://picx.zhimg.com/v2-70ea1761d1231e55d55c7e5478a53365_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='615' height='960'></svg>)

### **微信公众号：AutoML机器学习**

![](https://pic1.zhimg.com/50/v2-87083e55cd41dbef83cc840c142df48a_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='0' height='0'></svg>)

**MARSGGBO♥原创**  
**如有意合作或学术讨论欢迎私戳联系~**  
**邮箱:marsggbo@foxmail.com**   
**2022-04-26 13:53:50**


---

## python如何在打包时加入一些非py文件?

`link: https://www.zhihu.com/question/59479536/answer/2445883324 · created: 1650283665`


假设我的项目目录大致如下

```
myapp/
├── myapp
│   ├── configs
│   │   ├── data
│   │   │   └── data.yaml
│   │   └── trainer
│   │       └── trainer.yaml
│   ├── __init__.py
│   ├── run.py
│   └── trainer
│       ├── __init__.py
│       └── train.py
└── setup.py
```

注意要想制作成包的目录下必须要添加`__init__.py`文件，这里可以看到父目录名是`myapp`，它包含了一个同名的子目录，当然你也可以把这个子目录改成`src`，但是我习惯取相同的名字。

`setup.py`如下

```
from setuptools import setup, find_packages

setup(
    name="myapp",  # you should change "src" to your project name
    version="1.0",
    description="This is my app.",
    author="marsggbo",
    # replace with your own github project link
    #install_requires=["torch>=1.4"],
    packages=find_packages(),
    include_package_data=True,
)
```

我们运行如下命令

```
python setup.py sdist bdist_wheel
```

你会看到在你的目录下新生成了`build`和`dist`两个新文件夹，被打包的源代码就在`build/lib`里

```
myapp/
├── build
│   ├── bdist.linux-x86_64
│   └── lib
│       └── myapp
│           ├── __init__.py
│           ├── run.py
│           └── trainer
│               ├── __init__.py
│               └── train.py
├── dist
│   ├── myapp-1.0-py3-none-any.whl
│   └── myapp-1.0.tar.gz
├── myapp
│   ├── configs
│   │   ├── data
│   │   │   └── data.yaml
│   │   └── trainer
│   │       └── trainer.yaml
│   ├── __init__.py
│   ├── run.py
│   └── trainer
│       ├── __init__.py
│       └── train.py
├── myapp.egg-info
│   ├── dependency_links.txt
│   ├── PKG-INFO
│   ├── SOURCES.txt
│   └── top_level.txt
└── setup.py
```

可以看到只有py文件被打包了，而yaml文件都被丢掉了，为了解决这个问题，你需要创建一个`MANIFEST.in`文件，然后输入以下内容

```
recursive-include myapp/configs *.yaml
```

这一行代码的作用是去递归地提取出 `myapp/configs`路径下的所有yaml文件，当然如果不需要递归的话，你可以把`recursive-include`改成`include`。

现在我们重新执行打包命令

```
python setup.py sdist bdist_wheel
```

这个时候所有yaml文件也成功打包好了

```
myapp/
├── build
│   ├── bdist.linux-x86_64
│   └── lib
│       └── myapp
│           ├── configs
│           │   ├── data
│           │   │   └── data.yaml
│           │   └── trainer
│           │       └── trainer.yaml
│           ├── __init__.py
│           ├── run.py
│           └── trainer
│               ├── __init__.py
│               └── train.py
├── dist
│   ├── myapp-1.0-py3-none-any.whl
│   └── myapp-1.0.tar.gz
├── MANIFEST.in
├── myapp
│   ├── configs
│   │   ├── data
│   │   │   └── data.yaml
│   │   └── trainer
│   │       └── trainer.yaml
│   ├── __init__.py
│   ├── run.py
│   └── trainer
│       ├── __init__.py
│       └── train.py
├── myapp.egg-info
│   ├── dependency_links.txt
│   ├── PKG-INFO
│   ├── SOURCES.txt
│   └── top_level.txt
└── setup.py
```

### **微信公众号：AutoML机器学习**

**![](https://picx.zhimg.com/50/v2-87083e55cd41dbef83cc840c142df48a_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='0' height='0'></svg>)**

**MARSGGBO♥原创**  
**如有意合作或学术讨论欢迎私戳联系~**  
**邮箱:marsggbo@foxmail.com**


---

## 指数分布的概率密度函数是如何得出的？

`link: https://www.zhihu.com/question/337523566/answer/2443734925 · created: 1650175067`


> 开始介绍之前还是老样子先吐槽一下教科书不说人话，喜欢端着，真是耽误了一群数学天才。

## **伯努利分布**

伯努利分布很好理解，常见的例子就是抛硬币，假设硬币正面朝上的概率是 p，所以伯努利分布的**概率质量函数（probability mass function，简写作pmf**）是：

> “ 注意区分概率质量函数和概率密度函数，前者是针对离散情况而言的，后者是针对连续情况”

![f_{X}(x)=p^{x}(1-p)^{1-x}= \begin{cases}p & \text { if } x=1 \\ q & \text { if } x=0\end{cases} \\](https://www.zhihu.com/equation?tex=f_%7BX%7D%28x%29%3Dp%5E%7Bx%7D%281-p%29%5E%7B1-x%7D%3D+%5Cbegin%7Bcases%7Dp+%26+%5Ctext+%7B+if+%7D+x%3D1+%5C%5C+q+%26+%5Ctext+%7B+if+%7D+x%3D0%5Cend%7Bcases%7D+%5C%5C)

## **二项分布**

上面只是一个实验，如果抛10次有8次是正面朝上的概率就是 ![C_{10}^8 p^8(1-p)^2](https://www.zhihu.com/equation?tex=C_%7B10%7D%5E8+p%5E8%281-p%29%5E2)，这个其实就是二项分布，换言之二项分布的每一个单次实验其实就是服从伯努利分布。二项分布的**概率质量函数**是

![f(k, n, p)=\operatorname{Pr}(X=k)=\left(\begin{array}{l} n \\ k \end{array}\right) p^{k}(1-p)^{n-k} \\](https://www.zhihu.com/equation?tex=f%28k%2C+n%2C+p%29%3D%5Coperatorname%7BPr%7D%28X%3Dk%29%3D%5Cleft%28%5Cbegin%7Barray%7D%7Bl%7D+n+%5C%5C+k+%5Cend%7Barray%7D%5Cright%29+p%5E%7Bk%7D%281-p%29%5E%7Bn-k%7D+%5C%5C)

## **泊松分布**

那泊松分布是什么呢？其实现实中很多事情都可以用泊松分布来描述，而且其实泊松分布可以简单地是伯努利分布的极限情况。

假如你开了个馒头店，每天营业时间是早上12点到下午6点，是的你就是这么仁慈，员工得休息好才能好好上班。然后你统计了一周的顾客数量，发现每天来的人顾客数量不一样。那很自然地你就想根据来的顾客的数量来提前准备制作馒头的数量，免得顾客数量多的时候，馒头数量不够，导致钞票赚少了。同样的，如果馒头做多了，又浪费了。所以你想知道每天顾客数量是100的概率（也可以是200,400等）。要计算这个就需要用到泊松分布。

为方便计算，假设你的店新开张，总共5个顾客来消费了，分别是在1点，2点，3点，4点和6点到的，此时我们可以把整个营业时间划分成6个时间段，那么每个时间段顾客来与不来其实就是一个服从伯努利分布的随机变量。假设每个时间段内来顾客的概率是 p， 那么一天内来5个顾客的概率就是 ![C_{6}^5 p^5(1-p)^1](https://www.zhihu.com/equation?tex=C_%7B6%7D%5E5+p%5E5%281-p%29%5E1)。

看到这你肯定在想了，那如果第一天开张来了10个顾客呢？是的，你的想法很好。此时我们可以把时间段划分的更加小，可以是秒也可以是分钟。我们假设总共划分了![n](https://www.zhihu.com/equation?tex=n)个时间段，当![n](https://www.zhihu.com/equation?tex=n)趋于无穷小的时候，每个时间段也就趋于无穷小了，那么在这![n](https://www.zhihu.com/equation?tex=n)个时间段来了![k](https://www.zhihu.com/equation?tex=k)个顾客的概率（一个时间段内最多只有一个顾客出现或者没有顾客）是

![\lim _{n \rightarrow \infty}\left(\begin{array}{l} n \\ k \end{array}\right) p^{k}(1-p)^{n-k} \\](https://www.zhihu.com/equation?tex=%5Clim+_%7Bn+%5Crightarrow+%5Cinfty%7D%5Cleft%28%5Cbegin%7Barray%7D%7Bl%7D+n+%5C%5C+k+%5Cend%7Barray%7D%5Cright%29+p%5E%7Bk%7D%281-p%29%5E%7Bn-k%7D+%5C%5C)

发现了没，这不就是二项分布吗？所以这也就解释了前面我们说泊松分布可以简单地理解成是伯努利（或二项）分布的在时间段是极限小的情况。因为我们说抛硬币的时候通常是不考虑时间的，即基本上不会说我们每分钟或者每秒抛一次硬币，而泊松分布是将时间划分成若干个时间段，而这个时间段的大小视情况而定。

因为连续时间上的泊松分布被转化成了二项分布，而二项分布的期望是

![E(X)=np=\mu \\](https://www.zhihu.com/equation?tex=E%28X%29%3Dnp%3D%5Cmu+%5C%5C)

所以在这![n](https://www.zhihu.com/equation?tex=n)个时间段来了![k](https://www.zhihu.com/equation?tex=k)个顾客的概率

![p=\frac{\mu}{n} \\](https://www.zhihu.com/equation?tex=p%3D%5Cfrac%7B%5Cmu%7D%7Bn%7D+%5C%5C)

我们把这个概率带入到上面的极限中去可以得到（推导过程省略了）

![\lim _{n \rightarrow \infty}\left(\begin{array}{l} n \\ k \end{array}\right) p^{k}(1-p)^{n-k}=\frac{\mu^{k}}{k !} e^{-\mu} \\](https://www.zhihu.com/equation?tex=%5Clim+_%7Bn+%5Crightarrow+%5Cinfty%7D%5Cleft%28%5Cbegin%7Barray%7D%7Bl%7D+n+%5C%5C+k+%5Cend%7Barray%7D%5Cright%29+p%5E%7Bk%7D%281-p%29%5E%7Bn-k%7D%3D%5Cfrac%7B%5Cmu%5E%7Bk%7D%7D%7Bk+%21%7D+e%5E%7B-%5Cmu%7D+%5C%5C)

可以看到当时间段趋于无穷小时，最终得到的概率是与![n](https://www.zhihu.com/equation?tex=n)无关的，只跟均值和你想预测的![k](https://www.zhihu.com/equation?tex=k)有关。一般会把![\mu](https://www.zhihu.com/equation?tex=%5Cmu)用![\lambda](https://www.zhihu.com/equation?tex=%5Clambda)表示，所以泊松分布下的概率质量函数（注意泊松分布也是离散的概率分布）是

![P(X=k)=\frac{\lambda^{k}}{k !} e^{-\lambda} \\](https://www.zhihu.com/equation?tex=P%28X%3Dk%29%3D%5Cfrac%7B%5Clambda%5E%7Bk%7D%7D%7Bk+%21%7D+e%5E%7B-%5Clambda%7D+%5C%5C)

那么根据今天新开张的数据，均值![\mu](https://www.zhihu.com/equation?tex=%5Cmu)（或者说![\lambda](https://www.zhihu.com/equation?tex=%5Clambda)）的值就是5，开门营业的时间越久，才会评估越准确。我们用[这个网站](https://link.zhihu.com/?target=https%3A//homepage.divms.uiowa.edu/~mbognar/applets/pois.html)画出了概率质量函数，可以越靠近均值，概率越高。另外来10个顾客的概率只有0.018。所以说你还是趁早把店铺转租出去吧，好好进厂里搬砖吧。

![](https://pic1.zhimg.com/v2-2bdabc51cbf7463f7aa1e529c186875b_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='586' height='303'></svg>)

## **指数分布**

指数分布是从泊松分布推断出来，泊松分布考虑的是在时间间隔足够小的情况下每天来的顾客的数量的概率，而指数分布考虑的是时间间隔的概率。比如你想求出![T](https://www.zhihu.com/equation?tex=T)个时间段内都没来一个顾客的概率，这就等价于k=0,即 ![P(t>T)=P(X=0)=e^{-\lambda}](https://www.zhihu.com/equation?tex=P%28t%3ET%29%3DP%28X%3D0%29%3De%5E%7B-%5Clambda%7D)。把时间t作为变量对泊松分布公式稍微扩展一下就得到了指数分布

![P(t>T)=P(t>T,X=k=0)=\frac{(\lambda t)^{k}}{k !} e^{-\lambda t}=e^{-\lambda t} \\](https://www.zhihu.com/equation?tex=P%28t%3ET%29%3DP%28t%3ET%2CX%3Dk%3D0%29%3D%5Cfrac%7B%28%5Clambda+t%29%5E%7Bk%7D%7D%7Bk+%21%7D+e%5E%7B-%5Clambda+t%7D%3De%5E%7B-%5Clambda+t%7D+%5C%5C)

同理

![P(t\le T)=1-P(t>T)=1-e^{-\lambda t} \\](https://www.zhihu.com/equation?tex=P%28t%5Cle+T%29%3D1-P%28t%3ET%29%3D1-e%5E%7B-%5Clambda+t%7D+%5C%5C)

所以指数分布的累积分布函数是

![F(t)= \begin{cases}1-e^{-\lambda t}, & t \geq 0 \\ 0, & t<0\end{cases} \\](https://www.zhihu.com/equation?tex=F%28t%29%3D+%5Cbegin%7Bcases%7D1-e%5E%7B-%5Clambda+t%7D%2C+%26+t+%5Cgeq+0+%5C%5C+0%2C+%26+t%3C0%5Cend%7Bcases%7D+%5C%5C)

对 ![F(t)](https://www.zhihu.com/equation?tex=F%28t%29)求导后可以得到概率密度函数（注意这里不是概率质量函数了，因为指数分布是连续分布）：

![p(t)= \begin{cases}\lambda e^{-\lambda t}, & t \geq 0 \\ 0, & t<0\end{cases} \\](https://www.zhihu.com/equation?tex=p%28t%29%3D+%5Cbegin%7Bcases%7D%5Clambda+e%5E%7B-%5Clambda+t%7D%2C+%26+t+%5Cgeq+0+%5C%5C+0%2C+%26+t%3C0%5Cend%7Bcases%7D+%5C%5C)

对应到上面的例子，![\lambda](https://www.zhihu.com/equation?tex=%5Clambda)是每天来的顾客数量均值，假设是5，我们可以画出此时的指数分布的概率密度函数

![](https://pic1.zhimg.com/v2-1876ea83055b2b664917222a107d3f48_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='699' height='499'></svg>)

因为我们上面的例子考虑的是每天的顾客数，所以![x=1](https://www.zhihu.com/equation?tex=x%3D1)时，计算得到的![p(X>1)](https://www.zhihu.com/equation?tex=p%28X%3E1%29)表示超过1天都没有顾客的概率是0.00674,这表示你开的店每天大概率还是有人回来关顾的哈哈哈

当我们把![x=\frac{1}{18}\approx 0.0555](https://www.zhihu.com/equation?tex=x%3D%5Cfrac%7B1%7D%7B18%7D%5Capprox+0.0555)时，就表示 超过 ![6*\frac{1}{18}=\frac{1}{3}](https://www.zhihu.com/equation?tex=6%2A%5Cfrac%7B1%7D%7B18%7D%3D%5Cfrac%7B1%7D%7B3%7D)小时 （20分钟）（因为你一天只开门营业6个小时）没顾客来的概率是0.75749。

因为指数分布有个特点是无记忆性，换言之，不管你从哪个时间点（比如下午1点或者2点）去计算 ![p(x>0.1)](https://www.zhihu.com/equation?tex=p%28x%3E0.1%29)，得到的结果都是一样的，即未来20分钟内没顾客来的概率是0.75749，所以你买出一个馒头后可以比较放心的打一把农药来打发时间。

![](https://pic1.zhimg.com/v2-38808a2e720b55c02d49c01dc9ceaf7e_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='601' height='315'></svg>)

Exp Distribution

> “ 注意泊松分布和指数分布的前提是，事件之间不能有关联，否则就不能运用上面的公式。  
>  ”

todo: (超)几何分布，伽马分布，贝塔分布。。。

## **总结**

伯努利分布 > 二项分布 > 泊松分布 > 指数分布 就是一个个套娃的关系。

## 参考

* <https://www.zhihu.com/question/26441147/answer/429569625>
* [指数分布公式的含义是什么？](https://www.zhihu.com/question/24796044/answer/673838656)

### **微信公众号：AutoML机器学习**

![](https://picx.zhimg.com/50/v2-87083e55cd41dbef83cc840c142df48a_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='0' height='0'></svg>)

**MARSGGBO♥原创**  
**如有意合作或学术讨论欢迎私戳联系~**  
**邮箱:marsggbo@foxmail.com**   
**2022-04-16 22:29:56**


---

## 似然函数和后验概率的关系?

`link: https://www.zhihu.com/question/522023492/answer/2432847586 · created: 1649592620`


![](https://picx.zhimg.com/v2-16becfb363b70bb5a90db0ac83de8563_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1102' height='608'></svg>)

MLE&amp;amp;MAP

## **什么是先验/后验概率**

我们先给出一些符号定义，令![\theta](https://www.zhihu.com/equation?tex=%5Ctheta)表示模型参数，![D](https://www.zhihu.com/equation?tex=D)表示数据。

先验概率比较好理解，比如 ![p(D)](https://www.zhihu.com/equation?tex=p%28D%29)就表示数据的先验概率（prior probability）。

但是在之前我经常搞不明白 ![p(D|\theta)](https://www.zhihu.com/equation?tex=p%28D%7C%5Ctheta%29) 和![p(\theta|D)](https://www.zhihu.com/equation?tex=p%28%5Ctheta%7CD%29) 哪个才是后验概率（posterior probability）。其实二者都可以看做是后验概率，只不过少了定语。具体来说 ![p(D|\theta)](https://www.zhihu.com/equation?tex=p%28D%7C%5Ctheta%29) 是数据 ![D](https://www.zhihu.com/equation?tex=D) 的后验概率，即已经告诉你模型参数 ![\theta](https://www.zhihu.com/equation?tex=%5Ctheta) 了，要你求数据的概率，所以是后验概率。同理![p(\theta|D)](https://www.zhihu.com/equation?tex=p%28%5Ctheta%7CD%29) 是告诉你数据后，让你求![\theta](https://www.zhihu.com/equation?tex=%5Ctheta)的后验概率。所以，要根据语境去判断哪个才是后验概率。

## **似然概率**

下面介绍一下贝叶斯公式这个老朋友了，或者说是熟悉的陌生人。

![p(\theta|D)=\frac{p(D|\theta)p(\theta)}{p(D)} \tag{1} ](https://www.zhihu.com/equation?tex=p%28%5Ctheta%7CD%29%3D%5Cfrac%7Bp%28D%7C%5Ctheta%29p%28%5Ctheta%29%7D%7Bp%28D%29%7D+%5Ctag%7B1%7D+)

假设我们研究的对象是变量![\theta](https://www.zhihu.com/equation?tex=%5Ctheta)，那么此时先验概率就是 ![p(\theta)](https://www.zhihu.com/equation?tex=p%28%5Ctheta%29)，（![\theta](https://www.zhihu.com/equation?tex=%5Ctheta)的) 后验概率是![p(\theta|D)](https://www.zhihu.com/equation?tex=p%28%5Ctheta%7CD%29)。

那![p(D|\theta)](https://www.zhihu.com/equation?tex=p%28D%7C%5Ctheta%29) 是什么呢？它就是本文的另一个主角：似然概率 （likelihood probability）,顾名思义是给定参数![\theta](https://www.zhihu.com/equation?tex=%5Ctheta)，求数据是![D](https://www.zhihu.com/equation?tex=D)的概率是多少。

一般来说 ![p(D)](https://www.zhihu.com/equation?tex=p%28D%29)是不知道的或者说很难求解，但是我们可以知道后验概率和 （似然概率乘以先验概率）呈正相关关系，所以![p(D)](https://www.zhihu.com/equation?tex=p%28D%29)即使不知道也不影响对后验概率的求解。

## **极大似然估计 与 最大后验概率估计**

极大似然估计 （Maximum Likelihood Estimate, MLE）和最大后验概率估计（Maximum A Posteriori (MAP) estimation）其实是两个不同学派的方法论。

MLE是频率学派模型参数估计的常用方法，它的目的是想最大化已经发生的事情的概率。我们在用神经网络训练分类器的时候其实就可以理解成是MLE。具体来说，假设数据![D](https://www.zhihu.com/equation?tex=D)由一组数据样本组成，即![D=\{d_1,...,d_n\}](https://www.zhihu.com/equation?tex=D%3D%5C%7Bd_1%2C...%2Cd_n%5C%7D)，模型参数用![\theta](https://www.zhihu.com/equation?tex=%5Ctheta)表示，我们假设每个样本预测彼此独立，所以MLE的求解方式如下：

![\begin{aligned} \hat{\theta}_{\mathrm{MLE}} &=\arg \max P(D ; \theta) \\ &=\arg \max P\left(d_{1} ; \theta\right) P\left(d_{2} ; \theta\right) \cdots P\left(d_{n} ; \theta\right) \\ &=\arg \max \log \prod_{i=1}^{n} P\left(d_{i} ; \theta\right) \\ &=\arg \max \sum_{i=1}^{n} \log P\left(d_{i} ; \theta\right) \\ &=\arg \min -\sum_{i=1}^{n} \log P\left(d_{i} ; \theta\right) \end{aligned} \tag{2} ](https://www.zhihu.com/equation?tex=%5Cbegin%7Baligned%7D+%5Chat%7B%5Ctheta%7D_%7B%5Cmathrm%7BMLE%7D%7D+%26%3D%5Carg+%5Cmax+P%28D+%3B+%5Ctheta%29+%5C%5C+%26%3D%5Carg+%5Cmax+P%5Cleft%28d_%7B1%7D+%3B+%5Ctheta%5Cright%29+P%5Cleft%28d_%7B2%7D+%3B+%5Ctheta%5Cright%29+%5Ccdots+P%5Cleft%28d_%7Bn%7D+%3B+%5Ctheta%5Cright%29+%5C%5C+%26%3D%5Carg+%5Cmax+%5Clog+%5Cprod_%7Bi%3D1%7D%5E%7Bn%7D+P%5Cleft%28d_%7Bi%7D+%3B+%5Ctheta%5Cright%29+%5C%5C+%26%3D%5Carg+%5Cmax+%5Csum_%7Bi%3D1%7D%5E%7Bn%7D+%5Clog+P%5Cleft%28d_%7Bi%7D+%3B+%5Ctheta%5Cright%29+%5C%5C+%26%3D%5Carg+%5Cmin+-%5Csum_%7Bi%3D1%7D%5E%7Bn%7D+%5Clog+P%5Cleft%28d_%7Bi%7D+%3B+%5Ctheta%5Cright%29+%5Cend%7Baligned%7D+%5Ctag%7B2%7D+)

可以看到，上面其实就是我们常用的交叉熵损失函数。那么如何用MAP来优化模型参数呢？公式如下：

![\begin{aligned} \hat{\theta}_{\mathrm{MAP}} &=\arg \max P(\theta \mid D) \\ &=\arg \min -\log P(\theta \mid D) \\ &=\arg \min -\log P(D \mid \theta)-\log P(\theta)+\log P(D) \\ &=\arg \min -\log P(D \mid \theta)-\log P(\theta) \end{aligned} \tag{3} ](https://www.zhihu.com/equation?tex=%5Cbegin%7Baligned%7D+%5Chat%7B%5Ctheta%7D_%7B%5Cmathrm%7BMAP%7D%7D+%26%3D%5Carg+%5Cmax+P%28%5Ctheta+%5Cmid+D%29+%5C%5C+%26%3D%5Carg+%5Cmin+-%5Clog+P%28%5Ctheta+%5Cmid+D%29+%5C%5C+%26%3D%5Carg+%5Cmin+-%5Clog+P%28D+%5Cmid+%5Ctheta%29-%5Clog+P%28%5Ctheta%29%2B%5Clog+P%28D%29+%5C%5C+%26%3D%5Carg+%5Cmin+-%5Clog+P%28D+%5Cmid+%5Ctheta%29-%5Clog+P%28%5Ctheta%29+%5Cend%7Baligned%7D+%5Ctag%7B3%7D+)

可以看到 ![log(MAP(\theta))\approx log({MAP(\theta)})+log(\theta)](https://www.zhihu.com/equation?tex=log%28MAP%28%5Ctheta%29%29%5Capprox+log%28%7BMAP%28%5Ctheta%29%7D%29%2Blog%28%5Ctheta%29)。而![p(\theta)](https://www.zhihu.com/equation?tex=p%28%5Ctheta%29)其实就是常用的正则项，即对模型参数的约束。

参考：[张小磊：极大似然估计与最大后验概率估计](https://zhuanlan.zhihu.com/p/40024110)

### **微信公众号：AutoML机器学习**

**![](https://picx.zhimg.com/50/v2-87083e55cd41dbef83cc840c142df48a_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='0' height='0'></svg>)**

**MARSGGBO♥原创**  
**如有意合作或学术讨论欢迎私戳联系~**  
**邮箱:marsggbo@foxmail.com**   
**2022-04-10 17:21:14**


---

## 有哪些话一听就知道一个博士生是个水货？

`link: https://www.zhihu.com/question/458723832/answer/2432546117 · created: 1649578275`


像我这种不敢对任何博士生做评价的就是个水货。

ᥬ ᭄ᥬ ᭄


---

## 如何看待赛雷三分钟抨击巴黎公社与法国大革命？

`link: https://www.zhihu.com/question/523406993/answer/2401780461 · created: 1647937287`


咱就是说 为什么不把最后的内容也放出来供大家讨论？

![](https://pic1.zhimg.com/v2-de8318148b084942a7da967f857f6418_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1280' height='2844'></svg>)


---

## Pytorch中，将Dataloader的pin_memory设置为True会提高训练速度吗？

`link: https://www.zhihu.com/question/356098644/answer/2380453439 · created: 1646753963`


`pin_memory` 和 `non_blocking`的作用分别是什么?网上看了很多解释，只是稀里糊涂的有个感觉，就是用了这玩意速度能变快，但是不知所以然，这篇文章希望能帮助你解惑，也给自己做个笔记，以备日后查阅。

```
train_sampler = None
train_loader = torch.utils.data.DataLoader(
 train_dataset,
  ...,
  pin_memory=True
)

for data, labels in train_loader:
 data = data.to('cuda:0', non_blocking=True)
```

## **1. pin\_memory**

## **1.1 什么是锁页内存（Pinned Memory/PageLocked Memory）？什么是"Pinned"?**

> “ 参考Cuda锁页内存和零复制[1] ”

通常我们的主机处理器是支持虚拟内存系统的，也就是使用硬盘空间来代替内存。大多数系统中虚拟内存空间被划分成许多页，它们是寻址的单元，页的大小至少是4096个字节。虚拟寻址能使一个连续的虚拟地址空间映射到物理内存并不连续的一些页。

如果某页的物理内存被标记为**换出**状态，它就可以被更换到磁盘上，也就是说被踢出内存了。如果下次需要该页了，则重新加载到内存里。显然如果这一页切换的非常频繁，那么会浪费不少时间。

锁页(pinned page)是操作系统常用的操作，就是为了使硬件外设直接访问CPU内存，从而避免过多的复制操作。被锁定的页面会被操作系统标记为**不可被换出的**，所以设备驱动程序给这些外设编程时，可以使用页面的物理地址直接访问内存，CPU也可以访问上述锁页内存，但是此内存是不能移动或换页到磁盘上的。另外，在GPU上分配的内存默认都是锁页内存，这只是因为GPU不支持将内存交换到磁盘上。

## **1.2 什么时候设置`pin_memory=True`?**

> “ 参考 How to Optimize Data Transfers in CUDA C/C++[2] ”

总结一下上一小节的内容就是：

> “ 内存可以分为 **没锁的（pageable，可分页的）** 和 **锁了的（pinned）**。  
>  锁页内存和GPU显存之间的拷贝速度大约是6GB/s  
> 可分页内存和GPU显存间的拷贝速度大约是3GB/s。  
> GPU内存间速度是30GB/s,CPU间内存速度是10GB/s

Host（例如CPU）的数据分配默认是\*\*pageable(可分页的)\*\*，但是GPU是没法直接读取pageable内存里的数据的，所以需要先创建一个临时的缓冲区（pinned memory），把数据从pageable内存拷贝pinned内存上，然后GPU才能从pinned内存上读取数据，如下图（左）所示。

![](https://pic1.zhimg.com/v2-3c34b5f3aa1e0029fc1bc83179975eff_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1039' height='599'></svg>)

但是CPU将数据从pageable 内存拷贝到 临时的 pinned 内存是有时间开销的，而且这个pinned 内存 还只是临时的，所以用完之后会被销毁。所以为了进一步提高效率，我们需要设置`pin_memory=True`，作用就是从一开始就把一部分内存给锁住（上图（右）），这样一来就减少了Host内部的开销，避免了CPU内存拷贝时间。

按照官方的建议[3]是你默认设置为True就对了。

![](https://picx.zhimg.com/v2-190d77afe804e54efaa2a15f64bbeba3_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='809' height='542'></svg>)

## **2. `non_blocking`**

## **2.1 CUDA Default Streams**

> “ 参考 How to Overlap Data Transfers in CUDA C/C++[4] ”

在CUDA里， "**Stream**"是指一系列的操作，这些操作按照主机代码发出的顺序在设备上执行。同一个Stream里的操作是按顺序执行的，而不同Stream里的操作可以交错执行，并且在可能的情况下，它们甚至可以并发执行。

stream有很多种，无特殊指定的话使用的就是默认stream（default stream，也称作 null stream）。它和其他stream的却比就在于：1）如果其他stream上的操作没结束，null stream就不会开始； 2）在device上的其他stream要开始之前，null stream必须先完成。所以说null stream是设备相关操作的同步流（synchronizing stream）。

我们看下面使用default stream的例子，注意cuda代码有个特点，即代码是在Host和Device上通用的，换句话说有的代码可能运行在Host上，有的是在Device上。

```
cudaMemcpy(d_a, a, numBytes, cudaMemcpyHostToDevice);
increment<<<1,N>>>(d_a)
cudaMemcpy(a, d_a, numBytes, cudaMemcpyDeviceToHost);
```

上面3行代码都属于 default stream，因此是按顺序执行的。具体来说从device的角度看，从GPU上启动一个kernel是异步的操作，而data transfer操作是一个blocking或者synchronous操作。

1. 第一行是将数据从Host（CPU内存）拷贝到device（GPU显存）。注意此时还是在Host上执行的，也就是说这个时候Host上的CPU在将数据拷贝到Device上，所以必须得等到第一行运行结束后，才会进入到第二行代码
2. 第二行代码是在Device上启动(launch)和执行(execute)的。注意分成启动和执行两步骤。一旦第二行启动后，主机上的CPU就会立马执行第三行，并不会再去等执行了
3. 第三行代码是将数据从Device拷贝到Host，但是此时的data transfer需要等到第二行Device执行结束才能开始。

通过上面的例子我们知道kernel的启动是异步的，也就是说一旦kernel被启动，Host就可以直接运行下一行代码。比如我们更改一下代码，如下所示。下面代码当第二行kernel启动后，Device就会开始执行`increment`计算，而Host上的CPU会立马执行第三行。此时Host和Device同时都在干活，假设二者的计算时间相等，那么第四行基本上就可以无缝衔接了。

对于Device而言，上下两个代码示例并无差别，但是对于Host而言，其效率提升了。

```
cudaMemcpy(d_a, a, numBytes, cudaMemcpyHostToDevice);
increment<<<1,N>>>(d_a)
myCpuFunction(b)
cudaMemcpy(a, d_a, numBytes, cudaMemcpyDeviceToHost);
```

## **2.2 Non-default Stream**

上面介绍的是default stream，那么就有non-defalut stream，CUDA代码中定义的方法示例如下

```
cudaStream_t stream1;
cudaError_t result;
result = cudaStreamCreate(&stream1)
result = cudaStreamDestroy(stream1)
```

为了给non-defalut stream传输数据，我们使用`cudaMemcpyAsync()`函数，它类似于前一篇示例中讨论的`cudaMemcpy()`函数，但需要将 stream 标识符作为第五个参数传入，即

```
// 将数据从Host传输到Device
result = cudaMemcpyAsync(d_a, a, N, cudaMemcpyHostToDevice, stream1)
```

`cudaMemcpyAsync`在Host上是 **non-blocking** 的，也就是说数据传输kernel一启动，控制权就直接回到Host上了，即Host不需要等数据从Host传输到Device了。

non-default stream上的所有操作相对于 host code 都是 non-blocking 的，即它们不会阻塞Host代码。

所以下面代码中的第二行应该是在第一行启动后就立马执行了。Pytorch官方的建议[5]是`pin_memory=True`和`non_blocking=True`搭配使用，这样能使得data transfer可以overlap computation。

```
x = x.cuda(non_blocking=True)
pre_compute()
...
y = model(x)
```

注意`non_blocking=True`后面紧跟与之相关的语句时，就会需要做同步操作，等到data transfer完成为止，如下面代码示例

```
x=x.cuda(non_blocking=True)
y = model(x)
```

### **微信公众号：AutoML机器学习**

![](https://pic1.zhimg.com/50/v2-87083e55cd41dbef83cc840c142df48a_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='0' height='0'></svg>)

**MARSGGBO♥原创**  
**如有意合作或学术讨论欢迎私戳联系~**  
**邮箱:marsggbo@foxmail.com**   
**2022-03-08 21:06:58**

### **参考资料**

[1] Cuda锁页内存和零复制: *[https://www.findhao.net/easycoding/1349.html](https://link.zhihu.com/?target=https%3A//www.findhao.net/easycoding/1349.html)*

[2] How to Optimize Data Transfers in CUDA C/C++: *[https://developer.nvidia.com/blog/how-optimize-data-transfers-cuda-cc/](https://link.zhihu.com/?target=https%3A//developer.nvidia.com/blog/how-optimize-data-transfers-cuda-cc/)*

[3] Pin Memory: *[https://discuss.pytorch.org/t/when-to-set-pin-memory-to-true/19723](https://link.zhihu.com/?target=https%3A//discuss.pytorch.org/t/when-to-set-pin-memory-to-true/19723)*

[4] How to Overlap Data Transfers in CUDA C/C++: *[https://developer.nvidia.com/blog/how-overlap-data-transfers-cuda-cc/](https://link.zhihu.com/?target=https%3A//developer.nvidia.com/blog/how-overlap-data-transfers-cuda-cc/)*

[5] Non-blocking : *[https://pytorch.org/docs/stable/notes/cuda.html](https://link.zhihu.com/?target=https%3A//pytorch.org/docs/stable/notes/cuda.html)*


---

## 在元宇宙世界中，我要怎么证明「我是我」？

`link: https://www.zhihu.com/question/520721959/answer/2380089014 · created: 1646735847`


现实中我们靠脸认人，当两个人面对面的时候，“我就是我”是一个不需要证明的东西。而元宇宙里这一套可能就不太行了，因为很有可能对面的肌肉金轮真面目是大司马。

![](https://pica.zhimg.com/50/v2-5ca8dfbfb1dceccb09f7de1445990736_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='272' height='178'></svg>)

那在元宇宙里，我怎么证明我是我，你怎么证明你是你呢？这涉及到**数字身份**。

数字身份是一个很广的范畴，其发展经历了中心化数字身份、联邦化数字身份及分布式数字身份。其中，分布式数字身份以区块链、分布式账本等底层技术作为支撑，已将标识属性逐步从人、物扩展到数据，在实现数字对象全面互联互通、隐私身份管理等方面具有重要意义。

2015年，微软等企业在互联网身份大会中首次提出了“分布式数字身份**（Decentralized Identity，DID）**”的概念。目前，DID相关的技术方案由万维网联盟（World Wide Web Consortium，W3C）牵头编制，在传统互联网框架基础上，结合超文本传输协议（HTTP）、通用资源标识符（URL）、互联网通信协议集合（RFC）等多个互联网协议与标准进行建构。DID 充当身份中心。因为用户控制着他们的中心，他们可以决定何时、与谁以及在什么条件下透露他们的数字身份元素。W3C给出了DID的具体文档和相关方法：[Decentralized Identifiers (DIDs) v1.0](https://link.zhihu.com/?target=https%3A//www.w3.org/TR/did-core/)。

![](https://pic1.zhimg.com/v2-fa71dd8ea81fb979877f8ea3c2044657_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1080' height='695'></svg>)

身份认证有很多种实现方法，不过一个重要的前提是互相信任。上海CA联合赛博研究院在2020年国家网络安全宣传周上首次提出“数字信任体系”这一概念，明确了以可信数字身份验证识别和可信数据流通为核心，以五大愿景为建设目标的数字信任体系框架。该信任体系涵盖了跨度很广，也正是因为DID技术本身具备去中心化、身份自主可控等特征，以该技术为核心的可信数字身份体系也将成为实现数据资产可信交互的关键基础。

![](https://picx.zhimg.com/v2-abe9db07c14d49a0f59eaa1d83af6429_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='630' height='481'></svg>)

不同厂商都可以创建自己的元宇宙，但是目前还没有统一的身份认证系统，所以元宇宙的未来是彼此独立还是互通有无？期待吧！

参考:

* [推动构建新型数字信任体系，分布式数字身份技术发展未来可期！ -事件公告-上海市数字证书认证中心](https://link.zhihu.com/?target=https%3A//www.sheca.com/notices/e98b2d88c25a4aba82e40320960f8e02)
* [元宇宙语境下数字身份的价值、机遇和挑战](https://link.zhihu.com/?target=https%3A//vr.sina.com.cn/2021-12-08/doc-ikyakumx2735949.shtml)


---

## 全国人大代表建议「支持年轻人争当产业工人，而非从事快递外卖、网络直播等行业」，这反映了哪些问题？

`link: https://www.zhihu.com/question/520144586/answer/2375992757 · created: 1646497854`


为什么不建议 支持工厂提高工人待遇 ᥬ ᭄ᥬ ᭄


---

## 如何看待人大代表建议「被拐妇女拐入地基层政府主要负责人五年内不得被提拔」？

`link: https://www.zhihu.com/question/519814571/answer/2374340922 · created: 1646397948`


可以换个角度吗，就像抓黄赌毒一样，定时给kpi，作为升职的一种参考指标？然后群众举报有奖？


---

## 如何看待目前国内「隐私计算」行业现状，市场发展有哪些趋势？

`link: https://www.zhihu.com/question/519824410/answer/2373651246 · created: 1646370107`


隐私计算（Privacy-preserving computation） 是指在保证数据提供方不泄露原始数据的前提下，对数据进行分析计算的一系列信息技术，实现数据在流通与融合过程中的“可用不可见”。

2021年12月21日，由中国信息通信研究院、中国通信标准化协会指导承办的**可信隐私计算高峰论坛暨数据安全产业峰会**以线上会议形式召开，这个会议从政策、技术、产业、应用等探讨2021年隐私计算行业的发展，这里做个简单总结吧。

## 政策

自2016年工信部发布《大数据产业发展规划(2016-2020年)》后，多个部门相继发布多分鼓励隐私计算的文件，这使得数据的安全与保护，特别是数据流通过程中的合规性，成为持续稳定的市场需求，而不再是短暂的监管应对行为。

![](https://pic1.zhimg.com/v2-162b6ce868182a2d8a3ac2ea49dde267_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1381' height='292'></svg>)

## 技术

隐私计算中比较典型的技术路线包括

* **多方安全计算（Secure multi-party computation, MPC）**
* **联邦学习 (Federated Learning, FL)**
* **可信执行环境（Trusted Execution Environment, TEE)**
* **同态加密（Homomorphic Encryption, HE）**
* **零知识证明（Zero-Knowledge Proof, ZKP）**
* **差分隐私（Differential Privacy， DP）**

就我自己比较熟悉的深度学习领域而言，联邦学习目前属于较热的研究领域，还有蛮多需要研究的地方。

## 产业

在政府多部门的政策要求下，越来越多的企业加入了隐私计算这一竞争赛道。随着投入的加大，这方面招聘需求应该也会增加，大家应该可以考虑换个赛道卷了~

![](https://pic1.zhimg.com/v2-2978e5ea4f1d47ac83fd3273c1772b18_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1056' height='595'></svg>)

## 应用

就应用而言，需要较大的可能就是医疗和金融行业了。以新冠为例，目前各医院或相关机构都有大量的患者信息，但是出于保护患者隐私的目的，这些信息彼此之间是不互通的，这样也就造成了一个又一个的信息孤岛。如果想利用深度学习来帮助诊断，那么但各医院和机构的数据训练出来的模型可能没法直接用在其他医院。所以近期很多工作开始尝试使用联邦学习来在不同医院间大气数据桥梁，同时有保证数据隐私不外泄

![](https://picx.zhimg.com/v2-091f5788e4be5bef1a48507fd9e521b7_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1061' height='607'></svg>)

来源：隐私计算联盟、中国信通院云大所” [信通院发布2021年隐私计算行业观察](https://link.zhihu.com/?target=https%3A//www.secrss.com/articles/37491)


---

## SCI论文润色究竟是润色什么？

`link: https://www.zhihu.com/question/49375540/answer/2311811204 · created: 1642237811`


一个好的配色某种程度上能把像屎一样的论文雕出花来，这里根据网上已有的文章以及平时读论文时觉得好看的论文配色，做个总结分享。

## Color 1

```
#8ECFC9
#FFBE7A
#FA7F6F
#82B0D2
#BEB8DC
#E7DAD2
```

![](https://pic1.zhimg.com/v2-ec95c2fde36e02a0f2e4784c0f28b3e0_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='868' height='641'></svg>)

## Color 2

```
#2878b5
#9ac9db
#f8ac8c
#c82423
#ff8884
```

![](https://pic1.zhimg.com/v2-45465c466553835ec87ae9f268c814ac_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='908' height='637'></svg>)

## Color 3

```
#F27970
#BB9727
#54B345 
#32B897
#05B9E2
#8983BF
#C76DA2
```

![](https://picx.zhimg.com/v2-f6327b7ba5c43a28805ca31459986aa2_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='790' height='444'></svg>)

## Color 4

```
#A1A9D0
#F0988C
#B883D4
#9E9E9E
#CFEAF1
#C4A5DE
#F6CAE5
#96CCCB
```

![](https://picx.zhimg.com/v2-1df33c64e3ed04d3f5f003ebf4286b53_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='876' height='572'></svg>)

## Color 5

![](https://picx.zhimg.com/v2-ea563c74a9e5d93b158ecb5d701c5761_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='729' height='455'></svg>)

## Color 6

系列色——十六进制颜色码：

63b2ee - 76da91 - f8cb7f - f89588 - 7cd6cf - 9192ab - 7898e1 - efa666 - eddd86 - 9987ce - 63b2ee - 76da91

系列色——RGB颜色值：

（99,178,238）-（118,218,145）-（248,203,127）-（248,149,136）-（124,214,207）-（145,146,171）-（120,152,225）-（239,166,102）-（237,221,134）-（153,135,206）-（99,178,238）-（118,218,145）

![](https://pic1.zhimg.com/50/v2-5475aff589e2d2c67522c2e483e39801_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='420' height='181'></svg>)

## Color 7

系列色——十六进制颜色码：

3b6291 - 943c39 - 779043 - 624c7c - 388498 - bf7334 - 3f6899 - 9c403d - 7d9847 - 675083 - 3b8ba1 - c97937

系列色——RGB颜色值：

（59,98,145）-（148,60,57）-（119,144,67）-（98,76,124）-（56,132,152）-（191,115,52）-（63,104,153）-（156,64,61）-（125,152,71）-（103,80,131）-（59,139,161）-（201,121,55）

![](https://pic1.zhimg.com/50/v2-e3230b6471ab57d5672bd4052dd9ae98_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='420' height='182'></svg>)

## Color 8

系列色——十六进制颜色码：

002c53 - ffa510 - 0c84c6 - ffbd66 - f74d4d - 2455a4 - 41b7ac

系列色——RGB颜色值：

（0,44,83）-（255,165,16）-（12,132,198）-（255,189,102）-（247,77,77）-（36,85,164）-（65,183,172）

![](https://pica.zhimg.com/v2-f29182950b148825bbe82db06376c6bc_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='422' height='182'></svg>)

* [【SCI】中文核心、SCI论文绘图和图片配色\_浪里小飞侠的博客-CSDN博客\_sci配色](https://link.zhihu.com/?target=https%3A//blog.csdn.net/m0_37882192/article/details/110917449%3Fspm%3D1001.2101.3001.6650.2%26utm_medium%3Ddistribute.pc_relevant.none-task-blog-2%257Edefault%257ECTRLIST%257Edefault-2.pc_relevant_default%26depth_1-utm_source%3Ddistribute.pc_relevant.none-task-blog-2%257Edefault%257ECTRLIST%257Edefault-2.pc_relevant_default%26utm_relevant_index%3D5)
* 参考[1] [高质量论文配图配色（附RGB值及16进制码）\_slandarer的博客-CSDN博客\_论文图片配色](https://link.zhihu.com/?target=https%3A//blog.csdn.net/slandarer/article/details/114157177)
* [论文配色方案（自用）\_minopus的博客-CSDN博客\_论文配色](https://link.zhihu.com/?target=https%3A//blog.csdn.net/sinat_41299610/article/details/106912048%3Fspm%3D1001.2101.3001.6650.4%26utm_medium%3Ddistribute.pc_relevant.none-task-blog-2%257Edefault%257ECTRLIST%257Edefault-4.pc_relevant_default%26depth_1-utm_source%3Ddistribute.pc_relevant.none-task-blog-2%257Edefault%257ECTRLIST%257Edefault-4.pc_relevant_default%26utm_relevant_index%3D7)


---

## 采用数据驱动的方法解决某个任务时，怎么克服长尾分布带来的问题？

`link: https://www.zhihu.com/question/509316826/answer/2295475091 · created: 1641132676`


[ICLR2020 | Decoupling representation and classifier for long-tailed recognition](https://zhuanlan.zhihu.com/p/452668798)
> Decoupling representation and classifier for long-tailed recognition  
> 代码链接：[https://github.com/facebookresearch/classifier-balancing](https://link.zhihu.com/?target=https%3A//github.com/facebookresearch/classifier-balancing)

## **1. 主要贡献**

长尾分布数据集是目前训练模型的一个很大的挑战，模型在这类数据集上通常会在 head-classes (即数量较多的类别）上overfitting，而在tail-classes（即数量较少的类别）上under-fitting。解决imbalanced的问题常用的方法有：1）re-sampling dataset；2）re-weighting loss function; 3）把head-classes的特征迁移给tail-classes等。

该论文通过设置一系列的实验，发现以下现象：

* 把训练过程解耦成了两部分：**1）representations learning** （即特征提取）和 **2） classification** 能够有效提高模型在长尾分布数据集上的性能
* 作者发现以下两种方法（在 representations learning 过程中同时优化训练分类器）能提高性能：

+ 固定feature，然后使用class-balanced 采样策略retrain分类器
+ 对分类器的权重加约束（正则）也可以提高性能

* 以上方式用在像ResNet这些常用模型上也能在Long-Tailed (LT)数据集上取得不错的效果

## **2. Representations Learning**

## **2.1 Data Re-sampling**

每个样本被采样的概率可以表示成如下：![C](https://www.zhihu.com/equation?tex=C)表示类别数量, ![n_j](https://www.zhihu.com/equation?tex=n_j)表示第 j 类的样本数，![q\in\{0,1,0.5\}](https://www.zhihu.com/equation?tex=q%5Cin%5C%7B0%2C1%2C0.5%5C%7D)分别表示不同的采样策略。

![p_{j}=\frac{n_{j}^{q}}{\sum_{i=1}^{C} n_{i}^{q}} \tag{1} ](https://www.zhihu.com/equation?tex=p_%7Bj%7D%3D%5Cfrac%7Bn_%7Bj%7D%5E%7Bq%7D%7D%7B%5Csum_%7Bi%3D1%7D%5E%7BC%7D+n_%7Bi%7D%5E%7Bq%7D%7D+%5Ctag%7B1%7D+)

1. Instance-balanced (IB) sampling：这个就是最普通也是最常用的采样策略，即每个样本被采样的概率均等，对应公式(1)中的 ![q=1](https://www.zhihu.com/equation?tex=q%3D1)。
2. Class-balanced (CB) sampling: 这个就是说每个类别被采样的概率相等，比如我们总共有4类，每次采样的batch包含64个样本，那么每个batch中一定包含4个类别，每个类别的数量都是16，只不过类别里的样本被采样的概率就是相等的。具体的实现可以参考`catalyst.data.sampler.BatchBalanceClassSampler` [[代码](https://link.zhihu.com/?target=https%3A//github.com/catalyst-team/catalyst/blob/678dc06eda1848242df010b7f34adb572def2598/catalyst/data/sampler.py%3F_pjax%3D%2523js-repo-pjax-container%252C%2520div%255Bitemtype%253D%2522http%253A%252F%252Fschema.org%252FSoftwareSourceCode%2522%255D%2520main%252C%2520%255Bdata-pjax-container%255D%23L111)]。公式(1)中![q=0](https://www.zhihu.com/equation?tex=q%3D0)时表示每个类别被采样的概率相等
3. Progressively-balanced sampling：这个其实就是将上面 Instance-和Class- balanced做了结合，即下式， ![t,T](https://www.zhihu.com/equation?tex=t%2CT)分别表示当前的epoch和总的epoch数。

![p_{j}^{\mathrm{PB}}(t)=\left(1-\frac{t}{T}\right) p_{j}^{\mathrm{IB}}+\frac{t}{T} p_{j}^{\mathrm{CB}} \tag{2} ](https://www.zhihu.com/equation?tex=p_%7Bj%7D%5E%7B%5Cmathrm%7BPB%7D%7D%28t%29%3D%5Cleft%281-%5Cfrac%7Bt%7D%7BT%7D%5Cright%29+p_%7Bj%7D%5E%7B%5Cmathrm%7BIB%7D%7D%2B%5Cfrac%7Bt%7D%7BT%7D+p_%7Bj%7D%5E%7B%5Cmathrm%7BCB%7D%7D+%5Ctag%7B2%7D+)

1. Square-root sampling: 对应公式(1)中![q=0.5](https://www.zhihu.com/equation?tex=q%3D0.5)

## **2.2 Loss re-weighting**

比较常见的方法有 focal loss，或者给tail-classes赋予更高的权重等

## **3. Classification**

上一节总结了常用的学习特征的训练方法，这一节总结常用的训练分类器的方法。

1. **Classifier Re-training (cRT)**： 这个就是比较常规的做法，即把 feature representations固定住，然后使用class-balanced sampling 对classifier做finetune
2. **Nearest Class Mean classifier (NCM)**： 这个是非参数方法，即先使用训练集计算出 ![C](https://www.zhihu.com/equation?tex=C) 个类别的中心 feature tensor，然后每次做预测的时候使用 cosine similarity或者 MSE loss计算出每个样本离这些中心feature的距离，离谁更近就预测属于哪一类，这类似于KNN算法
3. ![\tau](https://www.zhihu.com/equation?tex=%5Ctau)**-normalized classifier** ：我们知道在 TL 数据集上，模型在预测的时候会倾向于把样本都预测成类别多的那一类，极端情况甚至全都预测成同一类。假设这一类是第 ![i](https://www.zhihu.com/equation?tex=i) 类，这个时候很有可能是因为最后预测器（即全连接层）的第 ![i](https://www.zhihu.com/equation?tex=i) 类的权重值远大于其他类别的权重，所以一种解决办法就是给分类器的权重加上正则项，公式如下，![\tau](https://www.zhihu.com/equation?tex=%5Ctau) 是一个超参数，当![\tau=1](https://www.zhihu.com/equation?tex=%5Ctau%3D1)时，下式就等价于普通的 L2正则。一般取值是在0到1之间。

![\widetilde{w_{i}}=\frac{w_{i}}{\left\|w_{i}\right\|^{\tau}} \tag{3} ](https://www.zhihu.com/equation?tex=%5Cwidetilde%7Bw_%7Bi%7D%7D%3D%5Cfrac%7Bw_%7Bi%7D%7D%7B%5Cleft%5C%7Cw_%7Bi%7D%5Cright%5C%7C%5E%7B%5Ctau%7D%7D+%5Ctag%7B3%7D+)

1. **Learnable weight scaling (LWS)**：公式3中的分母是依赖于权重值，当然我们也可以让分母设置成一个可学习的参数 ![f_i](https://www.zhihu.com/equation?tex=f_i)，它的初始值和公式3一致（如下式）。在优化 ![f_i](https://www.zhihu.com/equation?tex=f_i)的过程中，representations和classifier的参数都是固定住的。

![\widetilde{w_{i}}=f_{i} * w_{i}, \text { where } f_{i}=\frac{1}{\left\|w_{i}\right\|^{\tau}} \tag{4} ](https://www.zhihu.com/equation?tex=%5Cwidetilde%7Bw_%7Bi%7D%7D%3Df_%7Bi%7D+%2A+w_%7Bi%7D%2C+%5Ctext+%7B+where+%7D+f_%7Bi%7D%3D%5Cfrac%7B1%7D%7B%5Cleft%5C%7Cw_%7Bi%7D%5Cright%5C%7C%5E%7B%5Ctau%7D%7D+%5Ctag%7B4%7D+)

## **4. 实验**

## **4.1 实验设置**

因为长尾分布数据集中有的类别可能只有几张图片，有的可能有上千张图片，所以之前常用的Acc并不能有效表达出模型性能的好坏，所以后面论文给出了不同类别的分类准确率

* All: 所有类别的acc
* Many-shot: 图片数量大于100的类别的acc
* Medium-shot：图片数量在20到100之间的类别的acc
* Few-shot：图片数量小于20的类别的acc

## **4.2 Sampling Strategies & Decoupled Learning**

![](https://picx.zhimg.com/v2-c0946b08e3e272bb7768bfea5ec0df7e_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1193' height='551'></svg>)

从Figure1我们能看到一下几个现象：

1. 只看4个图像的 **Joint** （即backbone和classifier同时训练）那一列，我们可以看到随着采样策略的改善（从Instance到Progressively-balanced)，Medium和Few 类别以及整体（All）的accuracy是稳步提升的。但是对于 Many类别，它的accuracy在 Instance-balanced情况下是最高的，这个也符合预期，因为这个时候模型会更加侧重于数据多的类别。所以实验结果表明 **对于Joint的训练模式，数据采样非常重要。**
2. 论文中给出了3个decoupled learning的方法，分别是 NCM, cRT和![\tau](https://www.zhihu.com/equation?tex=%5Ctau)-norm。上图可以看到除了Many-shot，这三个方法在其他3个类别上都比Joint训练模式表现更好
3. 一个很有意思的实验结果是，在3个解耦学习的方法上，IB 采样策略训练得到的模型反而表现最好。换句话说，**如果我们使用解耦的训练方式，我们可能不用太花心思在数据采样上**。

Figure 2 (左) 给出了不同训练模式下 classifier权重的norm值。图中Class Index是按照类别包含的样本数降序排列的，即class-0含有组多样本。

* 可以看到对于Joint模式，weight norm值是逐渐减少的，即class-0的norm值最大。显然当这个norm值远大于其他类别的norm值时，模型很可能会将所有样本都只预测成class-0。
* cRT, ![\tau](https://www.zhihu.com/equation?tex=%5Ctau)-norm和LWS都有效提高了Medium和Few classes的weight norm。

Figure 2 (右) 给出了 ![\tau](https://www.zhihu.com/equation?tex=%5Ctau)-norm方法![\tau](https://www.zhihu.com/equation?tex=%5Ctau)对结果的影响。可以看到增加τ的大小能明显改善 Few classes的准确率，但是同时Many classes会对应减少。Medium和All 的准确率先增后降，而且后期降得特别厉害，所以τ值的选择也比较重要。

![](https://picx.zhimg.com/v2-c26fe28ced94b3d7d22bd19258c98f1c_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1202' height='669'></svg>)

## **4.3 实验结果对比**

作者在3个TL数据集上做了实验，可以看到提升效果都比较明显。

![](https://pic1.zhimg.com/v2-e978c26c393dda87ea9c42dbadf94df8_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='940' height='938'></svg>)

### **微信公众号：AutoML机器学习**

![](https://pic1.zhimg.com/50/v2-87083e55cd41dbef83cc840c142df48a_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='0' height='0'></svg>)

**MARSGGBO♥原创**  
**如有意合作或学术讨论欢迎私戳联系~**  
**邮箱:marsggbo@foxmail.com**


---

## ICLR 2022有哪些值得关注的投稿？

`link: https://www.zhihu.com/question/490962362/answer/2283679130 · created: 1640271815`


## 

## **1. 主要创新**

《UniNet: Unified Architecture Search with Convolution, Transformer, and MLP》是ICLR2022的一篇投稿论文，目前还没出结果。这里总结一下该工作的主要创新和贡献点：

1. UniNet是第一个将卷积，Transformer和MLP统一起来进行搜索的工作
2. 论文发现在融合上述三种不同模块的时候，传统的下采样模块（如stride=2的卷积）会成为模型性能的瓶颈。所以作者提出了 context-aware down-sampling modules (DSM), 包含 local-global-DSM (LG\_DSM) 和 global-DSM (G-DSM)
3. UniNet性能超过了efficientnet和SwinTransformer

## **2. 相关工作**

* Transformer：[ViT](https://link.zhihu.com/?target=https%3A//www.notion.so/Vision-Transformer-An-Image-is-Worth-16x16-Words-Transformers-for-Image-Recognition-at-Scale-55fee99eb3304874bc47c73b70e0aa77), [DeiT](https://link.zhihu.com/?target=https%3A//www.notion.so/Training-data-efficient-image-transformers-distillation-through-attention-DeiT-4c7d897e346245bc9ae6a256ad8a1374)
* MLP: [MLP-Mixer](https://link.zhihu.com/?target=https%3A//www.notion.so/MLP-Mixer-An-all-MLP-Architecture-for-Vision-bee3beaa4e01485e844355345899a3ce), [ResMLP](https://link.zhihu.com/?target=https%3A//www.notion.so/ResMLP-Feedforward-networks-for-image-classification-with-data-efficient-training-39be756bc46648198296460f9ace745c)
* 混合模型:

+ ConViT (ICML2021) [1] ：unify convolution and self-attention with gated positional self-attention (GPSA) and is more sample-efficient than self-attention.

![](https://pica.zhimg.com/v2-5c3084b3cf4e1c87a3f1b9471ece1809_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='654' height='860'></svg>)



+ CvT (ICCV2021) [2]：incorporate self-attention and convolution by generating Q, K, and V in self-attention with convolution.

![](https://pic1.zhimg.com/v2-341368d7f0684f852895c6962fd26ca2_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1565' height='788'></svg>)



+ CeiT [3]：replace the original patchy stem with convolutional stem and add depth-wise convolution to FFN layer, which obtains fast convergence and better performance.

![](https://pica.zhimg.com/v2-b2f1c998ee7a26c978eaa9fa9caa03be_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1567' height='736'></svg>)

## **3. 方法**

## **3.1 Unified Search Space**

搜索空间如下图所示。

![](https://pic1.zhimg.com/v2-92d5740e21a5d10eec0c796f2db44183_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1143' height='331'></svg>)

* GOP （General Operations）：包含 Convolution, transformer,和 MLP。三种操作都之采用了类似inverted residual的设计方式，即先把原来的通道数c 通过映射扩大ec，然后在通过映射还原为 c，各操作公式如下：

+ conv: ![y=x+op(x),](https://www.zhihu.com/equation?tex=y%3Dx%2Bop%28x%29%2C) 其中 ![op(x) = Proj_{ec\rightarrow{c}}(Conv(Proj_{c\rightarrow{ec}}(x)))](https://www.zhihu.com/equation?tex=op%28x%29+%3D+Proj_%7Bec%5Crightarrow%7Bc%7D%7D%28Conv%28Proj_%7Bc%5Crightarrow%7Bec%7D%7D%28x%29%29%29)
+ transformer: ![y=y'+FFN(y')](https://www.zhihu.com/equation?tex=y%3Dy%27%2BFFN%28y%27%29)，其中 ![y'=x+SelfAttention(x)](https://www.zhihu.com/equation?tex=y%27%3Dx%2BSelfAttention%28x%29), ![FFN(y')=Proj_{ec\rightarrow{c}}(Conv(Proj_{c\rightarrow{ec}}(y')))](https://www.zhihu.com/equation?tex=FFN%28y%27%29%3DProj_%7Bec%5Crightarrow%7Bc%7D%7D%28Conv%28Proj_%7Bc%5Crightarrow%7Bec%7D%7D%28y%27%29%29%29)
+ MLP: ![y=y'+FFN(y')](https://www.zhihu.com/equation?tex=y%3Dy%27%2BFFN%28y%27%29)，其中 ![y'=x+MLP(x)](https://www.zhihu.com/equation?tex=y%27%3Dx%2BMLP%28x%29), ![FFN(y')=Proj_{ec\rightarrow{c}}(Conv(Proj_{c\rightarrow{ec}}(y')))](https://www.zhihu.com/equation?tex=FFN%28y%27%29%3DProj_%7Bec%5Crightarrow%7Bc%7D%7D%28Conv%28Proj_%7Bc%5Crightarrow%7Bec%7D%7D%28y%27%29%29%29)

* DSM （Down-sampling Modules）

+ L-DSM: 这个就是常规的下采样模块，比如stride=2的卷积操作或者 max-pooling。这些是对local context做下采样
+ LG-DSM: 是局部和全局信息都会考虑的下采样模块。可以看到下采样是通过一个stride=2的卷积操作实现的，这里应该就是提取的local context。而attention机制呢就是一个全局的信息了。因为是2d卷积，所以需要先把input reshape成spatial grid，卷积计算完之后再flatten成原来的形状。
+ G-DSM：和LG-DSM的区别就是用了1d的卷积操作，但是论文里并没有解释为什么这个时候就不会保留local context了。

![](https://picx.zhimg.com/v2-f9a6b38d82606593b063ba8060a3387b_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='722' height='343'></svg>)

完整的搜索空间参数设置如下：

* GOP: { SA (self-attention), LSA (local SA), Conv, Depth-Wise Conv, MLP }
* e (通道数expansion比例)： { 2,3,4,5,6 }
* 模型是基于efficientnet搜索的，

+ 通道 channel缩放比例搜索空间： { 0.5, 0.75, 1.0, 1.25, 1.5 }
+ 堆叠个数 repeats： { -2, -1, 0, 1, 2 }
+ 总共有 K=5 个stages，每个stage的搜索空间大小是 （#channels \* #repeats） 5\*5=125

## **3.2 搜索算法**

搜索算法基于强化学习 PPO算法，所有候选操作借鉴 [Fnas: Uncertainty-aware fast neural architecture search](https://link.zhihu.com/?target=https%3A//www.notion.so/Fnas-Uncertainty-aware-fast-neural-architecture-search-8200bb38374b447bb7d676a667a23648) [4] 的做法把搜索空间映射成了一组tokens。论文也没有给很多细节，感兴趣的可以看看FNAS那篇论文。

## **4. 实验结果**

## **4.1 模型结构**

搜素到的模型结构如下表，可以看到每个stage的GOP都是固定的，这样一来搜索空间其实要少很多了，本来还以为是每一层的操作都要搜索。不过可以看到的是shallow stage采用的都是卷积操作，DSM也是传统的L-DSM（即stride=2的卷积层），可以理解成，浅层还是需要卷积来提取特征。

到了深层，GOP就选了Transformer和LG-DSM，可以理解成此时模型倾向于去提取全局的信息，这个也比较符合直觉。

不过有意思的是MLP貌似被遗忘在角落了。。。

![](https://pic1.zhimg.com/v2-411bf283347aec9940df18b3d827496e_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='576' height='372'></svg>)

## **4.2 ImageNet上的结果**

结果一个字：好。就完事了hhh

![](https://picx.zhimg.com/v2-afa93e72fc1baae0c1a95a6fe8d9cbd7_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='739' height='753'></svg>)

## **5. Ablation Study**

作者做了实验去证明他们提出的 GOP和 DSM模块的有效性。

## **5.1 GOP vs. 纯Conv**

可以看到用GOP比纯Conv高了1.4个点。

![](https://pic1.zhimg.com/v2-aef4c39e0a93ec17a54e05ce10c768de_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='713' height='186'></svg>)

## **5.2 不同DSM模块的有效性验证和迁移性实验**

Table 6 对比了将 DSM全都替换成某一种下采样模块后模型的性能变化，可以看到如果替换成 G-DSM后性能掉的最多，而LG-DSM性能保持的还不错，但是FLOPs和参数量都有一定的增加。L-DSM效果也还不错的亚子

![](https://picx.zhimg.com/v2-a5e761d16fe541db1d114ef5b4ba405d_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='588' height='389'></svg>)

作者还将DSM模块放到了Swin-Transformer (ST)和PVT-Tiny 这些模型上去，这两个模型都是总共由4个stage组成，所以作者把前两个stage的下采样模块替换成了L-DSM，最后两个stage替换成了 LG-DSM，结果如Table 7所示，可以看到都有一定的性能提升。

![](https://picx.zhimg.com/v2-1d180164911757df529783cba9e0aac2_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='548' height='381'></svg>)

## 个人看法

这篇论文标题是设计了一个把Convolution,Transformer和MLP一统江湖的搜索空间，但是仔细看了论文后感觉就是把每个stage的op换成了对应的操作而已，而且每个stage只是使用某一种操作，感觉标题略微优点标题党，不够也可以理解哈哈​。当然如何更加高效细腻度地基于三种OP进行搜索​也是一个值得探索的问题。

## **References**

* [1] St´ephane d’Ascoli, Hugo Touvron, Matthew Leavitt, Ari Morcos, Giulio Biroli, and Levent Sagun. [ConViT: Improving vision transformers with soft convolutional inductive biases](https://link.zhihu.com/?target=https%3A//www.notion.so/ConViT-Improving-vision-transformers-with-soft-convolutional-inductive-biases-d10425c9db5a479eafb0c5fedb6f339e). arXiv preprint arXiv:2103.10697, 2021.
* [2] Haiping Wu, Bin Xiao, Noel Codella, Mengchen Liu, Xiyang Dai, Lu Yuan, and Lei Zhang. [CvT: Introducing convolutions to vision transformers.](https://link.zhihu.com/?target=https%3A//www.notion.so/CvT-Introducing-convolutions-to-vision-transformers-fe917e96f329448f9d8522b6e4b6622d) arXiv preprint arXiv:2103.15808, 2021.
* [3] Kun Yuan, Shaopeng Guo, Ziwei Liu, Aojun Zhou, Fengwei Yu, and Wei Wu. Incorporating convolution designs into visual transformers. arXiv preprint arXiv:2103.11816, 2021.
* [4] Jihao Liu, Ming Zhang, Yangting Sun, Boxiao Liu, Guanglu Song, Yu Liu, and Hongsheng Li. Fnas: Uncertainty-aware fast neural architecture search. arXiv preprint arXiv:2105.11694, 2021a.

### **微信公众号：AutoML机器学习**

![](https://picx.zhimg.com/50/v2-87083e55cd41dbef83cc840c142df48a_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='0' height='0'></svg>)

**MARSGGBO♥原创**  
**如有意合作或学术讨论欢迎私戳联系~**  
**邮箱:marsggbo@foxmail.com**


---

## 如何评价 ICCV 2021 的论文接收结果？有哪些值得关注的研究？

`link: https://www.zhihu.com/question/473907895/answer/2280706551 · created: 1640095826`


# BossNAS: Exploring Hybrid CNN-transformers with Block-wisely Self-supervised NAS

## **1. 主要创新点**

本文基于block-wise搜索空间做了以下的改进：

1. 提出ensemble bootstrapping训练策略，这样可以不用教师网络，避免引入biased supervision （candidate preference和teacher preference）
2. 提出了 非监督的评估指标（公式5)
3. 在三个不同的搜索空间和数据集上都取得了不错的效果

1. 基于MBConv的搜索空间，在ImageNet上取得了0.78的Spearman相关系数
2. 基于NATS-Bench ![S_S](https://www.zhihu.com/equation?tex=S_S)搜索空间，在CIFAR-100上取得了0.76的Spearman性关系数
3. 提出了HyTra (即CNN+Transformer混合模型)的搜索空间，在ImageNet上取得82.5%的accuracy，比EfficientNet高2.4%。

## **2. Methods**

## **2.1 Ensemble Boostrapping训练Supernet**

BossNAS整体的的训练方式和[DNA](https://link.zhihu.com/?target=https%3A//www.notion.so/Blockwisely-supervised-neural-architecture-search-with-knowledge-distillation-8097fd741d4846f1a4b5473407073116)不太一样，在DNA里，学生网络每个block彼此之间的训练是独立开来的，比如学生网络 ![block_k](https://www.zhihu.com/equation?tex=block_k)的输入是教师网络 ![block_{k-1}](https://www.zhihu.com/equation?tex=block_%7Bk-1%7D)的输出，然后使用知识蒸馏(MSE loss)来使得学生网络的输出尽可能和教师网络输出保持一致。BossNAS认为这样会使得搜到的子网和教师网络高度相关，即搜索结果是带有bias的。

![](https://pica.zhimg.com/v2-e529c3b54283e7b12857d63ede25ec84_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1092' height='404'></svg>)

为了解决原本block独立训练的问题，BossNAS提出了Ensemble Bootstrapping策略

记![{S(W, A), T (W^T , α^T )}](https://www.zhihu.com/equation?tex=%7BS%28W%2C+A%29%2C+T+%28W%5ET+%2C+%CE%B1%5ET+%29%7D)分别表示学生和教师网络（由权重W和结构A决定)。为了教师网络带来的束缚（即学生网络很可能会非常像教师网络的结构，导致bias和diversity低），教师网络和学生网络是一样的，即![\alpha^T=A](https://www.zhihu.com/equation?tex=%5Calpha%5ET%3DA)。更具体地说，教师网络是用**EMA**策略更新的Supernet，学生网络就是常规的Supernet。

假设某个搜索阶段，我们采样了 p 个不同的子网，因为使用自监督训练方式，所以对于同一个样本会有 p 组不同的增强样本 （上图中 p=2），所谓 Ensemble Bootstrapping其实就是教师网络的第 k个block的输出是这 p 个网络输出的平均值，记为

![\widehat{\mathcal{T}_{k}}\left(\left\{\boldsymbol{\alpha}_{p}\right\} ;\left\{\boldsymbol{x}_{p}^{\prime}\right\}\right)=\frac{1}{|p|} \sum_{p=1}^{|p|} \mathcal{T}_{k}\left(\mathcal{W}^{\bullet}, \boldsymbol{\alpha}_{p} ; \boldsymbol{x}_{p}^{\prime}\right) \tag{1} ](https://www.zhihu.com/equation?tex=%5Cwidehat%7B%5Cmathcal%7BT%7D_%7Bk%7D%7D%5Cleft%28%5Cleft%5C%7B%5Cboldsymbol%7B%5Calpha%7D_%7Bp%7D%5Cright%5C%7D+%3B%5Cleft%5C%7B%5Cboldsymbol%7Bx%7D_%7Bp%7D%5E%7B%5Cprime%7D%5Cright%5C%7D%5Cright%29%3D%5Cfrac%7B1%7D%7B%7Cp%7C%7D+%5Csum_%7Bp%3D1%7D%5E%7B%7Cp%7C%7D+%5Cmathcal%7BT%7D_%7Bk%7D%5Cleft%28%5Cmathcal%7BW%7D%5E%7B%5Cbullet%7D%2C+%5Cboldsymbol%7B%5Calpha%7D_%7Bp%7D+%3B+%5Cboldsymbol%7Bx%7D_%7Bp%7D%5E%7B%5Cprime%7D%5Cright%29+%5Ctag%7B1%7D+)

上面公式中的 ![\mathcal{W}^{\bullet}](https://www.zhihu.com/equation?tex=%5Cmathcal%7BW%7D%5E%7B%5Cbullet%7D) 表示教师网络的权重，是使用EMA更新的，即 ![\mathcal{W}_{t}^{\bullet}=\tau \mathcal{W}_{t-1}^{\bullet}+(1-\tau) \mathcal{W}_{t}](https://www.zhihu.com/equation?tex=%5Cmathcal%7BW%7D_%7Bt%7D%5E%7B%5Cbullet%7D%3D%5Ctau+%5Cmathcal%7BW%7D_%7Bt-1%7D%5E%7B%5Cbullet%7D%2B%281-%5Ctau%29+%5Cmathcal%7BW%7D_%7Bt%7D), 其中 ![\mathcal{W}_t](https://www.zhihu.com/equation?tex=%5Cmathcal%7BW%7D_t)是online Supernet（学生网络）的权重。

因为每个block彼此之间训练独立，所以每个block优化方式是一样的，这里给出学生网络第k个block的优化函数。简单理解就是子网的输出要和ensemble的结果接近，损失函数使用的也是MSE。

![\begin{aligned} &\mathcal{W}_{k}^{*}=\underset{\mathcal{W}_{k}}{\arg \min } \sum_{p=1}^{|P|} \mathcal{L}_{\text {train }}\left(\left\{\mathcal{W}_{k}, \mathcal{W}_{k}^{\bullet}\right\},\left\{\boldsymbol{\alpha}_{p}\right\} ; \boldsymbol{x}\right) \\ &\text { where } \quad \mathcal{L}_{\text {train }}\left(\left\{\mathcal{W}_{k}, \mathcal{W}_{k}^{\bullet}\right\},\left\{\boldsymbol{\alpha}_{p}\right\} ; \boldsymbol{x}\right) \\ &=\left\|\mathcal{S}_{k}\left(\mathcal{W}_{k}, \boldsymbol{\alpha}_{p} ; \boldsymbol{x}_{p}\right)-\widehat{\mathcal{T}_{k}}\left(\mathcal{W}_{k}^{\bullet},\left\{\boldsymbol{\alpha}_{p}\right\} ;\left\{\boldsymbol{x}_{p}^{\prime}\right\}\right)\right\|_{2}^{2} \end{aligned} \tag{2}](https://www.zhihu.com/equation?tex=%5Cbegin%7Baligned%7D+%26%5Cmathcal%7BW%7D_%7Bk%7D%5E%7B%2A%7D%3D%5Cunderset%7B%5Cmathcal%7BW%7D_%7Bk%7D%7D%7B%5Carg+%5Cmin+%7D+%5Csum_%7Bp%3D1%7D%5E%7B%7CP%7C%7D+%5Cmathcal%7BL%7D_%7B%5Ctext+%7Btrain+%7D%7D%5Cleft%28%5Cleft%5C%7B%5Cmathcal%7BW%7D_%7Bk%7D%2C+%5Cmathcal%7BW%7D_%7Bk%7D%5E%7B%5Cbullet%7D%5Cright%5C%7D%2C%5Cleft%5C%7B%5Cboldsymbol%7B%5Calpha%7D_%7Bp%7D%5Cright%5C%7D+%3B+%5Cboldsymbol%7Bx%7D%5Cright%29+%5C%5C+%26%5Ctext+%7B+where+%7D+%5Cquad+%5Cmathcal%7BL%7D_%7B%5Ctext+%7Btrain+%7D%7D%5Cleft%28%5Cleft%5C%7B%5Cmathcal%7BW%7D_%7Bk%7D%2C+%5Cmathcal%7BW%7D_%7Bk%7D%5E%7B%5Cbullet%7D%5Cright%5C%7D%2C%5Cleft%5C%7B%5Cboldsymbol%7B%5Calpha%7D_%7Bp%7D%5Cright%5C%7D+%3B+%5Cboldsymbol%7Bx%7D%5Cright%29+%5C%5C+%26%3D%5Cleft%5C%7C%5Cmathcal%7BS%7D_%7Bk%7D%5Cleft%28%5Cmathcal%7BW%7D_%7Bk%7D%2C+%5Cboldsymbol%7B%5Calpha%7D_%7Bp%7D+%3B+%5Cboldsymbol%7Bx%7D_%7Bp%7D%5Cright%29-%5Cwidehat%7B%5Cmathcal%7BT%7D_%7Bk%7D%7D%5Cleft%28%5Cmathcal%7BW%7D_%7Bk%7D%5E%7B%5Cbullet%7D%2C%5Cleft%5C%7B%5Cboldsymbol%7B%5Calpha%7D_%7Bp%7D%5Cright%5C%7D+%3B%5Cleft%5C%7B%5Cboldsymbol%7Bx%7D_%7Bp%7D%5E%7B%5Cprime%7D%5Cright%5C%7D%5Cright%29%5Cright%5C%7C_%7B2%7D%5E%7B2%7D+%5Cend%7Baligned%7D+%5Ctag%7B2%7D)

那一个完整的优化函数表示如下：

![\begin{aligned}&\boldsymbol{\alpha}^{*}=\left\{\boldsymbol{\alpha}_{k}\right\}^{*}=\underset{\forall\left\{\boldsymbol{\alpha}_{k}\right\} \subset \mathcal{A}}{\arg \min } \sum_{k=1}^{| k \mid} \lambda_{k} \mathcal{L}_{\text {val }}\left(\mathcal{W}_{k}^{*}, \boldsymbol{\alpha}_{k} ; \boldsymbol{x}_{k}, \boldsymbol{y}_{k}\right) \\&\text { s.t. } \mathcal{W}_{k}^{*}=\underset{\mathcal{W}_{k}}{\arg \min } \mathcal{L}_{\text {train }}\left(\mathcal{W}_{k}, \mathcal{A}_{k} ; \boldsymbol{x}_{k}, \boldsymbol{y}_{k}\right)\end{aligned} \tag{3} ](https://www.zhihu.com/equation?tex=%5Cbegin%7Baligned%7D%26%5Cboldsymbol%7B%5Calpha%7D%5E%7B%2A%7D%3D%5Cleft%5C%7B%5Cboldsymbol%7B%5Calpha%7D_%7Bk%7D%5Cright%5C%7D%5E%7B%2A%7D%3D%5Cunderset%7B%5Cforall%5Cleft%5C%7B%5Cboldsymbol%7B%5Calpha%7D_%7Bk%7D%5Cright%5C%7D+%5Csubset+%5Cmathcal%7BA%7D%7D%7B%5Carg+%5Cmin+%7D+%5Csum_%7Bk%3D1%7D%5E%7B%7C+k+%5Cmid%7D+%5Clambda_%7Bk%7D+%5Cmathcal%7BL%7D_%7B%5Ctext+%7Bval+%7D%7D%5Cleft%28%5Cmathcal%7BW%7D_%7Bk%7D%5E%7B%2A%7D%2C+%5Cboldsymbol%7B%5Calpha%7D_%7Bk%7D+%3B+%5Cboldsymbol%7Bx%7D_%7Bk%7D%2C+%5Cboldsymbol%7By%7D_%7Bk%7D%5Cright%29+%5C%5C%26%5Ctext+%7B+s.t.+%7D+%5Cmathcal%7BW%7D_%7Bk%7D%5E%7B%2A%7D%3D%5Cunderset%7B%5Cmathcal%7BW%7D_%7Bk%7D%7D%7B%5Carg+%5Cmin+%7D+%5Cmathcal%7BL%7D_%7B%5Ctext+%7Btrain+%7D%7D%5Cleft%28%5Cmathcal%7BW%7D_%7Bk%7D%2C+%5Cmathcal%7BA%7D_%7Bk%7D+%3B+%5Cboldsymbol%7Bx%7D_%7Bk%7D%2C+%5Cboldsymbol%7By%7D_%7Bk%7D%5Cright%29%5Cend%7Baligned%7D+%5Ctag%7B3%7D+)

## **2.2 Search subnets**

2.1节介绍了如何训练Supernet。在训练结束后，BossNAS使用进化算法基于训练好的权重选择模型结构。类似于公式(1)中对教师网络不同路径做ensemble，在搜索的时候也会对学生网络不同路径做ensemble，第 **k** 个block输出的ensemble结果表示如下：

![\widehat{\mathcal{S}_{k}}\left(\left\{\boldsymbol{\alpha}_{p}\right\} ; \boldsymbol{x}_{2}\right)=\frac{1}{|p|} \sum_{p=1}^{|p|} \mathcal{S}_{k}\left(\boldsymbol{\alpha}_{p} ; \boldsymbol{x}_{2}\right) \tag{4} ](https://www.zhihu.com/equation?tex=%5Cwidehat%7B%5Cmathcal%7BS%7D_%7Bk%7D%7D%5Cleft%28%5Cleft%5C%7B%5Cboldsymbol%7B%5Calpha%7D_%7Bp%7D%5Cright%5C%7D+%3B+%5Cboldsymbol%7Bx%7D_%7B2%7D%5Cright%29%3D%5Cfrac%7B1%7D%7B%7Cp%7C%7D+%5Csum_%7Bp%3D1%7D%5E%7B%7Cp%7C%7D+%5Cmathcal%7BS%7D_%7Bk%7D%5Cleft%28%5Cboldsymbol%7B%5Calpha%7D_%7Bp%7D+%3B+%5Cboldsymbol%7Bx%7D_%7B2%7D%5Cright%29+%5Ctag%7B4%7D+)

最后最优的网络则是每个block的输出最接近ensemble的输出，优化函数表示如下：

![\begin{gathered}\boldsymbol{\alpha}^{*}=\underset{\forall \boldsymbol{\alpha} \in \mathcal{A}}{\arg \min } \sum_{k=1}^{|k|} \lambda_{k} \mathcal{L}_{\text {val }}\left(\boldsymbol{\alpha} ; \boldsymbol{x}_{k}\right) \\\text { where } \quad \mathcal{L}_{\text {val }}(\boldsymbol{\alpha} ; \boldsymbol{x})=\left\|\mathcal{S}_{k}\left(\boldsymbol{\alpha} ; \boldsymbol{x}_{1}\right)-\widehat{\mathcal{S}}_{k}\left(\mathcal{A}_{k} ; \boldsymbol{x}_{2}\right)\right\|_{2}^{2}\end{gathered} \tag{5} ](https://www.zhihu.com/equation?tex=%5Cbegin%7Bgathered%7D%5Cboldsymbol%7B%5Calpha%7D%5E%7B%2A%7D%3D%5Cunderset%7B%5Cforall+%5Cboldsymbol%7B%5Calpha%7D+%5Cin+%5Cmathcal%7BA%7D%7D%7B%5Carg+%5Cmin+%7D+%5Csum_%7Bk%3D1%7D%5E%7B%7Ck%7C%7D+%5Clambda_%7Bk%7D+%5Cmathcal%7BL%7D_%7B%5Ctext+%7Bval+%7D%7D%5Cleft%28%5Cboldsymbol%7B%5Calpha%7D+%3B+%5Cboldsymbol%7Bx%7D_%7Bk%7D%5Cright%29+%5C%5C%5Ctext+%7B+where+%7D+%5Cquad+%5Cmathcal%7BL%7D_%7B%5Ctext+%7Bval+%7D%7D%28%5Cboldsymbol%7B%5Calpha%7D+%3B+%5Cboldsymbol%7Bx%7D%29%3D%5Cleft%5C%7C%5Cmathcal%7BS%7D_%7Bk%7D%5Cleft%28%5Cboldsymbol%7B%5Calpha%7D+%3B+%5Cboldsymbol%7Bx%7D_%7B1%7D%5Cright%29-%5Cwidehat%7B%5Cmathcal%7BS%7D%7D_%7Bk%7D%5Cleft%28%5Cmathcal%7BA%7D_%7Bk%7D+%3B+%5Cboldsymbol%7Bx%7D_%7B2%7D%5Cright%29%5Cright%5C%7C_%7B2%7D%5E%7B2%7D%5Cend%7Bgathered%7D+%5Ctag%7B5%7D+)

## **3. CNN-Transformer混合搜索空间**

## **3.1 Candidate Blocks**

* CNN的部分采用的是ResNet的Residual Bottleneck，记为 **ResConv**
* Transformer部分是基于 [BotBlock](https://link.zhihu.com/?target=https%3A//www.notion.so/Aravind-Srinivas-Tsung-Yi-Lin-Niki-Parmar-Jonathon-Shlens-Pieter-Abbeel-and-Ashish-Vaswani-Bot-e79ccbbddbf94c82b85527b6af621ddb)和[NLBlock](https://link.zhihu.com/?target=https%3A//www.notion.so/Xiaolong-Wang-Ross-Girshick-Abhinav-Gupta-and-Kaiming-He-Non-local-neural-networks-In-CVPR-201-19f844893b3c401b9ea1c802c6b52dd6)做了改进的模块，记为 **ResAtt**

![](https://picx.zhimg.com/v2-fc881c164860344dec257b1730b90bc0_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='820' height='256'></svg>)

## **3.2 Hybrid CNN-Transformers**

完整的模型结构如下图示，不仅会搜每一层的block结构，还会搜索每一层的下采样操作（控制resolution）。

![](https://pic1.zhimg.com/v2-b4ed021ebab7cdf8b72f4c5f4ba8df36_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1203' height='346'></svg>)

## **4. Experiments**

## **4.1 Setup**

每个block训练20个epoch，其中第一个epoch是warmup epoch。每个training step随机采样4条路径。

## **4.2 搜索Hybrid CNN-Transformer的结果**

![](https://pic1.zhimg.com/v2-f05844624e442cd11cb6ce80ea4ce00e_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='806' height='968'></svg>)![](https://picx.zhimg.com/v2-9f486756a9725257784baf8b2c5a4981_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='785' height='455'></svg>)

上图给出了使用DNA算法和BossNAS算法在相同的HyTra搜索空间上搜到的网络结构，可以看到 DNA搜到的网络更倾向于选择卷积操作，作者对此的解释是因为DNA使用了教师网络，而教师网络本身带来了biased supervision。文章把这一现象称作 **candidate preference。**

## **4.3 在MBConv 搜索空间上的结果**

最终模型在ImageNet上的结果如下表，可以看到BossNAS结果的优势有一丢丢，但不明显

![](https://pic1.zhimg.com/v2-1cb911e9de438ddfddc6bb9bdeaed225_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='620' height='426'></svg>)

作者进一步比较了搜索一致性结果（Kendall tau: ![\tau](https://www.zhihu.com/equation?tex=%5Ctau), Pearson: ![R](https://www.zhihu.com/equation?tex=R), Spearman: ![\rho](https://www.zhihu.com/equation?tex=%5Crho)），相关性结果是基于 DNA 提供的23个模型结构和acc计算得到的,结果如Table 3所示。可以看到MnasNet相关性还不错，但是由于是multi-trial方法，所以耗时巨大。 另外我们还可以看到 教师网络 的选择对DNA算法影响非常大。文章将这个现象称作 **teacher preference**，而BossNAS完全不需要teacher network。

![](https://picx.zhimg.com/v2-071ab2539fc0462376fe30881999d5ad_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='664' height='326'></svg>)

## **4.4 在 NATS-Bench** S_S**搜索空间的结果**

该搜索空间基于CIFAR10/100进行试验。

![](https://pica.zhimg.com/v2-0a2ca706d7b1dbc1c3599c214921191b_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='662' height='292'></svg>)

## **4.5 Ablation Study**

BossNAS的训练和评估都是非监督的，为此作者对比了不同的训练和评估方法对最终结果的影响，结果如Table 5所示。

Training

* Supv. distill. 表示supervised distillation，其实就是DNA算法，即对中间层做监督学习
* Supv. class. 即对最后输出层使用真实label做监督学习
* Unsupv. bootstrap，和本文方法类似，只不过是教师网络和学生网络对应的相同路径做知识蒸馏
* Unsupv. EB: 学生网络的所有路径和教师网络的ensemble结果做知识蒸馏

Evaluation

* Supv. distill. 和 Supv. class类似，就是根据学生和教师网络输出的相似度来评估网络的好坏
* Supv. linear eval 表示supervised linear evaluation。这个是最常规的权重共享的NAS评估方法。具体来说该方式是首先把supernet权重固定，然后finetune一个权重共享的线性分类器。这个分类器会和所有子网相连接，每个子网的排序就是根据分类器最后得到的accuracy结果决定的。
* Unsupv. eval就是本文的方法，如公式 (5)

![](https://pic1.zhimg.com/v2-16f08569fb31d7589d82748f95273f43_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='733' height='328'></svg>)

## **4.6 Supernet训练收敛表现**

前面已经提到过，BossNAS的每个block只训练20个epoch就结束了，下图就给出了在MBConv搜索空间上，基于ImageNet数据集每个epoch对应的搜索一致性结果。可以看到基本上在第12个epoch的时候一致性基本上就固定了，另外前期相关性能够快速地提升。

![](https://pic1.zhimg.com/v2-ca2aa28ca3b222e3fdbaa0113629a82d_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='669' height='218'></svg>)

在NATS-Bench上已有类似的结果

![](https://pic1.zhimg.com/v2-c03859fbc6cc13716cdc83f11e554a0a_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='772' height='473'></svg>)


---

## ICCV 2021有什么值得关注的新研究？

`link: https://www.zhihu.com/question/464986281/answer/2264847431 · created: 1639110400`


[BN-NAS: Neural Architecture Search with Batch Normalization](https://link.zhihu.com/?target=https%3A//arxiv.org/abs/2108.07375)

## 1. Motivation

之前的One-shot NAS工作在搜索过程中有两个特点：

* 训练所有模块的参数
* 使用在验证集上的准确率作为评价指标来评估模型的好坏

很明显这两个步骤都非常耗时，所以这篇论文打起了 batch-normalization (BN) 的主义，即

* 只训练BN的参数
* 使用BN的参数作为评价指标

实验结果表明，这样做不仅训练速度加快，而且最终模型性能也得到了保证

![](https://pic1.zhimg.com/v2-345afe9fa028451f103ae88504665cc6_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1002' height='286'></svg>)

下面详细介绍一下算法细节

## 2. Methodology

如下图示，整个算法包含三个步骤：

1. Supernet training
2. subnet searching
3. subnet retraining

![](https://picx.zhimg.com/v2-e269ceb41e915970b4816cb455e7ceaf_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1380' height='602'></svg>)

## 2.1 Supernet Training

第一步是训练Supernet。不同于以往训练所有参数，BNNAS采取的策略是

1. 随机初始化Supernet参数
2. 只训练BN的参数，即Conv和Linear等有参数的层都frozen。

这样一来需要训练的参数量就极大地减少了。

作者选取了SPOS和FairNAS两篇论文作为baseline，他们supernet分别训练了100和150个epoch。作为对比，作者只训练BN，基于SPOS和FairNAS分别只训练了10和15个epoch。

题外话：我很好奇只训练BN的话，模型能收敛吗，或者模型的train acc能有多高？如果根本学不到东西，那BN参数指标真的有意义吗？

## 2.2 Subnet Searching

论文中的搜索空间长这样，可以看到是类似MobileNet的结构。模型由多个layer组成，每个layer有 N 个candidate operation，每个operation由多个conv+BN+relu组成，区别就是这些conv的卷积核和通道数（expand ratio）不一样 。

![](https://pic1.zhimg.com/v2-14de4e8ecebc6edc118e66ac0b4c23a3_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='661' height='570'></svg>)

需要注意的是每个operation最后都是BN，如上图中的红框所示，所以作者就用这个BN的参数来作为评价指标，具体的方法如下图所示

![](https://picx.zhimg.com/v2-cd046be1e0f012eea795af3dd76a1969_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='724' height='271'></svg>)

我们以 $Layer\_L$的Op2为例，它的指标值 $S\_{o\_{2,L}}$是其最后的BN层所有 $\gamma$的平均值。

这个只是某一层的BN-based指标值，那么一个子模型的指标值就是所有层的总和，计算如下：

![](https://picx.zhimg.com/v2-016430c7c51da6428ebb137ce125fab6_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='688' height='134'></svg>)

那么优化目标函数可以表示如下：

![](https://picx.zhimg.com/v2-32b398e677a02259017daf32d32182ce_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='659' height='140'></svg>)

## 2.3 Subnet Retraining

根据优化目标函数公式(5)可以通过不断优化找到最优的子模型结构 $a^\*$，之后对这个子模型做retrain。

## 3. 实验分析

## 3.1 相关性比较

前面介绍过了每一层的N个operations都会根据公式（3）计算得到对应的BN-based value，那么整个Supernet可以有一个 $N\*L$的矩阵表示。

下图中(a)表示训练所有参数的结果，(b)表示只训练BN参数的结果。横纵坐标都表示epoch数，具体的值就是不同epoch之间的相似度，这个相似度就是根据计算上面提到的 $N\*L$的矩阵$L\_2$距离得到的。

文中对下图的分析师(a)是在30个epoch的时候，不同epoch之间的相似度变得差不多了，而(b)在第10个epoch就很相似了。只能说有点牵强。。。明明还有那么多白色区域

![](https://pic1.zhimg.com/v2-b65aa4c2fe4c83bec97757070eddd8c8_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='751' height='698'></svg>)

## 3.2 Results on ImageNet

![](https://picx.zhimg.com/v2-e16e146e34b1916363b70b28769cab3c_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='704' height='392'></svg>)


---

## 矩阵和它的行列式、特征向量、特征值之间的关系是什么？

`link: https://www.zhihu.com/question/39354544/answer/2264846406 · created: 1639110352`


## **1. 矩阵的意义**

[https://www.cnblogs.com/marsggbo/p/10144060.html](https://link.zhihu.com/?target=https%3A//www.cnblogs.com/marsggbo/p/10144060.html)

这篇文章对矩阵的含义做了清晰的解释，以 ![Ma=b](https://www.zhihu.com/equation?tex=Ma%3Db)为例介绍矩阵M的含义 ：

* 从变换的角度来说，矩阵M可以理解为对向量 a做变换得到了 b
* 从坐标系的角度来说，M可以理解成是一个坐标系（常用的坐标是笛卡尔坐标系，即 ![I](https://www.zhihu.com/equation?tex=I)），向量a就是在M这个坐标系下的坐标，a对应到![I](https://www.zhihu.com/equation?tex=I)坐标系下的坐标是向量 b。

所以本质上说a和b是等价的，就好像我们给一个人拍照，站在楼上拍照和爬着拍照，角度不一样，但是拍的东西都是同一个东西，唯一的差别就是坐标系的不同。

## **2. 特征值和特征向量的意义**

基于上面的解释后，我们再来看特征值和特征向量的定义:

> “ 设 A 是n阶方阵，如果存在数m和非零n维列向量 x，使得 Ax=mx 成立，则称 m 是A的一个特征值（characteristic value)或本征值（eigenvalue)。  
>  ”

那特征值和特征向量具体是什么含义呢？

我们假设矩阵A的某个特征值为 m1, 对应的特征向量是 x1。根据定义和上面对矩阵的理解可以知道，x1是以A为坐标系的坐标向量，将其变换到以![I](https://www.zhihu.com/equation?tex=I)为坐标系后得到的坐标向量 与 它原来的坐标向量 永远存在一个 m1 倍的伸缩关系。

为了方便理解举一个简单的例子，假如矩阵A如下，可以看到它的特征值有2个，分别是1,100，分别对应2个特殊的特征向量，即 [1,0],[0,1]。

![A= \left[\begin{matrix} 1 & 0  \\ 0 & 100 \end{matrix}\right] \tag{1} ](https://www.zhihu.com/equation?tex=A%3D+%5Cleft%5B%5Cbegin%7Bmatrix%7D+1+%26+0++%5C%5C+0+%26+100+%5Cend%7Bmatrix%7D%5Cright%5D+%5Ctag%7B1%7D+)

所以矩阵A左乘任意的一个向量x，其实都可以理解成是把向量x沿着这2个特征向量的方向进行伸缩，伸缩比例就是对应的特征值。可以看到这2个特征值差别是很大的，最小的只有1，最大的特征值为100。

看下图的例子，矩阵A和向量 [1,1]相乘得到 [1,100]，这表示原来以A为坐标系的坐标[1,1]，经过转换到以![I](https://www.zhihu.com/equation?tex=I)为坐标系后 坐标变成了 [1,100]。我们直观地理解就是矩阵A把向量[1,1]更多地往y轴方向拉伸。

![](https://pica.zhimg.com/v2-e26d7fe8fd2898a8ae7d2c72c179fc27_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='561' height='526'></svg>)

假如A是多维(n)矩阵，且有n个不同的特征值，那么就可以理解成这个矩阵A和一个向量x相乘其实就是把向量x往n个特征向量的方向进行拉伸，拉伸比例是对应的特征值。那这样有什么作用呢？

## **3. 特征值和特征向量的应用**

意义就在于如果我们知道了特征值的大小，有时为了减少计算了，我们可以只保留特征值较大的，比如上面的图片中，我们可以看到变换后的向量x轴适合原来一样的，而y轴方向拉伸了100倍，所以通常为了实现压缩算法，我们可以只保留y轴方向的变换即可。 对应到高维情况也是类似的，多维矩阵会把向量沿着多个方向拉伸，有的方向可能拉伸幅度很小，而有的很大，我们只需要保留幅度大的即可达到压缩的目的。

### **微信公众号：AutoML机器学习**

**MARSGGBO♥原创**  
**如有意合作或学术讨论欢迎私戳联系~**  
**邮箱:marsggbo@foxmail.com**


---

## ICLR 2021 有什么值得关注的投稿？

`link: https://www.zhihu.com/question/423975807/answer/2263618619 · created: 1639036738`


## **1. 长话短说**

这篇论文主要是通过设计一系列实验得到不同实验集的ID（Intrinsic Dimension），然后给出观察到的现象。这些现象也是比较符合直觉的，总结起来有这么几点：

1. 数据集的ID越大，训练模型就需要越多的数据
2. 数据集的extrinsic dimension对模型的训练影响不是很大，比如ImageNet图像缩放到32x32后，训练模型所需要的数据量并不会就因此减少，更多是由它本身的ID值决定的

## **2. Related Work**

有这么一个假设，就是说子自然图像位于或者靠近 **低维流行 (low-dimensional manifold)。** 有两点现象能支持这个假设：

1. 自然图像是locally connected，即每张图片周围都是与他本身高度相似的图像，差别可能就是亮度，对比度等特征。
2. 自然图像位于 **低维结构（low-dimensional structure）** 上，因为图像的概率分布是高度集中的（即相似的纹理），如果我们只是对像素做均匀采样，很难得到一个有意义的图像。比如一张白色狗狗的照片，身体部位的像素绝大部分都是分布在白色区间，舌头则是高度集中在红色像素。

后续也有很多工作尝试去证明上面提到的假设。有的工作则是去尝试理解为什么深度模型能从训练集泛化到从未见过的测试集。有一类工作是从 **loss landscape**的角度来解释，有的则是认为 **低维数据** 与 **不包含外在维度（extrinsic dimension）的属性** 表征了分类问题的泛化难度：

* [1] 发现神经网络的特征是 low-dimensional 的
* [2] 发现神经网络不同层的特征的intrinsic dimension存在先增后降的特点

## **3. Intrinsic Dimension (ID) Estimation**

## **3.1 本论文使用的ID估计方法： MLE**

假设我们有一组数据点 ![\mathcal{P}\subset \mathbb{R}^N](https://www.zhihu.com/equation?tex=%5Cmathcal%7BP%7D%5Csubset+%5Cmathbb%7BR%7D%5EN)，这些点位于或靠近低维流形 ![\mathcal{M}\subseteq \mathbb{R}^N](https://www.zhihu.com/equation?tex=%5Cmathcal%7BM%7D%5Csubseteq+%5Cmathbb%7BR%7D%5EN),其中 ![dim(\mathcal{M})=d< <N](https://www.zhihu.com/equation?tex=dim%28%5Cmathcal%7BM%7D%29%3Dd%3C+%3CN)

一个常见的ID估计方法是找出每个样本点的 top-k 最近邻居，然后对邻居之间的距离进行建模。文献[3]中基于泊松过程使用了最大似然估计 (MLE) ，公式如下：

![\hat{m}_{k}(x)=\left[\frac{1}{k-1} \sum_{j=1}^{k-1} \log \frac{T_{k}(x)}{T_{j}(x)}\right]^{-1} \tag{1} ](https://www.zhihu.com/equation?tex=%5Chat%7Bm%7D_%7Bk%7D%28x%29%3D%5Cleft%5B%5Cfrac%7B1%7D%7Bk-1%7D+%5Csum_%7Bj%3D1%7D%5E%7Bk-1%7D+%5Clog+%5Cfrac%7BT_%7Bk%7D%28x%29%7D%7BT_%7Bj%7D%28x%29%7D%5Cright%5D%5E%7B-1%7D+%5Ctag%7B1%7D+)

其中![T_j(x)](https://www.zhihu.com/equation?tex=T_j%28x%29)表示 采样点 ![x](https://www.zhihu.com/equation?tex=x) 到 它第j个最近邻居的欧氏距离 (norm2)。不过公式(1)是某一个样本点的结果，所有后面有算法[4]做出了修正，即取多个 (n) 样本点ID估计值的均值

![\bar{m}_{k}=\left[\frac{1}{n} \sum_{i=1}^{n} \hat{m}_{k}\left(x_{i}\right)^{-1}\right]^{-1}=\left[\frac{1}{n(k-1)} \sum_{i=1}^{n} \sum_{j=1}^{k-1} \log \frac{T_{k}\left(x_{i}\right)}{T_{j}\left(x_{i}\right)}\right]^{-1} \tag{2} ](https://www.zhihu.com/equation?tex=%5Cbar%7Bm%7D_%7Bk%7D%3D%5Cleft%5B%5Cfrac%7B1%7D%7Bn%7D+%5Csum_%7Bi%3D1%7D%5E%7Bn%7D+%5Chat%7Bm%7D_%7Bk%7D%5Cleft%28x_%7Bi%7D%5Cright%29%5E%7B-1%7D%5Cright%5D%5E%7B-1%7D%3D%5Cleft%5B%5Cfrac%7B1%7D%7Bn%28k-1%29%7D+%5Csum_%7Bi%3D1%7D%5E%7Bn%7D+%5Csum_%7Bj%3D1%7D%5E%7Bk-1%7D+%5Clog+%5Cfrac%7BT_%7Bk%7D%5Cleft%28x_%7Bi%7D%5Cright%29%7D%7BT_%7Bj%7D%5Cleft%28x_%7Bi%7D%5Cright%29%7D%5Cright%5D%5E%7B-1%7D+%5Ctag%7B2%7D+)

基于MLE估计得到ID值有两个需要注意的问题：

1. 如公式(2)所示，估计值依赖于 k 的取值
2. 除了局部均匀性假设外，MLE还假设数据产生于一连串的独立随机变量，这些变量可以写成具有平滑密度的连续和足够平滑的随机变量的函数，但是对于自然图像数据集来说，这个假设我们很难判断真假。

## **3.2 一些其他ID估计的方法**

* [5] **GeoMLE** 利用基于不同大小邻居数量 (即 k) 的近邻距离 对 标准MLE进行多项式回归 来说明密度的非均匀性和流形的非线性。问题在于它的ID值是 多个样本 ![\hat{m}_{k}(x)](https://www.zhihu.com/equation?tex=%5Chat%7Bm%7D_%7Bk%7D%28x%29) 的平均，而公式(2) 中是对 ![\hat{m}_{k}(x)^{-1}](https://www.zhihu.com/equation?tex=%5Chat%7Bm%7D_%7Bk%7D%28x%29%5E%7B-1%7D) 求平均后，再取倒数得到最终的估计值。文章也明确说[5] 的估计值非常不准。下图是GeoMLE在 d-dimensional Hypercube data上的表现结果。

![](https://picx.zhimg.com/v2-6b0c0f7b243868d0365195955521136d_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1253' height='401'></svg>)

* [6] 提出了 **TwoNN** 算法来估计ID值，简单说就是他基于两个邻居之间的距离 （即 k=2 ）来估计ID。 文献[2]就是基于这个算法的。

![](https://pic1.zhimg.com/v2-51f6d373e93c0608a7f67f60153d0d9a_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1254' height='398'></svg>)

* 这篇文章不同邻居之间的距离是使用 norm2 的欧氏距离计算的，而 [7] 中使用的是 geodesic distance，记为 **kNN graph distance**.

![](https://pic1.zhimg.com/v2-d0e1143236f61b7f47daed4003cae742_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1244' height='412'></svg>)

上面3个图可以看到GeoMLE和TwoNN的估计值一般会比真实值要打，即overestimate。而KNN graph则是略微地underestimate。不同估计方法对不同数据集的ID估计结果如下。TwoNN对MNIST的ID估计值比CIFAR-10还高，这可能多少和直觉相违背。另外前三个数据集对CIFAR10的ID估计值都要比CIFAR100高，这个感觉也有点反直觉。

![](https://pic1.zhimg.com/v2-f03fbf7f71018b44fcbc848b6fe8433c_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='969' height='280'></svg>)

## **4. 在合成数据上验证 Intrinsic Dimension**

## **4.1 直观感受ID对图像分类的影响**

作者用BigGAN做了个实验。BigGAN有 128个latent entries，输出大小为128x128x3的图像。作者将128个latent entries大多数设置为0，只留下 ![\bar{d}](https://www.zhihu.com/equation?tex=%5Cbar%7Bd%7D) 个free entries，即视为intrinsic dimension。然后给出了不同 ![\bar{d}](https://www.zhihu.com/equation?tex=%5Cbar%7Bd%7D) 设置下一个类别（即 basenji）生成的图像的对比，如下图示。可以看到 ID值越小，生成的图片背景越简单，当 ![\bar{d}=128](https://www.zhihu.com/equation?tex=%5Cbar%7Bd%7D%3D128) 时，背景复杂了很多。其实换个角度想，当数据的ID越小的时候则表示该数据越容易被区分。文献[2]的实验对比了resent18/50/152等就发现网络最后一层的ID值越低，模型最终的acc也相对高一些。

![](https://pic1.zhimg.com/v2-ed9d95c00c3051c6a900f4ef2f708a89_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='769' height='834'></svg>)

作者还在 ![\bar{d}=10](https://www.zhihu.com/equation?tex=%5Cbar%7Bd%7D%3D10) 的情况下比较了不同 k 的取值对最终ID估计的影响，结果如下。我们可以看到如下几个现象：

![](https://picx.zhimg.com/v2-ce1c8b3fe09ba2b064ced06b0d4c0e88_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1160' height='494'></svg>)

* 纵坐标10代表ground truth，当k=4的时候得到的ID估计值非常接近真实值。
* 原本的latent维度是128，虽然其他k值有一定误差，但是整体上偏差不是很大，他们都很接近10
* ID的估计比较robust，可以看到即使把采样点数量从125增加到2000后，不同k得到的ID的预测值都是相对稳定的。这表明我们可以只使用一部分数据就能很好地得到ID估计值。

## **4.2 两个假设**

作者还进一步在合成数据集上设计了实验来验证两个假设：

1. **ID低的数据的sample complexity要小于 ID高的数据**

为了验证这个，作者选择了basenji和beagle这两类图像来用BigGAN来生成4组不同的数据集，主要区别是intrinsic dimension的不同，具体设置如下：

* intrinsic dimension是指latent size，四个数据集对应的大小分别是16,32,64,128
* extrinsic dimension是指最终生成的图像大小，四个数据集都是一样的，即 3x32x32

数据集生成好后，作者使用ResNet-18 在这4个数据集上去训练，实验结果如下。可以看到ID （即latent size）越小的数据集，训练ResNet-18所需的训练样本数量也就越少。实验结果证明了假设。

![](https://picx.zhimg.com/v2-9670d7878a4c6a09fbe0871d898897d0_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1023' height='455'></svg>)

1. extrinsic dimension和sample complexity没有关系

为了验证第二个假设，作者这次固定intrinsic，改变extrinsic dimension，也生成了4个不同的数据集，具体设置如下：

* intrinsic dimension： latent size都固定位128
* extrinsic dimension：生成图像的大小分别是16， 32， 64， 128， 256

实验结果如下图，可以看到此时4个数据集在使用2000个训练样本后基本就能达到相似的分类准确率了。实验结果表明extrinsic dimension对sample complexity的影响很小。

![](https://picx.zhimg.com/v2-66537215138ace3d6c490dfa7c620e7e_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1071' height='461'></svg>)

## **5. 在真实数据集上验证 Intrinsic Dimension**

前面都是在GAN生成的数据集上做的实验，作者还在像MNIST，CIFAR-10等真实数据集上也做了验证试验。下图是在原始数据集上使用MLE得到的在不同 k 大小下的 ID 估计值。可以看到估计的结果符合预期，即数据集越难，ID值越大。

![](https://pica.zhimg.com/v2-dc58337b6dc021ef513eaa4f58376786_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1089' height='290'></svg>)

因为每个数据集的图形大小不一样，所以不同数据集的图像大小都缩放到 32x32 以保证extrinsic dimension都一样。实验设置和上面的合成数据集的设置类似，比如在ImageNet上随机选取两个类别的数据构造成一个二分类数据子集，然后计算出 ID 值。Table 2是基于两个类别得到的ID值，Table 1是基于原始数据集得到的ID值，可以看到二者虽然具体的ID值不同牡丹石整体呈现的趋势是类似的，即数据集越难，ID值越大。

![](https://picx.zhimg.com/v2-fff321bd9416091b9b388dfe450748c5_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1223' height='322'></svg>)

下图是在4个真实数据集上的结果，每个数据集跑了5次，每次选取不同的两个类别组成subnet。可以看到在真实数据集上的结果和Figure 4的结果类似，intrinsic dimension大的数据集（如ImageNet）需要采样更多的训练样本。

![](https://pica.zhimg.com/v2-fb142955e0ad7cab33b0f8cf943a72ab_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1087' height='476'></svg>)

作者还做了一个比较有意思的实验，就是给数据集加上噪声。其实像ImageNet本身真实的ID我们是不知道的，但是噪声数据的ID我们是可以控制的，所以假如我们构造一个ID为 ![\underline{d}](https://www.zhihu.com/equation?tex=%5Cunderline%7Bd%7D) 的噪声并把它加到原图像上去，那么得到的新的图像的ID肯定是大于或等于![\underline{d}](https://www.zhihu.com/equation?tex=%5Cunderline%7Bd%7D)的。Table 3 给出了加上不同ID噪声后，CIFAR-10数据集的ID估计值的变化情况。可以看到加上噪声后数据集的ID似乎并没有达到噪声的ID值，这很可能是因为数据点太少导致的。不过可以看到的是加入噪声的ID值越大，得到的新的数据集自身的ID值也是随之增加的。

![](https://picx.zhimg.com/v2-59e0a54b908ec8b8e6b24e88c86c4808_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1100' height='283'></svg>)

基于加入噪声后的数据集，作者也做了sample complexity实验的比较，实验现象和前面的类似。

![](https://pic1.zhimg.com/v2-197132a27f59465d4de15f1f989b4849_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1117' height='421'></svg>)

## **Reference**

[1] Sixue Gong, Vishnu Naresh Boddeti, and Anil K Jain. On the intrinsic dimensionality of image representations. In Proceedings of the IEEE Conference on Computer Vision and Pattern Recog- nition, pp. 3987–3996, 2019.

[2] Alessio Ansuini, Alessandro Laio, Jakob H Macke, and Davide Zoccolan. Intrinsic dimension of data representations in deep neural networks. In Advances in Neural Information Processing Systems, pp. 6111–6122, 2019.

[3] Elizaveta Levina and Peter J Bickel. Maximum likelihood estimation of intrinsic dimension. In Advances in neural information processing systems, pp. 777–784, 2005.

[4] David J.C. MacKay and Zoubin Ghahramani. Comments on ‘Maximum Likelihood Estimation of Intrinsic Dimension’ by E. Levina and P. Bickel (2004), 2005. URL [http://www](https://link.zhihu.com/?target=http%3A//www/). [inference.org.uk/mackay/dimension/](https://link.zhihu.com/?target=http%3A//inference.org.uk/mackay/dimension/).

[5] Marina Gomtsyan, Nikita Mokrov, Maxim Panov, and Yury Yanovich. Geometry-aware maximum likelihood estimation of intrinsic dimension. In Asian Conference on Machine Learning, pp. 1126–1141, 2019.

[6] Elena Facco, Maria d’Errico, Alex Rodriguez, and Alessandro Laio. Estimating the intrinsic dimension of datasets by a minimal neighborhood information. Scientific Reports, 7(1):12140, 2017.

[7] Daniele Granata and Vincenzo Carnevale. Accurate estimation of the intrinsic dimension using graph distances: Unraveling the geometric complexity of datasets. Scientific reports, 6:31377, 2016.


---

## 如何评价华为天才少年钟钊团队成功开启了 AutoML 大规模商用的先河？什么是 AutoML？

`link: https://www.zhihu.com/question/501845921/answer/2248004394 · created: 1638164688`


很多答主说这是华为的营销活动，这可能只回答了“如何评价”这一问题。

因为我的研究方向刚好恰巧就是AutoML，所以我稍微回答一下后者，“什么是AutoML？”，顺便也蹭蹭热度哈哈。对AutoML感兴趣的可以看看我们实验室发表的相关综述：

[AutoML: A Survey of the State-of-the-Art](https://link.zhihu.com/?target=https%3A//arxiv.org/abs/1908.00709)

## 1. 简介

AutoML的全称是**Automated Machine Learning，**也就是自动机器学习。

传统的机器学习可能是依靠人工设计的特征对数据做处理。举个最简单的例子，我们在对学生成绩好坏做评价的时候，他每个科目的成绩就可以视为一个特征，最简单的办法就是求和或者加权平均（也就是卷死人的GPA）。这个例子很简单，但是假如我们想让机器自动区分猫和狗的时候，涉及到的特征就很多了，单靠人工设计就没那么简单了，所以人们会尝试着使用**卷积神经网络(CNN)**来对猫和狗进行分类。

![](https://picx.zhimg.com/v2-cf178ea52f819b2362500d8f2a3309d7_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='743' height='503'></svg>)![](https://pic1.zhimg.com/v2-b95488a7063831af9a66e21673156b21_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='819' height='530'></svg>)

随着卷积神经网络的成功和流行，科研狗们开始了漫漫的调参之路。。。

一个完整的训练CNN的流程包含很多部分，整个流程划分成了如下几个部分[1]:

![](https://pic1.zhimg.com/v2-87f90036fc25d951532f01bc5430449b_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='720' height='357'></svg>)

* 数据准备
* 特征工程
* 模型生成
* 模型评估

下面我会对 **数据增强** 和 **神经架构搜索(Neural Architecture Search, NAS)**简要地介绍一下经典的研究和应用。

## 2. 数据准备

数据增强（Data augmentation）可以视为数据准备阶段中的一个非常重要的环节，他可以很好地对原有数据集进行扩充，提高模型的泛化能力，常见的数据增强操作有翻转，旋转，缩放，高斯噪声等等，但是如何选择合适的数据增强操作很大程度上是依靠以往的经验。

如何针对不同的数据集找到更加合适的数据增强策略是一个值得研究的问题，谷歌公司在这一个方向上走在前列，他们最先做了尝试，提出了AutoAugment算法[2] ，具体的原理在这里不做赘述，网上已经有很多文章介绍了。不过值得一提的是目前Pytorch的torchvision库已经内置了AutoAugment的增强操作，[3]如下

```
policies = [T.AutoAugmentPolicy.CIFAR10, T.AutoAugmentPolicy.IMAGENET, T.AutoAugmentPolicy.SVHN]
augmenters = [T.AutoAugment(policy) for policy in policies]
imgs = [
    [augmenter(orig_img) for _ in range(4)]
    for augmenter in augmenters
]
row_title = [str(policy).split('.')[-1] for policy in policies]
plot(imgs, row_title=row_title)
```

![](https://pic1.zhimg.com/v2-d6985ac5c110c2e82b2bd977871fe817_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='629' height='438'></svg>)

## 3. 神经架构搜索(Neural Architecture Search, NAS)

随着对深度学习研究的不断深入，各种千奇百怪的模型冒出来了，从早期的AlexNet，到ResNet，再到Transformer，很多后续工作都是基于这些鼻祖网络做修修补补工作进一步挖掘模型的性能，但是这一过程需要很强的专业知识，这对于我等vegetable bird来说难度比较大，所以就有人提出是否可以让算法自己去找到更加合适的模型结构呢？天才少年钟钊团队干的也就是这个事，他们使用NAS技术去自动找到性能更好，速度更快的模型，而不用再去人工地试错。

有的人可能会说“哦，这不就是拿巨大的算力去暴力搜索吗，我人工设计可能还更快更好呢”。当然你可以简单地把NAS技术理解成一种暴力破解的算法，但是不可否认的是如果我们能设计出一种更加高效地搜索模型结构的算法话，那我们可以很方便地把NAS技术迁移到不同的应用场景中去，这相比于每次都靠人工去设计和调整网络要更加高效。另外钟钊是将AutoML应用到空间增强、超分辨率等图像处理，这个比图像分类任务要复杂的多，对计算资源的需求估计很大，整个搜索过程耗费多少计算资源在新闻里没有提，我也很好奇。

所以目前如何去设计更加高效的NAS算法也是一个被研究的问题。我之前写的一篇总结我们AutoML综述的文章已经详细介绍过了NAS算法的原理和细节，感兴趣的可以去看看。

[AutoML综述更新 【AutoML：A Survey of the State-of-the-Art】](https://zhuanlan.zhihu.com/p/158162306)

## 4. 我对AutoML的看法

新闻里只是说了钟钊同学作为leader带领团队把AutoML落地应用到了千万台华为手机上，很多答主开始嘲讽说没有性能对比（新闻里其实有，虽然不详细），也没有技术细节，反正哪哪都不是，甚至还不如他。我倒觉得没必要，因为这的确是对华为公司本身的一个宣传行为，文章受众不仅仅是局限在我们这些搞AI的人，长篇大论地介绍技术细节我觉得更加合适的方式是华为弄一个技术分享会。一篇文章看看就得了，提供批评意见也可以，不需要冷嘲热讽。

![](https://pica.zhimg.com/v2-c0b37dd20a0a9e778bad11d60c7dd64f_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='595' height='470'></svg>)

另外关于AutoML的发展，我觉得以后更可能是以基础设施的形式存在，对于普通用户，我们只需要提供数据，AutoML框架能够自动根据提前设计好的搜索策略找到合适的模型。对于科研工作者，我们可以花更多精力在核心问题上，比如搜索空间的设计，搜索算法的设计等等，其他不关心的模块依然可以自动化处理。华为内部团队有开发过AutoML框架，叫[Vega](https://link.zhihu.com/?target=https%3A//github.com/huawei-noah/vega)，已经开源了，感兴趣地可以去官网看看。总的来说现有的AutoML技术很大程度上还是依靠人工指定的搜索空间和搜索策略来进行搜索的，当然如果搜索空间和搜索算法也能实现自动设计那就太淦了哈哈哈，期待能有其他新的AutoML范式出现。


---

## Macbook M1/Pro/Max的GPU适配Pytorch和Tensorflow的进度如何？

`link: https://www.zhihu.com/question/498702755/answer/2224136306 · created: 1636944444`


感谢评论区小伙伴提醒，他终于踏着祥云又来了

![](https://picx.zhimg.com/v2-99d81d419202e2fd3b2f919dec5a0435_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1280' height='2844'></svg>)[https://github.com/pytorch/pytorch/issues/47702](https://link.zhihu.com/?target=https%3A//github.com/pytorch/pytorch/issues/47702)

关于是否给pytorch适配M1这个问题在官方github issue上讨论都快有一年多了哈哈。

4天前 soumith大大亲自给出答复，pytorch团队决定适配M1，至于什么时候发布出来还不确定，可能4个月后？不过决定适配总是好的，我买mac的决心又有了哈哈哈

![](https://picx.zhimg.com/v2-bba8b1a92d1c8967ad72374f51cbcd15_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1280' height='2844'></svg>)


---

## 如何看待与评价 AAAI 2022 的录用结果？

`link: https://www.zhihu.com/question/497725523/answer/2215163989 · created: 1636458687`


终于出结果了，不过悲惨的是今年录取率降到了15％。恭喜中奖了的朋友们

---

今年有幸当了一回让人唾骂的审稿人。

我审的一篇文章是NIPS转投的，只有3个reviewer给了意见。今天去看rebuttal的时候，发现这篇论文作者貌似就没有交rebuttal，估计是直接弃疗了。。。哎，至少也挣扎一下啊。

或者难不成直接转投CVPR了？

---

北京时间2021.11.30 上午9:20，还是没收到邮件，看了下外网，把娃吓到了，还以为出了

![](https://pica.zhimg.com/v2-373245e3ab1fa225c5a9b1a9726602fb_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1280' height='2844'></svg>)


---

## 去香港还是英国读研究生？

`link: https://www.zhihu.com/question/375220833/answer/2187443215 · created: 1635128749`


是去香港还是英国留学，这个问题没有一个统一的回答，因为每个人的情况不一样。我大致总结了有以下几个原因，后面也会从这几个方面来介绍香港和英国留学的区别

1. 学校排名
2. 费用
3. 生活方便程度
4. 就业认可度

## **1. 学校排名**

香港八校整体排名其实还是算不错的，可以看到QS前100的有5所，香港浸会大学和香港岭南大学排名稍微偏后，但是各自都有王牌专业，比如浸会大学的传媒专业就十分强劲，在业界认可度是非常高的，这个专业在亚洲是Top3的存在，如果你想选这个专业，浸会大学是个非常不错的选择。

英国大学排名靠前的就很多了，当然如果你拿到了牛津，剑桥这种级别学校的offer，那你麻溜的去英国哈哈哈。如果是和香港心仪的大学排名接近的大学，那你还需要考虑一下专业和收费的问题。

![](https://picx.zhimg.com/v2-6d87bd925c626288e8b2fed8c49f4621_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='778' height='781'></svg>)![](https://picx.zhimg.com/v2-a6984983320a16baa995c259694eaf64_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='791' height='857'></svg>)

## **2. 费用**

费用主要有两部分，一个是学费，一个是生活费。香港和英国的授课型硕士一般都是一年学制的，所以学费也指的是一年的费用。不同专业收费是不同的，这里我就以计算机为例，把排名相近的学校的学费做了一下比较和总结：

![](https://pica.zhimg.com/v2-74f45356287e401fcb14ee0dc04c7b7e_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='941' height='303'></svg>)
> “ 数据来源：指南者留学 [http://www.compassedu.hk/](https://link.zhihu.com/?target=http%3A//www.compassedu.hk/) ”

虽然这里仅仅给出的是计算机硕士专业的学费，但是还是可以看到英国留学在学费这一块还是要明显比香港贵的。统计结果显示英国学费比香港平均贵9万人民币左右，这个其实还是个不小的开销的。如果家庭条件有限，香港是个性价比更高的选择。

如果你想选的专业不是计算机，你可以用 **指南者留学APP** 查看和对比不同学校专业和收费情况。他有一个功能我觉得非常nice，就是它会给出每个专业开设了哪些课程，你可以通过查看专业课程大概了解这个专业到底需要学些什么东西，而不至于被专业名称给骗了。

![](https://pic1.zhimg.com/v2-61c85ad24f5cb3bb9a8a8e87517d353f_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='904' height='897'></svg>)

## **3. 生活方便程度**

这一点毋庸置疑是香港更方便，虽然本地人说粤语，但是你跟他说普通话，大部分人还是会很友好地用普通话回你的（除了部分茶餐厅的工作人员。。）。

另外，香港的生活、饮食习惯和内地也是差不多的，内地过的一些节日香港也会有，只不过香港不像内地有长假，每次放假都只是一两天而已。当然除了内地的一些节日，香港还有一些西方的节日也过的（放假）。

对了，平时如果手痒想买东西，京东和淘宝也是可以很方便使用的。天猫超市和京东都可以送货到家。

另外你如果到香港留学，可以申请香港居民身份证，之后你就可以享受香港政府提供的一系列户外活动服务，大部分收费非常便宜甚至是免费的。你可以申请骑马，划帆船，射箭等。另外虽然说香港面积小，但是令人震惊的是他有很多公园和海岛，这些地方一般都是免费的，如果喜欢户外游玩，香港是个非常不错的地方。

![](https://picx.zhimg.com/v2-4e37a16d37e77159767dbe1802754925_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='682' height='229'></svg>)

## **4. 就业认可度**

无论是在英国还是香港读硕士，毕业出来认可度都是不错的。像腾讯华为这些私企每年招聘都会专门开设海外专场。另外国企或者选调生这一块也是认可的，而且香港是被视为境外留学的，也就是通常说的海龟。虽然近年来海龟这个词含金量没以前高了，但是在找工作的时候也还是有帮助的。

另外，我自己个人的建议是如果你打算以后毕业回国工作，那香港是个非常不错的选择。原因有两个。一是因为香港硕士毕业以后，只要你能在香港找到工作，香港政府会给你一年的时间继续待在香港工作，之后续签也是很容易的。只要待满七年就可以申请永居身份。另一个就是最近大家热议的大湾区，毋庸置疑，大湾区是以后发展的宝地，如果你硕士在香港读，你能多一年的时间掌握行情，毕竟近水楼台嘛。

## **5. 香港留学优势**

因为我自己在香港留学，所以我自己还是比较倾向于推荐香港的。当然前提是你申请的英国大学排名和香港的接近。原因主要有以下几点吧：

1. 香港几乎所有大学都是英语教学，所以如果你想提高自己的英语能力，在香港也是可以的。另外你如果对粤语感兴趣，香港当然是不二之选。
2. **性价比高**。这个在前面已经介绍过了，香港留学的学费是明显要比英国便宜的。但是有一个缺点就是房租贵而且小，所以如果想省钱，平时可以自己买菜做饭。香港这边的菜市场东西还是蛮便宜的，如果你自己天天去外面下馆子，那肯定开销也不小。
3. **师资优秀**。能在香港留下来教书的老师都是强者中的强者，而且很多老师自己本身就是博导，所以如果你以后有读博意愿的话你可以在硕士期间就找到心仪的老师积累科研经历。
4. **良好的跳板**。如果你一心想去欧美更好的大学深造，但是自己本科学校过不了门槛，那香港是个非常好的选择。我认识不少人高考考得不太好，本科是二本，双非等，通过来香港读一年的硕士后，有的后来去了港大读博，有的去了美国哥伦比亚大学深造。这个跳板真的不是吹的。

如果有什么其他的问题，欢迎私信或者付费咨询。


---

## 如何评价华中科技大学校长李元元卸任，由尤政担任新校长？

`link: https://www.zhihu.com/question/493432715/answer/2179637422 · created: 1634702064`


听说 渣科是唯一一所党委书记和校长都是院士的高校

电信学院最近好像领导班子也有变动，还搞了不同城市的校友微信群

我虽然买股票不行，但是感觉当初选学校算投资对了 ᥬ ᭄ᥬ ᭄渣科发展趋势不错，学弟学妹们赶快冲啊啊啊啊啊啊啊啊啊


---

## 如何评价《英雄联盟手游》10 月 8 日双系统不限号不删档测试？

`link: https://www.zhihu.com/question/491103003/answer/2160313402 · created: 1633681825`


没玩过端游lol，纯路人体验，感觉lol手游打击感没有王者荣耀好，游戏界面也太昏暗了 。

节奏也太慢了，买装备必须回城。

另外移动视野的时候也不太好控制，有的时候移动的范围太大了，不太跟手

不过皮肤还挺精致的，但是我还是选择农药，主要是也不想再学新东西了hhh

感觉像我一样只玩过王者荣耀的大部分玩家应该不会被吸引过去吧

![](https://pic1.zhimg.com/v2-7fb21f7d5bd007863b4e36a376fd5982_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2844' height='1280'></svg>)


---

## 为什么奥特曼、七龙珠里的人物一开始不用大招结束战斗？

`link: https://www.zhihu.com/question/36837429/answer/2148236850 · created: 1632987788`


可以参考华强买瓜。

要先试探，之后再开大招

![](https://pic1.zhimg.com/v2-8802d30d3afcea26468658b4ea942269_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='432' height='360'></svg>)![](https://pic1.zhimg.com/v2-664642c5f359b6ac1e56e37fd9474adf_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='432' height='360'></svg>)


---

## 可收缩式的数据线原理是什么？

`link: https://www.zhihu.com/question/26452808/answer/2097105754 · created: 1630485312`


【可收缩网线其实就靠一颗钢珠控制-哔哩哔哩】[https://b23.tv/XiV5pp](https://link.zhihu.com/?target=https%3A//b23.tv/XiV5pp)


---

## 和同事一起开车自驾游西藏，说好AA制，事后清单里有一千元汽车磨损费，这个钱该给吗？

`link: https://www.zhihu.com/question/465716749/answer/1994428880 · created: 1626104046`


![](https://pica.zhimg.com/50/v2-6bbc98cfac16b432222ea0dcf76459d3_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240'></svg>)![](https://picx.zhimg.com/50/v2-74175267233ad127da96213a695e5fd0_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240'></svg>)


---

## 想去香港浸会大学读研究生，大概一年的费用是多少？

`link: https://www.zhihu.com/question/40446748/answer/1993663111 · created: 1626078039`


## 学费

学费绝对是留学开销的大头了，我查了一下浸会大学文学院两个专业的学费，如下图，大概都是在10W一年左右。另外两个专业的课程也都给出了，仅供参考

![](https://pica.zhimg.com/v2-0f932e493d4416e167e57bf86fbd6725_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='521' height='642'></svg>)

图片来自【指南者留学APP】

除了学费，相信你关心的东西还有不少，比如衣食住行等各个方面，毕竟香港和内地的生活习惯还是有很大差别的，这里我通过介绍各种APP的方式来解答你关于开销问题的疑虑

## 食

### 食堂

学校食堂一顿基本上在30到50左右，一天如果都在学校吃基本上就是100左右能hold住，当然你顿顿吃贵的，那价格也就上去了。

### 外卖

学校食堂吃腻了可以试试外卖，第一个必须推荐 foodpanda，之前点了 **湖南少奶（九龙城一家湘菜馆）** 的外卖，一共花了1000多港币，但是外卖费用只要25，这在香港我已经很知足了哈哈哈，平均下来每个人200多左右

![](https://pica.zhimg.com/v2-17c0fb5ae5c074ed56b9697c0926c2c9_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='701' height='677'></svg>)

### 港版大众点评：Openrice （开饭喇）

这个上面的评价都还蛮准确的，而且店铺收集的也很全，遇事不决就用openrice

![](https://pica.zhimg.com/v2-dd778e01e99ea4f3b7e8292ec39fc86e_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='677' height='674'></svg>)

### 日式美食

如果你喜欢吃日式美食，那么推荐你下载 **KABU** 这个APP，你可以用它提前预约，否则等你到现场去等，估计登上几个小时都排不上号（惨痛经验啊。。）

我们之前吃过的一家日式烤肉店叫 牛角，这家店在旺角，感兴趣的小伙伴可以去试试

![](https://pica.zhimg.com/v2-32c9d071c4d6e7da74cdfbb2d8b3c68e_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='686' height='580'></svg>)

## 住

### 寄托留学租房

首先推荐微信小程序 **寄托留学租房**，这上面有很多是转租或者房东直租的，价格要比中介便宜不少，很多可以加微信再详聊的，注意要区分真假信息，另外租金价格也要货比三家后再签合同，最好是咨询一下认识的师兄师姐。非常不推荐像 **港漂家** 这类的，我个人的感受是租金贵，另外就是你给钱后态度就变了，反正印象不太好。能直接找房东租房时最好的，价格会相对便宜不少

我个人经验是 如果你住双人间，价格2000-3000左右比较合理；如果是单人间基本上是4000往上吧 。很多中介会要你一次性交一年的房租，如果可以找到月租的一定要找月租的哈哈哈。总的来说一年的房租大概在3万到7万左右

![](https://picx.zhimg.com/v2-2db37f886214ad07987251e096b8daf6_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1080' height='2400'></svg>)

### 28Hse

28Hse类似于内地的安居客，功能也还可以，不过还是那句话，优先找上面的房东

![](https://pic1.zhimg.com/v2-80c7a49da9a15d00441c426d06b84a25_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='671' height='570'></svg>)

## 行

### 谷歌地图

出门导航直接下载个谷歌地图就完事了，内地的地图软件在香港有的时候不靠谱

### 巴士

如果要坐巴士，可以下载 APP 1933- KMB，他可以很精准地告诉你下一辆公交车大概几分钟后到站，这样你就可以很从容地出门了

![](https://picx.zhimg.com/v2-b5663e3d7af9b47f23d8a9879c4fe1fe_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='678' height='588'></svg>)

## 玩

### 网上购物

是的你没有看错，在香港你也可以像内地一样网上购物~~~~再也不是乡巴佬了

![](https://picx.zhimg.com/50/v2-cf4c496f4f615e46d351d0b63a803426_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='225' height='225'></svg>)

But邮费却是一个不小的开支，不过我来告诉你省邮费的方式

![](https://pica.zhimg.com/v2-ce0fca2cd00b4a8b2e632f67af0a4f20_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='451' height='512'></svg>)

我自己常用的有三种方法：

第一种就是用 天猫超市 （打钱），你只需要买满249，总重量在10公斤以内即可包邮，且送货上门

![](https://pic1.zhimg.com/v2-4a53e68ea056974c37d67622dc28f046_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1080' height='2400'></svg>)

第二种是京东超市，这个显得小家子气一点，买满99，而且在3公斤内包邮

![](https://pic1.zhimg.com/v2-9e39a7caf2f4b6138a12f1a4e9792897_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1440' height='3201'></svg>)

第三种就是集运，淘宝和京东都提供这种服务。集运简单理解就是 你在淘宝好几个店都剁手买了东西，注意要统一下单，之后这些东西都会发往一个中点站，通常是在东莞或者广州，这个你不用管，当这些东西都到了之后，淘宝会把这些东西打包起来发往香港，最后送到你手上。一般来说内地段是免邮费的，但香港路段就是要收费的了。

当然，香港本地也是由电商的，你可以下载 price， 这个软件提供了一些线下门店的联系方式和货品价格，我一般用这个来看价格，最后买东西还是回去实体店

![](https://picx.zhimg.com/v2-88a90560dcabff010134a616bf50349e_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='707' height='689'></svg>)

### 支付

你可以下载港版支付宝，即 AliPay就可以在线支付了，目前有不少门店都是支持的，当然你可以用微信支付，不过你需要先申请开通港版钱包，具体开通方式可以查看这篇文章

[微信开通香港钱包方法](https://zhuanlan.zhihu.com/p/101651544)

### 听音乐

来香港后，内地的听歌软件很多歌都会变成灰色了，我推荐下载 Spotify，刚开始有三个月的免费试用，你也可以下载YouTube music，都还不错，只不过想要白嫖的话可能需要忍受时不时的广告

![](https://picx.zhimg.com/v2-28f28f9e0701aed6780c21cf11f74109_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='663' height='579'></svg>)

说了这么多，对于想来香港但是还没拿到offer的同学肯定是极其痛苦的，所以你可能还需要一个软件来帮助你选择合适的学校和专业。

![](https://pic1.zhimg.com/v2-c50bc7a1517d9c027edb336640ad8f69_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='482' height='355'></svg>)

对于还在读大二大三的童鞋，如果有想来香港继续深造的想法的，其实现在可以开始了解了。但是估计大多数同学也不知该从何开始了解，选什么学校，什么专业，得花多少钱，这些都是得花不少时间去了解的，一想到这，是不是又打开了王者荣耀在峡谷里畅玩了一把哈哈哈

![](https://picx.zhimg.com/50/v2-52ea21094bac31008f77e999dc8b4cd3_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='225' height='225'></svg>)

## 留学申请软件-指南者留学

香港一共有八所公立大学，简称八大，分别是 香港大学，香港科技大学，香港中文大学，香港城市大学，香港理工大学，香港浸会大学，香港岭南大学和香港教育大学。

这里我推荐一个软件，叫 **指南者留学，**这个软件界面精简，但是提供的内容不简单，关键还是免费的。它总共有4个板块：首页，院校，服务和我的。

我看了下院校，他很全面地提供了各个港校的不同专业的情况

![](https://picx.zhimg.com/v2-1c5d09fc6325de25646780e23867707f_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1080' height='2400'></svg>)

图片来自【指南者留学APP】

比如它很清晰地给出了不同学校的不同专业的申请条件，课程设置情况等等，另外每个学校的录取率也有做统计

![](https://picx.zhimg.com/v2-d046b509004058e23f5ef5719220d007_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='976' height='705'></svg>)

图片来自【指南者留学APP】

很多同学会私信问我这样一个问题：我本科不是211也不是双非，我可以申请吗？

其实每个人的情况都不一样，我不太好给出一个统一的建议，最好的是看看其他类似你情况的人的经验， **指南者留学** 这个软件就很贴心的提供了这么一个功能，你可以看看其他人申请成功都做了哪些努力，你就可以借鉴他们的方向去努力了

![](https://pic1.zhimg.com/v2-b9c191d60e1782dda607db1141063e2d_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1011' height='678'></svg>)

图片来自【指南者留学APP】

当然，如果你担心自己一个人找不到合适的项目，这个软件也有提供一些付费服务，比如给你提供实战项目和科研实习等，不过我的建议是最好自己打好一定基础后再去上这些课，不然只会是浪费钱，这些都是锦上添花的东西，而不是让你一蹴而就的

![](https://picx.zhimg.com/v2-7db0c7ce88e758b36219d17694e4846e_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1050' height='672'></svg>)

图片来自【指南者留学APP】

最后，祝愿大家都能拿到自己心仪的offer，早起来香港沉浸式的体验当地学习生活，如果有想来浸会计算机系读书的，说不定你某一门课的助教就是我哈哈哈，期待相遇~~


---

## 如何入门并逐渐精通AutoML/AutoDL及其在计算机视觉领域的研究？

`link: https://www.zhihu.com/question/461037620/answer/1902814323 · created: 1621828171`


只谈谈个人的学习方法，希望对想学习AutoML的同学有帮助

## 综述

第一步当然是得看综述，这样你能有一个全局的概念，不至于看一大堆NAS论文的时候不知道他们的区别是什么，而迷失在技术细节里。

谈到综述，那必然首推NAS综述鼻祖： **Neural Architecture Search: A Survey**

[Neural Architecture Search: A Survey](https://link.zhihu.com/?target=https%3A//arxiv.org/abs/1808.05377)![](https://picx.zhimg.com/v2-3739d240368534f5477c3cc47ef8deb9_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='780' height='306'></svg>)

NAS流程图

这篇综述将NAS划分成三个组成部分：搜索空间，搜索策略和性能评估策略。后续基本所有NAS论文也都遵循这个框架设计思路，或者在这个框架下改进。

接下来推荐你看看我们实验室的AutoML综述：**AutoML: A Survey of the State-of-the-Art**

[AutoML: A Survey of the State-of-the-Art](https://link.zhihu.com/?target=https%3A//arxiv.org/abs/1908.00709)

我们的综述清晰地给出了一个完整的AutoML的pipeline框架，如下图示。

![](https://picx.zhimg.com/v2-b7d685e80d1ba1e7699b22a1df5a295b_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1292' height='629'></svg>)

AutoML Pipeline

可以看到我们把传统的机器学习模型和深度神经网络都统一到了一个框架下，NAS（虚线框里面的部分）也在这个AutoML pipeline中。我们还总结了现有的搜索空间和搜索策略等技术细节，详情可以看原论文或者之前的文章

[AutoML综述更新 【AutoML：Survey of the State-of-the-Art】](https://zhuanlan.zhihu.com/p/158162306)

NAS和AutoML的综述有不少，你精度几篇之后，另外几篇可以作为补充阅读，这样你就对AutoML能有一个大题的了解了。

## 阅读经典

阅读论文的时候可能很多技术细节你读的云里雾里，没关系，你这个时候只需要知道它属于哪一类，大概用了某一种方法就可以了。接下来你就需要阅读一些经典的NAS论文，因为后续很多论文都是基于早期的工作做改进或者魔改，又或者是一些rethinking的工作。

这里推荐你阅读一下论文：

* 强化学习

+ 最早的NAS：B. Zoph, Q. V. Le, Neural architecture search with reinforcement learning, in: 5th International Conference on Learning Representations, ICLR 2017
+ [ENAS：Efficient Neural Architecture Search via Parameters Sharing](https://link.zhihu.com/?target=http%3A//proceedings.mlr.press/v80/pham18a.html) ENAS是较早提出权重共享（weight-sharing）的搜索策略，这个也让NAS的搜索从最初成千上百的GPU消耗降到了只需要一个GPU。技术细节可以看看我之前的博客

[论文笔记系列-Efficient Neural Architecture Search via Parameter Sharing](https://link.zhihu.com/?target=https%3A//www.cnblogs.com/marsggbo/p/9435954.html)

* 进化算法

+ 这里只推荐一篇论文，华为的CARS：**Z. Yang, Y. Wang, X. Chen, B. Shi, C. Xu, C. Xu, Q. Tian,C. Xu, CARS: continuous evolution for efficient neural architecture search, CVPR 2020**。早期的进化算法资源消耗的多，而且时间还长（比如AmoebaNet用了450 K40搜索了3150个GPU days），因为不同子网络是互相独立搜索的。不过CARS将进化算法和权重共享做了结合，效率大大提升，源码也开源了，感兴趣地可以了解一下,里面部分代码我也有贡献hhh

[huawei-noah/vega](https://link.zhihu.com/?target=https%3A//github.com/huawei-noah/vega/blob/master/docs/en/algorithms/cars.md)

* 梯度下降

+ 提到梯度下降，那肯定就是鼻祖工作 DARTS了：**H. Liu, K. Simonyan, Y. Yang, DARTS: differentiable architecture search, ICLR 2020.**  后面几乎所有基于梯度下降的都是基于它的思路做的改进

* 强烈推荐看看这篇论文 Once for All: Train One Network and Specialize it for Efficient Deployment。这个是韩松老师团队的工作，他们可以在完成搜索后，可以直接导出模型，而且模型不需要重头训练就能有很好的效果。我有在自己的框架实现这个，发现的确是可以不用train from scratch，导出的任意一个子模型效果都还不错，我们只需要finetune一下下就能进一步提高模型性能。这种训练范式可以理解成 one-shot NAS。类似的工作还有

[Single Path One-Shot Neural Architecture Search with Uniform Sampling](https://link.zhihu.com/?target=https%3A//arxiv.org/abs/1904.00420)

## 阅读原论文代码

算法知道了，下一步要啃的硬骨头就是代码了，以下推荐的代码真的要认真去跑一下，并且理解它的设计思路

* DARTS

+ 这个是原作者开源的代码

[quark0/darts](https://link.zhihu.com/?target=https%3A//github.com/quark0/darts)



+ 这个是更好理解的代码版本，推荐看这个

[khanrc/pt.darts](https://link.zhihu.com/?target=https%3A//github.com/khanrc/pt.darts)

吃了中饭后再更新。。。

吃完继续

* ENAS

+ 原论文是基于TensorFlow写的，emm不做过多评价

[melodyguan/enas](https://link.zhihu.com/?target=https%3A//github.com/melodyguan/enas)



+ 如果你更加钟意pytorch，可以看看这个代码

[carpedm20/ENAS-pytorch](https://link.zhihu.com/?target=https%3A//github.com/carpedm20/ENAS-pytorch)

* Once-for-all: 这个前面提到的韩松老师他们的工作，代码写的很清晰

[mit-han-lab/once-for-all](https://link.zhihu.com/?target=https%3A//github.com/mit-han-lab/once-for-all)

## NAS大一统

如果前面的代码你都体验过后，你会发现，不同框架实现起来千差万别，你想在你的数据集上尝试不同算法得花大把时间做代码迁移（魔改），而且往往还不一定成功。这个时候你需要一个NAS框架来帮助你。目前已经有不少开源的NAS框架，这里我只推荐两个吧，这两个我真的推荐好多次了哈哈哈哈

* 华为的Vega

+ [marsggbo：华为诺亚实验室AutoML框架-Vega：(1) 介绍](https://zhuanlan.zhihu.com/p/258362976)
+ [marsggbo：华为诺亚AutoML框架-Vega：(2) 代码结构](https://zhuanlan.zhihu.com/p/306462348)

* 微软的NNI

+ [marsggbo：Retiarii：微软在NAS框架上的新动作，已被顶会OSDI2020接收](https://zhuanlan.zhihu.com/p/372128920)

最近我自己也在实现NAS框架，完成之后会开源出来，也欢迎大家在评论区提出意见，比如你觉得现有框架有哪些痛点，或者你希望框架是什么样的~~~

另外有出版社也找到我希望写一本关于AutoML的书籍，这里也想征集一下大家的想法和意见，这类书籍应该怎么写，或者你希望这本书里写什么内容~~

当然，如果你对AutoML颇有研究，也希望参与这本书的写作，欢迎私信我~~~

### 微信公众号：AutoML机器学习

![](https://picx.zhimg.com/50/v2-87083e55cd41dbef83cc840c142df48a_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='0' height='0'></svg>)

**MARSGGBO♥原创**  
如有意合作或学术讨论欢迎私戳联系~  
邮箱:marsggbo@foxmail.com


---

## 新手如何实现个简单AutoML框架。有参考的github开源项目介绍吗？

`link: https://www.zhihu.com/question/319723361/answer/1896039662 · created: 1621486375`


微软的NNI。后面的版本应该会基于他们的最新论文Retiarii改进。

[marsggbo：Retiarii：微软在NAS框架上的新动作，已被顶会OSDI2020接收](https://zhuanlan.zhihu.com/p/372128920)

华为的Vega

[marsggbo：华为诺亚实验室AutoML框架-Vega：(1) 介绍](https://zhuanlan.zhihu.com/p/258362976)[marsggbo：华为诺亚AutoML框架-Vega：(2) 代码结构](https://zhuanlan.zhihu.com/p/306462348)

亚马逊的Autogluon

[awslabs/autogluon](https://link.zhihu.com/?target=https%3A//github.com/awslabs/autogluon)

其他

* AutoKeras
* AutoPytorch

NAS实现规范

[marsggbo：神经网络架构搜索（NAS）最佳科学研究实践指南](https://zhuanlan.zhihu.com/p/298060189)

打个广告，我们实验室将NAS应用到COVID-19 CT图像分类的应用，论文已被AAA2021接收，代码也已经开源

[https://github.com/HKBU-HPML/CovidNet3D](https://link.zhihu.com/?target=https%3A//github.com/HKBU-HPML/CovidNet3D)

### **微信公众号：AutoML机器学习**

**![](https://pica.zhimg.com/50/v2-87083e55cd41dbef83cc840c142df48a_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='0' height='0'></svg>)**

**MARSGGBO♥原创**  
**如有意合作或学术讨论欢迎私戳联系~**  
**邮箱:marsggbo@foxmail.com**  
**2020-11-11 10:34:59**


---

## 2020 年过去了，人工智能领域都有哪些突破?

`link: https://www.zhihu.com/question/452342087/answer/1811379221 · created: 1617248139`


感谢 [@亚马逊云科技](https://www.zhihu.com/people/d354f56f08d0764ded5a68eb036f5ba6) 的邀请，我的方向主要是AutoML，所以就介绍一下这个领域在2020的一些发展吧。

## 智能体-王者荣耀

> 论文：Mastering Complex Control in MOBA Games with Deep Reinforcement Learning

在游戏方面的研究一直在进行着，主要用到的技术是深度强化学习（deep reinforcement learning, DRL）。

在2015年，有研究用deep Q-Network训练agent玩Atari游戏，下面是游戏列表，看看你都玩了哪些游戏。

![](https://pic1.zhimg.com/v2-97ebe6cad33c61530bc835b76d47dc31_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='929' height='221'></svg>)![](https://picx.zhimg.com/v2-fb9898da8658c4d9023393fbdee48281_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='922' height='214'></svg>)

2016年让人工智能大火的AlphaGo诞生。2018年，OpenAI团队利用AI技术在Dota2游戏中战胜了专业玩家。

之前参加过腾讯内部举办的Workshop，其中他们就分享了他们利用AutoML在王者荣耀游戏上搜索超参的工作。之后腾讯在2020年的一篇被AAAI接收的论文（简称MOBA1v1）使用DRL技术在王者荣耀1V1模式下完胜人类玩家。下图是AlphaGo和MOBA1V1的对比，可以看到后者的搜索和动作空间都远大于AlphaGo，而且我们都体验过被460的折磨，所以算法对实时性的要求也是非常高的。

![](https://picx.zhimg.com/v2-24660885ab318a13565dfdb04cde98c1_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='594' height='244'></svg>)

看看下面的系统设计，可以粗略地感受一下每时每刻需要处理的信息量之大。之前还以为是腾讯会直接通过后台数据拿到所有对象的数据，没想到是通过每一帧的图像信息提取特征的。

![](https://picx.zhimg.com/v2-b513b57a7639c7af38fae82e75e8d5de_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1027' height='762'></svg>)

1V1已经战胜人类了，之后继续用AutoML在5V5中战胜人类还会远吗？期待~

## 国产AI框架

在2020年之前，国内的AI框架只有百度的PaddlePaddle在艰难地求生。而到了2020年后，一批国产AI框架如雨后春笋般都冒出来了。

### 旷世-天元（MegEngine）

2020.03.26 旷世开源了天元深度学习框架，官方称 MegEngine 具有"训练推理一体化"特性，其中"训练"是在 Python 环境中进行的，而"推理"则特指在 C++ 环境下使用训练完成的模型进行推理。早期智能手机人脸识别都用到了旷世的技术，难不成就是用的这个框架？

![](https://pic1.zhimg.com/v2-f33f8ed10e6cf8ffdac0728d03447614_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='628' height='307'></svg>)

### 华为Mindspore

2020.03.28 华为发布了MindSpore框架。这个框架没怎么用过，不过之前在华为实习的时候有幸参与了[Vega框架](https://link.zhihu.com/?target=https%3A//www.google.com.hk/url%3Fsa%3Dt%26rct%3Dj%26q%3D%26esrc%3Ds%26source%3Dweb%26cd%3D%26cad%3Drja%26uact%3D8%26ved%3D2ahUKEwib8sWL4tXvAhVLFogKHc-DBdYQFjAAegQIBRAD%26url%3Dhttps%253A%252F%252Fzhuanlan.zhihu.com%252Fp%252F258362976%26usg%3DAOvVaw211M1MF9Rd6aBLKm4Qswdy)的实现，里面不少算子就提供了对MindSpore的支持，所以可能华为内部也不少工作都是基于MindSpore开发的。

![](https://picx.zhimg.com/v2-3b06431f02850e8bcceba77c134f7325_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1264' height='436'></svg>)

### 清华大学-计图（Jittor）

2020.04.02 清华大学开源了自研的 **计图（Jittor）**深度学习框架。

> [清华大学发布深度学习框架--计图（Jittor）-清华大学新闻网](https://link.zhihu.com/?target=https%3A//news.tsinghua.edu.cn/info/1416/77422.htm)

计图创新的采用了统一计算图，用户并不需要手动切换，计图可以动态的将计算图拆分成可以优化的子静态图。让计图在保持动态图灵活性的同时，还可以发挥出静态图的运算性能。计图与国际主流平台相比，具有多项先进特性，其统一计算图的特性如下图所示。

![](https://pic1.zhimg.com/v2-020eb553024a0913ec6e7135b3955dc1_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='650' height='400'></svg>)

### Oneflow

2020.07.31 Oneflow正式在GitHub上开源。OneFlow 从研发之初就主打高效性，致力于解决大规模分布式 AI 训练问题。Oneflow发布前几天的时候加入了一个技术讨论群，Oneflow创始人袁进辉也在群里，然后每天像手机预告一下发布Oneflow的预告海报，还时不时回复群里人的问题，第一次感觉离大佬这么近哈哈哈

[https://github.com/Oneflow-Inc/oneflow](https://link.zhihu.com/?target=https%3A//github.com/Oneflow-Inc/oneflow)

袁进辉在一次采访中说道：

> 遍地黄金的日子过去了，低垂的果子已经没了”，技术创新主导的时代必将来临，让我们有“像鹰一样的眼光，像狼一样的精神，像熊一样的胆量，像豹一样的速度”，去抓住属于技术人的机遇。

希望国产AI框架越做越好！

## AutoML平台&框架

既然已经有了Pytorch、TensorFlow、PaddlePaddle、Keras、MNext，还有一批国产框架诞生，肯定是因为还有不少问题仍待解决。

我认为其中一个发展方向应该就是实现AutoML的全自动化的框架平台，我之前的一篇文章简要介绍了AutoML技术的发展，尤其重点总结了NAS（Neural Architecture Search）技术。

[AutoML综述更新 【AutoML：Survey of the State-of-the-Art】](https://zhuanlan.zhihu.com/p/158162306)

NAS技术也越来越被广泛应用到各个领域，未来应该也会变成一个非常basic的组件，我们除了可以直接调用别人设计好的网络结构，也可以直接通过NAS来搜索自定义的网络结构。更多技术细节可以阅读我们的综述论文。

[https://www.researchgate.net/publication/347624256\_AutoML\_A\_survey\_of\_the\_state-of-the-art](https://link.zhihu.com/?target=https%3A//www.researchgate.net/publication/347624256_AutoML_A_survey_of_the_state-of-the-art)

其实不少AI公司都推出了自己的AutoML平台，比如

### **百度-EasyDL**

[EasyDL-零门槛AI开发平台](https://link.zhihu.com/?target=https%3A//ai.baidu.com/easydl/)

### **谷歌-Google Cloud AutoML**

### **阿里巴巴-阿里云机器学习平台PAI（Platform of Artificial Intelligence）**

[机器学习PAI 产品简介 | 阿里云文档中心](https://link.zhihu.com/?target=https%3A//www.alibabacloud.com/help/zh/product/30347.htm)![](https://pic1.zhimg.com/v2-a27808caacac640d72fe9bb47c22828f_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1530' height='1140'></svg>)

### **微软-Azure Machine Learning**

[Azure Machine Learning - ML as a Service | Microsoft Azure](https://link.zhihu.com/?target=https%3A//azure.microsoft.com/en-us/services/machine-learning/%23features)![](https://picx.zhimg.com/v2-6c1b29b20f848a17e4e3c2f39c8faa29_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='734' height='413'></svg>)

### **亚马逊-SageMaker**

[Amazon SageMaker 机器学习\_机器学习模型构建训练部署-AWS云服务](https://link.zhihu.com/?target=https%3A//aws.amazon.com/cn/sagemaker/)![](https://pic1.zhimg.com/v2-e7c286be2abef854ca779e12f08311ce_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2286' height='574'></svg>)

不过以上平台都是商用的，换句话说你如果想自定义AutoML算法，这些平台并不能满足你的需求。我个人比较推荐的可以自定义的框架（我自己亲测好用的）如下，这两个我真的推荐无数次了，对AutoML感兴趣的朋友一定要试试

### 微软NNI

[microsoft/nni](https://link.zhihu.com/?target=https%3A//github.com/microsoft/nni)

### 华为Vega

[huawei-noah/vega](https://link.zhihu.com/?target=https%3A//github.com/huawei-noah/vega)

另外，我们实验室也基于NNI搜索了用于COVID-19 CT图像分类，这个工作已被AAAI2021接收，代码已开源，感兴趣的可以看看

[HKBU-HPML/CovidNet3D](https://link.zhihu.com/?target=https%3A//github.com/HKBU-HPML/CovidNet3D)

### **微信公众号：AutoML机器学习**

![](https://picx.zhimg.com/50/v2-87083e55cd41dbef83cc840c142df48a_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='0' height='0'></svg>)

**MARSGGBO♥原创**  
**如有意合作或学术讨论欢迎私戳联系~**  
**邮箱:marsggbo@foxmail.com**


---

## NAS（网络结构搜索）在哪能找到交流平台与教学？

`link: https://www.zhihu.com/question/449702566/answer/1783640357 · created: 1615901141`


王婆卖瓜一下，你可以关注以下信息平台：

* 公众号：[AutoMl机器学习](https://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/mp/profile_ext%3Faction%3Dhome%26__biz%3DMzI5OTI3ODAyNg%3D%3D%23wechat_redirect)

主要是AutoML相关内容，下面是内容截图

![](https://picx.zhimg.com/v2-d694e0e1e5f9994cd69eb53615607af2_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1080' height='2400'></svg>)![](https://pic1.zhimg.com/v2-e3c411a305ffba03678d5f53c80777a7_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1080' height='2400'></svg>)

* 知乎专栏：

[AutoML](https://www.zhihu.com/column/automl)

* AutoML论文合集

[Literature on Neural Architecture Search – AutoML](https://link.zhihu.com/?target=https%3A//www.ml4aad.org/automl/literature-on-neural-architecture-search/)[AutoML](https://link.zhihu.com/?target=https%3A//marsggbo.github.io/automl_a_survey_of_state_of_the_art/)

* AutoML综述：

[(PDF) AutoML: A Survey of the State-of-the-Art](https://link.zhihu.com/?target=https%3A//www.researchgate.net/publication/334963534_AutoML_A_Survey_of_the_State-of-the-Art)

综述论文中文版：

[marsggbo：AutoML综述更新 【AutoML：Survey of the State-of-the-Art】](https://zhuanlan.zhihu.com/p/158162306)

* NAS框架

+ 微软的NNI（强烈推荐）

[https://github.com/microsoft/nni](https://link.zhihu.com/?target=https%3A//github.com/microsoft/nni)



+ 华为的Vega，之前有幸实习参与过项目开发，还不错。之前写了文章介绍，可参考：

[marsggbo：华为诺亚实验室AutoML框架-Vega：(1) 介绍](https://zhuanlan.zhihu.com/p/258362976)[marsggbo：华为诺亚AutoML框架-Vega：(2) 代码结构](https://zhuanlan.zhihu.com/p/306462348)


---

## 有什么办法可以考上华中科技大学？

`link: https://www.zhihu.com/question/445301375/answer/1783055353 · created: 1615880211`


超常发挥到极致的两个极端 就可以考上华科。

平时能考清华，结果考差了可以来华科，毕竟南方小清华

平时考的一般，结果高考考的不错，但也没那么好，你就可以选华科(我就是这种哈哈哈哈)

附上若干年前拍的照片，现在设施越来越好了，估计再也看不到海了哈哈哈

![](https://picx.zhimg.com/v2-85fecc8d289b5590d9be63b63bc90be2_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='853' height='640'></svg>)![](https://picx.zhimg.com/v2-bbd53c0a49a74dfd277eae1a37d878d2_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1920' height='1080'></svg>)![](https://pic1.zhimg.com/v2-4e86c23e1b37bd0ca46cbfbeeef2c182_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1920' height='1080'></svg>)![](https://pic1.zhimg.com/v2-bf055cf55d45df2580889a17bf738d4c_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='640' height='853'></svg>)![](https://picx.zhimg.com/v2-a884f2b0f85a9d04deadd028138396c9_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='720' height='541'></svg>)![](https://picx.zhimg.com/v2-1d7a54e38b48a44a7f78b65a7e644989_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='800' height='600'></svg>)![](https://pic1.zhimg.com/v2-4deed73411834b70cf87dd75c7040e85_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='849' height='482'></svg>)![](https://picx.zhimg.com/v2-f147725773e0bfbe0f51cd1c2d368e08_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1456' height='1080'></svg>)


---

## Python中既然可以直接通过父类名调用父类方法为什么还会存在super函数？

`link: https://www.zhihu.com/question/20040039/answer/1781379412 · created: 1615799109`


如果套娃套的很深，那岂不是要挖祖坟才能把父类的方法都执行一遍？`super` 一个很大的作用就是我们可以不用关心所有父类的所有细节，只专注于我们当前想要实现的类即可。关于`super` 的理解，我把之前写的文章搬过来，希望有帮助。

[marsggbo：Python的super函数直观理解](https://zhuanlan.zhihu.com/p/356720970)
> `super`相关的介绍文章看了无数遍，每次看得都云里雾里的，没过多久就忘了，只模糊知道跟MRO有关，但是稍微一复杂就不知道怎么回事了，本篇文章主要记录我对super的理解，尽量以简单易懂的方式介绍，如果你看完这篇文章还是没懂。。。那么很抱歉，我尽力了hhhh

## **粗暴简单的理解**

**super的作用就是执行父类的方法**，虽然这句话不完全对，但是也差不多是那么个意思了。

比如以单继承为例

```
class A:
    def p(self):
        print('A')
class B(A):
    def p(self):
        super().p()
B().p()

>>> A
```

可以看到`B().p()`其实就是执行的`A.p`

## **万能模板解题技巧**

前面介绍的是最简单的情况，那万一复杂一点，比如多继承的情况呢？这种情况我们只要知道 MRO 序列，无论super怎么变化都不怕了，记住公式就完事了。MRO 序列简单理解就是记录了各个类继承的先后顺序，看下面的例子就明白了

> MRO 的介绍可以看这篇文章： [https://python3-cookbook.readthedocs.io/zh\_CN/latest/c08/p07\_calling\_method\_on\_parent\_class.html](https://link.zhihu.com/?target=https%3A//python3-cookbook.readthedocs.io/zh_CN/latest/c08/p07_calling_method_on_parent_class.html)

我们看下面的例子

```
class A:
    def p(self):
        print('A')
class B():
    def p(self):
        print('B')
class C(A,B):
    def p(self):
        print('C')
class D(C):
    def p(self):
        print('D')
a = A()
b = B()
c = C()
d = D()
```

四个类的MRO (可以通过查看`__mro__`属性获得，例如`A.__mro__`)) 分别是：

* A: (A, object)
* B: (B, object)
* C: (C, A, B, object)
* D: (D, C, A, B, object)

什么意思呢，我们以`A`类为例，它的MRO顺序是他自己和`object`，很好理解，因为python里一切都是对象，所以你可以看到四个类的终点都是`object`。那`C`类的 MRO 也好理解，第一个顺序永远是寄几，然后按照代码顺序依次是 `A,B`，最后是`object`。

相信看到这你应该知道MRO是什么意思了吧，那`super`是怎么用的呢？

super本身其实就是一个类，`super()`其实就是这个类的实例化对象，它需要接收两个参数 `super(class, obj)`,它返回的是`obj`的MRO中`class`类的父类（可能有点绕，待会看后面的栗子就好懂了）:

* `class`：就是类，这里你可以是`A,B,C`或者`D`
* `obj`：就是一个具体的实例对象，即`a,b,c,d`。我们经常在类的`__init__`函数里看到super的身影，而且一般都是写成这个样子的`super(className, self).__init__()`，`self`其实就是某个实例化的对象。

## **举几个栗子**

看到这里如果还是没明白，咱们就多看几个例子就完事了，建议你可以打开`ipython`输入如下示例，可以更加直观感受`super`：

## **栗子1**

首先我们看看下面的命令是什么意思呢？

```
super(C, d).p()
```

前面我们说过`super`的作用是 **返回的是`obj`的MRO中`class`类的父类**,在这里就表示**返回的是`d`的MRO中`C`类的父类**：

1. 返回的是`d`的MRO：`(D, C, A, B, object)`
2. 中`C`类的父类：`A`

那么`super(C, d)`就等价于`A`,那么`super(C, d).p()`会输出`A`

## **栗子2**

下面代码结果是什么呢？

```
super(A, c).p()
```

**返回的是`c`的MRO中`A`类的父类**：

1. 返回的是`c`的MRO：`(C, A, B, object)`
2. 中A类的父类：`B`

所以最后的输出是`B`

## **最后几个栗子**

> 注意：有的类里面没有`super()`

```
class A:
    def p(self):
        print('A')
class B(A):
    def p(self):
  super().p()
        print('B')
class C(B):
    def p(self):
        print('C')
class D(C):
    def p(self):
        print('D')

d = D()
d.p()
```

这个很简单，最后只会输出`D`

那如果D类改成如下样子呢？

```
class D(C):
    def p(self):
        super().p()
        print('D')
```

很简单，我们首先写出D的MRO为 (D,C,B,A,object)，缺省状态下,super()就表示前一个父类，这里就是C类，那么`super().p()`就会调用`C`的`p`函数，但是`C.p`里没有调用`super`，所以就与`A,B`类无关了，那么最终的输出就是`C,D`

我们再看看最复杂的继承情况

```
class A:
    def p(self):
        print('A')
class B(A):
    def p(self):
        super().p()
        print('B')
class C(B):
    def p(self):
        super().p()
        print('C')
class D(C):
    def p(self):
        super().p()
        print('D')
d = D()
d.p()
```

这里建议你自己在纸上画一下

![](https://pic1.zhimg.com/v2-8a713d800aecf831b64fd1bd911c664f_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1046' height='512'></svg>)

所以最终结果是 `A B C D`

## **多继承**

如果一个类继承多个类，原理一样，我们只要知道了MRO就能知道执行顺序了，比如下面的例子：

```
class A:
    def __init__(self):
        print('A')
class B:
    def __init__(self):
        print('B')
class C(A,B):
    def __init__(self):
        super(C,self).__init__()
        print('C')
class D(B,A):
    def __init__(self):
        super(B,self).__init__()
        print('D')
print(C.__mro__)
print(D.__mro__)
print('initi C:')
c = C()
print('initi D:')
d = D()
```

输出结果为

```
(<class '__main__.C'>, <class '__main__.A'>, <class '__main__.B'>, <class 'object'>)
(<class '__main__.D'>, <class '__main__.B'>, <class '__main__.A'>, <class 'object'>)
initi C:
A
C
initi D:
A
D
```

结果解释，`C` 初始化后的打印结果应该很好理解，首先需要执行 `super(C,self)` 的`_init_` 函数，根据`C` 的MRO可以知道`super(C,self)` 返回的是`A` ，所以可以看到最后的确是先打印出了A，然后是C

我们再看`D` 初始化的结果，注意执行的是`super(B,self)` ，根据`D` 的MRO我们可以知道返回的是`A` 所以打印的结果也是 A，然后打印出了D

## **总结**

对于无论有多少个`super(class, obj)`，我们首先需要知道`obj`的MRO是什么，然后找到`class`的前一个class是什么就好了。

### **微信公众号：AutoML机器学习**

![](https://pica.zhimg.com/50/v2-87083e55cd41dbef83cc840c142df48a_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='0' height='0'></svg>)

**MARSGGBO♥原创**  
**如有意合作或学术讨论欢迎私戳联系~**  
**邮箱:marsggbo@foxmail.com**  
**2021-03-12 21:40:18**


---

## PyTorch FX 功能提供了哪些新的使用场景？

`link: https://www.zhihu.com/question/447721553/answer/1764083595 · created: 1614936786`


简单看了下文档，源代码还没细究，简单地跑了两个demo，感觉蛮有意思的，可以看到首先是对`nn.Module` 模块进行解析得到中间表达式（`st.graph` ），后面的`st.code` 可以自动转化成`forward` 函数

![](https://picx.zhimg.com/v2-caef60196eb4102ac3dbf59680d04986_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='738' height='835'></svg>)

不过目前版本不支持逻辑控制，这也可以理解

![](https://pica.zhimg.com/v2-6b47f64a62c620fc0f020a81c7980a48_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='825' height='656'></svg>)

不过说道新的应用场景，我觉得FX可以很好地和NAS、模型压缩等结合起来，原因如下：

目前很多NAS和模型压缩（通道压缩）算法本质上还是生成一个mask，通过mask来得到模型。这样做法简单而且好理解，但是我觉得在实际部署时非常不方便。

为方便说明，我们以模型通道压缩为例。假如你对VGG16完成了通道压缩，得到了mask。如果我们想得到压缩后的模型有两种方法：

* 一种常见的做法是在forward的时候将模型权重乘上mask，即将压缩的通道权重置为0，但是这种压缩方式很显然并没有真正减少模型参数量
* 另一种就是根据mask在\_*init*\_函数中来手动修改vgg16源代码每一层的通道数，但是如果模型代码很复杂，在\_*init*\_函数中可能使用了for循环来构建模块，这个时候手动修改就显得没那么容易了

NAS任务同样也会遇到上面两个问题，虽然使用Mask可以指定使用哪一个模型，但是我始终觉得这种两种处理方式都不太好，而Pytorch1.8的FX功能可能会让我们实现一个优雅的处理解决方案

![](https://pica.zhimg.com/50/v2-17a6a01b652bfa0f57e9295dddc8c6f8_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='143' height='163'></svg>)

后面抽时间看看FX源码，看看是否真的可行，未完待续。。。


---

## 为什么网上流行南方比东北冷的观点？

`link: https://www.zhihu.com/question/425013547/answer/1701974782 · created: 1611799928`


南北双方辩友吵架都不在一个维度上，总结起来就是

室内南方更冷

室外北方更冷


---

## 如何看待AAAI 2021录用结果？

`link: https://www.zhihu.com/question/432851243/answer/1607434381 · created: 1606911105`


这次中了，但运气成分大。本来4467，一顿rebuttal之后两个reject改成了accept。

rebuttal的感悟就是要揣摩reviewer的心思，做好舔狗的同时要保持真诚。

reviewer说我的novelty不够，我就说you are right, but ...开始解释一波

加更:如果有大佬做的NAS方向的论文被接收了，欢迎私戳，我打算做一个nas论文推荐集合，免费帮忙宣传。

rebuttal整理好了，可以看看这篇文章

<https://zhuanlan.zhihu.com/p/344196352>

公众号【AutoML机器学习】


---

## Knowledge-Based Systems 这个期刊容易中吗？

`link: https://www.zhihu.com/question/326496605/answer/1591891899 · created: 1606184485`


2020年貌似已经升级为1区了。

[AutoML: A Survey of the State-of-the-Art](https://link.zhihu.com/?target=https%3A//arxiv.org/abs/1908.00709)<https://zhuanlan.zhihu.com/p/158162306>

下图是我的提交记录，我提交的是一个AutoML（自动机器学习）方向的综述，第一次投是2月份，然后4月份直接拒了，虽然当时很心痛，因为综述写起来真的是要命，不过reviewer感觉很专业，提了很多有用的建议。

![](https://pic1.zhimg.com/v2-9033673667a85c981bebf3c948a99251_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1851' height='182'></svg>)

后来疫情在家痛定思痛，参照reviewer的意见把Survey基本上是把主要内容和画图都重新写了一遍，内容也丰富了很多，引用文献超过了300多个。这一过程很痛苦，好多次想着算了，随便写写得了，但是睡觉起来后又觉得瞎写一通也是浪费时间，还不如认真写。就这么前前后后一直拖到7月份才写完（主要是疫情在家效率的确很低）。给老师检查之后，在2020.7.8重新提交，之后就听天由命了。

差不多到了9月20几号，reviewer的意见发来了，这一次居然只有两个reviewer，而上一次有4个。谢天谢地，这次reviewer的意见非常少，甚至有一个reviewer一个意见都没有。之后我就在国庆节期间抓紧时间按照reviewer的建议做了调整，提交revised版本。

到了2020.11.22号收到了accept通知，这个时候没有反而没有收到 reviewer意见的时候那么激动了，不过还是很高兴，付出有收获了，毕竟前前后后改了都有六七个版本。

总结一下，kbs期刊收到第一次reviewer的意见应该是提交后的两个月，第一轮如果通过了（给你机会修改论文），那么2个月后应该会收到最终结果。所以基本上4到5个月会出结果，看起来好像比一般的期刊速度快。最后祝大家论文都中中中！！！


---

## 吉林一高校规定学生7点半必须起床，称「没课也要下床，用制度约束学生作息」，你赞成吗？

`link: https://www.zhihu.com/question/427908006/answer/1550430821 · created: 1604033334`


负责后勤和学生学习的领导班子怕工作总结会上没东西可说，硬是逼出了一个领导们都赞同，家长也满意，唯独学生不喜欢的主意，这样KPI就稳住了。

made，这跟我开会前没做啥东西，但是为了应对开会还是不得不硬凑出东西来一样一样的，出来混都不容易哈哈哈哈

![](https://pic1.zhimg.com/50/v2-84d64f299643f087c92e5ab1f355032b_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='225' height='225'></svg>)


---

## 普通人如何对抗算法，从而避免信息茧房？

`link: https://www.zhihu.com/question/424898089/answer/1534768499 · created: 1603240337`


> 信息茧房是指人们关注的信息领域会习惯性地被**自己的兴趣**所引导，从而将自己的生活桎梏于像蚕茧一般的“茧房”中的现象。

说到底，如果你感兴趣的东西越多，那你的房子就越大。如果你感兴趣的东西不多，那么你就只能靠提高你自己对事物的接受程度了。

算法是次要责任人，你自己才是主要负责人，把锅丢给算法不可取。


---

## 有哪些AI开源框架可供开发者使用？

`link: https://www.zhihu.com/question/54884091/answer/1527493987 · created: 1602846499`


知乎居然支持文本自动转视频功能了 有点酷

* AutoML开发框架

AutoML全称是Automated Machine Learning，即自动机器学习，听起来是不是很酷，没错的确很酷，如果感兴趣的话可以读一下我们实验室写的AutoML综述： AutoML: A Survey of State-of-the-art。

![](https://pic1.zhimg.com/v2-83339b83c0a1c95e86b920b41e4736d6_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1299' height='661'></svg>)<https://zhuanlan.zhihu.com/p/158162306>

至于开发框架主要以基于深度学习的为主推荐一下几个：

1. 利益相关首先推荐 [Vega](https://link.zhihu.com/?target=https%3A//github.com/huawei-noah/vega)，之前写了一篇介绍Vega的文章，如下。简而言之，Vega是目前第一个实现端到端AutoML的框架，目前正在参与实习工作，新的版本放出来后易用性相比于已放出的1.0版本会有很大提升，敬请期待。

<https://zhuanlan.zhihu.com/p/258362976>![](https://picx.zhimg.com/v2-dd2a99d48066f9b7b66caff640afdb00_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1377' height='400'></svg>)

2. 第二个推荐巨硬的 NNI, 易用性很强，下至胎儿，上至100岁都很容易上手。反正Vega和NNI选哪个都不差

[microsoft/nni](https://link.zhihu.com/?target=https%3A//github.com/microsoft/nni)![](https://picx.zhimg.com/v2-ca12c4ea927679918ab7198b00b9af8d_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1545' height='761'></svg>)

3. 其他没怎么用过，仅列出名字，欢迎大佬们评论区留言评价以下这些框架：

[https://autokeras.com/](https://link.zhihu.com/?target=https%3A//autokeras.com/)[AutoKeras](https://link.zhihu.com/?target=https%3A//autokeras.com/)[awslabs/autogluon](https://link.zhihu.com/?target=https%3A//github.com/awslabs/autogluon)

* 3D Deep Learning

下面这个是最近由MIT大学韩松团队开发的用于3D 深度学习场景的开源框架。

[mit-han-lab/e3d](https://link.zhihu.com/?target=https%3A//github.com/mit-han-lab/e3d)![](https://pic1.zhimg.com/v2-7e6485069fc9f1dadc68201983b327e2_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='849' height='428'></svg>)

* 基于Pytorch深度定制的开发框架

+ 首推Pytorch-lightning ，目前已经更新到1.0版本，这个库的易用性是保姆级别的，TPU、GPU、多机多卡、amp等一大堆功能都给你弄好了

[https://github.com/PyTorchLightning/pytorch-lightning](https://link.zhihu.com/?target=https%3A//github.com/PyTorchLightning/pytorch-lightning)

* torchline: 这个库是我基于pytorch-lightning进一步封装的，主要是引入了注册机制，所有的模型、优化器、损失函数、数据集等都可以通过一个yml文件完成配置，不用再写一大堆的argparse了，易用性进一步提高。

<https://zhuanlan.zhihu.com/p/97244535>



+ fast.ai： 这个库怎么说呢，我个人是不太喜欢用的，文档写的不合我的胃口。原因可以看这个回答，总之这个库的tutorial里居然好多地方都是 `from ... import *` ，然后代码示例里就一堆不知道从哪里来的函数和类，emm，我还得去源代码里找具体是干啥的

[如何评价Fastai？](https://www.zhihu.com/question/297031440/answer/1059976791)

**目标检测**

* 首推鼎鼎大名的mmdetection

[https://github.com/open-mmlab/mmdetection](https://link.zhihu.com/?target=https%3A//github.com/open-mmlab/mmdetection)

![](https://pic1.zhimg.com/v2-8543ef72f0b1301b86dcdaaedcf0d1e6_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='502' height='191'></svg>)

* 当然Pytorch官方的 Detectron2 也是一个非常不错的选择

[https://github.com/facebookresearch/detectron2](https://link.zhihu.com/?target=https%3A//github.com/facebookresearch/detectron2)

![](https://pic1.zhimg.com/50/v2-378187915986b5d66c31019d6b843d98_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='332' height='95'></svg>)

* 联邦学习开发框架: [FedML.ai](https://link.zhihu.com/?target=https%3A//fedml.ai/)

![](https://picx.zhimg.com/v2-746d2b261b6750fa6eae9e07cfadefa4_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='974' height='474'></svg>)<https://zhuanlan.zhihu.com/p/262497372>

* 图形学开发框架：

[taichi-dev/taichi](https://link.zhihu.com/?target=https%3A//github.com/taichi-dev/taichi)

TaiChi是由胡渊鸣大佬基于Python开发，可以非常方便实现下面这些酷到不行的特效

![](https://picx.zhimg.com/v2-e664be26838b3fc7099f5062c8c4d7e2_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='818' height='222'></svg>)

而且Taichi作者也专门开设了 **GAMES201课程**

[taichi-dev/games201](https://link.zhihu.com/?target=https%3A//github.com/taichi-dev/games201)

另外 GAMES101 系列课程也强烈安利，闫令琪老师讲的炒鸡赞，我也开设了专栏记录课程笔记，欢迎品尝

[GAMES计算机图形学入门学习](https://www.zhihu.com/column/c_1251988592790597632)

未完待续


---

## 你怎么看回形针PaperClip《和 10 个批评者一块视频聊天》？

`link: https://www.zhihu.com/question/423360626/answer/1498814779 · created: 1601344564`


目前很多领域都缺少优秀的科普，带来的影响就是大众和行业之间存在很大的信息差。

比如不在学术圈的人觉得搞学术的都很厉害，不明觉厉，学术内的认为灌水的太多。优秀的科普能够帮助大众去了解某个领域，然后人们能够一定程度上去辨别哪些东西是好的，坏的。我觉得反过来也可以监督领域的发展，避免行业忽悠外行，形成良性循环。

总的来说，如何在恰饭和科普之间做一个很好的平衡需要不断的去探索，如果科普的同时也能赚不少钱，那么学术能力没那么强的人可以做大众和前沿学术成果之间的桥梁，也就不用再绞尽脑汁伪造数据刷论文了，也是挺好的。

希望回形针越做越好吧，以后做视频不要再犯那些错误。

PS: 最后的 白 这位观众的观点听的我真的满头问号，有朋友同感吗hhh


---

## 人工智能细分领域最流行、最常用的开发软件是什么？

`link: https://www.zhihu.com/question/421105005/answer/1497062214 · created: 1601256601`


## 1.写代码

VSCode用来写代码

Vscode超级推荐的快捷键：Ctrl + D

比如一个文件里一共有10个 `myname`字符，你想把前面5个替换成 `youname`,那么你就可以首先鼠标选中第一个*`myname`，*然后按五次 Ctrl + D 后就可以选中前面5个`myname`，之后你只需要在键盘上写入`youname` ，就完成了替换。

其他快捷键想到再补充

## 2. 框架

框架推荐Pytorch，或者TensorFlow>=2.0

很多人都基于Pytorch做了封装，更进一步简化框架使用门槛，比如Pytorch-lightning，fast.ai，还有我自己写的裁缝库（各种封装哈哈哈，不过感觉挺好用的）torchline

[marsggbo/torchline](https://link.zhihu.com/?target=https%3A//github.com/marsggbo/torchline)

## 3. 调试

调试代码很多人都用Pycharm，但是在服务器上你怎么办呢？这里强烈推荐 ipdb

```
pip install ipdb
```

用法很简单

首先运行py文件

```
python -m ipdb main.py
```

之后就会进入命令调试

* b [main.py:15](https://link.zhihu.com/?target=http%3A//main.py%3A15/) 这个表示在第15行设置一个断点
* b utils/other\_file.py:66 同理你也可以在其他文件里设置断点，只要指定路径就好了
* clear 1 取消第一个断点
* c 运行到下一个断点
* n 运行到下一行代码
* s 这个命令可以进入某一个函数进行调试
* r 这个命令是直接跳转到 return 语句，一般用在函数里或者for循环语句

ipdb常用的命令就是这些，欢迎补充。

## 4. Windows下命令行工具

[Cmder | Console Emulator](https://link.zhihu.com/?target=https%3A//cmder.net/)

Cmder超级推荐，用过的都说好，比Windows自带的命令行窗口好用很多，同时支持Linux下的很多命令，用起来很顺滑。

## 5. 代码版本控制

Vscode的插件库里宝库非常多，这里推荐安装Git graph，有了这个后你不用再记忆那么多git命令了

![](https://picx.zhimg.com/50/v2-2de7247548dd502c8a1e90cd74f34b1d_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='305' height='691'></svg>)

## 6. Markdown写笔记

推荐小书匠软件，好看免费还好用

<https://zhuanlan.zhihu.com/p/181343407>

其他可选：

* 印象笔记
* OneNote
* 有道笔记

## 7. 论文阅读软件

还在用阿逗比的Acrobat或者福昕阅读器吗？学术论文用这些看的话各种知识点七零八落的，这个时候你需要

[BookxNote Pro电子学习笔记软件](https://link.zhihu.com/?target=http%3A//www.bookxnote.com/)

是的，这个软件也是免费的哦，这个软件是Windows版本的Marginnote，关键目前是免费的，而且你可以通过搭配坚果云完成文档和笔记的云同步，简直香到不行，都舍不得推荐给你们，生怕用的人多开始收费，hhhhhhhhhhhhhhhh ┭┮﹏┭┮

## 8. 知识脑图

这里强推Xmind，懂的都懂哈哈哈

## 9. Visio替代品

Visio常用来话流程图，但是除非你下载盗版的，不然穷逼用不起，所以我当然还是推荐几个免费的。

坚果云自带这个功能，但是好像目前版本不支持导出PDF了，所以不爱ta了

ProcessOn在线流程图画图工具，免费用户好像可以创建10个文档，其实也是够用了

重磅来了！！！Drawio最好没有之一！！！

免费、功能强大、支持导出各种格式、还可以备份到谷歌云、GitHub、gitlab、本地等，好用到想哭啊

[Flowchart Maker & Online Diagram Software](https://link.zhihu.com/?target=https%3A//app.diagrams.net/)

## 10. Mathpix

[Mathpix Snip](https://link.zhihu.com/?target=https%3A//mathpix.com/)![](https://picx.zhimg.com/v2-364308520447ee51b88ba74cab8ff695_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1213' height='495'></svg>)

Mathpix可以非常方便地将图片中的数学公式转化成latex代码，写论文超级方便。每个月好像只有一定数量的免费使用次数，如果你使用频率很高，可以去闲鱼上买账号~

## 11. Mobaxterm

跑实验肯定要用到服务器，这里强烈推荐MobaXterm，ssh和ftp等功能这个软件都有，用起来非常方便。

![](https://picx.zhimg.com/v2-bcf15fb8c5ead888de6aceed2485dfb1_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1090' height='706'></svg>)

## 12. One Commander

超级好用的文件管理器，可以以树形结构展示不同层次文件夹的内容，不用在不同文件夹里来回切换了

未完待续。。。


---

## 东莞华为实验室被曝起火，目前情况如何？起火原因是什么？

`link: https://www.zhihu.com/question/422875065/answer/1492903049 · created: 1601027408`


听说是东莞团泊洼实验室，搞材料的

希望没人出事

希望不是内部有鬼


---

## 如何看待华为诺亚方舟实验室开源的AutoML算法工具链VEGA？

`link: https://www.zhihu.com/question/404378649/answer/1488612338 · created: 1600831252`


有幸来华为诺亚实验室实习参与Vega开发，把写的文章搬运一下，谈一下我对Vega的看法以及与其他AutoML框架的比较。

> 本文主要简单地介绍Vega的特点以及它与其他AutoML框架的区别，让你对Vega有一个直观的理解。  
> 文章太长不看可以直接降落至最后的总结部分。

[huawei-noah/vega](https://link.zhihu.com/?target=https%3A//github.com/huawei-noah/vega)

## **1. 现有AutoML框架总结**

目前已经出现了很多AutoML开源框架，可以大致分成两类：

* 一类是基于传统机器学习算法，例如 [TPOT](https://link.zhihu.com/?target=https%3A//github.com/EpistasisLab/tpot)、[Auto-Sklearn](https://link.zhihu.com/?target=https%3A//github.com/automl/auto-sklearn)、 [Hyperopt](https://link.zhihu.com/?target=https%3A//github.com/hyperopt/hyperopt)，[H2O](https://link.zhihu.com/?target=https%3A//docs.h2o.ai/h2o/latest-stable/h2o-docs/index.html) 如果你不需要神经网络的话则可以考虑使用这几个框架。
* 另一类则是基于神经网络的AutoML框架，比较流行的有 [NNI](https://link.zhihu.com/?target=https%3A//github.com/microsoft/nni)、 [Auto-kears](https://link.zhihu.com/?target=https%3A//github.com/keras-team/autokeras) 以及本篇文章要介绍的华为诺亚方舟实验室开源的 [Vega](https://link.zhihu.com/?target=https%3A//github.com/huawei-noah/vega) 框架。

## **2. Auto-Keras & NNI**

在介绍Vega之前，首先简单介绍一下Auto-Keras和NNI。

* Auto-Keras，看名字也知道它是基于Keras实现的，换句话说它只支持TensorFlow，目前最新版本的要求是**Python >= 3.5 and TensorFlow >= 2.3.0**，因此如果你常用的框架是Pytorch，这个可能不适合你。
* NNI是微软开发的**轻量型**AutoML工具包，如下图示，其提供的功能非常丰富，包括自动特征工程、NAS（神经网络架构搜索）、模型压缩、超参数搜索等等，而且还提供了可视化界面方便管理。我本人也用过NNI的NAS模块，易用性非常高。NNI将搜索空间和搜索算法解耦，而且设计了一种统一的接口，可以很方便地实现你的NAS算法，具体可看官方文档介绍：[https://nni.readthedocs.io/zh/latest/nas.html](https://link.zhihu.com/?target=https%3A//nni.readthedocs.io/zh/latest/nas.html)

![](https://pic1.zhimg.com/v2-4fdb9e86dd0461c352b207d0dfa82684_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1624' height='803'></svg>)

## **3. Vega**

Vega是华为诺亚方舟实验室自研的AutoML算法工具链([https://github.com/huawei-noah/vega](https://link.zhihu.com/?target=https%3A//github.com/huawei-noah/vega))，有如下几个主要特点。

## **3.1 完备的AutoML能力**

Vega涵盖HPO(超参优化, HyperParameter Optimization)、Data-Augmentation、NAS(网络架构搜索， Network Architecture Search)、Model Compression、Fully Train等关键功能，同时这些功能自身都是高度解耦的，可以根据需要进行配置，构造完整的pipeline。

乍看起来，你也许会觉得这个NNI很相似，但是正如前面介绍的，NNI其实是一个**轻量型**的工具包，也就是说你如果只需要实现某一个具体的功能，例如NAS或者模型压缩，那NNI是一个很好的选择，但是如果你希望将多个功能组合成一个完整的pipeline（如下图示），那么你需要的是Vega。

![](https://pic1.zhimg.com/v2-2a391b1bc447c5ee08244eb1a1e557af_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='727' height='259'></svg>)

Vega解决的思路是将每一个功能（如模型压缩和NAS等）都抽象成一个具有统一接口的PipeStep类，通过遍历每个Step实现端到端的Pipeline，具体的实现原理在后续文章中会介绍。

## **3.2 业界标杆的自研算法**

Vega提供了诺亚方舟实验室自研的 业界标杆 算法，并提供 Model Zoo 下载SOTA(State-of-the-art)模型。

![](https://pic1.zhimg.com/v2-73860207cd387183767164922db6aa7f_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1057' height='672'></svg>)

## **3.3 高并发模型训练能力**

Vega提供高性能Trainer，加速模型训练和评估。Vega设计了Scheduler模块，可以很方便的管理本地集群部署等任务。

![](https://picx.zhimg.com/v2-8227e2ff21f0120e81a18bbd412ab89d_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1428' height='806'></svg>)

## **3.4 多Backend支持**

Vega支持PyTorch，TensorFlow，MindSpore。虽然NNI也支持多种深度学习框架，但是Vega对不同框架的算子设计了统一接口。而且你可以只需要指定要运行的Backend即可切换至不同的深度学习框架。

## **3.5 可插拔式**

Vega采用可插拔式的配置方法，你可以只需要修改yml文件中的参数就能灵活地切换不同数据集、算法等组件，换句话说**你可以基于Vega搭建属于你自己的工具库**，因此在处理一个新项目的时候，你可以很方便地复用你之前的工作成果。

## **3.6 提供多个特色模块**

Vega提供了丰富的搜索空间，你可以很方便地自定义你的搜索空间快速验证你的idea。另外Vega还提供了**Report**模块，该模块可以很方便地管理训练过程中的各种日志等信息，使用起来更加简单顺手。

## **4. 总结**

通过上面介绍我们知道Vega和NNI都是提供了非常丰富的功能的AutoML框架，区别在于NNI定位于**轻量型**的工具包，所以如果你只想实现NAS算法或者模型压缩，那么你可以使用NNI来验证你的想法。Vega则定位于从**Pipeline**的角度来解决AutoML问题，因此使用Vega有一定门槛，需要你学习它的设计理念和代码逻辑，但是如果你掌握之后，你会发现Vega的易用性是不输NNI的，本系列文章主要是一起来学习Vega，然后搭建属于你自己的工具库。

### **微信公众号：AutoML机器学习**

![](https://pica.zhimg.com/50/v2-87083e55cd41dbef83cc840c142df48a_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='0' height='0'></svg>)

**MARSGGBO♥原创**  
**如有意合作或学术讨论欢迎私戳联系~**  
**邮箱:marsggbo@foxmail.com**


---

## 有哪些值得推荐的人工智能领域的优质科普平台或渠道？

`link: https://www.zhihu.com/question/414750781/answer/1415517477 · created: 1597669753`


> 知乎是一个宝藏，你可以跟着大佬学到很多东西。欢迎评论区大佬们毛遂自荐。 (该回答不定时更新)

## 知乎用户

主要收集关注超过1000或者回答和文章大多与人工智能相关的知乎用户

[@marsggbo](https://www.zhihu.com/people/6b2df8f2c5dae1c6b27be02f8bc53bfe) （我自己打个广告哈哈哈）

[致知计划之数码季 - 知乎](https://www.zhihu.com/campaign/knowledge/digital/list/9?zh_hide_nav_bar=true)人工智能领域入选用户：

[@anarion](https://www.zhihu.com/people/b0fef3f75dccd112ff67e2adbeda40e3) [@yanwan](https://www.zhihu.com/people/9c35d34336ab94eca92ef5b1bd600817) [@Zign](https://www.zhihu.com/people/7b0a686eb563b41579389cb71df0cec9) [@marsggbo](https://www.zhihu.com/people/6b2df8f2c5dae1c6b27be02f8bc53bfe)[@学弱猹](https://www.zhihu.com/people/77b195f4016956a60304aefb3961ca36) [@JayLou娄杰](https://www.zhihu.com/people/cdac834d039095f39ea677a44ff2a294) [@刘浚嘉](https://www.zhihu.com/people/5ca839df57cb6ca6203ffa5320ee8776) [@Kevin Zhang](https://www.zhihu.com/people/24cabbda55549e523c975eea61c65528) [@李启方](https://www.zhihu.com/people/cb6f4f9ce608e2cb0523303560d2298b) [@洪泽鑫](https://www.zhihu.com/people/d70e206f9a082597ad3bbc9d80d1ba0f) [@梦藏君](https://www.zhihu.com/people/73f1a5da2ff6c43dea47699dd2af96e8) [@袁承兴](https://www.zhihu.com/people/f08166e19c62995c4936c6c60709a7f2) [@猴子](https://www.zhihu.com/people/c9b28ce4b50bf0444d17d010224cb06f)[@嘉慧Lincoln](https://www.zhihu.com/people/29a386cc4b62dd3a95af790ba2fcf1cb)[@Trustintruth](https://www.zhihu.com/people/9c7c6ee759313632df2ef593844533de)[@桔了个仔](https://www.zhihu.com/people/cc759c5d7c383aa95e7633f06bcf6d82) [@李明殊](https://www.zhihu.com/people/4502e19662989d2584c5a14a7386a03f) [@Serendipity](https://www.zhihu.com/people/09733810a89d25118c12b0514939747f) [@Guohao Li](https://www.zhihu.com/people/46e01b5318ce6abc0110d44419aa25da) [@平凡](https://www.zhihu.com/people/a0265e93117d3d366adda36310194727) [@薰风初入弦](https://www.zhihu.com/people/386626a76133f0d525fdc1ede18bbad6) [@Pjer](https://www.zhihu.com/people/3c13de714f625abc1057d2de1aeafbd9) [@舒意恒Y.Shu](https://www.zhihu.com/people/f3ca6a4373115308f078d44eaa218ded) [@镜君](https://www.zhihu.com/people/76dd41b6a09bb213bf423d00d1a5fdde) [@江户川柯壮](https://www.zhihu.com/people/f3a26afe55bdfb9227a2365d5a9e956d) [@老石](https://www.zhihu.com/people/8d7fdbc65228d5b8b7ce2855f0902ed7) [@白山头](https://www.zhihu.com/people/8c46430610b72d15cd0b754c7986202c) [@疯狂绅士](https://www.zhihu.com/people/7d67a08e4281d242a1f6b792aa15800a) [@微调](https://www.zhihu.com/people/e3f5794fa10022aa07c05b0b9e6dc537) [@溪亭日暮](https://www.zhihu.com/people/bdb96a8e8ee73da6f3fe8cb31f25ba4f)[@Forever snow](https://www.zhihu.com/people/68805261dfc24779a3080a9d3683001b)[@艾斯奥特曼](https://www.zhihu.com/people/9dd9dacb3fe9035c0353d2008452c2c5)

其他宝藏Zhihuer：

[@白小鱼](https://www.zhihu.com/people/d55e47e9d2bcd03a441ee6d9c544519e) [@宝珠道人](https://www.zhihu.com/people/84cc1b94de2e930e82beba03bf0ad23c) [@CVer](https://www.zhihu.com/people/a2985dc0d44e9c5860beec83abee89eb) [@荷兰猪](https://www.zhihu.com/people/83b7c686295e6db0dea8caf604368719) [@王源](https://www.zhihu.com/people/186282e45de0e1040b7882c9be8f5de8) [@King James](https://www.zhihu.com/people/b0ff3e08049971ebe28acdaed6cfc257) [@Lancewu](https://www.zhihu.com/people/4631c85ba2007a32b723744717decece) [@朴素贝叶斯](https://www.zhihu.com/people/cdf04f51d372a02c84ac6bc259f3da92) [@甜草莓](https://www.zhihu.com/people/43e9db945b094a0a908247f46bb3b789) [@易哥](https://www.zhihu.com/people/a3eba260c2b4c8c4b793ddca4f7260a8) [@王方浩](https://www.zhihu.com/people/3f3942e224988b84be3aaefe72a768ea) [@石塔西](https://www.zhihu.com/people/d386670451ad397bea826a0593ca6536) [@苗华栋](https://www.zhihu.com/people/0b50a44942f90280e75ae51faba0b6d7) [@labuladong](https://www.zhihu.com/people/1c2ff6f15798f956783662b8b25156bd) [@袁洋](https://www.zhihu.com/people/498ba8f98e3c4f88fb1dc622eb6ce572) [@游凯超](https://www.zhihu.com/people/176cf88046a1cae595b55e12d58c95e9) [@风辰](https://www.zhihu.com/people/89aa060e43db0e5bb83a4dcdf2ecc69e) [@张心欣](https://www.zhihu.com/people/9d0cd62f9071c2b003b2ef7b017fb7f5) [@肥橘猫与肥柴犬](https://www.zhihu.com/people/d59dfa467c174e6d18e30db82a0d925f) [@忆臻](https://www.zhihu.com/people/1b72d70b702b3920638f0235d380ebd8) [@jinzhao](https://www.zhihu.com/people/62118c9b6d1b528f9029c14092568904) [@夏飞](https://www.zhihu.com/people/043e0f54210d499b400471f32642771e) [@蔡杰](https://www.zhihu.com/people/2265af666ddf487cedbf1c4f9e06b188) [@Jack-Cui](https://www.zhihu.com/people/4717da6123e864f9a9550ae8f53db16d) [@lokinko](https://www.zhihu.com/people/9ca23a25c24e381bc9ec03a58d107812) [@第四范式](https://www.zhihu.com/people/2cdad35400a29e120710910688768cae) [@第四范式天枢](https://www.zhihu.com/people/e5a156d65680ec3007f4972ae615e2d9) [@阿里巴巴达摩院](https://www.zhihu.com/people/1c0da560cd8dd2e4c16d6d836a6a24ee) [@科技猛兽](https://www.zhihu.com/people/a8bb7335e2669bf299b22d0eff2e0da3) [@Kevin Zhang](https://www.zhihu.com/people/24cabbda55549e523c975eea61c65528) [@P小二](https://www.zhihu.com/people/ec848789340d90df90da291d66e9a733) [@机器之心](https://www.zhihu.com/people/06a67981ced7a2e9f07005185605685c) [@新智元](https://www.zhihu.com/people/59ee4d25ff7a093ad6590f32bc9e4361) [@量子位](https://www.zhihu.com/people/36f69162230003d316d0b8a6d8da20ba) [@霍华德](https://www.zhihu.com/people/4a0d3a504b9859139f2c003005230717) [@唐杉](https://www.zhihu.com/people/f93acfe8dc4325dee1bdd5c2f8852981) [@镜君](https://www.zhihu.com/people/76dd41b6a09bb213bf423d00d1a5fdde) [@李启方](https://www.zhihu.com/people/cb6f4f9ce608e2cb0523303560d2298b) [@Valkla](https://www.zhihu.com/people/8dac090c7e9475dbccdc6b1ae4c5ae0a) [@Zign](https://www.zhihu.com/people/7b0a686eb563b41579389cb71df0cec9) [@疯狂绅士](https://www.zhihu.com/people/7d67a08e4281d242a1f6b792aa15800a) [@徐方鑫](https://www.zhihu.com/people/a75dcdf94efbae1a300a31ae24265ac3) [@臻恒](https://www.zhihu.com/people/f97528ae4a73b5bf0504a7123453a37e) [@JZWSVIC](https://www.zhihu.com/people/fa4c2698701a87222254037026648044) [@微软亚洲研究院](https://www.zhihu.com/people/27b8390344b45c7289032f3218ced120) [@胡津铭](https://www.zhihu.com/people/55b5bdc6e86bd94d0bea084eb7435006) [@予以初始](https://www.zhihu.com/people/14ca7c47319e3ba2c9908035156bf293) [@极市平台](https://www.zhihu.com/people/18fd48d899394f9df14116dd62ea2824) [@潜心](https://www.zhihu.com/people/43729695e8f8f4d0796cc1360db7a9ca) [@黄浴](https://www.zhihu.com/people/c4f733221248f43b8946b5182bb048db)

## 知乎专栏

还是带点私心安利一下自己的专栏：

* **[AutoML专栏](https://www.zhihu.com/column/automl)**。主要介绍自动机器学习算法为主，附带也会更新一些Pytorch、python等一些实用教程，关注一下不会亏的~~
* **[深度学习论文分享](https://www.zhihu.com/column/dlpaper)**
* **[机器学习系列教程笔记](https://www.zhihu.com/column/c_1272200900321603584)**：分享各种优秀视频教程的课后笔记
* **[GAMES计算机图形学入门](https://www.zhihu.com/column/c_1251988592790597632)**：分享GAMES系列图形学课程笔记

其他优秀专栏

* [光喻的人工智能笔记](https://www.zhihu.com/column/tenniel-ai)
* [炼丹法分享](https://www.zhihu.com/column/c_1079708475860500480)
* [RL in Robotics](https://www.zhihu.com/column/c_1188392852261134336)
* [数据分析学习与实践](https://www.zhihu.com/column/rstudio)
* [转行AI小专栏](https://www.zhihu.com/column/transfer2AI)
* [AI小分队--夏飞](https://www.zhihu.com/column/feixia)
* [AI部落](https://www.zhihu.com/column/nlp-dl)
* 写给妹子的深度学习教程
* [炼丹实验室](https://www.zhihu.com/column/easyml)
* [混沌巡洋舰](https://www.zhihu.com/column/c_29122335)
* [设计人工智能网络](https://www.zhihu.com/column/designintelligence)
* [一周一paper](https://www.zhihu.com/column/one-paper-a-week)
* [边缘智能](https://www.zhihu.com/column/edge-intelligence)
* 非凸优化学习之路
* [有三AI学院-强化学习与AutoML](https://www.zhihu.com/column/c_1182237553686765568)
* [高斯世界下的Machine Learning](https://www.zhihu.com/column/gpml2016)
* [『运筹帷幄』人工智能|数据科学|运筹学交叉](https://www.zhihu.com/column/operations-research)
* [『运筹AI帷幄』大数据时代的人工智能](https://www.zhihu.com/column/c_1070706735982915584)
* [旷视Model组](https://www.zhihu.com/column/r-basemodel)
* [神经网络架构搜索（NAS）](https://www.zhihu.com/column/c_1129401647213957120)
* [SIGAI](https://www.zhihu.com/column/c_201634018)
* [我的机器学习笔记](https://www.zhihu.com/column/c_1155064304431783936)
* [炼丹师的笔记本](https://www.zhihu.com/column/syzhang)
* [深度学习与计算机视觉](https://www.zhihu.com/column/c_93469304)
* [轻量型网络设计](https://www.zhihu.com/column/c_1141783021610070016)
* [深度学习源码解析](https://www.zhihu.com/column/c_144268772)
* [王喆的机器学习笔记](https://www.zhihu.com/column/wangzhenotes)
* [GiantPandaCV](https://www.zhihu.com/column/giantpandacv)
* [图形之道](https://www.zhihu.com/column/taichi)
* [计算机视觉论文速递](https://www.zhihu.com/column/c_172507674)
* [MMLab学术视野](https://www.zhihu.com/column/mmlab-ai)
* [深度与强化学习基础](https://www.zhihu.com/column/ikerpeng)
* [薰风的计算机科学家之路](https://www.zhihu.com/column/IsonomiaCS)
* [深度模型压缩领域论文](https://www.zhihu.com/column/EdgeDeepLearning)
* [R4D](https://www.zhihu.com/column/c_1065911842173468672)
* [AutoML随笔](https://www.zhihu.com/column/automlresearch)
* [DeepLearning学习笔记](https://www.zhihu.com/column/deeplearningnotes)
* [机器不学习](https://www.zhihu.com/column/lowlearning)
* [Eureka机器学习读书笔记](https://www.zhihu.com/column/xiadayj)
* [SCI](https://www.zhihu.com/column/scipaper)
* [论智](https://www.zhihu.com/column/lunzhi)
* [人工智能学习笔记](https://www.zhihu.com/column/c_80412427)
* [机器学习算法与自然语言处理](https://www.zhihu.com/column/qinlibo-ml)
* [AI学人](https://www.zhihu.com/column/aixueren)
* [机器学习笔记](https://www.zhihu.com/column/mlearn)
* [深度炼丹](https://www.zhihu.com/column/c_94953554)
* [新智元](https://www.zhihu.com/column/aiera)
* [gluon](https://www.zhihu.com/column/gluon)
* [卷积神经网络（CNN）入门讲解](https://www.zhihu.com/column/c_141391545)
* Gemfield
* [深度学习经典，前沿论文阅读笔记](https://www.zhihu.com/column/liuyan0612)
* [有三AI学院](https://www.zhihu.com/column/c_151876233)
* [搜罗最好玩的计算机视觉论文和应用](https://www.zhihu.com/column/c_1111987294722121728)
* [深度学习技术追踪](https://www.zhihu.com/column/c_1102261020604628992)
* [机器学习知识点](https://www.zhihu.com/column/c_184412713)
* [高性能机器学习平台](https://www.zhihu.com/column/tjizhi)
* [智能单元](https://www.zhihu.com/column/intelligentunit)

### 科普书籍

如果说要推荐适合小朋友看的科普书籍，建议可看看这本 知乎版《十万个为什么》，这个适合3岁以上下朋友看，全书是以彩绘的形式来解答小朋友的各种刁钻问题。

下面是书里的一个插图，下次小朋友问你 **阿姨/蜀黍, 为什么扫地机器人不会迷路啊?** 你就可以用非常浅显易懂的语句解释了 ~

![](https://pic1.zhimg.com/v2-27b472d7613af7ddb16117c24054d684_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='720' height='621'></svg>)

其他适合小孩子的科普书籍：

适合大孩子看的科普书籍有如下

## 课程学习

* 首推学习社区：[B站](https://link.zhihu.com/?target=https%3A//www.bilibili.com/)
* [慕课网-免费的IT技能学习平台](https://link.zhihu.com/?target=http%3A//www.imooc.com/course/list)
* [课程 - 实验楼](https://link.zhihu.com/?target=https%3A//www.shiyanlou.com/courses/)
* [Udacity](https://link.zhihu.com/?target=https%3A//classroom.udacity.com/nanodegrees/nd009/parts/0091345400/modules/009134540075460/lessons/7196318710/concepts/6405791910923)
* [Khan Academy](https://link.zhihu.com/?target=https%3A//zh-hans.khanacademy.org/)
* [网易公开课](https://link.zhihu.com/?target=http%3A//open.163.com/)
* [Andrew Ng机器学习课程](https://link.zhihu.com/?target=https%3A//www.bilibili.com/video/av9912938/%3Ffrom%3Dsearch%26seid%3D17934445043963203420%23page%3D74) 以及 [课程笔记](https://zhuanlan.zhihu.com/p/165347323)
* [Andrew Ng DeepLearning课程](https://link.zhihu.com/?target=https%3A//www.bilibili.com/video/BV1pJ41127Q2%3Ffrom%3Dsearch%26seid%3D9171102014356576548) 以及 [课程笔记和作业](https://link.zhihu.com/?target=https%3A//github.com/marsggbo/deeplearning.ai_JupyterNotebooks)
* [机器学习白板推导系列课程](https://link.zhihu.com/?target=https%3A//www.bilibili.com/video/av70839977%3Fp%3D88)，真的是手把手推导公式，强烈推荐！！！！！[课程笔记](https://zhuanlan.zhihu.com/p/190208778)整理在这了

## AI社区

* [Quora机器学习](https://link.zhihu.com/?target=https%3A//www.quora.com/topic/Machine-Learning%3Fq%3Dmachine%2520learning%2520)
* [Quora深度学习](https://link.zhihu.com/?target=https%3A//www.quora.com/topic/Deep-Learning)
* [https://www.ziiai.com/](https://link.zhihu.com/?target=https%3A//www.ziiai.com/)
* [https://www.tinymind.cn/](https://link.zhihu.com/?target=https%3A//www.tinymind.cn/)
* [欢迎来到 AIQ - 专业的人工智能技术社区](https://link.zhihu.com/?target=https%3A//www.6aiq.com/domain/machine_learning)
* [AI研习社 - 研习AI产学研新知，助力AI学术开发者成长。](https://link.zhihu.com/?target=https%3A//www.yanxishe.com/)
* [https://www.paperweekly.site/](https://link.zhihu.com/?target=https%3A//www.paperweekly.site/)
* [https://www.kdnuggets.com/](https://link.zhihu.com/?target=https%3A//www.kdnuggets.com/)
* [https://www.analyticsvidhya.com/](https://link.zhihu.com/?target=https%3A//www.analyticsvidhya.com/)

补充一下贾扬清大神推荐的几个学习网站：[贾扬清知乎直播时推荐的3个学习网站是什么？](https://www.zhihu.com/question/416905571/answer/1430286791)

* 强烈推荐没事在这瞎逛逛：[https://www.reddit.com/r/MachineLearning/](https://link.zhihu.com/?target=https%3A//www.reddit.com/r/MachineLearning/)
* Hacker News：[https://news.ycombinator.com/](https://link.zhihu.com/?target=https%3A//news.ycombinator.com/)
* TechCrunch：[https://techcrunch.com/](https://link.zhihu.com/?target=https%3A//techcrunch.com/)

## 各大AI公司research官网

* [facebook](https://link.zhihu.com/?target=https%3A//research.fb.com/category/machine-learning/)
* [Microsoft Research](https://link.zhihu.com/?target=https%3A//www.microsoft.com/en-us/research/)
* [腾讯 AI Lab - 腾讯人工智能实验室官网](https://link.zhihu.com/?target=https%3A//ai.tencent.com/ailab/zh/index)
* [Research – Google AI](https://link.zhihu.com/?target=https%3A//ai.google/research/)
* [Baidu Research](https://link.zhihu.com/?target=http%3A//research.baidu.com/)
* [JD AIR](https://link.zhihu.com/?target=https%3A//air.jd.com/)
* [亚马逊AI](https://link.zhihu.com/?target=https%3A//www.amazon.science/)
* [美团AI](https://link.zhihu.com/?target=https%3A//tech.meituan.com/)

### **关注微信公众号不迷路：AutoML机器学习**

**MARSGGBO♥原创**  
**如有意合作或学术讨论欢迎私戳联系~**  
**邮箱:marsggbo@foxmail.com**


---

## 香港国安法表决通过，对香港未来发展有何影响？

`link: https://www.zhihu.com/question/404288642/answer/1311243358 · created: 1593512698`


假装【谢邀，人在飞机，刚下香港】

香港各大学校的学生会应该可以好好的整顿了，学校里的各种黄色涂鸦标语也可以彻彻底底清理掉了，在学校学习也更加安心了，不用再像去年那样跑到深圳“避难”，现在想想就窝囊，被那些渣搞的大家生活学习节奏全乱。

香港搞研究的基本都是内地学生的，以后可以沉迷学习了～开心～

本人在香港上学，有啥问题欢迎评论区讨论。也欢迎关注公众号，一起沉迷学习

公众号:【AutoML机器学习】


---

## 华中科技大学的校园环境如何？

`link: https://www.zhihu.com/question/327091155/answer/1283631083 · created: 1592182811`


无图无真相，整理了本科时候拍的一些照片。中间校区适宜摆拍，西校区适宜体验现代生活，玩累了可以去东校区体验最淳朴的乡下生活。

![](https://picx.zhimg.com/v2-534c8ca23ebc895a6405ecf6282d5eaf_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1536' height='2048'></svg>)

东九孔子

![](https://picx.zhimg.com/v2-d78e880ebd6d4474c1adee401b6ad121_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1536' height='2048'></svg>)

华科趵突泉

![](https://picx.zhimg.com/v2-fd04ae68fa179030686886de451e5faf_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1536' height='2048'></svg>)

东九教学楼A栋

![](https://picx.zhimg.com/v2-04dee06a48d65b518789f45cd0973481_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2048' height='1536'></svg>)

东九雪景

(下图是QQ空间上盗的图哈哈哈哈)

![](https://pica.zhimg.com/v2-a934cc19f3edab8b491b01c7065e1f4a_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='853' height='640'></svg>)

东九前的玉兰花海

![](https://pic1.zhimg.com/v2-96d2d7ff4b07028370e07e70918ac41b_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2276' height='1280'></svg>)

宿舍眺望

![](https://pic1.zhimg.com/v2-dc8a1f2aadd0fa5df078c550f77aed29_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2276' height='1280'></svg>)

宿舍再眺望

![](https://pica.zhimg.com/v2-241748d66ce5da631f43de0e267782d9_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1280' height='2276'></svg>)

南一楼毛爷爷

![](https://pic1.zhimg.com/v2-e71cc356f284c89be1a32e3745c9498f_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1280' height='2276'></svg>)

东九教学楼前的玉兰花贼漂亮，而且会有好几种颜色过渡，没记错的话应该先是红色，然后变成黄白色

![](https://picx.zhimg.com/v2-8268475f5f9799ed4c40f74444bc95c7_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1536' height='2048'></svg>)

玉兰花（黄白）

![](https://pica.zhimg.com/v2-60e57bd458096a02d8c2f68208117167_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2276' height='1280'></svg>)![](https://pic1.zhimg.com/v2-035e0a98580a54c62b5b2af0b752d073_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1280' height='2276'></svg>)![](https://picx.zhimg.com/v2-8ff607cc99b0fb4d0d44e0c299560cce_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1536' height='2048'></svg>)![](https://pica.zhimg.com/v2-70ee3e3a2cb2dec999d3a7865abfb8f5_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2048' height='1532'></svg>)![](https://picx.zhimg.com/v2-57fc0b6eb38092a0acabeb7c18bf7f5f_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2048' height='1532'></svg>)

主图书馆前坪

![](https://pic1.zhimg.com/v2-bd05231aaf49259c9ac47cdb6eafb828_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2048' height='1536'></svg>)![](https://pica.zhimg.com/v2-ec23f2607284eeba0563e5a1325e9bee_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1920' height='1080'></svg>)

亲眼见更好看的秋景，整条马路都是金黄树叶

![](https://picx.zhimg.com/v2-a75c98e0168402c0bdcdb8c97bac4c46_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1532' height='2048'></svg>)

东图书馆小径

![](https://picx.zhimg.com/v2-abc3561726bafcf2a2aeda018027fc1b_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1443' height='1080'></svg>)![](https://pica.zhimg.com/v2-5d83069edb4143fd5c2ef6c2cc44a209_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2784' height='544'></svg>)![](https://pic1.zhimg.com/v2-90117df3db83ddd9f5fbecde122cf672_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='720' height='960'></svg>)![](https://pica.zhimg.com/v2-5c6899a0ddd9a3fc25f427882b2ce9c5_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1536' height='2048'></svg>)


---

## 如何看待何冰微博因后浪事件被网友爆破？

`link: https://www.zhihu.com/question/392881184/answer/1206496808 · created: 1588835607`


很多回答说视频展现的是少数人的生活，没有很好地反映民意。我就想如果视频里加上外卖小哥以及996的大伙们艰苦奋斗的画面，就会有另一个说辞，说是资本赞美韭菜。

一个人人平等的社会人人向往，但是个人感觉人人平等接近不可能，因为出生之前每个人的出厂配置(智商，情商)就不一样，后天生长环境也不一样，这样肯定就有人发展的好。所以我还是蛮好奇的，到底什么样的政策才能让所有人满意？什么样的视频才能让大家满意？


---

## 如何评价Fastai？

`link: https://www.zhihu.com/question/297031440/answer/1059976791 · created: 1583477056`


简单用过几次，用起来不太顺手。原因如下：

1. 封装感觉有点用力过猛，不过如果你只是想开箱即用那应该也是不错的选择
2. fastai的整体架构里有不少新的概念，要熟练掌握fastai得额外花不少时间
3. API调用查的头大，官方提供的tutorial导入包也是是非常粗暴的 `from ... import \*`，这在其他回答里也有提到，总之让初学者看后会感觉头秃。其实个人觉得pytorch的数据集读取的逻辑是非常清晰而且容易理解的，具体的可以看看之前写的文章

<https://zhuanlan.zhihu.com/p/76893455>

如果非要推荐一个基于pytorch封装的框架的话，我推荐

[pytorch-lightning](https://link.zhihu.com/?target=https%3A//github.com/PyTorchLightning/pytorch-lightning)

他没有引入过多的新概念，因此只要你会pytorch，你就可以无缝衔接的使用这个库，而且这个库已经帮你搭好了各种可能需要的配置，比如apex，分布式训练，单机多卡训练，设置TPU都已经支持了，献上官方的介绍图

![](https://pic1.zhimg.com/v2-e3f33475e792450df0c8a012d23f1c4c_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2687' height='2241'></svg>)

可以看到pytorch-lightning将训练过程抽丝剥茧抽象化，你只需要关注具体的训练步骤即可，因此代码量极大减少，用起来真的是香，所以强烈推荐。

最后的最后还得推荐一个库

<https://zhuanlan.zhihu.com/p/97244535>

这个库是基于pytorch-lightning进一步封装的，但是并没有增加新的概念，它所做的事情是提高你的代码复用性。比如说你上个月为一个项目写了一个模型A和对应的损失函数B，这个月你接到新的任务，你发现模型还可以继续使用A，但是损失函数可能得改改，你可能会把A的代码copy过来，重新写了一个损失函数，又完成了一个新的项目，之后你又有新的项目，你又得不断重新复制粘贴。。。

总之你的代码复用性是复制粘贴实现的，而torchline帮助你简化这一过程，你只需要在配置文件中修改对应的模型的名字，或者修改loss的名字即可轻松切换不同方法，而不再需要不断修改代码。

torchline还在不断更新中，欢迎感兴趣的朋友们start和提意见，也欢迎提出PR，让pytorch用的更顺滑！

[https://github.com/marsggbo/torchline](https://link.zhihu.com/?target=https%3A//github.com/marsggbo/torchline)


---

## Pytorch中LSTM网络输入张量的维度如何确定？

`link: https://www.zhihu.com/question/375117485/answer/1054894461 · created: 1583292910`


[marsggbo：理解Pytorch中LSTM的输入输出参数含义](https://zhuanlan.zhihu.com/p/100360301)


---

## 如何看待浙江卫视《王牌对王牌》？

`link: https://www.zhihu.com/question/39963140/answer/1037115361 · created: 1582614852`


什么时候正片别剪的像预告就满足了。


---

## pytorch里如何使用logger保存训练参数日志？

`link: https://www.zhihu.com/question/361602016/answer/941584819 · created: 1576716512`


推荐使用 test\_tube这个库，他可以很方便的使用各种logger方法，而且还能自动保存不同版本的日志文件


---

## 判别式模型和生成模型有什么本质上的区别？

`link: https://www.zhihu.com/question/268906476/answer/878401193 · created: 1572621995`


不知道我理解的对不对。

之所以有生成模型和判别模型这两种方法，是因为通常我们有训练数据x和对应的标签Y，所以我们可以计算出P(Y|X),这就是判别模型的依据。

然后如果我们还知道P(X)的分布，我们就可以通过P(X,Y)=P(X)P(Y|X)进一步求出生成模型.


---

## 如何评价FAIR于2019年10月10日开源的Detectron2目标检测框架？

`link: https://www.zhihu.com/question/350117858/answer/858869821 · created: 1571190952`


之前用过mmdetection，昨天也把detectron2的源代码大致读了一遍，发现两者还是蛮相似的。不过Detectron2毕竟是fb官方出品，而且基于Pytorch1.3，相信更新会更加快速，紧跟fb大军。

另附上Detectron2的源代码阅读笔记，希望对新手有用。

[marsggbo：Detectron2代码阅读笔记-(一)](https://zhuanlan.zhihu.com/p/86749823)[marsggbo：Detectron2代码阅读笔记(二)](https://zhuanlan.zhihu.com/p/86808911)


---

## 如何评价2019《中国好声音》总决赛？

`link: https://www.zhihu.com/question/349598659/answer/849175462 · created: 1570504766`


这届冠军应该给周深。

[![](https://pic3.zhimg.com/v2-de5806c262dcabf9f8c88e360b88315b.jpeg)周深 崔佳莹《我爱你中国》https://www.zhihu.com/video/1164863015622156288](https://link.zhihu.com/?target=https%3A//www.zhihu.com/video/1164863015622156288)


---

## TensorFlow输出的CNN网络信息存储在什么文件中？其中的CNN结构、参数集等信息是如何组织的？

`link: https://www.zhihu.com/question/285721627/answer/445499684 · created: 1531889591`


提个建议，用pytorch吧，查看网络结构和参数非常方便。


---

## 怎样评价《动物世界》？

`link: https://www.zhihu.com/question/282156179/answer/437982685 · created: 1531120270`


不请自来。想提醒一下这个问题是怎样评价李易峰的《**动物世界**》，不是怎样评价《动物世界》的李易峰。

关于电影，有很多一脸懵的地方，希望看过电影的大家能够指点一二。

1.电影取名叫《动物世界》可能是想呼应后面石头剪刀布的游戏中的人性，但是小丑的切入点和作用是什么？时不时来个小丑打怪的场景实在不明白。

2.男主时不时的出现幻觉有什么实质性的影响吗？想表达什么？

3.电影中很多镜头看的晃眼，效果参照《西游记后传》。

4.男主被抓上船之前的飙车镜头有炫技之嫌，前后衔接突兀。

吐槽了这些也必须说说好的地方:

1.电影的确会让人不由得思考。简单的石头剪刀布游戏的确能够让人感受到人性的可怕。当时我就在想如果我去玩这个游戏结果会怎么样？我会像男主一样选择相信老乡(同中国人)，还是会在诱惑下选择欺骗他人。游戏简单，人心不简单。

2.电影特效做的还行，当时一边吃绝味一边看，小丑打怪的镜头着实恶心到我了ʅ(´⊙◞⊱◟⊙｀)ʃ。

总结:该片评分虚高，不如去看隔壁电影《我不是药神》。


---

## CNN 在分类图片时图片大小不一怎么办？

`link: https://www.zhihu.com/question/45873400/answer/335928123 · created: 1520390944`


最近也遇到题主所说的问题，即传统CNN需要输入图片大小固定。

## 1.为什么需要输入图片的大小固定

我们知道卷积层对于图像的大小是没有要求的，一般的卷积核都是3\*3, 5\*5等，而输入图像一般不会小于这个大小。所以问题就是出在全连接层。

我们假设全连接层到输出层之间的参数是 ![W^{f*o}](https://www.zhihu.com/equation?tex=W%5E%7Bf%2Ao%7D)

* ![f](https://www.zhihu.com/equation?tex=f) 表示全连接层的节点个数
* ![o](https://www.zhihu.com/equation?tex=o) 表示输出层的节点个数

很显然 ![o](https://www.zhihu.com/equation?tex=o) 一般是固定的，而 ![f](https://www.zhihu.com/equation?tex=f) 则会随着输入图像大小的变化而变化。

## 2.解决办法

## 1).resize or crop

这种方法比较粗暴，而且会在预处理环节增加很大的计算量，一般而言是没有办法的办法。

## 2).SPP(Spatial Pyramid Pooling 空间金字塔池化)

只需要在全连接层加上SPP layer就可以很好的解决题主的问题

介绍参考(写的很好懂)：

[深度学习笔记（一）空间金字塔池化阅读笔记Spatial Pyramid Pooling in Deep Convolutional Networks for Visual Recognition](https://link.zhihu.com/?target=http%3A//blog.csdn.net/liyaohhh/article/details/50614380)[SPP-net原理介绍-大数据算法](https://link.zhihu.com/?target=http%3A//x-algo.cn/index.php/2017/01/13/1587/)

代码实现参考：

[Pytorch实现spp net](https://link.zhihu.com/?target=http%3A//www.erogol.com/spp-network-pytorch/)

```
import math
from collections import OrderedDict
import torch.nn as nn
import torch.nn.init as init
import torch as th
import torch.nn.functional as F
from torch.autograd import Variable


class SPPLayer(nn.Module):

    def __init__(self, num_levels, pool_type='max_pool'):
        super(SPPLayer, self).__init__()

        self.num_levels = num_levels
        self.pool_type = pool_type

    def forward(self, x):
        bs, c, h, w = x.size()
        pooling_layers = []
        for i in range(self.num_levels):
            kernel_size = h // (2 ** i)
            if self.pool_type == 'max_pool':
                tensor = F.max_pool2d(x, kernel_size=kernel_size,
                                      stride=kernel_size).view(bs, -1)
            else:
                tensor = F.avg_pool2d(x, kernel_size=kernel_size,
                                      stride=kernel_size).view(bs, -1)
            pooling_layers.append(tensor)
        x = th.cat(pooling_layers, dim=-1)
        return x

class DetectionNetSPP(nn.Module):
    """
    Expected input size is 64x64
    """

    def __init__(self, spp_level=3):
        super(DetectionNetSPP, self).__init__()
        self.spp_level = spp_level
        self.num_grids = 0
        for i in range(spp_level):
            self.num_grids += 2**(i*2)
        print(self.num_grids)

        self.conv_model = nn.Sequential(OrderedDict([
          ('conv1', nn.Conv2d(3, 128, 3)), 
          ('relu1', nn.ReLU()),
          ('pool1', nn.MaxPool2d(2)),
          ('conv2', nn.Conv2d(128, 128, 3)),
          ('relu2', nn.ReLU()),
          ('pool2', nn.MaxPool2d(2)),
          ('conv3', nn.Conv2d(128, 128, 3)), 
          ('relu3', nn.ReLU()),
          ('pool3', nn.MaxPool2d(2)),
          ('conv4', nn.Conv2d(128, 128, 3)),
          ('relu4', nn.ReLU())
        ]))

        self.spp_layer = SPPLayer(spp_level)

        self.linear_model = nn.Sequential(OrderedDict([
          ('fc1', nn.Linear(self.num_grids*128, 1024)),
          ('fc1_relu', nn.ReLU()),
          ('fc2', nn.Linear(1024, 2)),
        ]))

    def forward(self, x):
        x = self.conv_model(x)
        x = self.spp_layer(x)
        x = self.linear_model(x)
        return x
```


---

## 哪些影视作品给你留下了童年阴影？

`link: https://www.zhihu.com/question/41892678/answer/294893115 · created: 1515824835`


让我感到十分恐惧的《憨豆先生》，每每看到他那表情就让我觉得非常恐怖，而且眼睛又瞪得很大

![](https://picx.zhimg.com/v2-3a2c7dc678f3248e3a4fd28c7b0d417f_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='425'></svg>)![](https://pic1.zhimg.com/v2-b056dc02d0155d21caa4712fdeba49d6_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='701'></svg>)  
![](https://picx.zhimg.com/v2-ce5db97bf28d2f072ca2072f55d926b2_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='450' height='482'></svg>)

而且大部分是不说话的，所以让我感觉不能呼吸，很压抑。

![](https://picx.zhimg.com/50/v2-f3c80abafaa5bd2de06aa470c49ce3c0_720w.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='285' height='400'></svg>)

小时候看到别人笑的时候我真的觉得好恐怖

现在也还是这样。。。。。。


---

## 运气好是一种怎样的体验？

`link: https://www.zhihu.com/question/26889313/answer/281255496 · created: 1513950451`


怒答一发。说一个我同学的例子。

此人关山口职业技术学院大四学生，人帅有气质。

因经常逛校园bbs，后被学校通过大数据挖掘，如此国家栋梁凭借优秀才能获得保研名额。

( ･\_･)ﾉ⌒●~\*

  

就是昨天(2017.12.21)，小米的感恩季活动，他抽中100元券，用来买了一个台灯。

然而故事并没有结束

。

。

。

正是因为买了这台灯，他又抽奖抽到了1999红包，然后顺手又买了小米note3。

  
![](https://pica.zhimg.com/v2-5a580b2eda7ca10664d5ac060f5988b7_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1058' height='1412'></svg>)  
![](https://picx.zhimg.com/v2-49fa136468fb6735cdc65dc02ce8e77d_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='640' height='1136'></svg>)  
![](https://pic1.zhimg.com/v2-d83c8f9f9c892f5aa9332fc9c5f49db7_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='640' height='1136'></svg>)  
![](https://picx.zhimg.com/50/v2-dd2fd5283feb82a5110b66d49c884c31_720w.gif?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='400' height='426'></svg>)  
  
  

我这么一个只抽到实物券的，而且还要花10元邮费才能拿到东西的人表示相当惭愧。

  

最后大佬大发慈悲，将之前参与活动获得的小米胶囊耳机赠予我，特写此答案以表谢意！(๑•॒̀ ູ॒•́๑)啦啦啦

———2017.12.24更新———

非常羡慕，十分嫉妒。今天马云爸爸又搞活动，ta又抽中了最高奖188元。。。。而我这等衰神只有16.8

  
  
![](https://picx.zhimg.com/v2-b8461bc2f339f00e11aff39ff4442e9a_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1080' height='1920'></svg>)


---

## 为什么神经网络在考虑梯度下降的时候，网络参数的初始值不能设定为全0，而是要采用随机初始化思想？

`link: https://www.zhihu.com/question/36068411/answer/223788092 · created: 1504242488`


1. [[神经网络权重初始化问题 - marsggbo - 博客园](https://link.zhihu.com/?target=http%3A//www.cnblogs.com/marsggbo/p/7462682.html)]
2. [CS231n Convolutional Neural Networks for Visual Recognition](https://link.zhihu.com/?target=http%3A//cs231n.github.io/neural-networks-2/%23init)


---

## 如何选择神经元权重等参数的初始值？

`link: https://www.zhihu.com/question/25403372/answer/223787002 · created: 1504242317`


1. [[神经网络权重初始化问题 - marsggbo - 博客园](https://link.zhihu.com/?target=http%3A//www.cnblogs.com/marsggbo/p/7462682.html)]
2. [CS231n Convolutional Neural Networks for Visual Recognition](https://link.zhihu.com/?target=http%3A//cs231n.github.io/neural-networks-2/%23init)


---

## 单位脉冲响应、单位阶跃响应的作用？

`link: https://www.zhihu.com/question/29461110/answer/100990437 · created: 1463302470`


在说脉冲响应之前，我们首先要知道离散时间信号其实是由一连串单个的脉冲信号组成的。很抽象哈，看看下面的例子。

假设我们有一离散信号x[n]，如下图所示

![](https://pic1.zhimg.com/17d151224910f352c660d8b5fcaf854e_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1152' height='974'></svg>)

由冲激信号的抽样性质，我们可以得到![x[-2]=x[-2]\delta [n+2]](https://www.zhihu.com/equation?tex=x%5B-2%5D%3Dx%5B-2%5D%5Cdelta+%5Bn%2B2%5D),![x[-1]=x[-1]\delta [n+1]](https://www.zhihu.com/equation?tex=x%5B-1%5D%3Dx%5B-1%5D%5Cdelta+%5Bn%2B1%5D)等等。因此我们将x[n]分解成一组**加权**了的**移位**的脉冲之和。，图像如下：

![](https://picx.zhimg.com/acced95eb35a89035b11762903f8214f_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='922' height='2041'></svg>)

因此对于这个x[n]信号我们可以表示成![x[n] = ... + x[-2]\delta [n+2] + x[-1]\delta [n+1] +x[0]\delta [0] +x[1]\delta [n-1]+...](https://www.zhihu.com/equation?tex=x%5Bn%5D+%3D+...+%2B+x%5B-2%5D%5Cdelta+%5Bn%2B2%5D+%2B+x%5B-1%5D%5Cdelta+%5Bn%2B1%5D+%2Bx%5B0%5D%5Cdelta+%5B0%5D+%2Bx%5B1%5D%5Cdelta+%5Bn-1%5D%2B...)

用求和公式表示就是![x[n] = \sum_{k=-\infty }^{+\infty}{x[k]\delta [n-k]} ](https://www.zhihu.com/equation?tex=x%5Bn%5D+%3D+%5Csum_%7Bk%3D-%5Cinfty+%7D%5E%7B%2B%5Cinfty%7D%7Bx%5Bk%5D%5Cdelta+%5Bn-k%5D%7D+)。

正如前面所说的，离散时间信号是由一组**加权**了的**移位**的脉冲信号组成，对应到该例子中的x[n]，那么它的脉冲信号的加权就是x[k]，移位是k。

接下来咱们要求一下x[n]的响应y[n]了。但是通过前面的例子我们已经知道离散时间信号是由一组**加权**了的**移位**的脉冲信号组成（重要的事情就是要多说几遍），所以为了使响应的求法更具一般性，我们只需知道脉冲信号![\delta [n-k]](https://www.zhihu.com/equation?tex=%5Cdelta+%5Bn-k%5D)的响应,然后乘上前面的加权x[k]，即可求得k时刻对应的响应，然后再用求和符号即可得到x[n]的输出响应。

这里我们将![h_{k}[n] ](https://www.zhihu.com/equation?tex=h_%7Bk%7D%5Bn%5D+)记为该系统对移位单位脉冲信号![\delta [n-k]](https://www.zhihu.com/equation?tex=%5Cdelta+%5Bn-k%5D)的响应,所以我们可以很自然的得到![y[n] = \sum_{k=-\infty}^{\infty}{x[k]h_{k}[n] } ](https://www.zhihu.com/equation?tex=y%5Bn%5D+%3D+%5Csum_%7Bk%3D-%5Cinfty%7D%5E%7B%5Cinfty%7D%7Bx%5Bk%5Dh_%7Bk%7D%5Bn%5D+%7D+).

因为以上讨论都是以线性时不变系统为基础，所以由时不变这一性质，我们可以知道对时间移位的脉冲信号的响应也都会移位，也就是说![h_{k} [n] = h_{0} [n-k]](https://www.zhihu.com/equation?tex=h_%7Bk%7D+%5Bn%5D+%3D+h_%7B0%7D+%5Bn-k%5D),为了书写方便，一般规定![h_{0} [n]=h[n]](https://www.zhihu.com/equation?tex=h_%7B0%7D+%5Bn%5D%3Dh%5Bn%5D),所以![y[n]=\sum_{k=-\infty}^{\infty}{x[k]h_{k}[n] }= \sum_{k=-\infty}^{\infty}{x[k]h[n-k] }](https://www.zhihu.com/equation?tex=y%5Bn%5D%3D%5Csum_%7Bk%3D-%5Cinfty%7D%5E%7B%5Cinfty%7D%7Bx%5Bk%5Dh_%7Bk%7D%5Bn%5D+%7D%3D+%5Csum_%7Bk%3D-%5Cinfty%7D%5E%7B%5Cinfty%7D%7Bx%5Bk%5Dh%5Bn-k%5D+%7D).

---------------------------------总结--------------------------------------------

* 对任意离散时间信号有![x[n] = \sum_{k=-\infty }^{+\infty}{x[k]\delta [n-k]} ](https://www.zhihu.com/equation?tex=x%5Bn%5D+%3D+%5Csum_%7Bk%3D-%5Cinfty+%7D%5E%7B%2B%5Cinfty%7D%7Bx%5Bk%5D%5Cdelta+%5Bn-k%5D%7D+)。
* 若已知某线性时不变系统的脉冲信号![\delta [n]](https://www.zhihu.com/equation?tex=%5Cdelta+%5Bn%5D)的响应是h[n],那么x[n]的输出响应则是![y[n]=\sum_{k=-\infty}^{\infty}{x[k]h_{k}[n] }= \sum_{k=-\infty}^{\infty}{x[k]h[n-k] }](https://www.zhihu.com/equation?tex=y%5Bn%5D%3D%5Csum_%7Bk%3D-%5Cinfty%7D%5E%7B%5Cinfty%7D%7Bx%5Bk%5Dh_%7Bk%7D%5Bn%5D+%7D%3D+%5Csum_%7Bk%3D-%5Cinfty%7D%5E%7B%5Cinfty%7D%7Bx%5Bk%5Dh%5Bn-k%5D+%7D)
  
  
  
* 分割线
2017.5.16  
  
  

回答中的图片是这本教材。

![](https://pica.zhimg.com/v2-f37143073d7b26f110f73ec299eb5b44_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1518' height='2048'></svg>)![](https://picx.zhimg.com/v2-0a5e9b263e4a7516db9cc0c0aa5f93f1_r.jpg?source=2c26e567)![](data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1518' height='2048'></svg>)
