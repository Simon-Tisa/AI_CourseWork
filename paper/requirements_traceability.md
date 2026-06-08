# 课程论文要求与项目完成度最终追踪

最后复核日期：2026-06-08

## 选题定位

本项目选择《人工智能》课程论文方向（一）：复现任意人工智能算法。

最终论文题目：

**基于 U-KAN 的医学图像分割算法复现、实验诊断与注意力增强研究**

说明：早期讨论中曾口误写成 kNN / UKNN，最终已统一纠正为 KAN / U-KAN。项目围绕 Kolmogorov-Arnold Network 在医学图像分割中的应用展开，复现 U-KAN，并加入 Attention-U-KAN 改进尝试、U-Net 基线和 no-KAN 消融。

## 最终交付物

| 交付物 | 文件/位置 | 状态 |
| --- | --- | --- |
| Word 课程论文 | `paper/基于U-KAN的医学图像分割算法复现、实验诊断与注意力增强研究_重写版.docx` | 已完成 |
| Markdown 正文源稿 | `paper/course_paper_draft_v2.md` | 已完成 |
| 论文生成脚本 | `scripts/build_course_paper_v2.py` | 已完成，可重新生成 Word 和图表 |
| 主实验与补实验表格 | `paper/tables/*.csv` | 已完成 |
| 论文图片 | `paper/figures/` 与 `experiments/figures/` | 已完成 |
| 工程代码 | `src/`, `scripts/`, `configs/`, `tests/` | 已完成 |
| README | `README.md` | 已完成，包含环境、数据、训练、评估、绘图和论文生成命令 |
| Git 提交 | `b023484 docs: rewrite course paper with experiment diagnosis` | 已完成 |
| GitHub 远端推送 | `origin=https://github.com/Simon-Tisa/AI_CourseWork.git` | 本地已提交；推送受 Windows/GitHub 凭据限制 |

## 课程要求逐项验收

| 课程要求 | 最终落实方式 | 状态 |
| --- | --- | --- |
| 方向（一）复现任意人工智能算法 | 复现 U-KAN 医学图像分割算法；本地重写 PyTorch 训练、评估和报告流程 | 已完成 |
| 算法原理介绍 | 论文第 3 章说明 KAN 与 MLP 的区别、U-KAN 结构、Attention-U-KAN 改进 | 已完成 |
| 模型搭建 | `src/ukan_course/models/` 实现 U-Net、U-KAN、no-KAN、Attention-U-KAN | 已完成 |
| 实验平台 | 论文表 3 记录 Python、PyTorch、CUDA、RTX 4080 Laptop GPU 等环境 | 已完成 |
| 训练过程 | 训练日志、训练曲线、`实验记录.docx`、`experiments/figures/*training_curves.png` | 已完成 |
| 实验结果展示与分析 | 论文第 5-7 章包含主实验、消融、补实验、效率和错误案例分析 | 已完成 |
| 正文字数不少于 2000 字 | DOCX 结构检查显示中文字符规模约 3714，超过要求 | 已完成 |
| 正文字体小四、1.5 倍行距 | DOCX Normal 样式为 12pt；正文段落 1.5 倍行距 | 已完成 |
| 课程论文来源说明 | 正文开头“来源说明与过程声明”说明论文、源码、数据集、LLM 辅助和图源 | 已完成 |
| 每张图片注明来源 | 图 1-图 14 均在图注中写明作者自绘、论文/官方项目来源或本项目生成 | 已完成 |
| 摘要 | 说明背景、算法、实验矩阵、补充实验和结论 | 已完成 |
| 引言 | 说明医学图像分割背景、U-Net 局限、KAN 动机和选题原因 | 已完成 |
| 数据介绍与预处理 | BUSI/CVC 数据规模、mask 占比、BUSI 多 mask 合并、固定 split | 已完成 |
| 数据可视化 | 图 5 展示 BUSI 与 CVC 样本；`experiments/figures/*samples.png` 也保留 | 已完成 |
| 实验设置与参数 | 论文表 3 与 YAML 配置对应，包含 batch size、epoch、lr、kan_lr、seed 等 | 已完成 |
| 对照实验 | 每个数据集均包含 U-Net、no-KAN、U-KAN、Attention-U-KAN 四组 | 已完成 |
| 定量评估 | IoU、Dice、Precision、Recall、Specificity、参数量、推理时间 | 已完成 |
| 定性评估 | BUSI/CVC 预测对比图和错误案例图 | 已完成 |
| 错误案例分析 | 图 14 与第 6.5 节分析边界偏差、漏分割和过分割原因 | 已完成 |
| 代码运行截图 | 根目录 `实验记录.docx` 与课程要求图片目录保存训练/评估过程截图；正文中用流程图和训练曲线归纳 | 已完成 |
| 讨论 | 论文讨论 KAN 收益、Attention 负结果、seed 波动、CVC 继续训练、效率代价 | 已完成 |
| 结论 | 第 8 章总结复现结果、补实验结论和局限 | 已完成 |
| 参考文献 | 论文列出 U-KAN、KAN、U-Net、CBAM、相关 KAN 医学论文和数据集来源 | 已完成 |

## 加分项覆盖

| 加分项 | 课程要求 | 最终落实情况 |
| --- | --- | --- |
| GitHub 源代码链接 | 完整代码上传 GitHub，不以附件或微信提交源码 | 仓库 remote 已设为 `https://github.com/Simon-Tisa/AI_CourseWork.git`；本地提交已完成，推送需本机凭据 |
| 详细 README | 说明依赖、环境、数据准备、运行步骤、项目结构 | `README.md` 已覆盖环境诊断、数据处理、训练、评估、绘图、论文生成和项目结构 |
| 项目结构 | 模块划分清晰、代码可读、可维护 | `configs/`, `scripts/`, `src/`, `tests/`, `experiments/`, `paper/` 分层组织 |
| 自构/整理数据集 | 可用公开数据集并进一步整理清洗 | BUSI 多 mask 并集合并；CVC 标准化；固定 split；生成数据统计和样本图 |
| 论文格式排版 | 标题层次、图表编号、来源、参考文献、页面美观 | Word 使用真实 Heading 样式、正文小四 1.5 倍行距、11 张表、14 张图 |
| 自绘图片 | PowerPoint/Visio/AI 等自绘可酌情加分 | 使用作者 PPT 手绘图，另自绘 KAN/Attention/实验流程/诊断流程/补实验图 |
| 过程记录与独立思考 | 高分建议体现额外实践和思考过程 | 第 6 章完整写出 BUSI no-KAN 跳变疑问、seed 6142 验证、CVC 继续训练验证 |

## 实验矩阵

| 编号 | 数据集 | 模型 | 目的 | 状态 |
| --- | --- | --- | --- | --- |
| E1 | BUSI | U-Net | 传统 CNN 基线 | 已完成 |
| E2 | BUSI | U-KAN(no-KAN) | MLP 替代 KAN 的消融 | 已完成 |
| E3 | BUSI | U-KAN | 主复现实验 | 已完成 |
| E4 | BUSI | Attention-U-KAN | 注意力增强改进 | 已完成 |
| E5 | CVC | U-Net | 跨数据集 CNN 基线 | 已完成 |
| E6 | CVC | U-KAN(no-KAN) | 跨数据集 KAN 消融 | 已完成 |
| E7 | CVC | U-KAN | 跨数据集复现 | 已完成 |
| E8 | CVC | Attention-U-KAN | 跨数据集改进验证 | 已完成 |
| E9 | BUSI | no-KAN / U-KAN seed 6142 | 随机种子稳定性补实验 | 已完成 |
| E10 | CVC | U-KAN 继续训练 | 收敛性补实验 | 已完成 |

## 最终主要结论

1. BUSI 主实验中 U-KAN 取得 IoU=0.6874、Dice=0.8147，是四组模型中最优。
2. CVC 主实验中 U-KAN 取得 IoU=0.7874、Dice=0.8810，也是四组模型中最优。
3. no-KAN 与 U-KAN 的对比说明，在相同 U 型主体框架中，KANLinear 相比普通 Linear 对分割性能有实际贡献。
4. Attention-U-KAN 在 BUSI 和 CVC 上均未超过原始 U-KAN，因此论文将其作为改进尝试和负结果讨论，而不是强行写成提升。
5. BUSI seed 6142 补实验显示 U-KAN 仍高于 no-KAN，但 BUSI 绝对指标对随机划分和初始化敏感。
6. CVC U-KAN 继续训练 50 epoch 未超过原始 best checkpoint，因此当前证据不支持“只是没跑够”的简单解释。
7. U-KAN 推理速度显著慢于 U-Net，说明 KAN 带来精度收益的同时也有推理时间代价。

## 质量检查记录

| 检查项 | 结果 |
| --- | --- |
| `scripts/build_course_paper_v2.py` 重新生成论文 | 通过 |
| Python 编译检查 | `python -m py_compile scripts/build_course_paper_v2.py` 通过 |
| DOCX 结构解析 | 108 段、11 表、14 图、16 个 Heading |
| 正文规模 | 中文字符规模约 3714，满足不少于 2000 字 |
| 正文格式 | Normal 样式 12pt，正文段落 1.5 倍行距 |
| 新增关键图片视觉抽查 | 实验流程图、诊断流程图、补实验图、错误案例图均已打开检查 |
| 页面级渲染 | 受本机缺少 DOCX 转 PDF/PNG 外部转换程序限制，`render_docx.py` 报 WinError 2 |

## 当前唯一外部缺口

本地分支 `course-paper-ukan` 已提交最终论文，但 `git push origin course-paper-ukan` 在当前受限进程中无法访问 Windows/GitHub 凭据，报 `SEC_E_NO_CREDENTIALS`。需要在用户本机终端执行：

```powershell
git push origin course-paper-ukan
```
