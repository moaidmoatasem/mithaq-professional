import sys
from pathlib import Path

# Make `import daqiq` work without pip install for all test files
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
