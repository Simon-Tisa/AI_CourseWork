# 最终质量复核记录

复核日期：2026-06-08

## 复核目标

本记录用于检查重写版课程论文是否真正满足最初目标：方向（一）算法复现、KAN/U-KAN 医学图像分割、完整工程代码、充分实验、论文式图表组织、课程加分项覆盖，以及对异常结果的独立思考。

## 论文内容复核

| 项目 | 结论 |
| --- | --- |
| 选题是否一致 | 已统一为 KAN / U-KAN，不再使用 kNN / UKNN |
| 是否是算法复现 | 是，复现 U-KAN，并包含 U-Net、no-KAN、Attention-U-KAN 对照 |
| 是否有论文来源说明 | 有，正文开头说明论文、源码、数据集、LLM 辅助和图源 |
| 是否参考相关论文组织实验 | 有，第 2 章总结 U-KAN、ResU-KAN、KC-UNet、TransUKAN、VMKLA-UNet 等论文实验结构 |
| 是否包含实验思考过程 | 有，第 6 章写明 BUSI no-KAN 跳变怀疑、seed 6142 验证、CVC 继续训练验证 |
| 是否避免过度包装 | 有，明确写出 Attention-U-KAN 未超过原始 U-KAN，是负结果和局限 |
| 是否包含效率权衡 | 有，表 10 比较参数量、推理时间、IoU 和 Dice |
| 是否有错误案例分析 | 有，图 14 和第 6.5 节分析漏分割、过分割和边界偏差 |

## 图表复核

最终重写版包含：

- 14 张图：相关论文综述表截图、KAN/MLP 图、U-KAN 官方框架图、Attention 模块图、数据样本、实验流程图、训练曲线、预测对比图、主结果图、诊断流程图、补实验图、错误案例图。
- 11 张表：相关论文组织方式、数据统计、实验环境、BUSI/CVC 主结果、消融、seed 稳定性、CVC 继续训练、官方对照、效率、加分项落实。

图源已在正文中逐图说明，包括作者自绘、作者 PPT 手绘、官方项目、本地实验脚本生成和本地课程论文材料。

## 工程复核

| 项目 | 状态 |
| --- | --- |
| 环境诊断脚本 | `scripts/doctor_env.py` |
| 数据处理脚本 | `prepare_busi.py`, `prepare_cvc.py`, `make_splits.py`, `dataset_report.py` |
| 训练脚本 | `scripts/train.py` |
| 评估脚本 | `scripts/evaluate.py` |
| 绘图脚本 | `plot_training_curves.py`, `visualize_predictions.py`, `build_course_paper_v2.py` |
| 模型代码 | `src/ukan_course/models/` |
| 测试代码 | `tests/` |
| README | 已包含复现实验命令和项目结构 |

## 验证证据

- 重写版生成命令已成功运行：

```powershell
& 'C:\Users\蔡雪峰\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\scripts\build_course_paper_v2.py
```

- 编译检查通过：

```powershell
python -m py_compile .\scripts\build_course_paper_v2.py
```

- DOCX 结构解析结果：

```text
paragraphs=108
tables=11
images=14
chinese_chars≈3714
headings=16
```

- 页面渲染尝试结果：`render_docx.py` 因本机缺少 DOCX 转 PDF/PNG 外部程序失败，错误为 `WinError 2`。这不是论文文件损坏；DOCX 可被 `python-docx` 正常解析。

## 当前风险

1. GitHub 推送尚未完成：本地分支领先远程若干提交，当前受限进程无法读取 Windows/GitHub 凭据。
2. 若提交前需要最终页面视觉检查，建议在本机 Word 中打开重写版 DOCX 快速翻页检查分页；当前已完成结构检查和关键图片视觉抽查。

## 结论

从课程要求、实验完整性、加分项覆盖、工程可复现性和论文表达质量看，重写版已经明显优于早期草稿。它不仅报告结果，也保留了从异常训练曲线到补充实验验证的思考链条，能体现独立分析和额外实践投入。
