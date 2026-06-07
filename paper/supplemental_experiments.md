# 补充实验计划

## 发现的问题

1. BUSI 训练曲线中 U-KAN(no-KAN) 在个别 epoch 出现较明显的验证 IoU 跃升。由于 BUSI 验证集规模较小，且目标区域面积占比较低，单个 epoch 的阈值化分割结果可能造成较大波动。
2. 原训练日志曾使用 batch 平均 IoU 记录验证指标，而 `evaluate.py` 使用全验证集像素级混淆矩阵聚合 IoU。两者口径不同，可能导致训练曲线 best epoch 与最终评估值不完全一致。后续补实验已改为全验证集聚合指标。
3. CVC 四个模型的 best epoch 普遍靠后，说明 100 epoch 可能仍处于缓慢提升区间，存在训练轮数不足的可能。
4. Attention-U-KAN 在 BUSI 和 CVC 上均未超过原始 U-KAN，说明简单通道-空间注意力不是稳定增益，需要在论文中作为改进尝试和局限讨论。

## 已有曲线诊断

可用以下命令重新生成诊断表：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\analyze_training_logs.py
```

当前 `paper/tables/training_diagnostics.csv` 中最关键的观察如下：

| 实验 | best epoch | 日志 best IoU | 最终 epoch IoU | 最大正跳变 | 后 10 epoch 变化 | 最终评估 IoU |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| BUSI U-Net | 96 | 0.6264 | 0.6185 | 0.1012 | +0.0223 | 0.6369 |
| BUSI U-KAN(no-KAN) | 72 | 0.6793 | 0.6353 | 0.1079 | +0.0265 | 0.6486 |
| BUSI U-KAN | 77 | 0.6581 | 0.6519 | 0.0972 | -0.0029 | 0.6874 |
| BUSI Attention-U-KAN | 89 | 0.6486 | 0.6367 | 0.2092 | -0.0073 | 0.6769 |
| CVC U-Net | 99 | 0.7832 | 0.7832 | 0.1093 | +0.0150 | 0.7803 |
| CVC U-KAN(no-KAN) | 85 | 0.7746 | 0.7648 | 0.1317 | +0.0027 | 0.7699 |
| CVC U-KAN | 86 | 0.7893 | 0.7816 | 0.1344 | +0.0006 | 0.7874 |
| CVC Attention-U-KAN | 98 | 0.7784 | 0.7648 | 0.1420 | +0.0024 | 0.7631 |

结论：BUSI no-KAN 的 72 epoch 是局部峰值，确实需要用多 seed 复核。CVC 中 U-Net 最像训练不足，U-KAN 和 no-KAN 后段更接近平台期，但继续训练主模型可以作为收敛性补充证据。

## 补实验 A：BUSI 随机种子稳定性

目的：验证 U-KAN(no-KAN) 的高点是否来自单一随机种子/划分偶然性。

新增配置：

- `configs/busi_no_kan_seed6142.yaml`
- `configs/busi_ukan_seed6142.yaml`

运行命令：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\train.py --config configs\busi_no_kan_seed6142.yaml --overwrite
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\train.py --config configs\busi_ukan_seed6142.yaml --overwrite
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\evaluate.py --name busi_no_kan_seed6142
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\evaluate.py --name busi_ukan_seed6142
```

论文使用方式：若 seed 6142 下 U-KAN 仍高于 no-KAN，则可说明 KAN 模块收益更稳定；若两者接近或反转，则应以“单 seed 结果存在波动，后续需多 seed 平均”为讨论点。

## 补实验 B：CVC 继续训练

目的：验证 CVC 100 epoch 是否未充分收敛。

建议先只对 CVC U-KAN 做继续训练，因为它是主复现模型。使用已有 best checkpoint 初始化，降低学习率继续训练 50 epoch：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\train.py --config configs\cvc_ukan.yaml --run-name cvc_ukan_seed2981_ft50 --epochs 50 --lr 0.00005 --kan-lr 0.0005 --min-lr 0.000001 --resume-from experiments\results\cvc_ukan_seed2981\model.pth --overwrite
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\evaluate.py --name cvc_ukan_seed2981_ft50
```

论文使用方式：如果继续训练显著提升，则说明 CVC 原实验可能训练不足；如果提升有限，则说明 100 epoch 已基本达到平台期。
