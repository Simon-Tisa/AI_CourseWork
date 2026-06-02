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

## Data

Place raw public datasets under `data/raw`. Processing scripts will create standardized datasets under `data/processed`.

## Reproducibility

The project uses deterministic splits with U-KAN seeds `2981`, `6142`, and `1187`.
