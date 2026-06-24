# 参考文献真实性与引用闭环审计

审计日期：2026-06-22

## 审计结论

- 文末共 18 条参考文献，编号连续。
- 正文实际引用覆盖 `[1]` 至 `[18]`，不存在未引用条目或缺失条目。
- 9 条正式出版物已用 DOI/Crossref 元数据核对题名、作者、年份、卷期、页码或文章号。
- U-KAN、ResU-KAN、KC-UNet、TransUKAN、VMKLA-UNet 已与项目本地 PDF 首页或元数据交叉核对。
- KAN、Attention U-Net、TransUKAN 采用 arXiv 网络文献格式；官方代码、PyTorch 和 Albumentations 采用 `[EB/OL]` 格式并记录访问日期。

## 核验记录

| 编号 | 文献 | 核验依据 | 状态 |
|---|---|---|---|
| [1] | U-KAN | AAAI DOI `10.1609/aaai.v39i5.32491`；本地 PDF | 通过 |
| [2] | KAN | arXiv `2404.19756`，HTTP 200 | 通过 |
| [3] | U-Net | Springer DOI `10.1007/978-3-319-24574-4_28` | 通过 |
| [4] | CBAM | Springer DOI `10.1007/978-3-030-01234-2_1` | 通过 |
| [5] | Attention U-Net | arXiv `1804.03999`，HTTP 200 | 通过 |
| [6] | BUSI 数据集 | DOI `10.1016/j.dib.2019.104863` | 通过 |
| [7] | CVC-ClinicDB 基准 | DOI `10.1155/2017/4037190` | 通过 |
| [8] | U-KAN 官方代码 | GitHub 官方仓库，HTTP 200 | 通过 |
| [9] | PyTorch 文档 | 官方文档，HTTP 200 | 通过 |
| [10] | Albumentations 文档 | 官方文档，HTTP 200 | 通过 |
| [11] | ResU-KAN | DOI `10.1007/s10489-025-06467-5`；本地 PDF | 通过 |
| [12] | KC-UNet | DOI `10.1109/ACCESS.2025.3605148`；本地 PDF | 通过 |
| [13] | TransUKAN | arXiv `2409.14676`；本地 PDF；HTTP 200 | 通过 |
| [14] | VMKLA-UNet | DOI `10.1038/s41598-025-97397-2`；本地 PDF | 通过 |
| [15] | Dice/Jaccard 优化理论 | DOI `10.1109/TMI.2020.3002417` | 通过 |
| [16] | Tversky Loss | DOI `10.1007/978-3-319-67389-9_44` | 通过 |
| [17] | Boundary Loss | PMLR 102:285-296 官方页面 | 通过 |
| [18] | Focal Tversky Loss | DOI `10.1109/ISBI.2019.8759329` | 通过 |

## 正文引用位置

- `[1]-[3]`：选题、U-Net/KAN/U-KAN 原理与结构。
- `[4]-[5]`：CBAM 与 Attention Gate 改进依据。
- `[6]-[7]`：BUSI 与 CVC-ClinicDB 数据来源和数据特征。
- `[8]-[10]`：官方 U-KAN 工程、PyTorch 优化器/调度器和 Albumentations 增强实现。
- `[11]-[14]`：KAN 医学图像分割相关工作。
- `[15]`：Dice/Jaccard 指标关系与评价解释。
- `[16]-[18]`：失败分析和后续边界/类别不平衡损失设计。

