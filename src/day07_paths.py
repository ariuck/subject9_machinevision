"""Scope cleanup to this lesson's generated directories."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {
    "samples/day07/train", "samples/day07/validation", "samples/day07/test",
    "samples/day07/ground_truth", "samples/day07/challenge", "samples/day07/mini_challenge",
    "outputs/day07/fp", "outputs/day07/fn", "outputs/day07/heatmap",
}

def reset_generated_directory(directory):
    directory = Path(directory)
    relative = directory.relative_to(ROOT) if directory.is_absolute() else directory
    if relative.as_posix() not in ALLOWED:
        raise ValueError(f"Refusing cleanup: {directory}")
    expected = ROOT / relative
    if expected.resolve() != expected.absolute() or expected.is_symlink():
        raise ValueError(f"Refusing symlink cleanup: {directory}")
    shutil.rmtree(expected)
