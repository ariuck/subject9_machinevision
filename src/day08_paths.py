"""Keep regeneration within known lesson-8 generated paths."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]

def checked_path(path, allowed):
    path = Path(path)
    relative = path.relative_to(ROOT) if path.is_absolute() else path
    if relative.as_posix() not in allowed:
        raise ValueError(f"Unexpected generated directory: {path}")
    absolute = ROOT / relative
    if absolute.resolve() != absolute.absolute() or absolute.is_symlink():
        raise ValueError(f"Refusing symlink cleanup: {path}")
    return absolute

def reset_dataset(path):
    shutil.rmtree(checked_path(path, {"samples/day08"}))

def clear_synthetics(path):
    absolute = checked_path(path, {"outputs/day08/cutpaste/generated", "outputs/day08/mini_challenge/generated"})
    for old in absolute.glob("synthetic_*.png"):
        if old.is_symlink() or not old.is_file():
            raise ValueError(f"Unexpected generated file: {old}")
        old.unlink()
