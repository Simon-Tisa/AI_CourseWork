# MATLAB Result Visualization Scripts

This folder contains MATLAB scripts for regenerating data-driven result figures from the experiment outputs. Generated PNG/PDF files are written to `matlab_figures/output/`, which is ignored by Git.

## Scripts

- `fig01_dataset_samples.m`: BUSI/CVC image and mask examples.
- `fig02_mask_ratio_distribution.m`: foreground mask-ratio distribution.
- `fig03_main_results.m`: main IoU/Dice comparison.
- `fig04_busi_training_curves.m`: BUSI training curves.
- `fig05_cvc_training_curves.m`: CVC training curves.
- `fig06_busi_prediction_comparison.m`: BUSI prediction comparison.
- `fig07_cvc_prediction_comparison.m`: CVC prediction comparison.
- `fig08_error_cases.m`: representative U-KAN error cases.
- `fig09_supplemental_experiments.m`: seed-stability and continued-training checks.
- `fig10_efficiency_tradeoff.m`: accuracy, inference time, and parameter tradeoff.
- `fig11_metric_heatmap.m`: metric heatmap.
- `fig12_failure_distribution_size.m`: per-image Dice distribution and lesion-size grouping.
- `fig13_error_composition.m`: false-positive and false-negative error composition.
- `audit_all_data.m`: consistency checks for result CSV files, masks, predictions, and split files.
- `run_all_figures.m`: runs the visualization scripts in sequence.

## Usage

Run from the project root:

```powershell
matlab -batch "cd('matlab_figures'); run_all_figures; audit_all_data"
```

The scripts read from:

- `experiments/tables/*.csv`
- `experiments/results/*/log.csv`
- `experiments/results/*/predictions/*.png`
- `data/processed/*/images`
- `data/processed/*/masks/0`
- `data/splits/*_val.txt`

All plotted values are loaded from local experiment artifacts rather than typed manually into the MATLAB scripts.
