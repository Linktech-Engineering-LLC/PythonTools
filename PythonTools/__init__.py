from pathlib import Path
import sys

def _load_version():
    # Start at the package directory
    here = Path(__file__).resolve().parent

    # Search upward for VERSION (project root)
    for parent in [here, here.parent]:
        version_file = parent / "VERSION"
        if version_file.exists():
            return version_file.read_text().strip()

    # Frozen bundle (PyInstaller)
    if hasattr(sys, "_MEIPASS"):
        vf = Path(sys._MEIPASS) / "VERSION"
        if vf.exists():
            return vf.read_text().strip()

    return "0.0.0"

__version__ = _load_version()
