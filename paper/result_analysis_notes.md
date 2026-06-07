# 实验结果分析笔记

本文档用于把当前实验结果转化为论文中可用的分析观点。它不是最终正文，但可直接改写进“实验结果与分析”和“讨论”章节。

## 1. 当前主实验结果

| 数据集 | 模型 | IoU | Dice | Precision | Recall | Specificity | 参数量 | 单图推理时间 ms |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| BUSI | U-Net | 0.6369 | 0.7782 | 0.8308 | 0.7319 | 0.9867 | 7.76M | 3.60 |
| BUSI | U-KAN(no-KAN) | 0.6486 | 0.7869 | 0.8459 | 0.7356 | 0.9880 | 2.76M | 35.22 |
| BUSI | U-KAN | 0.6874 | 0.8147 | 0.8177 | 0.8118 | 0.9838 | 6.36M | 37.15 |
| BUSI | Attention-U-KAN | 0.6769 | 0.8074 | 0.8075 | 0.8072 | 0.9828 | 6.36M | 40.69 |
| CVC | U-Net | 0.7803 | 0.8766 | 0.9248 | 0.8332 | 0.9929 | 7.76M | 3.72 |
| CVC | U-KAN(no-KAN) | 0.7699 | 0.8700 | 0.9048 | 0.8378 | 0.9907 | 2.76M | 43.46 |
| CVC | U-KAN | 0.7874 | 0.8810 | 0.9140 | 0.8503 | 0.9916 | 6.36M | 45.90 |
| CVC | Attention-U-KAN | 0.7631 | 0.8656 | 0.9207 | 0.8168 | 0.9926 | 6.36M | 44.02 |

## 2. 可写入论文的主要观察

### 2.1 U-KAN 相对 no-KAN 的收益

在 BUSI 上，U-KAN 相比 no-KAN：

- IoU 提升 0.0388；
- Dice 提升 0.0279；
- Recall 从 0.7356 提升到 0.8118。

在 CVC 上，U-KAN 相比 no-KAN：

- IoU 提升 0.0175；
- Dice 提升 0.0111；
- Recall 从 0.8378 提升到 0.8503。

这说明在相同 U-KAN 主体框架中，将 MLP 替换为 KANLinear 后，模型对病灶区域的召回能力和整体重叠指标均有提升。论文中应重点强调 no-KAN 与 U-KAN 的对比最能说明 KAN 模块本身的作用，因为两者结构差异最小。

### 2.2 U-KAN 相对 U-Net 的收益与代价

BUSI 上 U-KAN 比 U-Net IoU 提升 0.0504，Dice 提升 0.0365。CVC 上 U-KAN 比 U-Net IoU 提升 0.0070，Dice 提升 0.0044。说明 U-KAN 在复杂乳腺超声病灶分割中收益更明显，在 CVC 上收益较小但仍为最高。

代价是推理时间明显增加。U-Net 单图推理约 3.6-3.7 ms，而 U-KAN 系列约 37-46 ms。论文中不能只写精度，也要写效率权衡：KANLinear 的 B-spline 基函数计算、token 展平和逐 token 操作会带来额外推理开销。

### 2.3 Attention-U-KAN 的负面结果

Attention-U-KAN 在两个数据集上均未超过原始 U-KAN：

- BUSI：IoU 0.6769，低于 U-KAN 的 0.6874；
- CVC：IoU 0.7631，低于 U-KAN 的 0.7874。

这可以写成一个有价值的消融结论：简单地在 skip fusion 后加入通道-空间注意力并不一定提升 U-KAN。可能原因包括：

1. BUSI/CVC 数据规模有限，注意力模块带来的额外参数可能增加过拟合风险。
2. 通道-空间注意力可能过度抑制弱边界或小目标区域。
3. 注意力插入位置可能不够合适，未来可尝试只在高层语义特征处加入，或结合边界损失、多尺度注意力。
4. U-KAN 本身已经通过 tokenized KAN block 提升了中高层非线性表征，简单注意力的边际收益有限。

论文中应避免把 Attention-U-KAN 写成“显著提升”，而应写成“本文尝试的一种改进方向，实验显示其效果不如原始 U-KAN，提示后续改进需要更精细设计”。

## 3. 训练曲线与稳定性

### 3.1 BUSI no-KAN 局部峰值

BUSI no-KAN 在日志中的最佳 epoch 为 72，日志 best IoU 为 0.6793。但其最终 epoch IoU 为 0.6353，最终 `evaluate.py` 指标为 0.6486。epoch 72 附近的 IoU 确实像局部峰值。

可能解释：

1. BUSI 验证集只有 156 张图，且 mask 平均面积占比约 7.83%，阈值化分割对少量样本较敏感。
2. 旧训练日志曾使用 batch 平均指标，而最终评估使用全验证集像素级混淆矩阵汇总，两者口径不完全一致。
3. 官方 U-KAN README 明确提示随机种子对评价指标影响很大，并建议使用 2981、6142、1187 三个 seed 的平均结果。

因此论文中不应把 no-KAN 的某个曲线峰值作为强结论，应补 seed 6142 并报告平均或至少讨论稳定性。

### 3.2 CVC 收敛性

CVC 训练诊断表显示：

- U-Net best epoch = 99，后 10 epoch IoU 仍提升 0.0150，较可能训练不足；
- U-KAN best epoch = 86，后 10 epoch 仅提升 0.0006，基本接近平台；
- no-KAN best epoch = 85，后 10 epoch 提升 0.0027；
- Attention-U-KAN best epoch = 98，后 10 epoch 提升 0.0024。

因此，“CVC 四个模型都没有收敛”这个判断需要修正为：

> CVC 的 U-Net 和 Attention-U-KAN best epoch 靠近训练末端，可能仍有继续训练空间；U-KAN 和 no-KAN 的后段变化较小，更接近平台期。为稳妥起见，本文对主复现模型 U-KAN 进行继续训练补实验，以判断 100 epoch 是否足够。

## 4. 与 U-KAN 官方结果的关系

官方 README 中的 Seg U-KAN 单 run checkpoint 表显示：

- BUSI U-KAN：IoU 65.26，F1 78.75；
- BUSI no-KAN：IoU 63.49，F1 77.07；
- CVC U-KAN：IoU 85.61，F1 92.19。

我们的 BUSI U-KAN IoU 0.6874、Dice 0.8147，高于官方 README 中 BUSI 单 run checkpoint 数值，说明 BUSI 复现结果是合理且较好的。

我们的 CVC U-KAN IoU 0.7874、Dice 0.8810，低于官方 README 中 CVC checkpoint 数值。可能原因包括：

1. 官方训练通常推荐 400 epoch，而我们当前主实验为 100 epoch；
2. 预处理、数据版本、split 和随机种子可能不同；
3. 官方结果可能来自多 seed 或特定 checkpoint，而本文当前结果来自本地单 seed 验证；
4. 本项目使用更轻量、课程化的工程重写，并未直接使用官方预训练权重。

论文中建议写成：

> 本文实验并非直接复用官方 checkpoint，而是在本地环境中重构训练流程并从头训练。BUSI 结果达到并超过官方单 run 参考值；CVC 结果低于官方参考，可能与训练轮数和数据划分有关，因此本文加入继续训练实验作为补充分析。

## 5. 推荐补实验

### 5.1 BUSI seed 6142 稳定性实验

目标：验证 U-KAN 相对 no-KAN 的收益是否稳定，而不是 seed 2981 的偶然结果。

命令：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\train.py --config configs\busi_no_kan_seed6142.yaml --overwrite
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\train.py --config configs\busi_ukan_seed6142.yaml --overwrite
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\evaluate.py --name busi_no_kan_seed6142
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\evaluate.py --name busi_ukan_seed6142
```

### 5.2 CVC U-KAN 继续训练

目标：验证 CVC 100 epoch 是否不足。

命令：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\train.py --config configs\cvc_ukan.yaml --run-name cvc_ukan_seed2981_ft50 --epochs 50 --lr 0.00005 --kan-lr 0.0005 --min-lr 0.000001 --resume-from experiments\results\cvc_ukan_seed2981\model.pth --overwrite
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\evaluate.py --name cvc_ukan_seed2981_ft50
```

如果时间允许，可以再补一个 CVC U-Net 继续训练，因为 CVC U-Net 的 best epoch 是 99，最像训练不足。

## 6. 论文表述策略

建议采用“诚实但有说服力”的写法：

1. 主线结论聚焦 U-KAN 复现成功：两个数据集上 U-KAN 都是当前实验矩阵最佳。
2. 改进模型不强行包装：Attention-U-KAN 是合理尝试，但结果提示简单注意力不稳定。
3. 把异常曲线变成独立思考：通过训练诊断表和补 seed 计划说明我们不是盲目相信单次结果。
4. 把 CVC 差距变成局限讨论：说明 100 epoch 和课程资源限制，并用继续训练补实验增强可信度。
5. 把 GitHub、README、数据整理、过程截图、自绘图作为课程加分项明确展示。
