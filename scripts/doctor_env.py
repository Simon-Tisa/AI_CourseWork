from __future__ import annotations

import importlib.util
import platform
import sys


MODULES = [
    "torch",
    "torchvision",
    "cv2",
    "albumentations",
    "sklearn",
    "pandas",
    "yaml",
    "timm",
    "tensorboardX",
    "medpy",
    "pytest",
]


def module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def main() -> int:
    print(f"python_executable={sys.executable}")
    print(f"python_version={sys.version.split()[0]}")
    print(f"platform={platform.platform()}")
    for name in MODULES:
        print(f"module.{name}={module_available(name)}")

    if module_available("torch"):
        import torch

        print(f"torch_version={torch.__version__}")
        print(f"torch_cuda_available={torch.cuda.is_available()}")
        print(f"torch_cuda_version={torch.version.cuda}")
        print(f"torch_device_count={torch.cuda.device_count()}")
        if torch.cuda.is_available():
            print(f"torch_device_0={torch.cuda.get_device_name(0)}")

    missing = [name for name in MODULES if not module_available(name)]
    if missing:
        print("missing_modules=" + ",".join(missing))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
