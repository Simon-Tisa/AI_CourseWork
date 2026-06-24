# MATLAB 图表审计清单

## 论文现有数据类图片

| 论文当前图号 | 内容 | MATLAB 源码 | MATLAB 输出 |
|---|---|---|---|
| 图 6 | BUSI 与 CVC 样本及专家轮廓 | `fig01_dataset_samples.m` | `output/fig01_dataset_samples_matlab.png` |
| 图 7 | mask 前景占比分布 | `fig02_mask_ratio_distribution.m` | `output/fig02_mask_ratio_distribution_matlab.png` |
| 图 9 | 主实验 IoU/Dice 对比 | `fig03_main_results.m` | `output/fig03_main_results_matlab.png` |
| 图 11 | BUSI 四模型训练曲线 | `fig04_busi_training_curves.m` | `output/fig04_busi_training_curves_matlab.png` |
| 图 12 | CVC 四模型训练曲线 | `fig05_cvc_training_curves.m` | `output/fig05_cvc_training_curves_matlab.png` |
| 图 14 | BUSI 预测结果对比 | `fig06_busi_prediction_comparison.m` | `output/fig06_busi_prediction_comparison_matlab.png` |
| 图 15 | CVC 预测结果对比 | `fig07_cvc_prediction_comparison.m` | `output/fig07_cvc_prediction_comparison_matlab.png` |
| 图 16 | U-KAN 典型过分割与漏分割案例 | `fig08_error_cases.m` | `output/fig08_error_cases_matlab.png` |
| 图 20 | seed 稳定性与继续训练 | `fig09_supplemental_experiments.m` | `output/fig09_supplemental_experiments_matlab.png` |

每张图片还输出同名矢量 PDF。错误案例脚本会重新计算全部验证样本的逐图 Dice，并将自动选中的样本写入 `output/fig08_error_cases_selected.csv`。mask 分布统计写入 `output/fig02_mask_ratio_statistics.csv`。

## 已纳入论文的扩展图

| 编号 | 内容 | MATLAB 源码 | MATLAB 输出 |
|---|---|---|---|
| 图 21 | IoU、推理时间和参数量权衡 | `fig10_efficiency_tradeoff.m` | `output/fig10_efficiency_tradeoff_matlab.png` |
| 图 10 | IoU、Dice、Precision、Recall、Specificity 热力图 | `fig11_metric_heatmap.m` | `output/fig11_metric_heatmap_matlab.png` |
| 图 17 | 逐图 Dice 分布与病灶面积分层 | `fig12_failure_distribution_size.m` | `output/fig12_failure_distribution_size_matlab.png` |
| 图 18 | FP/FN 误差构成与逐图平衡 | `fig13_error_composition.m` | `output/fig13_error_composition_matlab.png` |
| 图 22 | 命令、实验产物与论文结果证据链 | `fig14_runtime_evidence.m` | `output/fig14_runtime_evidence_matlab.png` |
| 图 23 | 真实训练、评估与预测生成截图 | `fig15_runtime_screenshots.m` | `output/fig15_runtime_screenshots_matlab.png` |

## 数据完整性审计

运行 `audit_all_data.m` 后将生成：

- `output/data_integrity_audit.csv`
- `output/data_integrity_audit.txt`

审计重新读取全部验证集真值与预测 mask，累计 TP、FP、FN、TN，并核对：

- `segmentation_results.csv`
- 每个实验目录的 `metrics.csv`
- 验证 split 与预测文件数量
- BUSI/CVC mask 数量和平均前景占比
- seed 均值表、继续训练表和训练日志完整性

## 不属于数据统计图的论文图片

以下图片不依赖实验数据，不在本轮 MATLAB 重绘范围内：

- 图 1、图 3、图 4、图 19：从原论文提取的经典结构或激活示例
- 图 2、图 5、图 8、图 13：作者自绘的原理、改进结构与流程图
- 图 24：Git 分支与提交记录

这些图片分别属于算法结构图、逻辑流程图或工程证据截图，不应伪装成统计图。
