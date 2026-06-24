# MATLAB 数据图生成说明

本目录用于生成课程论文中所有由实验数据、数据集样本或模型预测驱动的图片。

## 目录

- `fig01_dataset_samples.m`：BUSI/CVC 原图、真值和叠加图
- `fig02_mask_ratio_distribution.m`：全数据集 mask 前景占比分布
- `fig03_main_results.m`：两数据集主实验 IoU/Dice 对比
- `fig04_busi_training_curves.m`：BUSI 四模型训练曲线
- `fig05_cvc_training_curves.m`：CVC 四模型训练曲线
- `fig06_busi_prediction_comparison.m`：BUSI 预测对比
- `fig07_cvc_prediction_comparison.m`：CVC 预测对比
- `fig08_error_cases.m`：U-KAN 典型错误案例
- `fig09_supplemental_experiments.m`：随机种子与继续训练补充实验
- `fig10_efficiency_tradeoff.m`：精度、推理时间与参数量权衡
- `fig11_metric_heatmap.m`：完整评价指标热力图
- `fig12_failure_distribution_size.m`：逐图 Dice 分布与病灶面积分层
- `fig13_error_composition.m`：过分割/漏分割误差构成
- `fig14_runtime_evidence.m`：命令、产物与结果的工程证据链
- `fig15_runtime_screenshots.m`：真实训练与评估终端截图排版
- `audit_all_data.m`：预测 mask、汇总 CSV、日志和补实验数据完整性审计
- `run_all_figures.m`：依次运行上述脚本
- `output/`：MATLAB 实际导出的 PNG、PDF 和审计 CSV

## 运行

在 MATLAB 中将当前目录切换到本目录，然后运行：

```matlab
run_all_figures
audit_all_data
```

每张图片同时输出 300 DPI PNG 和矢量 PDF。脚本不会修改论文 Word 文件，也不会覆盖原有 Python/Pillow 图。

## 数据来源

脚本直接读取：

- `paper/tables/*.csv`
- `experiments/results/*/log.csv`
- `experiments/results/*/predictions/*.png`
- `data/processed/*/images`
- `data/processed/*/masks/0`
- `data/splits/*_val.txt`

所有实验数值均来自现有项目文件，不在 MATLAB 脚本中手工重写。
