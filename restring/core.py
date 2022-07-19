
# std
import more_itertools as mit
import re
import ast
import textwrap as txw
import itertools as itt
from pathlib import Path

# third-party
from loguru import logger
from flynt.transform.transform import transform_chunk as fstring_transform

# local
from recipes import op
from recipes.iter import first_false_index
from recipes.io import iter_lines, write_replace, backed_up
from recipes.dicts import pformat

# ---------------------------------------------------------------------------- #
DEFAULT_WIDTH = 80

RGX_LINE_COMMENT = re.compile(r'(?m)^((?![\n])\s*)#(?P<comment>.*)$')

RGX_PYSTRING = re.compile(r'''(?xsm)     # verbose, dotall (. matches newline)
    # NOTE: this pattern cannot parse multiple strings per line:'hello' ' world'
    (?P<pre>                            # preceeding content
        ^\s*                            #   whitespace
        [^#'"\n]*?)                     #   not comment and not opening quote
    (?P<marks>(?i:[rf]{0,2}))           # string class indicator
    (?P<quote>                          # quote characters
        (?P<q>['"]){1}(?:(?P=q){2})?)   #   single or triple quote
    (?P<content>.*?)                    # string contents
    (?<!\\)                             # ignore escaped quotes \' \"
    (?P=quote)                          # closing quote
    (?P<post>[^\n]*)                    # trailing code
    ''')

# RGX_PRINTF_STR = re.compile(
#     r'''(?x)
#         %
#         (?:\(\w+\))?          # mapping key (name)
#         [#0\-+ ]{0,2}         # conversion flags
#         \d*                   # min field width
#         \.?(?:\d*|\*?)      # precision
#         [diouxXeEfFgGcrsa%] # conversion type.
#         ''')

RGX_TRAILSPACE = re.compile(r'[ \t]+\n')


get_contents = op.ItemVector('content', default='')
get_comments = op.ItemVector('comment', default=None)


def always_true(_):
    return True


def is_comment(text):
    return RGX_LINE_COMMENT.match(text)


def has_code(text):
    return text and not is_comment(text)


def parse_string_blocks(text):
    """
    Parse strings from python source code. Yield list of re.Match objects for
    lines constituting a single (multi-line, implicitly joined) str.

    Parameters
    ----------
    text : str
        Source code string

    Examples
    --------
    >>> 

    Yields
    -------
    list
        The line buffer. These lines are interpreted as a single (implicitly
        joined) string by python.
    """
    if not text:
        return

    buffer = []
    matched = RGX_PYSTRING.finditer(text)
    while (match := next(matched, None)):
        logger.opt(lazy=True).debug(
            'Match:\n{}', lambda: pformat(match.groupdict(), ignore='q')
        )

        # Flush buffer if this match starts a new string.
        # Checks:
        # If there are any items in the buffer
        # AND
        # any (non-comment) code following previous string closing quote
        # OR
        # code on any line between previous match and this match
        #   => closes the previous (joined) string
        if (buffer and
                (has_code(prev['post']) or
                 any(map(has_code,
                         text[(prev.end() + 1):match.start()].splitlines())))
            ):

            # multiple strings per line?
            another = None
            if RGX_PYSTRING.match(post := match['post']):
                faux = text[match.start():match.start('post')]
                faux = faux.replace(match['quote'], '$') + post
                another = RGX_PYSTRING.match(faux)
                # if another:
                #     logger.debug('')

            # Flush buffer if this match starts a new string
            yield buffer
            buffer = [another] if another else []

        # This line continues a joined string
        buffer.append(match)
        prev = match

    # final string
    yield buffer


def parse_strings(text):
    for matches in parse_string_blocks(text):
        # get quotation characters
        first, last = matches[0], matches[-1]

        # find end position so we don't munge trailing content in the file
        start = first.start('marks')
        end = last.start('post')

        # Get indent for line from file. We have to make the first line break
        # earlier so we can use the result as a drop-in replacement
        indent = ' ' * (start - first.start())
        indents = [indent, indent]

        yield (start, end, first['marks'], first['quote'], indents,
               get_contents(matches))


# def _read_around(filename, line_nr, pre=10, post=10):
#     lines = list(iter_lines(filename,
#                             max(line_nr - pre, 0),
#                             line_nr + post + 1,
#                             strip=''))
#     split = min(pre, line_nr)
#     return lines[:split], lines[split:]


# def get_string_block(filename, line_nr, pre=10, post=10):
#     # TODO: use linecache
#     head, tail = _read_around(filename, line_nr, pre, post)
#     start = first_false_index(head[::-1], RGX_PYSTRING.match, default=0)
#     return ''.join(head[-start:] + tail)


def wrap(lines, width=DEFAULT_WIDTH, marks='', quote="'", indents=('', ''),
         expandtabs=True):

    # add indent space for quotes
    single = (len(quote) != 3)
    opening = marks + quote
    # every line will start with the str opening marks eg: rf"
    if single:
        width -= len(opening)

    # add opening quotes
    indents = list(indents)
    indents[0] += opening
    # add indent space for quotes
    if single:
        # every line will start with the str opening marks eg: rf"
        indents[1] += opening

    # check if we need to wrap
    # widths = map(len, map(''.join, itt.zip_longest(indents, lines, fillvalue='')))
    # if max(widths) <= width:
    #     logger.info('No wrap required.')
    #     return False, ''.join(lines)

    # hard wrap
    lines = txw.TextWrapper(width, *indents, expandtabs,
                            replace_whitespace=False, drop_whitespace=False
                            ).wrap(''.join(lines))
    lines[0] = lines[0].lstrip()

    # add quote marks
    if single:
        # FIXME
        lines = list(map(''.join, zip(lines, itt.repeat(quote))))
    else:
        lines[-1] += quote

    return lines


def maybe_joined_str(line):
    return (match := RGX_PYSTRING.match(line)) and not has_code(match['post'])

# class MetaString(type):
#     def __matmul__(cls, fileinfo):


class StringWrapper:

    @classmethod
    def parse(cls, text, offset=0):
        for start, end, marks, quote, indents, lines in parse_strings(text):
            yield cls(start + offset, end + offset, marks, quote, indents, lines)

    @classmethod
    def from_file(cls, filename, line_nr, selection='', chunksize=10):
        # not line numbers are 1 indexed
        file = Path(filename)
        assert file.exists()

        with file.open('r') as fp:
            # move to position a few lines before given line
            read_lines(fp, max(line_nr - chunksize - 1, 0))
            # read chunk
            head = read_lines(fp, min(chunksize, line_nr - 1))

            # cursor position now at start of line containing the beginning the
            # string
            offset = fp.tell()

            # find the starting line of the current string
            start = first_false_index(head[::-1], maybe_joined_str)

            # read next chunk
            lines = read_lines(fp, max(line_nr - chunksize, 0))

        if start:
            lines = head[-start:] + lines

        block = ''.join(lines)
        for wrapper in StringWrapper.parse(block, offset):
            if any(map(op.contained(selection).within, wrapper.lines)):
                return wrapper

        raise ValueError(f'Could not find any string in {filename} near line '
                         f'{line_nr}.')

    # alias
    fromfile = from_file

    def __init__(self, start, end, marks, quote, indents, lines):
        self.start = int(start)
        self.end = int(end)
        self.marks = str(marks)
        self.quote = str(quote)
        self.indents = indents
        self.lines = list(lines)

    def wrap(self, width=DEFAULT_WIDTH, expandtabs=True):
        return wrap(self.lines, width,
                    self.marks, self.quote,
                    self.indents[:2], expandtabs)

    def wrap_in_file(self, filename, width, expandtabs):
        width = int(width)
        assert width > 0

        file = Path(filename)
        assert file.exists()

        new = self.wrap(width, expandtabs)

        # changed
        if (new != self.lines):
            with backed_up(filename, 'r+') as fp:
                fp.seek(self.end)
                tail = fp.read()
                fp.seek(self.start)
                fp.write('\n'.join(new))
                if len(new) != len(self.lines):
                    # only needed if new different number of lines to old
                    fp.write(tail)
                    fp.truncate()
        else:
            logger.info('No wrap required.')


def read_lines(fp, nlines):
    # return list(mit.repeatfunc(fp.readline, nlines))
    return [fp.readline() for _ in range(nlines)]


def rewrap(filename, line_nr, width=DEFAULT_WIDTH, expandtabs=True, selection=''):
    # hard wrap python strings in a file
    # selection is used to disambiguate between multiple strings per line
    width = width or DEFAULT_WIDTH
    assert width > 0

    #
    wrapper = StringWrapper.from_file(filename, line_nr, selection)
    wrapper.wrap_in_file(filename, width, expandtabs)
    return wrapper

# ---------------------------------------------------------------------------- #


def strip_trailing_space(filename, _ignored=()):
    """
    Strip trailing whitespace from file.

    This implementation only rewrites the file if necessary and only rewrites
    the portion of the file that is necessary, so is somewhat optimized
    compared to blind replace and rewrite.
    """
    with open(filename, 'r+') as file:
        while True:
            pos = file.tell()
            line = file.readline()
            if RGX_TRAILSPACE.search(line):
                # remaining content to be rewriten
                content = line + file.read()

                file.seek(pos)
                file.write(RGX_TRAILSPACE.sub('\n', content))
                file.truncate()
                break

# ---------------------------------------------------------------------------- #


# def get_code_block(filename, line_nr, pre=10, post=10, condition=always_true):

#     # n = count_lines(filename)
#     head, tail = _read_around(filename, line_nr, pre, post)
#     strings0 = list(get_strings(head[::-1]))[::-1]
#     strings1 = list(get_strings(tail))
#     lines, string_matches = zip(*(*strings0, *strings1))
#     lines = list(lines)
#     if not lines:
#         raise ValueError(
#             f'Could not find any strings in {filename} at line {line_nr}'
#         )

#     pre = head[:-len(strings0)]
#     post = tail[len(strings1):]
#     return *find_block(pre, lines, post, condition), string_matches


# def find_block(pre, lines, post, condition=always_true):
#     """
#     Try find a parsable code block by prepending / appending lines until it
#     compiles as an ast
#     """
#     npre, npost = len(pre), len(post)
#     for i, j in sorted(itt.product(range(npre), range(npost)), key=sum):
#         block = pre[(npre - i):] + lines + post[:j]
#         with contextlib.suppress(SyntaxError):
#             tree = ast.parse(txw.dedent(''.join(block)))
#             if condition(tree):
#                 return i, j, block

#     raise ValueError('Could not get logical code block')


# def _first_parsable_block(lines, join, initial=''):
#     block = initial
#     for line in lines:
#         block = join(block, line)
#         with contextlib.suppress(SyntaxError):
#             ast.parse(txw.dedent(block))
#             return block


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
