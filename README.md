# U-KAN Course Paper Project

This repository reproduces Segmentation U-KAN for 2D medical image segmentation and adds a lightweight attention-enhanced U-KAN variant for the Artificial Intelligence course paper.

## Environment

The preferred interpreter is:

```text
C:\ProgramData\Anaconda\envs\torch\python.exe
```

Run diagnostics:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\doctor_env.py
```

If required modules are missing, install:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 -m pip install -r requirements.txt
```

Optional developer/reporting helpers can be installed with:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 -m pip install -r requirements-optional.txt
```

`pytest` is only needed for automated tests. `matplotlib` improves figure rendering, but the reporting scripts include a Pillow fallback. `timm` and `medpy` are not required by this reimplemented training pipeline.

## Data

Place raw public datasets under `data/raw`. Processing scripts will create standardized datasets under `data/processed`.

Expected local layout:

```text
data/raw/busi/Dataset_BUSI_with_GT/...
data/raw/cvc/PNG/Original
data/raw/cvc/PNG/Ground Truth
```

Prepare data, deterministic splits, and dataset figures:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\prepare_busi.py --raw-dir data\raw\busi --out-dir data\processed
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\prepare_cvc.py --raw-dir data\raw\cvc --out-dir data\processed
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\make_splits.py --dataset busi --seed 2981
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\make_splits.py --dataset cvc --seed 2981
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\dataset_report.py --dataset busi
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\dataset_report.py --dataset cvc
```

## Reproducibility

The project uses deterministic splits with U-KAN seeds `2981`, `6142`, and `1187`.

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
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\evaluate.py --name cvc_ukan_seed2981
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\evaluate.py --name cvc_attention_ukan_seed2981
```

Generate paper-ready tables and prediction figures:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\plot_training_curves.py --names busi_unet_seed2981 busi_no_kan_seed2981 busi_ukan_seed2981 busi_attention_ukan_seed2981 --out experiments\figures\busi_training_curves.png
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\plot_training_curves.py --names cvc_unet_seed2981 cvc_ukan_seed2981 cvc_attention_ukan_seed2981 --out experiments\figures\cvc_training_curves.png
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\visualize_predictions.py --dataset busi --ukan-name busi_ukan_seed2981 --attention-name busi_attention_ukan_seed2981 --out experiments\figures\busi_prediction_comparison.png
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\visualize_predictions.py --dataset cvc --ukan-name cvc_ukan_seed2981 --attention-name cvc_attention_ukan_seed2981 --out experiments\figures\cvc_prediction_comparison.png
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_python.ps1 .\scripts\summarize_results.py
```

## Project Structure

```text
configs/      Experiment configuration files.
data/         Raw, processed, and split-list data folders.
scripts/      Data preparation, training, evaluation, and reporting commands.
src/          Reimplemented U-KAN, Attention-U-KAN, datasets, losses, and metrics.
tests/        Unit and smoke tests.
experiments/  Logs, metrics, prediction masks, and generated figures.
paper/        Course-paper figures, tables, and draft materials.
```

## Source Attribution

Model implementation is based on the official U-KAN segmentation code and rewritten for this course project. Figures generated by scripts in this repository are treated as self-generated experimental figures and must be labeled accordingly in the paper.
