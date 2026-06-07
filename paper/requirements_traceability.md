# 课程论文要求与项目完成度追踪

## 选题定位

本项目选择《人工智能》课程论文方向（一）：复现任意人工智能算法。论文拟题为：

**基于 U-KAN 的医学图像分割算法复现与注意力增强改进研究**

核心任务是复现 U-KAN 在二维医学图像分割中的主要模型思想、训练流程和评价方式，并在此基础上加入轻量通道-空间注意力模块，形成 Attention-U-KAN 改进模型。实验使用 BUSI 作为主数据集，CVC-ClinicDB 作为补充数据集，并加入 U-Net 与 U-KAN(no-KAN) 作为对照。

## 课程要求拆解

| 课程要求 | 本项目对应内容 | 当前状态 |
| --- | --- | --- |
| 课程论文来源说明 | 需说明 U-KAN 论文、官方源码、KAN/pykan、相关 KAN 医学分割论文、公开数据集、大语言模型辅助情况 | 待写入论文正文 |
| 摘要 | 概括医学图像分割背景、U-KAN 复现、Attention-U-KAN 改进、BUSI/CVC 结果和结论 | 待写 |
| 引言 | 说明医学图像分割意义、U-Net 系列局限、KAN 的非线性建模动机和选择 U-KAN 的原因 | 待写 |
| 算法简介 | 介绍 U-Net、KANLinear、B-spline、Tokenized KAN Block、U-KAN 编码器/解码器、Attention-U-KAN | 代码和资料已具备，正文待写 |
| 数据介绍 | BUSI 780 张图像，CVC 612 张图像，均完成 80/20 划分 | 已完成 |
| 数据预处理 | BUSI 多 mask 并集合并；CVC 图像/mask 标准化；二值化 mask；统一 split 文件 | 已完成 |
| 数据可视化 | `busi_samples.png`、`cvc_samples.png` | 已完成 |
| 实验环境 | Python 3.10.18、PyTorch 2.9.1+cu126、RTX 4080 Laptop GPU 等 | 已有 doctor 脚本，论文需整理截图 |
| 参数设置 | YAML 记录 input size、batch size、epoch、lr、kan_lr、seed、embed dims | 已完成 |
| 对照实验 | U-Net、U-KAN(no-KAN)、U-KAN、Attention-U-KAN；BUSI/CVC 各四组 | 已完成主实验 |
| 定量评估 | IoU、Dice、Precision、Recall、Specificity、参数量、单图推理时间 | 已完成 |
| 定性评估 | 原图、GT、U-KAN、Attention-U-KAN、error map 对比图 | 已完成 BUSI/CVC |
| 错误案例分析 | 基于预测对比图和 error map 分析漏分/误分 | 待写入正文 |
| 代码运行截图 | 训练、评估、可视化、结果汇总命令截图 | 原始截图已放在课程要求目录，论文需筛选排版 |
| 讨论 | 分析 U-KAN 收益、注意力模块未稳定提升、随机种子波动、训练轮数不足风险 | 已有分析材料 |
| 结论 | 总结复现和改进实验结论 | 待写 |
| 参考文献 | U-KAN、KAN、pykan、KC-UNet、ResU-KAN、数据集、开源代码等 | 待统一格式 |

## 加分项覆盖

| 加分项 | 课程要求 | 本项目落实情况 |
| --- | --- | --- |
| GitHub 源代码链接 | 完整代码上传 GitHub，不以附件或微信方式提交源码 | remote 已指向 `https://github.com/Simon-Tisa/AI_CourseWork.git`，本地分支需 push |
| 详细 README | 依赖、环境配置、数据准备、运行步骤、项目结构 | `README.md` 已覆盖数据、训练、评估、绘图、结果汇总命令 |
| 项目结构 | 模块划分清晰、代码注释合理、可维护 | 已按 `configs`、`scripts`、`src`、`tests`、`experiments`、`paper` 组织 |
| 数据整理 | 可使用公开数据集并进一步整理、清洗和标注 | BUSI/CVC 已统一为 U-KAN 所需格式；BUSI 多 mask 已合并 |
| 论文排版 | 标题编号、图表编号、公式、参考文献、图源标注规范 | 待在最终 Word 论文中完成 |
| 自绘图片 | 自绘结构图、流程图可加分 | 待绘制 U-KAN 结构图、Attention 模块图、实验流程图 |
| 过程记录 | 高分建议体现额外实践投入、过程记录或独立思考 | 已有训练截图、结果表、诊断表和补实验计划 |

## 当前实验矩阵

| 编号 | 数据集 | 模型 | 目的 | 状态 |
| --- | --- | --- | --- | --- |
| E1 | BUSI | U-Net | 传统 CNN 基线 | 已完成 |
| E2 | BUSI | U-KAN(no-KAN) | MLP 替代 KAN 的消融 | 已完成 |
| E3 | BUSI | U-KAN | 主复现实验 | 已完成 |
| E4 | BUSI | Attention-U-KAN | 注意力增强改进 | 已完成 |
| E5 | CVC | U-Net | 补充 CNN 基线 | 已完成 |
| E6 | CVC | U-KAN(no-KAN) | 补充 KAN 消融 | 已完成 |
| E7 | CVC | U-KAN | 跨数据集复现 | 已完成 |
| E8 | CVC | Attention-U-KAN | 跨数据集改进验证 | 已完成 |
| E9 | BUSI | no-KAN / U-KAN seed 6142 | 随机种子稳定性补实验 | 配置已准备，待运行 |
| E10 | CVC | U-KAN 继续训练 | 收敛性补实验 | 训练脚本已支持，待运行 |

## 已生成资产

数据与统计：

- `data/splits/busi_seed2981_train.txt`
- `data/splits/busi_seed2981_val.txt`
- `data/splits/cvc_seed2981_train.txt`
- `data/splits/cvc_seed2981_val.txt`
- `data/splits/busi_seed6142_train.txt`
- `data/splits/busi_seed6142_val.txt`
- `experiments/results/busi_dataset_stats.csv`
- `experiments/results/cvc_dataset_stats.csv`

论文图：

- `experiments/figures/busi_samples.png`
- `experiments/figures/cvc_samples.png`
- `experiments/figures/busi_training_curves.png`
- `experiments/figures/cvc_training_curves.png`
- `experiments/figures/busi_prediction_comparison.png`
- `experiments/figures/cvc_prediction_comparison.png`

论文表：

- `paper/tables/segmentation_results.csv`
- `paper/tables/training_diagnostics.csv`

## 当前主要结论

1. BUSI 上 U-KAN 的 IoU/Dice 为 0.6874/0.8147，是四个模型中最优，优于 U-Net、no-KAN 和 Attention-U-KAN。
2. CVC 上 U-KAN 的 IoU/Dice 为 0.7874/0.8810，也略优于 U-Net 和 no-KAN。
3. Attention-U-KAN 在 BUSI 和 CVC 上均未超过原始 U-KAN，说明简单通道-空间注意力并非稳定增益，应作为改进尝试和局限讨论，而不是强行包装成全面提升。
4. U-Net 推理速度显著快于 U-KAN 系列，KAN 提升精度的同时带来更高推理时间，这可以写入效率分析。
5. BUSI no-KAN 在训练曲线中存在局部峰值，需要用 seed 6142 补实验验证单 seed 结果的稳定性。
6. CVC U-Net best epoch 位于第 99 轮，后段仍在上升；U-KAN 后 10 轮变化很小，更接近平台期。可通过 CVC U-KAN 继续训练补充收敛性证据。

## 当前缺口

1. GitHub 远端尚需用户本机执行 `git push origin course-paper-ukan`。
2. seed 6142 和 CVC 继续训练补实验尚未运行。
3. 论文正文尚未完成，包括摘要、引言、算法原理、实验设计、结果分析、讨论、结论和参考文献。
4. 自绘图尚未完成，包括 U-KAN 结构图、Attention-U-KAN 模块图、实验流程图、数据处理流程图。
5. 课程论文最终 Word 排版尚未完成，需要按课程要求设置小四号、1.5 倍行距、图表编号和来源标注。

## 下一步优先级

1. 等用户运行 BUSI seed 6142 的 no-KAN 和 U-KAN 补实验，确认随机种子稳定性。
2. 等用户运行 CVC U-KAN 继续训练 50 epoch，确认是否训练不足。
3. 在补实验等待期间，先撰写不依赖新增结果的论文部分：课程论文来源说明、引言、算法原理、数据与实验设置。
4. 整理参考文献和图源说明。
5. 生成自绘图并开始 Word 论文排版。
