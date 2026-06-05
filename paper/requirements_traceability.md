# 课程论文要求与项目完成度追踪

## 选题定位

本项目选择课程论文方向（一）：复现任意人工智能算法。

论文题目建议为：基于 U-KAN 的医学图像分割算法复现与注意力增强改进研究。

核心目标：

- 复现 U-KAN 在二维医学图像分割任务中的主要模型结构、训练流程和评价方式。
- 在复现基础上加入轻量通道-空间注意力模块，形成 Attention-U-KAN。
- 使用 BUSI 作为主数据集，CVC-ClinicDB 作为补充数据集。
- 增加传统 CNN U-Net、U-KAN `--no_kan`、U-KAN、Attention-U-KAN 的对照链条。

## 课程正文要求对照

| 课程要求 | 项目对应内容 | 当前状态 |
| --- | --- | --- |
| 课程论文来源说明 | `paper/draft_outline.md` 已列出 U-KAN、KAN、pykan、数据集、开源代码和大语言模型辅助说明 | 已有初稿，论文终稿需扩写 |
| 摘要 | 需概括医学分割背景、U-KAN、注意力改进、BUSI/CVC 结果 | 待实验结果后撰写 |
| 引言 | 说明医学图像分割价值、U-Net 局限、KAN 非线性建模动机 | 待论文正文撰写 |
| 算法简介 | 需讲 U-Net、KANLinear、B-spline、Tokenized KAN Block、Attention-U-KAN | 代码已具备，正文待写 |
| 数据介绍 | BUSI 780 例，CVC 612 例，已生成统计表和样本图 | 已完成 |
| 数据预处理 | `prepare_busi.py`、`prepare_cvc.py`、`make_splits.py` | 已完成 |
| 数据可视化 | `experiments/figures/busi_samples.png`、`cvc_samples.png` | 已完成 |
| 实验环境 | `doctor_env.py` 可输出 Python、PyTorch、CUDA、GPU 信息 | 待用户环境截图 |
| 参数设置 | YAML 配置记录 batch size、epoch、lr、KAN lr、seed 等 | 已完成 |
| 对照实验 | U-Net、no-KAN、U-KAN、Attention-U-KAN；BUSI/CVC | 代码与配置已完成，训练待跑 |
| 定量评估 | IoU、Dice、Precision、Recall、Specificity、参数量、单图推理时间 | 评估脚本已完成，结果待训练后生成 |
| 定性评估 | `visualize_predictions.py` 输出预测对比和错误图 | 脚本已完成，结果待训练后生成 |
| 错误案例分析 | 基于预测图和 error map 撰写 | 待训练结果 |
| 代码运行截图 | 需要保存环境诊断、数据处理、训练、评估、可视化命令截图 | 待用户本机运行后整理 |
| 讨论 | 分析 U-KAN 与注意力模块收益、失败原因、资源限制 | 待结果后撰写 |
| 结论 | 总结复现与改进效果 | 待结果后撰写 |
| 参考文献 | U-KAN、KAN、pykan、相关 KAN 医学分割论文、数据集链接 | 待整理为统一格式 |

## 加分项对照

| 加分项 | 要求 | 当前落实 |
| --- | --- | --- |
| GitHub 源代码链接 | 完整代码上传 GitHub，不以附件提交源码 | 本地仓库完整，remote 指向 `Simon-Tisa/AI_CourseWork.git`，需要用户执行 `git push` |
| 详细 README | 依赖、环境、数据、训练、评估、可视化、结构说明 | 已覆盖，并已补 U-Net 与结果生成命令 |
| 项目结构清晰 | 模块化、可维护 | 已按 `configs`、`scripts`、`src`、`tests`、`experiments`、`paper` 组织 |
| 数据整理质量 | 数据清洗、标准化、划分、统计、可视化 | BUSI/CVC 已标准化；BUSI 多 mask 已合并 |
| 排版规范 | 标题、图表、公式、参考文献、来源标注 | 待论文终稿实现 |
| 自绘图 | 算法结构、注意力模块、流程图 | 待生成 `paper/figures` |

## 实验矩阵

| 编号 | 数据集 | 模型 | 目的 |
| --- | --- | --- | --- |
| E1 | BUSI | U-Net | 传统 CNN 基线 |
| E2 | BUSI | U-KAN `--no_kan` | 官方 MLP 替代消融 |
| E3 | BUSI | U-KAN | 主复现实验 |
| E4 | BUSI | Attention-U-KAN | 改进模型 |
| E5 | CVC | U-Net | 补充 CNN 基线 |
| E6 | CVC | U-KAN `--no_kan` | 补充 KAN 模块消融 |
| E7 | CVC | U-KAN | 跨数据集复现 |
| E8 | CVC | Attention-U-KAN | 跨数据集改进验证 |

优先级：先跑 BUSI 四组，再跑 CVC 四组。若时间紧张，论文主体至少保证 BUSI 四组和 CVC 的 U-KAN/Attention-U-KAN。

## 已生成资产

- 数据划分：
  - `data/splits/busi_seed2981_train.txt`
  - `data/splits/busi_seed2981_val.txt`
  - `data/splits/cvc_seed2981_train.txt`
  - `data/splits/cvc_seed2981_val.txt`
- 数据统计：
  - `experiments/results/busi_dataset_stats.csv`
  - `experiments/results/cvc_dataset_stats.csv`
- 数据样本图：
  - `experiments/figures/busi_samples.png`
  - `experiments/figures/cvc_samples.png`

## 当前最大缺口

1. 训练结果尚未生成：需要在用户本机 `C:\ProgramData\Anaconda\envs\torch\python.exe` 环境运行。
2. GitHub 最新本地提交尚未推送：Codex 沙箱无法使用 Windows Git 凭据。
3. 论文正文、参考文献格式、自绘结构图、运行截图尚未完成。
4. PyTorch 测试尚未在用户 torch env 中完整执行。

## 下一步执行顺序

1. 用户先执行 `git push origin course-paper-ukan`，确保 GitHub 链接可用。
2. 用户运行一批 smoke test，确认模型、数据、CUDA 可以端到端跑通。
3. 先训练 BUSI 四组模型，评估并生成预测图、训练曲线和汇总表。
4. 再训练 CVC 三组模型，补充跨数据集结果。
5. 基于结果写论文正文，并生成自绘结构图和运行截图拼图。
