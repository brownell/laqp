"""
File operation utilities
"""
import shutil
from pathlib import Path

def safe_copy(src, dst):
    """Safely copy a file"""
    shutil.copy2(str(src), str(dst))

def safe_move(src, dst):
    """Safely move a file"""
    shutil.move(str(src), str(dst))

def ensure_dir(path):
    """Ensure directory exists and is empty"""
    lib_path = Path(path)
    if lib_path.exists():
        shutil.rmtree(lib_path)
    lib_path.mkdir(parents=True, exist_ok=True)
