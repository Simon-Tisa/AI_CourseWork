# 最终质量复核记录

复核日期：2026-06-22

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

最终版包含：

- 24 张图：经典论文结构图、作者自绘原理与流程图、MATLAB 数据统计、训练曲线、预测对比、失败案例、逐图与面积分层、FP/FN 构成、补充实验、效率权衡、工程证据链、真实终端截图和 Git 记录。
- 20 张表：研究问题、数据统计、预处理、环境、模型矩阵、训练参数、BUSI/CVC 主结果、消融、seed 稳定性、继续训练、官方对照、效率和加分项落实等。

图源已在正文中逐图说明，包括作者自绘、作者 PPT 手绘、官方项目、本地实验脚本生成和本地课程论文材料。

## 工程复核

| 项目 | 状态 |
| --- | --- |
| 环境诊断脚本 | `scripts/doctor_env.py` |
| 数据处理脚本 | `prepare_busi.py`, `prepare_cvc.py`, `make_splits.py`, `dataset_report.py` |
| 训练脚本 | `scripts/train.py` |
| 评估脚本 | `scripts/evaluate.py` |
| 绘图脚本 | `matlab_figures/fig01_*.m` 至 `fig15_*.m`，统一入口 `run_all_figures.m` |
| 模型代码 | `src/ukan_course/models/` |
| 测试代码 | `tests/` |
| README | 已包含复现实验命令和项目结构 |

## 验证证据

- 重写版生成命令已成功运行：

```powershell
& 'C:\Users\蔡雪峰\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\scripts\build_final_course_paper.py
```

- 编译检查通过：

```powershell
python -m py_compile .\scripts\build_final_course_paper.py .\scripts\qa_final_docx.py .\scripts\audit_citations.py
```

- DOCX 结构解析结果：

```text
paragraphs=287
tables=20
images=24
chinese_chars_before_references=16778
headings=58
```

- 页面渲染尝试结果：`render_docx.py` 因本机缺少 DOCX 转 PDF/PNG 外部程序失败，错误为 `WinError 2`。这不是论文文件损坏；DOCX 可被 `python-docx` 正常解析。

## 当前风险

1. GitHub remote 已正确指向 `https://github.com/Simon-Tisa/AI_CourseWork.git`，最终提交前仍需确认最新未提交文件已经 commit 并 push。
2. 页面级自动渲染仍受本机缺少 LibreOffice/soffice 限制；已完成 DOCX 压缩包、结构、图号、图片嵌入、替代文本、引用闭环和关键图片视觉检查。

## 结论

从课程要求、实验完整性、加分项覆盖、工程可复现性和论文表达质量看，最终版已形成完整证据链。它不仅报告结果，也保留了从异常训练曲线到补充实验验证的思考过程，并通过 MATLAB 数据审计、参考文献真实性核验和正文引用闭环增强了可复核性。
