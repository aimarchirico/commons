"""Make sibling script modules importable from this directory's tests."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
