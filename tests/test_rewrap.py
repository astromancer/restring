
import pytest
from restring import rewrap
from pathlib import Path

import tempfile
import shutil


# fd, name = tempfile.mkstemp('.py')
# shutil.copy('_rewrap_examples.py', name)

raw = Path('_rewrap_examples.py').read_text()
cases = raw.split(f'# {"-" * 76} #\n')

6, 17, 26
rewrap(name,)