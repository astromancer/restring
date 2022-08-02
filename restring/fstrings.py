

# std
import ast
import textwrap as txw

# third-party
from loguru import logger
from flynt.transform.transform import transform_chunk as fstring_transform

# local
from recipes.io import write_replace


class GetMod(ast.NodeVisitor):
    def __init__(self):
        super().__init__()
        self.mod = None

    def visit_BinOp(self, node):
        if isinstance(node.op, ast.Mod):
            self.mod = node


def get_mod(tree):
    v = GetMod()
    v.visit(tree)
    return v.mod


def _convert_fstring(block, string=None, quote=None, width=DEFAULT_WIDTH, expandtabs=True):
    if not isinstance(string, StringWrapper):
        string = StringWrapper.parse(block)

    # get mod part
    block = txw.dedent(block)
    tree = ast.parse(block)
    mod = get_mod(tree)
    # if v.rhs is None:
    #     raise ValueError('not found')
    original = ast.get_source_segment(block, mod)  # python >=3.8
    modstring = ast.get_source_segment(block, mod.right)

    # return f'{string.unwrapped!r} % {modstring}'

    quote = quote or string.quote
    # FIXME: this function is frekkin useless!
    new, changed = fstring_transform(
        f'{string.unwrapped!r} % {modstring}', quote)
    new = StringWrapper.parse(new)
    new.indents = string.indents

    return original, new.wrap(width, expandtabs), changed


def convert_fstring(filename, line_nr, quote=None, width=DEFAULT_WIDTH, expandtabs=True):

    i, j, block, strings = get_code_block(filename, line_nr)
    s = StringWrapper.from_matches(zip(block[i:-j or None], strings))

    block = ''.join(block)
    origin, new, changed = _convert_fstring(block, s, quote, width, expandtabs)
    if changed:
        write_replace(filename, {origin: new})
    else:
        logger.info('String not converted.')
