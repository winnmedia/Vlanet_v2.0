"""
   
"""
import os
from pathlib import Path

def get_version():
    """  ."""
    version_file = Path(__file__).parent.parent.parent / 'VERSION'
    if version_file.exists():
        return version_file.read_text().strip()
    return "0.1.0"  # 

def get_commit_hash():
    """ Git   ."""
    try:
        import subprocess
        result = subprocess.run(
            ['git', 'rev-parse', '--short', 'HEAD'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    return "unknown"

#     
VERSION = get_version()
COMMIT_HASH = get_commit_hash()
FULL_VERSION = f"{VERSION}-{COMMIT_HASH}"