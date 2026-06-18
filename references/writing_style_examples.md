# hexin 风格样本

精选高赞文章开头、代表性回答与想法片段。模仿写作风格时请对照语气、句式、转折方式。


## 一、文章开头样本（高赞，按得票排序）


### 《巴西「主权大模型」“翻车”：当模型可以随便融合，怎么证明它偷了你的权重？》  

*2026-06 · None 赞 · http://zhuanlan.zhihu.com/p/2050534438925235435*


```text
> 插播：以下内容节选自我们团队最近出版的书籍《动手学 AutoML：从 NAS 到大模型优化实战》，感兴趣的朋友可以前往 jd 搜索购买，感谢支持

动手学AutoML书籍封面

---

## 1. 先从一个翻车现场说起

前几天有个挺戏剧性的事：巴西里约热内卢市政的 IT 机构 iPlanRIO 高调发布了一个叫 **Rio 3.5 Open 397B** 的开源大模型，号称是公帑资助、自主研发，性能还吊打 DeepSeek v4 Pro 和 Qwen 3.7 Plus，背后是 50 万雷亚尔的公共投入。

听起来很提气是吧。结果没几天就被扒了。

有分析团队放出了一套可复现的检测方法，结论是：这个所谓的「主权模型」，**大概率是把别人的模型权重直接融合（merge）出来的**——大约 60% 来自 Nex N2 Pro，40% 来自 Qwen 3.5。证据也很硬核：
```


### 《进阶篇 | 不靠人工设计，让遗传算法自己进化出 SOTA 的 LLM 剪枝指标》  

*2026-06 · None 赞 · http://zhuanlan.zhihu.com/p/2050167804033292239*


```text
> 插播：以下内容节选自我们团队最近出版的书籍《动手学 AutoML：从 NAS 到大模型优化实战》，感兴趣的朋友可以前往 jd 搜索购买，感谢支持 [https://item.jd.com/15384990.html](https://link.zhihu.com/?target=https%3A//item.jd.com/15384990.html)

---

在上一篇《说人话：一文搞懂现在火热的 LLM agent 自进化原理》里，我们用 LLM agent「自进化」当引子，把进化算法的基本原理捋了一遍——「选择—变异—保留」这套循环，搜的对象可以是网络结构、也可以是 agent 的 prompt 和工具链。

但那篇基本还停留在「原理」层面。这篇我想上点强度，给你看一个真正进阶的应用——**让进化算法自己「进化」出一个数学公式**，而且这个公式比人类专家手工设计的还要好。
```


### 《说人话：一文搞懂现在火热的 LLM agent 自进化原理》  

*2026-06 · None 赞 · http://zhuanlan.zhihu.com/p/2049816837009969932*


```text
> 插播：以下内容节选自我们团队最近出版的书籍《动手学 AutoML：从 NAS 到大模型优化实战》，感兴趣的朋友可以前往 jd 搜索购买，感谢支持

动手学AutoML书籍封面

最近 LLM agent「自进化」（self-evolving agent）这个词特别火。

逻辑大概是这样：让 agent 自己生成一堆变体（改改 prompt、换换工具组合、调调 workflow），在任务上跑一遍（rollout），谁的表现好就留下谁，再在好的那批身上继续改——这么一轮一轮迭代下去，agent 就「越进化越强」。

我第一次刷到这类工作的时候，第一反应不是「哇好新」，而是——

> 这不就是 **进化算法（Evolutionary Algorithm）** 吗？

**生成变体 = 变异 / 交叉，跑任务打分 = 适应度评估，留下好的 = 选择**。这套「选择—变异—保留」的循环，在 AutoML、尤其是神经架构搜索（NAS）领域，已经被反复打磨了快十年。换的只是搜索对象：以前搜的是网络结构，现在搜的是 agent 的 prompt 和工具链。
```


### 《说人话：AI 这么火，为什么最后是卖内存的韩国海力士赚翻了？》  

*2026-06 · None 赞 · http://zhuanlan.zhihu.com/p/2049596447658718796*


```text
> 插播：之前写的《动手学 AutoML》终于出版了，从 NAS 到超参优化都有覆盖，适合想系统入门 AutoML 的同学。好了广告结束，现在进入正题。  
> [我们的书《动手学 AutoML》出版啦！从 NAS 到大模型优化，系统讲透这套方法论](https://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/s%3F__biz%3DMzI5OTI3ODAyNg%3D%3D%26mid%3D2247487029%26idx%3D1%26sn%3D7b5cd973c57b45e92b11e2f1e8dcf31d%26scene%3D21%23wechat_redirect)

动手学AutoML书籍封面

作为 AI 行业从业者，经常会有亲戚朋友问我一些关于 AI 的事情，比如

"这 ChatGPT 到底咋回事啊？""它咋啥都会写还会画？""听说显卡内存涨疯了，海力士股票翻了好几倍，跟你们 AI 是不是有关系？"
```


### 《为什么你的多智能体系统越加 agent 越慢？DeLM 用去中心化解了这个矛盾》  

*2026-06 · None 赞 · http://zhuanlan.zhihu.com/p/2048720788275180090*


```text
> 插播：之前写的[《动手学 AutoML》](https://link.zhihu.com/?target=https%3A//item.jd.com/14945889.html)终于出版了，从 NAS 到超参优化都有覆盖，适合想系统入门 AutoML 的同学。好了广告结束，现在进入正题。  
> [我们的书《动手学 AutoML》出版啦！从 NAS 到大模型优化，系统讲透这套方法论](https://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/s/kSREs-iI0kAcPEkU1mFZPA)

动手学AutoML书籍封面

> 原文：[Decentralized Multi-Agent Systems with Shared Context](https://link.zhihu.com/?target=https%3A//arxiv.org/abs/2606.10662)（Yuzhen Mao, Azalia Mirhoseini, Stanford University）

---
```


### 《当 AI 开始造自己：Anthropic 递归自我改进报告深度解读》  

*2026-06 · None 赞 · http://zhuanlan.zhihu.com/p/2048719162080491226*


```text
> 插播：之前写的[《动手学 AutoML》](https://link.zhihu.com/?target=https%3A//item.jd.com/14945889.html)终于出版了，从 NAS 到超参优化都有覆盖，适合想系统入门 AutoML 的同学。好了广告结束，现在进入正题。

> 原文：[When AI builds itself](https://link.zhihu.com/?target=https%3A//www.anthropic.com/institute/recursive-self-improvement)

---

## 1. 前言

你有没有想过这样一个问题：如果 AI 写代码的能力已经超过了写它的人，那下一代 AI 是不是也可以由 AI 自己来造？

这不是科幻。Anthropic 在 2026 年 6 月发了一篇博客，标题极其直白——**When AI builds itself**（当 AI 造自己）。文中用大量内部数据展示了一件事：**AI 已经在加速 AI 自身的开发**，且趋势在加速。
```


### 《NF-CoT：当 LLM 的思维链不再是文字，而是连续概率流》  

*2026-06 · None 赞 · http://zhuanlan.zhihu.com/p/2048718395135244079*


```text
> 插播：之前写的《动手学 AutoML》终于出版了，从 NAS 到超参优化都有覆盖，适合想系统入门 AutoML 的同学。好了广告结束，现在进入正题。  
> [我们的书《动手学 AutoML》出版啦！从 NAS 到大模型优化，系统讲透这套方法论](https://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/s/kSREs-iI0kAcPEkU1mFZPA)

动手学AutoML书籍封面

> 原文：Latent Reasoning with Normalizing Flows

---

## 1. 前言

你有没有想过一个问题：大模型在"思考"的时候，为什么非得一个字一个字把推理过程说出来？

Chain-of-Thought（CoT）确实让模型变聪明了，但代价也很离谱——**每一步推理都必须变成人话才能继续**。即使模型内部只是做了一个简单的语义更新，它也得把这个更新"翻译"成一串 token 输出到序列里，然后才能看到自己刚才在想什么。

这就好比：你做数学题时，每写一步草稿都要先把它翻译成完整的中文句子，才能继续往下算。效率当然低。
```


### 《Transformer 真的需要三个投影矩阵吗？Q-K=V 让 KV Cache 直接砍半》  

*2026-06 · None 赞 · http://zhuanlan.zhihu.com/p/2048717365010027716*


```text
> 插播：之前写的[《动手学 AutoML》](https://link.zhihu.com/?target=https%3A//item.jd.com/14945889.html)终于出版了，从 NAS 到超参优化都有覆盖，适合想系统入门 AutoML 的同学。好了广告结束，现在进入正题。

> 原文：[Do Transformers Need Three Projections? Systematic Study of QKV Variants](https://link.zhihu.com/?target=https%3A//arxiv.org/abs/2606.04032)

---

## 1. 前言

你有没有想过，Transformer 里每个 attention head 都要算 Q、K、V 三个投影，**这三个真的缺一不可吗？**
```


### 《FlashMemory-DeepSeek-V4：用 13.5% 的显存干 100% 的活，超长上下文推理的 less is more》  

*2026-06 · None 赞 · http://zhuanlan.zhihu.com/p/2048428311282446662*


```text
> 插播：之前写的《动手学 AutoML》终于出版了，从 NAS 到超参优化都有覆盖，适合想系统入门 AutoML 的同学。好了广告结束，现在进入正题。

动手学AutoML书籍封面

> 原文：FlashMemory-DeepSeek-V4: Lightning Index Ultra-Long Context via Lookahead Sparse Attention

---

## 1. 前言

你有没有想过，当一个 LLM 在处理一段 500K token 的超长上下文时，**GPU 上那些 KV cache 里有多少是真正被用到的？**

答案是：**90% 以上的请求，光靠最后 8K token 就能准确回答。**

这就是这个领域最核心的矛盾——你为了应对那 10% 的"真需要回忆全文"的情况，不得不把整个 KV cache 全量加载到 GPU 显存里。500K token 的 context，KV cache 动辄 1.8GB+，而大部分时候你只需要其中很小一部分。
```


### 《Self-Harness：让 Agent 自己改自己的 harness，pass rate 最高翻倍》  

*2026-06 · None 赞 · http://zhuanlan.zhihu.com/p/2048419900767703241*


```text
> 插播：之前写的[《动手学 AutoML》](https://link.zhihu.com/?target=vscode-file%3A//vscode-app/Applications/Visual%2520Studio%2520Code.app/Contents/Resources/app/out/vs/code/electron-browser/workbench/workbench.html)终于出版了，从 NAS 到超参优化都有覆盖，适合想系统入门AutoML 的同学。感兴趣的同学可以上京东搜索。

> 原文：[Self-Harness: Harnesses That Improve Themselves](https://link.zhihu.com/?target=https%3A//arxiv.org/abs/2606.09498)

---

## 1. 前言

你有没有想过，你的 AI Agent 到底是被谁"调教"出来的？
```


### 《Mirage：把世界模型的 3D 记忆搬进 Latent Space，快 10 倍还省 55 倍显存》  

*2026-06 · None 赞 · http://zhuanlan.zhihu.com/p/2048413967098418149*


```text
插播：之前写的[《动手学 AutoML》](https://link.zhihu.com/?target=vscode-file%3A//vscode-app/Applications/Visual%2520Studio%2520Code.app/Contents/Resources/app/out/vs/code/electron-browser/workbench/workbench.html)终于出版了，从 NAS 到超参优化都有覆盖，适合想系统入门

AutoML 的同学。感兴趣的同学可以上京东搜索。

> 原文：[Latent Spatial Memory for Video World Models](https://link.zhihu.com/?target=https%3A//arxiv.org/abs/2606.09828)

---

## 1. 什么是世界模型？从 LLM 到"脑中模拟器"

你有没有想过，人类为什么能在脑子里"预演"未来？
```


### 《Frontier：LLM 推理仿真器，端到端误差从 51.7% 降到 2.6%》  

*2026-06 · None 赞 · http://zhuanlan.zhihu.com/p/2048410700926674150*


```text
插播：之前写的[《动手学 AutoML》](https://link.zhihu.com/?target=vscode-file%3A//vscode-app/Applications/Visual%2520Studio%2520Code.app/Contents/Resources/app/out/vs/code/electron-browser/workbench/workbench.html)终于出版了，从 NAS 到超参优化都有覆盖，适合想系统入门

AutoML 的同学。感兴趣的同学可以上京东搜索。广告结束，现在进入正题。

> 原文：[Frontier: Towards Comprehensive and Accurate LLM Inference Simulation](https://link.zhihu.com/?target=https%3A//arxiv.org/abs/2605.21312)

---

## 1. 前言

你有没有想过，在决定用 PDD 还是 co-location 部署一个 200B 的 MoE 模型之前，能不能先"模拟跑一遍"？
```


## 二、代表性回答摘录


### 问：模拟计算芯片能帮助LLM的边缘部署吗？  

*2026-06 · None 赞*


```text
> 原文：[Frontier: Towards Comprehensive and Accurate LLM Inference Simulation](https://link.zhihu.com/?target=https%3A//arxiv.org/abs/2605.21312)

---

## 1. 前言

你有没有想过，在决定用 PDD 还是 co-location 部署一个 200B 的 MoE 模型之前，能不能先"模拟跑一遍"？

不是假设，是真实的问题。一个 200B 参数的 MoE 模型，合理的配置组合（parallelism 策略 + 批大小 + 架构选型）轻松超过 1000 种。在 64-GPU H100 集群上，扫 100 个配置就要花 12,800–25,600 GPU-hours，成本高达 **$180,000**。没有哪个团队能负担得起这个开销，大多数人的选择是"用个保守的默认配置凑合"，结果是**白白损失了 3–5× 的吞吐量**。

所以 inference simulator 这个方向一直有人做。但做好很难。
```


### 问：const常量折叠？  

*2026-05 · None 赞*


```text
## 用编译器「常量折叠」的思路压缩 LLM？这篇 EuroSys 2026 的工作把 FFN 参数砍了 80%

> 原文：[LLMFolder: Revisiting Constant Folding in Large Language Models](https://link.zhihu.com/?target=https%3A//dl.acm.org/doi/10.1145/3767295.3769339)（EuroSys 2026） 作者：Gansen Hu, Zhaoguo Wang, Wei Huang, Jinglin Wei, Haibo Chen（上交 IPADS 实验室）

---

## 1. 前言

今天想和大家聊一篇角度很新颖的工作——LLMFolder，来自上交 IPADS 实验室，发在 EuroSys 2026。

这篇论文的出发点是个很自然的问题：LLM 太大了，部署成本高。缓解这个问题的主流手段是**剪枝（pruning）**——把不重要的权重去掉。但剪枝有个大坑：**压缩比一高，精度掉得很厉害**。比如压缩到 80%，accuracy 可能就已经难以接受了。
```


### 问：Attention mechanism目前有什么缺点和改进空间？  

*2026-05 · None 赞*


```text
> 原文：[SolidAttention: Low-Latency SSD-based Serving on Memory-Constrained PCs](https://link.zhihu.com/?target=https%3A//www.usenix.org/system/files/fast26-zheng.pdf)（FAST 2026，上海交通大学 IPADS 实验室）

---

## 1. 前言

你有没有想过，在自己的笔记本上本地跑一个长上下文的 LLM，体验一下"私有 AI 助手"到底是什么感觉？

这个想法很美好，现实很骨感。

现在主流的笔记本——就是那种配个 16GB 内存、8GB 显存的标配机器——在面对 128k token 上下文时，连 KV cache 都装不下。一个 8B 参数的模型，光 KV cache 就需要 **16GB 内存**，比模型权重本身多 4 倍多。

所以现在的本地部署方案（llama.cpp、Ollama 这些）基本默认你的内存够用，但大多数人的机器其实根本不够用。
```


### 问：web端加载大模型现在有什么好方法吗？  

*2026-05 · None 赞*


```text
> 原文：[Accelerating Model Loading in LLM Inference by Programmable Page Cache](https://link.zhihu.com/?target=https%3A//www.usenix.org/system/files/fast26-liu-yubo.pdf)（USENIX FAST 2026）

---

## 1. 前言

你有没有遇到过这种情况：一个 LLM 推理服务，业务流量一上来，需要紧急扩容，但新起一个实例，光是模型加载就要等一两分钟，有时甚至更长？

这不是什么小概率踩坑，这是 MaaS（Model-as-a-Service）场景下普遍存在的痛点。Qwen2.5-72B 这类大模型，光文件就 130+ GB，加载到 NPU/GPU 上是个实实在在的 I/O 密集操作。论文里测了一组数据：**模型加载的开销占推理服务整个启动时延的 50% 以上**，这还是算上了容器初始化、KV cache 初始化的情况。
```


### 问：GPT模型如何优化kv-cache对芯片影响的问题？  

*2026-05 · None 赞*


```text
> 原文：[Bidaw: Enhancing Key-Value Caching for Interactive LLM Serving via Bidirectional Computation–Storage Awareness](https://link.zhihu.com/?target=https%3A//www.usenix.org/system/files/fast26-hu-shipeng.pdf)

---

## **1. 前言**

你有没有想过，像 Replika、Duolingo 这类依赖多轮对话的 LLM 应用，在底层到底有多"重"？

用户问一句话，LLM 要回一段话。下一轮用户再问，LLM 不仅要理解新问题，还要"记住"之前说过的所有内容——这个"记住"在工程上的实现，就是把历史轮次产生的 **KV tensor** 全部加载进 GPU 重新计算。
```


### 问：有没有什么方法来识别大模型推理过程中KV cache的冷热程度。？  

*2026-05 · None 赞*


```text
> 原文：[EPIC: Efficient Position-Independent Caching for Serving Large Language Models](https://link.zhihu.com/?target=https%3A//arxiv.org/abs/2410.15332)

## 1. 前言

你有没有想过，当你用 RAG 系统给 LLM 塞了 5 篇文档 + 一个问题时，这 5 篇文档的 KV cache 其实在不同请求之间是可以复用的？

毕竟文档内容没变，变的只是用户的问题。但现实是，**绝大多数系统只支持前缀匹配的 KV cache 复用**——也就是说，只有当两个请求的开头完全一致时，缓存才能命中。这就很尴尬了：你 RAG 检索出来的文档顺序稍微变一下，或者 system prompt 改了一个字，前面缓存的 KV 全部失效，得重算。

这也是整个行业在 KV cache 复用上的**核心矛盾**：你想复用的 chunk（文档/few-shot 示例）在不同请求里出现的位置不一样，但 KV 向量里偏偏编码了位置信息（RoPE），导致"位置一变，缓存作废"。
```


### 问：MoE与Dense模型之间是否存在规模等效算法？  

*2026-05 · None 赞*


```text
> 原文：[Read-ME: Refactorizing LLMs as Router-Decoupled Mixture of Experts with System Co-Design](https://link.zhihu.com/?target=https%3A//proceedings.neurips.cc/paper_files/paper/2024/file/d298cf34e4539f9134db7f38b42f69fe-Paper-Conference.pdf)

## **1. 前言**

做 MoE 推理优化的牛马应该对这个场景不陌生：

你好不容易把 Mixtral-8x7B 或者 DeepSeek-MoE 部署起来，满心期待地等着"稀疏激活带来的效率红利"落地，结果一跑推理，GPU 显存占用跟 dense 模型差不了多少，延迟也没降多少。

为什么？

因为**MoE 的优势是推理时只激活少数 expert，但落地被"全量加载 + 低效调度"的系统设计给卡死了**。

这也是整个 MoE 推理领域的核心矛盾之一：模型架构设计和系统推理策略之间的脱节。
```


### 问：基于Decoder的LLM为何需要位置编码？  

*2026-04 · None 赞*


```text
## **1. 前言**

你有没有过这种感觉——看了五六篇 RoPE 的解析文章，每篇都说"RoPE 利用了旋转矩阵来编码相对位置"，然后给你列一堆公式，最后贴一段 `rotate_half` 的代码，你点点头，好像懂了，但第二天回想起来，还是不知道那个旋转矩阵是从哪儿来的，也不明白代码里的 `chunk(2, dim=-1)` 到底在干什么。

我就是这样。

作为研究 LLM 推理效率的牛马，KV cache 管理、prefix sharing 这些东西几乎每天都要打交道，RoPE 的性质直接决定了 KV cache 能不能共享（不能共享就白搭）。所以最近花时间把这条线从头捋了一遍，从最朴素的 sin/cos 位置编码开始，一路推到 RoPE 的实现，争取把每个"为什么"都说清楚。

有几个问题在网上真的很难找到好答案：
```


## 三、知乎想法样本（短动态）

- (2026-06) 巴西「主权大模型」“翻车”：当模型可以随便融合，怎么证明它偷了你的权重？ | 巴西里约热内卢市政发布的开源大模型Rio 3.5 Open 397B，号称自主研发，性能吊打其他模型，结果被扒出大概率是直接融合别人的模型权重。这引出了一个关键问题：当模型融合变得容易，「这个模型到底是不是你的」，要怎么证明？ 为了解决「融合之后怎么追溯版权」，RouteMark工作被提出。其核心发现是，融合后每个expert依然对它「原始训练领域」的输入最敏
- (2026-06) 进阶篇 | 不靠人工设计，让遗传算法自己进化出 SOTA 的 LLM 剪枝指标 | LLM剪枝的核心在于设计一个剪枝指标来给权重打分，过去这由人工完成，如Magnitude、Wanda等方法。现在，可以把“寻找最优剪枝指标”转化为一个符号回归问题，用进化算法（遗传编程）来自动搜索数学表达式。算法将表达式编码为树，通过变异、交叉和基于剪枝后模型困惑度的选择来进化。最终，进化出的公式（Pruner-Zero）在LLaMA全系列上表现优于主流
- (2026-06) 说人话：一文搞懂现在火热的 LLM agent 自进化原理 | 最近 LLM agent「自进化」特别火，逻辑是让 agent 自己生成变体，在任务上跑一遍，谁表现好就留下，再继续改，一轮轮迭代下去。但第一反应是——这不就是进化算法吗？这套「选择—变异—保留」的循环，在 AutoML、尤其是神经架构搜索领域，已被反复打磨快十年。区别只是搜索对象：以前搜网络结构，现在搜 agent 的 prompt 和工具链。 进化算法的核心是模仿生物进
- (2026-06) 说人话：AI 这么火，为什么最后是卖内存的韩国海力士赚翻了？ | AI说穿了就是个"猜下一个字"的机器，它的本体是一个有几千亿"未知数"的大方程，猜一个字就要算一遍，全是天文数字级别的乘加，所以离不开几千核一起算的GPU。 而这几千亿个未知数（外加越聊越长的记忆）大到一张卡都装不下、还得越聊越占。 可显卡算得再快，内存又大又快地喂不上也白搭。 而能又大又快喂饱AI的好内存（HBM），全世界就三家能造——海力士正是跑在最前面那一个。 所以
- (2026-06) 为什么你的多智能体系统越加 agent 越慢？DeLM 用去中心化解了这个矛盾 | 你有没有发现，多 agent 系统加着加着就变慢了？直觉上，多个 agent 并行干活应该更快，但现实往往相反：子任务越多，系统反而越慢、越绕、越贵。 这个问题被 Stanford 的 DeLM 归因到一个东西上——中心化调度（centralized orchestration）。现在主流的 MAS 都有一个主 agent 负责拆任务、派活、收集结果，所
- (2026-06) 当 AI 开始造自己：Anthropic 递归自我改进报告深度解读 | AI 造自己不是科幻。Anthropic 在 2026 年 6 月发了一篇博客，标题直白——When AI builds itself。文中展示了一件事：AI 已经在加速 AI 自身的开发，且趋势在加速。 外部评测显示，AI 处理长任务的能力翻倍周期从 7 个月缩短到 4 个月，如果趋势不停，2027 年 AI 就能处理人类需要数周完成的任务。 Anthropic 
- (2026-06) NF-CoT：当 LLM 的思维链不再是文字，而是连续概率流 | 你有没有想过一个问题：大模型在“思考”的时候，为什么非得一个字一个字把推理过程说出来？Chain-of-Thought（CoT）确实让模型变聪明了，但代价也很离谱——每一步推理都必须变成人话才能继续。 NF-CoT 给了一个很漂亮的解：用 Normalizing Flow 在 LLM 内部建模连续思维链的概率分布，既有精确的 likelihood，又能像普通 token 
- (2026-06) Transformer 真的需要三个投影矩阵吗？Q-K=V 让 KV Cache 直接砍半 | 你有没有想过，Transformer 里每个 attention head 都要算 Q、K、V 三个投影，这三个真的缺一不可吗？K 和 V 需要全量缓存，这玩意儿在长上下文场景下是真正的显存杀手。 作者系统性地测试了三种“省矩阵”的方案，核心发现是：不是所有投影共享都能带来推理加速，只有共享 K 和 V 才能直接转化为 KV Cache 的减
- (2026-06) Self-Harness：让 Agent 自己改自己的 harness，pass rate 最高翻倍 | LLM Agent 的 harness（如 system prompt、工具配置等）对性能影响巨大，但目前全靠人肉工程，难以规模化且无法通用。Self-Harness 提出新思路：让 Agent 自己改自己的 harness，通过一个三步迭代循环实现：首先从执行失败的痕迹中挖掘反复出现的失败模式；接着用同一个模型基于这些模式，提出多
- (2026-06) Mirage：把世界模型的 3D 记忆搬进 Latent Space，快 10 倍还省 55 倍显存 | 世界模型是能根据动作预测未来观察的系统，维护持久3D空间表示是关键。此前RGB点云方案存在瓶颈：video diffusion model在latent space工作，但空间记忆在pixel space，每步都需“latent→pixel→latent”来回折腾，既慢又损信息。Mirage的核心idea很自然：既然diffusio
- (2026-06) Mirage：把世界模型的 3D 记忆搬进 Latent Space，快 10 倍还省 55 倍显存 | 世界模型是能根据动作预测未来观察的系统，维护持久3D空间表示是关键。此前RGB点云方案存在瓶颈：video diffusion model在latent space工作，但空间记忆在pixel space，每步都需“latent→pixel→latent”来回折腾，既慢又损信息。Mirage的核心idea很自然：既然diffusio
- (2026-06) Frontier：LLM 推理仿真器，端到端误差从 51.7% 降到 2.6% | 部署大型 MoE 模型前，能否先“模拟跑一遍”？合理的配置组合轻松超过 1000 种，在真实集群上扫描成本极高。Frontier 这个仿真器正面解决了这个问题。 现有仿真器存在两大问题：架构不完整，无法建模 PDD/AFD 等 disaggregated serving 架构；仿真精度不够，误差甚至会导致错误决策。 Frontier 的核心设计对应解决了
- (2026-06) 《动手学AutoML》手把手教你实现自动机器学习 | #AutoML #机器学习 #AI入门 #手把手教学 #程序员学习 本书分为四个部分，共 11 章。 . 第一部分 基础篇（第 1、2 章）介绍 AutoML 的理论基础与技术背景，包括机器学习建模流程、AutoML 的系统定义、优化目标、演进趋势与典型系统框架与平台。该部分为后续各章打下完整的认知基础。 . 第二部分 进阶篇（第 35 章）聚焦 AutoML 中的神经架构搜索，系统
- (2026-06) 我们的书《动手学 AutoML》出版啦！从 NAS 到大模型优化，系统讲透这套方法论 | 我们团队写的《动手学 AutoML：从 NAS 到大语言模型优化实战》出版了。这本书覆盖了从经典 AutoML 方法到 LLM 时代应用的完整技术链路。AutoML 的核心思路——定义搜索空间、设计评估策略、自动化迭代优化——正以新面貌出现在前沿工作中，例如 Agent 自动进化、大模型压缩等。这本书教你用算法自动找到“最优配置”的系统性方法，每个
- (2026-06) 我们的书《动手学 AutoML》出版啦！从 NAS 到大模型优化，系统讲透这套方法论 | 我们团队写的《动手学 AutoML：从 NAS 到大语言模型优化实战》终于出版了。这本书覆盖了从经典 AutoML 方法到 LLM 时代应用的完整技术链路。 每次有人问我“AutoML 是不是过时了”，我都觉得挺有意思——你仔细看看现在最火的那些工作，底下用的搜索和优化逻辑，和 AutoML 当年研究的东西其实是一脉相承的。 可以说，AutoML 