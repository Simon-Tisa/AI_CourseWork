# U-KAN Course Project

This repository reproduces Segmentation U-KAN for 2D medical image segmentation and adds a lightweight attention-enhanced U-KAN variant. The implementation covers dataset preparation, deterministic splits, model training, evaluation, result aggregation, and reproducible visualization scripts.

## Repository

```text
Repository: https://github.com/Simon-Tisa/AI_CourseWork/tree/course-paper-ukan
Project path: course-paper-ukan branch root
Branch: course-paper-ukan
```

Clone and enter the project folder:

```powershell
git clone https://github.com/Simon-Tisa/AI_CourseWork.git
cd AI_CourseWork
git checkout course-paper-ukan
```

## Environment

The preferred interpreter is:

```text
C:\ProgramData\Anaconda\envs\torch\python.exe
```

Run diagnostics:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\doctor_env.py
```

Install dependencies when required:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 -m pip install -r requirements.txt
```

Optional developer dependencies can be installed with:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 -m pip install -r requirements-optional.txt
```

`pytest` is only needed for automated tests. `matplotlib` improves figure rendering, but the project also includes lightweight fallbacks for basic visualization. `timm` and `medpy` are not required by this reimplemented training pipeline.

Main dependencies:

```text
torch
torchvision
opencv-python
albumentations
numpy
pandas
scikit-learn
PyYAML
Pillow
tensorboardX
```

## Data

Raw datasets are not committed to this repository. Download the public datasets manually and place them under `data/raw`. Processing scripts create standardized datasets under `data/processed`.

Recommended download pages:

```text
BUSI: https://www.kaggle.com/datasets/aryashah2k/breast-ultrasound-images-dataset
CVC-ClinicDB: https://www.kaggle.com/datasets/balraj98/cvcclinicdb
```

After downloading and unzipping, organize the raw files as follows. The BUSI folder should contain `Dataset_BUSI_with_GT`, and the CVC folder should contain the `PNG/Original` and `PNG/Ground Truth` subfolders.

Expected local layout:

```text
data/raw/busi/Dataset_BUSI_with_GT/...
data/raw/cvc/PNG/Original
data/raw/cvc/PNG/Ground Truth
```

Prepare datasets, deterministic splits, and dataset reports:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\prepare_busi.py --raw-dir data\raw\busi --out-dir data\processed
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\prepare_cvc.py --raw-dir data\raw\cvc --out-dir data\processed
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\make_splits.py --dataset busi --seed 2981
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\make_splits.py --dataset cvc --seed 2981
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\dataset_report.py --dataset busi
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\dataset_report.py --dataset cvc
```

## Reproducibility

The project uses deterministic split files under `data/splits`. Main experiments use seed `2981`, and supplemental BUSI stability checks use seed `6142`.

Run a one-batch smoke test before full training:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\train.py --config configs\busi_ukan.yaml --epochs 1 --limit-train-batches 1 --limit-val-batches 1 --output-dir experiments\smoke --run-name smoke_busi_ukan_seed2981 --overwrite
```

Training starts from scratch. If an experiment directory already contains `log.csv`, use `--overwrite` intentionally or choose another `--run-name`/`--output-dir`.

Run the main experiment matrix:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\train.py --config configs\busi_unet.yaml
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\train.py --config configs\busi_no_kan.yaml
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\train.py --config configs\busi_ukan.yaml
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\train.py --config configs\busi_attention_ukan.yaml
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\train.py --config configs\cvc_unet.yaml
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\train.py --config configs\cvc_no_kan.yaml
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\train.py --config configs\cvc_ukan.yaml
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\train.py --config configs\cvc_attention_ukan.yaml
```

Evaluate trained checkpoints:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\evaluate.py --name busi_unet_seed2981
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\evaluate.py --name busi_no_kan_seed2981
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\evaluate.py --name busi_ukan_seed2981
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\evaluate.py --name busi_attention_ukan_seed2981
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\evaluate.py --name cvc_unet_seed2981
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\evaluate.py --name cvc_no_kan_seed2981
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\evaluate.py --name cvc_ukan_seed2981
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\evaluate.py --name cvc_attention_ukan_seed2981
```

Aggregate results and generate prediction figures:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\plot_training_curves.py --names busi_unet_seed2981 busi_no_kan_seed2981 busi_ukan_seed2981 busi_attention_ukan_seed2981 --out experiments\figures\busi_training_curves.png
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\plot_training_curves.py --names cvc_unet_seed2981 cvc_no_kan_seed2981 cvc_ukan_seed2981 cvc_attention_ukan_seed2981 --out experiments\figures\cvc_training_curves.png
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\visualize_predictions.py --dataset busi --ukan-name busi_ukan_seed2981 --attention-name busi_attention_ukan_seed2981 --output-path experiments\figures\busi_prediction_comparison.png
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\visualize_predictions.py --dataset cvc --ukan-name cvc_ukan_seed2981 --attention-name cvc_attention_ukan_seed2981 --output-path experiments\figures\cvc_prediction_comparison.png
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\summarize_results.py
```

Expected outputs:

```text
experiments/results/<run_name>/metrics.csv       Evaluation metrics for one run.
experiments/results/<run_name>/predictions/      Saved binary prediction masks.
experiments/results/<run_name>/log.csv           Epoch-level training log.
experiments/results/<run_name>/model.pth         Best validation checkpoint.
experiments/tables/segmentation_results.csv      Aggregated metrics table.
experiments/tables/training_diagnostics.csv      Training-curve diagnostics.
experiments/figures/*.png                        Python-generated figures.
matlab_figures/output/*.png                      MATLAB-generated figures.
```

Optional MATLAB visualizations and data checks:

```powershell
matlab -batch "cd('matlab_figures'); run_all_figures; audit_all_data"
```

## Project Structure

```text
configs/         YAML experiment configuration files.
data/            Raw, processed, and split-list data folders.
scripts/         Data preparation, training, evaluation, and result commands.
src/             Reimplemented U-KAN, Attention-U-KAN, datasets, losses, and metrics.
tests/           Unit and smoke tests.
experiments/     Metrics, prediction masks, logs, checkpoints, and generated figures.
matlab_figures/  MATLAB scripts for data-driven result visualizations.
```

## Module Overview

```text
src/ukan_course/datasets/segmentation_dataset.py
    Loads processed images and masks, applies Albumentations transforms, and returns tensors.

src/ukan_course/models/unet.py
    Implements the CNN baseline used for comparison.

src/ukan_course/models/kan.py
    Implements the KAN-style processing blocks used by U-KAN.

src/ukan_course/models/ukan.py
    Implements the reproduced U-KAN segmentation model and no-KAN ablation variant.

src/ukan_course/models/attention.py
    Implements lightweight channel-spatial attention.

src/ukan_course/models/attention_ukan.py
    Inserts attention modules into U-KAN skip-fusion locations.

src/ukan_course/losses.py
    Defines the BCE + Dice segmentation loss.

src/ukan_course/metrics.py
    Computes IoU, Dice, precision, recall, and specificity.

src/ukan_course/utils.py
    Provides seed control, configuration loading, and common helpers.
```

Key command scripts:

```text
prepare_busi.py / prepare_cvc.py    Convert raw public datasets into a unified layout.
make_splits.py                      Generate deterministic train/validation split files.
train.py                            Train one configured model and save logs/checkpoints.
evaluate.py                         Evaluate a saved checkpoint and export predictions.
summarize_results.py                Aggregate per-run metrics into one CSV table.
analyze_training_logs.py            Summarize convergence and best-epoch diagnostics.
plot_training_curves.py             Draw training curves from log.csv files.
visualize_predictions.py            Create qualitative prediction comparison figures.
```

## Tests

Run lightweight tests after installing optional dependencies:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 -m pytest tests
```

The tests cover dataset loading, model forward passes, metric calculations, and data-preparation utilities. The training script also supports a one-batch smoke test before long experiments.

## Source Attribution

The model implementation is based on the official U-KAN segmentation project and rewritten for this course project. Dataset preparation, training, evaluation, result aggregation, and visualization scripts are included so that experiments can be reproduced from the public datasets and saved configuration files.
