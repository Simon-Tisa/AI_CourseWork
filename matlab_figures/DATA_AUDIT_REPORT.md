# 数据完整性审计报告

## 审计范围

已检查以下数据链：

1. `paper/tables/segmentation_results.csv`
2. 11 个实验目录中的 `metrics.csv`
3. 11 个实验目录中的验证集预测 PNG
4. BUSI/CVC 固定验证 split
5. 全部处理后 mask
6. 训练日志、随机种子稳定性表和继续训练表

## 已确认结果

- `segmentation_results.csv` 与每个实验目录的 `metrics.csv` 完全一致，最大绝对差为 `0`。
- 所有实验的预测文件数量与对应验证 split 完全一致：
  - BUSI 每个 run：156 张。
  - CVC 每个 run：122 张。
- 数据集统计重新计算结果：
  - BUSI：780 张，平均 mask 占比 `0.0782656678353302`。
  - CVC-ClinicDB：612 张，平均 mask 占比 `0.0930012666235476`。
- CVC 的保存预测 mask 经 MATLAB 重新累计后与最终指标完全一致。
- BUSI 在 MATLAB 中模拟 OpenCV 最近邻缩放后，最大绝对指标差为
  `2.7804184669078e-06`，不会改变论文报告的四位小数。

## 微小差异原因

BUSI 原图和 mask 尺寸不统一，评估时由 Albumentations/OpenCV 缩放到
256×256。MATLAB 与 OpenCV 对最近邻缩放的像素边界索引实现存在微小差异，
会使少量边界像素移动。CVC 原始尺寸固定为 384×288，其缩放结果能够完全匹配。

因此：

- 论文主表继续以 `evaluate.py` 直接输出的 `metrics.csv` 为权威结果。
- MATLAB 主结果图直接读取这些权威 CSV，不重新改写数值。
- MATLAB 逐图失败分析采用与 OpenCV 接近的索引映射，BUSI 的误差低于
  `3e-6`，只用于分布、分层和错误类型分析，不替代主表指标。

## 结论

当前论文表格和 MATLAB 主结果图所使用的实验数据正确、一致、可追溯。
未发现模型名称错配、split 数量错误、预测文件缺失、汇总 CSV 手工录入错误
或补充实验均值计算错误。
