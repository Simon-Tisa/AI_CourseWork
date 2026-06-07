# 课程论文正文结构草案

## 题目

基于 U-KAN 的医学图像分割算法复现与注意力增强改进研究

## 课程论文来源说明

本部分需要放在正文开头，建议写清以下来源：

1. 主要复现对象：U-KAN Makes Strong Backbone for Medical Image Segmentation and Generation。
2. 官方源码来源：CUHK-AIM-Group/U-KAN，重点参考 `Seg_UKAN` 中的 `archs.py`、`kan.py`、`train.py`、`val.py`。
3. 理论背景来源：KAN 原始论文、pykan 项目、U-Net 论文。
4. 相关工作来源：KC-UNet、ResU-KAN、U2-KAN、TransUKAN、PDS-UKAN 等 KAN 医学图像分割论文。
5. 数据来源：BUSI 乳腺超声图像数据集、CVC-ClinicDB 结肠息肉分割数据集。
6. 工具辅助说明：大语言模型用于资料梳理、代码调试建议、论文结构建议和文字润色；实验代码运行、数据准备、训练结果和分析由本人完成并核验。

## 摘要

摘要建议控制在 250-350 字，包含：

- 医学图像分割背景；
- U-KAN 将 KAN 层引入 U-Net 中间 token 表征的核心思想；
- 本文完成 U-KAN 复现，并加入通道-空间注意力形成 Attention-U-KAN；
- 实验数据集为 BUSI 和 CVC-ClinicDB；
- 主要结果：U-KAN 在 BUSI 和 CVC 上均取得当前实验矩阵中的最高 IoU/Dice；
- 结论：KAN 模块在本实验中有效，但注意力增强没有稳定超过原始 U-KAN，后续需进一步设计更稳健的融合策略。

## 1 引言

写作要点：

- 医学图像分割在计算机辅助诊断、病灶定位、手术规划中的意义；
- U-Net 的编码器-解码器结构和跳跃连接是医学分割常用基线；
- CNN 局部建模能力强，但复杂边界和长程依赖仍有挑战；
- Transformer/MLP 改进方法常带来较高计算开销；
- KAN 通过可学习非线性函数替代固定激活函数，为更强非线性建模和可解释性提供新思路；
- U-KAN 将 KAN 层放在 tokenized intermediate representation 上，兼顾卷积局部特征和 KAN 非线性表达；
- 本文贡献：
  1. 工程化复现 U-KAN 医学分割流程；
  2. 加入 U-Net、no-KAN、U-KAN、Attention-U-KAN 的完整对照；
  3. 在 BUSI 与 CVC 两个公开数据集上完成训练、评估、可视化和稳定性诊断；
  4. 分析注意力改进未稳定提升的原因和训练曲线异常。

## 2 算法原理

### 2.1 U-Net 基线

说明 U-Net 的 encoder-decoder、skip connection、上采样、逐像素预测。

### 2.2 Kolmogorov-Arnold Networks

说明：

- KAN 的基本思想是将 MLP 中节点上的固定激活函数转化为边上的可学习一元函数；
- U-KAN 代码中的 `KANLinear` 使用 B-spline 基函数与可学习样条权重；
- `base_weight` 和 `spline_weight` 分别对应基础线性部分和样条非线性部分；
- KAN 在表达能力和可解释性方面具有潜在优势。

可写公式：

- 二分类 Dice；
- IoU；
- BCE + Dice loss；
- KANLinear 的基础项加样条项表达。

### 2.3 U-KAN 分割模型

按结构写：

- 前三层卷积编码器提取低层局部纹理；
- `PatchEmbed` 将中高层特征 token 化；
- `KANBlock` 对 tokenized feature 建模；
- 解码器通过上采样和 skip fusion 恢复空间分辨率；
- 最后 1x1 卷积输出二分类 logits。

要明确：

- `U-KAN(no-KAN)` 不是 U-Net，而是将 U-KAN 中的 `KANLinear` 替换为普通 `nn.Linear` 的 MLP 消融版本；
- U-Net 是另一个独立 CNN baseline。

### 2.4 Attention-U-KAN 改进

说明本文改进：

- 在 decoder 与 encoder skip feature 相加后加入通道-空间注意力；
- 通道注意力用于重标定不同 feature channel；
- 空间注意力用于突出病灶区域、抑制背景噪声；
- 动机来自医学分割中边界模糊、背景干扰和 skip fusion 语义差异问题。

同时要诚实写出当前结果：

- Attention-U-KAN 并未稳定超过原始 U-KAN；
- 这说明简单注意力插入不是无条件有效，需要更精细的位置选择、损失设计或多尺度机制。

## 3 实验设计

### 3.1 数据集

表 1：数据集统计。

| 数据集 | 图像数 | 图像尺寸范围 | mask 平均面积占比 | 训练/验证 |
| --- | ---: | --- | ---: | --- |
| BUSI | 780 | 190-1048 x 310-719 | 0.0783 | 624/156 |
| CVC-ClinicDB | 612 | 384 x 288 | 0.0930 | 490/122 |

### 3.2 数据预处理

写：

- BUSI 原图转 RGB png；
- BUSI 多个 mask 用逻辑 OR 合并；
- CVC mask 二值化；
- 按 seed 2981 生成 80/20 固定划分；
- 训练时 resize 到 256x256；
- 数据增强包括随机旋转和水平/垂直翻转。

### 3.3 实验环境

表 2：实验环境。

| 项目 | 配置 |
| --- | --- |
| 操作系统 | Windows |
| Python | 3.10.18 |
| PyTorch | 2.9.1+cu126 |
| GPU | NVIDIA GeForce RTX 4080 Laptop GPU |
| CUDA | 12.6 |
| 主要依赖 | torch, torchvision, albumentations, OpenCV, scikit-learn, pandas, PyYAML |

### 3.4 模型与参数设置

表 3：训练参数。

| 参数 | 取值 |
| --- | --- |
| input size | 256 x 256 |
| batch size | 8 |
| epochs | 100 |
| optimizer | Adam |
| normal lr | 1e-4 |
| KAN lr | 1e-2 |
| min lr | 1e-5 |
| scheduler | CosineAnnealingLR |
| loss | BCE + Dice |
| seed | 2981 |
| embed dims | [128, 160, 256] |

### 3.5 评价指标

包括：

- IoU；
- Dice；
- Precision；
- Recall；
- Specificity；
- 参数量；
- 单图推理时间。

## 4 实验结果与分析

### 4.1 主结果表

从 `paper/tables/segmentation_results.csv` 生成正式表格。

核心结论：

- BUSI 上 U-KAN 最优：IoU 0.6874，Dice 0.8147；
- CVC 上 U-KAN 最优：IoU 0.7874，Dice 0.8810；
- no-KAN 低于 U-KAN，说明 KAN 层在两个数据集上都有收益；
- Attention-U-KAN 未超过 U-KAN，需要作为负面消融结果讨论；
- U-Net 速度明显更快，说明精度与效率存在权衡。

### 4.2 训练曲线分析

使用：

- `experiments/figures/busi_training_curves.png`
- `experiments/figures/cvc_training_curves.png`
- `paper/tables/training_diagnostics.csv`

需要写：

- BUSI no-KAN 存在局部峰值，单 seed 结果可能不稳定；
- CVC U-Net best epoch 位于 99，可能未完全收敛；
- CVC U-KAN 后 10 epoch 变化很小，更像接近平台；
- 官方 U-KAN README 明确强调随机种子对指标重要，并建议 2981/6142/1187 三次运行平均。

### 4.3 可视化结果

使用：

- `experiments/figures/busi_prediction_comparison.png`
- `experiments/figures/cvc_prediction_comparison.png`

分析角度：

- 哪些样本边界较准确；
- 哪些样本存在漏分；
- 哪些样本背景被误分；
- Attention-U-KAN 是否在局部边界更平滑但整体 IoU 未提升。

### 4.4 消融实验

消融链条：

1. U-Net：传统 CNN baseline；
2. U-KAN(no-KAN)：相同 U-KAN 框架下替换 KAN 为 MLP；
3. U-KAN：恢复 KANLinear；
4. Attention-U-KAN：在 U-KAN 上加入注意力。

写作重点：

- no-KAN 与 U-KAN 的比较最干净，因为两者主结构相同；
- U-Net 与 U-KAN 体现 CNN baseline 与 KAN-enhanced backbone 的差异；
- Attention-U-KAN 是本文改进尝试，但结果说明简单注意力不一定带来稳定收益。

## 5 讨论

建议分四点：

1. **KAN 模块有效性**：BUSI/CVC 上 U-KAN 均优于 no-KAN。
2. **注意力模块局限**：可能引入额外重标定导致小数据集过拟合，或注意力位置不够合适。
3. **随机种子与训练稳定性**：BUSI 曲线存在局部峰值，官方也提示种子影响大，因此需要补 seed。
4. **效率权衡**：U-KAN 参数量低于 U-Net，但推理时间明显更长，原因可能是 KANLinear 和 token flatten 操作较慢。

## 6 结论

结论写法：

- 本文完成了 U-KAN 医学图像分割算法复现；
- 在 BUSI 和 CVC 上，U-KAN 均取得当前实验矩阵最优 IoU/Dice；
- KAN 层相对 MLP 替代版本有明显收益；
- Attention-U-KAN 改进未稳定超过原始 U-KAN，说明改进方向仍需进一步优化；
- 本项目形成了可复现代码、README、数据处理、实验表格、训练曲线、可视化结果和补实验计划。

## 图表清单

| 编号 | 内容 | 文件或来源 | 图源写法 |
| --- | --- | --- | --- |
| 图 1 | U-KAN 总体结构图 | 待自绘 | 作者根据 U-KAN 论文与源码自行绘制 |
| 图 2 | Attention-U-KAN 注意力模块图 | 待自绘 | 作者自行绘制 |
| 图 3 | 数据预处理流程图 | 待自绘 | 作者根据本文实验流程自行绘制 |
| 图 4 | BUSI/CVC 数据样本 | `busi_samples.png`, `cvc_samples.png` | 本文代码生成 |
| 图 5 | 训练曲线 | `busi_training_curves.png`, `cvc_training_curves.png` | 本文代码生成 |
| 图 6 | 预测结果对比 | `busi_prediction_comparison.png`, `cvc_prediction_comparison.png` | 本文代码生成 |
| 图 7 | 代码运行截图 | 课程要求目录中的训练/评估截图 | 本文代码运行过程截图 |

| 编号 | 内容 | 来源 |
| --- | --- | --- |
| 表 1 | 数据集统计 | `experiments/results/*_dataset_stats.csv` |
| 表 2 | 实验环境 | `doctor_env.py` 输出 |
| 表 3 | 参数设置 | YAML 配置 |
| 表 4 | BUSI 结果 | `segmentation_results.csv` |
| 表 5 | CVC 结果 | `segmentation_results.csv` |
| 表 6 | 训练稳定性诊断 | `training_diagnostics.csv` |
| 表 7 | 补实验结果 | 待 seed 6142 / ft50 运行后补充 |
