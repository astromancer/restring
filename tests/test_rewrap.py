
import pytest
from pathlib import Path

import tempfile
import shutil

from restring.core import StringWrapper
from recipes.pprint import banner

# fd, name = tempfile.mkstemp('.py')
# shutil.copy('_rewrap_examples.py', name)

{
 '<{self.__class__.__name__}: span=[{self.start}:{self.end}]>{sep}'
 '{sep.join(map(repr, self.lines))}':
     ['<{self.__class__.__name__}: span=[{self.start}:{self.end}]>{sep}',
      '{sep.join(map(repr, self.lines))}'],
    
     
}

width = 80

examples = Path(__file__).parent  / '_rewrap_examples.py'
text = examples.read_text()
for i, s in enumerate(StringWrapper.parse(text)):
    print(i)
    print(banner(s))

    w = s.indents[0] + '\n'.join(s.wrap(width))
    print(banner(w, '~'))
    
    # # s = StringWrapper.from_matches(block)
    

    # print('~'*88)
    # from IPython import embed
    # embed(header="Embedded interpreter at 'tests/test_rewrap.py':24")
    # break


# cases = raw.split(f'# {"-" * 76} #\n')

# # 6, 17, 26
# rewrap(name,)
