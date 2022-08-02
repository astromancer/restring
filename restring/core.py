
# std
import re
import textwrap as txw
import itertools as itt
from pathlib import Path

# third-party
from loguru import logger

# local
from recipes import op
from recipes.io import backed_up
from recipes.iter import first_false_index
from recipes.string.brackets import braces, level


# FIXME: wrap brackets when needed at return '...'


# ---------------------------------------------------------------------------- #
DEFAULT_WIDTH = 80

RGX_LINE_COMMENT = re.compile(r'(?m)^((?![\n])\s*)#(?P<comment>.*)$')

# NOTE: this pattern cannot parse multiple strings per line:'hello' ' world'
# see: `parse_string_blocks`
RGX_PYSTRING = re.compile(r'''(?xsm)     # verbose, dotall (. matches newline)
    (?P<pre>                            # preceeding content
        ^\s*                            #   whitespace
        [^#'"\n]*?)                     #   not comment and not opening quote
    (?P<marks>(?i:(?:[rf]|[rb]){0,2}))  # string class indicator
    (?P<quote>                          # quote characters
        (?P<q>['"]){1}(?:(?P=q){2})?)   #   single or triple quote
    (?P<content>.*?)                    # string contents
    (?<!\\)                             # ignore escaped quotes \' \"
    (?P=quote)                          # closing quote
    (?P<post>[^\n]*)                    # trailing code
    ''')

RGX_TRAILSPACE = re.compile(r'[ \t]+\n')

# ---------------------------------------------------------------------------- #
get_contents = op.ItemVector('content', default='')
get_comments = op.ItemVector('comment', default=None)

# ---------------------------------------------------------------------------- #

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
    prev = None
    matched = RGX_PYSTRING.finditer(text)
    while (match := next(matched, None)):
        # logger.opt(lazy=True).debug(
        #     'Match:\n{}',
        #     lambda: pformat(match.groupdict(), ignore='q').replace('\n', '  \n')
        # )

        # Flush buffer if this match starts a new string.
        # Checks:
        # If there are any items in the buffer
        # AND
        # any (non-comment) code following previous string closing quote
        # OR
        # code on any line between previous match and this match
        #   => closes the previous (joined) string
        # logger.opt(lazy=True).debug('{}', lambda: f'{buffer = };')
        if prev and \
            any(map(has_code,
                    text[prev.start('post'):match.start('marks')].splitlines())):
            # Flush buffer if this match starts a new string
            logger.debug('Found string with {} lines:\n> {}', len(buffer), buffer)
            yield buffer

            another = _check_prev_post(text, prev)
            buffer = [another] if another else [match]

        else:
            # This line continues a joined string
            buffer.append(match)

        prev = match

    # final string
    if buffer:
        logger.debug('Found string with {} lines:\n> {}', len(buffer), buffer)
        yield buffer


def _check_prev_post(text, prev):
    # multiple strings per line?
    if RGX_PYSTRING.match(post := prev['post']):
        faux = text[prev.start():prev.start('post')]
        faux = faux.replace(prev['quote'], '$') + post
        if another := RGX_PYSTRING.match(faux):
            logger.info(
                'There are multiple independent strings in this line. '
                'Replacing quotes {!r} of the previous string (here in '
                "the current match's 'pre' group) with '$'.",
                prev['quote']
            )
        return another


# def _get_info_matches(matches):
#     # get quotation characters
#     first, last = matches[0], matches[-1]

#     # find end position so we don't munge trailing content in the file
#     start = first.start('marks')
#     end = last.start('post')

#     # Get indent for line from file. We have to make the first line break
#     # earlier so we can use the result as a drop-in replacement
#     indent = ' ' * (start - first.start())
#     indents = [indent, indent]

#     return (start, end, first['marks'], first['quote'], indents, get_contents(matches))


# def parse_strings(text):
#     for matches in parse_string_blocks(text):
#         yield _get_info_matches(matches)


def wrap(lines, width=DEFAULT_WIDTH, marks='', quote="'", indents=('', ''),
         expand_tabs=True):

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
    #     logger.info('No wrap required.')expandtabs
    #     return False, ''.join(lines)

    # hard wrap
    lines = txw.TextWrapper(width, *indents, expand_tabs,
                            replace_whitespace=False, drop_whitespace=False
                            ).wrap(''.join(lines))
    if lines:
        lines[0] = lines[0].lstrip()

    # add quote marks
    if single:
        # FIXME
        lines = list(map(''.join, zip(lines, itt.repeat(quote))))
    else:
        lines[-1] += quote

    return lines


# def wrap_fstring(string, width):

#     indexers = [str.rindex, always(0)]

#     lines = ['']
#     for parts in braces.isplit_pairs(string, ):
#         pos = len(lines[-1])
#         # unbraced part / braced part
#         for part, indexer in zip(parts, indexers):
#             if pos + len(part) > width:
#                 idx = indexer(part)
#                 lines[-1] += part[:idx]
#                 lines.append(part[idx:])
#             else:
#                 lines[-1] += part

#     return lines


# def _wrap_ex(string, width):
#     lines = ['']
#     for pre, braced in braces.isplit_pairs(string):
#         pos = len(lines[-1])
#         if pos + len(pre) > width:
#             idx = pre.rindex(' ')
#             lines[-1] += pre[:idx]
#             lines.append(pre[idx:])
#         else:
#             lines[-1] += pre

#         pos = len(lines[-1])
#         if pos + len(braced) > width - 1:
#             lines.append(braced)
#         else:
#             lines[-1] += braced

#         # if braced and not lines[-1].startswith('f')

#     return lines


def wrap_fstring(string, width, marks='f', quote="'", indents=('', ''),
                 split_at=tuple(' .,:;')):

    # user can use marks='F' / 'R' / 'rf' etc, for different styling, but 'f'
    # will be used by default where necessary
    f = 'f'
    for f in 'Ff':
        if f in marks:
            marks = marks.replace(f, '')
            break

    # will prepend f for line when necessary below
    lines = [f'{indents[0]}{marks}{f}{quote}']
    _open = fopen = indents[1]
    ending = ''
    # single :=
    if len(quote) != 3:
        _open = f'{indents[1]}{marks}{quote}'
        fopen = f'{indents[1]}{marks}{f}{quote}'
        ending = quote
        width -= 1  # for closing quote

    for pre, braced in braces.isplit_pairs(string, condition=(level == 0)):
        pos = len(lines[-1])
        if pos + len(pre) > width:
            idx = pre.rindex(' ')
            lines[-1] += pre[:idx] + ending
            lines.append(_open + pre[idx:])
        else:
            lines[-1] += pre

        pos = len(lines[-1])
        if pos + len(braced) > width - 1:  # -1 for f prefix
            idx = 0
            lines[-1] += braced[:idx] + ending
            lines.append(fopen + braced[idx:])
        else:
            lines[-1] += braced

        # print(lines)
        # print('*' * width)

    if lines:
        lines[0] = lines[0].lstrip()

    lines[-1] += ending

    return lines


def maybe_joined_str(line):
    return (match := RGX_PYSTRING.match(line)) and not has_code(match['post'])


# def int2tup(v):
#     """wrap integer in a tuple"""
#     return (v, ) if isinstance(v, numbers.Integral) else tuple(v)

# class MetaString(type):
#     def __matmul__(self, fileinfo):
#         assert isinstance(fileinfo, MutableMapping)
#         for filename, line_nrs in fileinfo.items():
#             for line_nr in int2tup(line_nrs):
#                 yield self.fromfile(filename, line_nr)


class StringWrapper:  # (metaclass=MetaString)

    @classmethod
    def parse(cls, text, offset=0):
        for matches in parse_string_blocks(text):
            yield cls(matches, offset)

    @classmethod
    def from_file(cls, filename, line_nr, chunksize=10, width=DEFAULT_WIDTH):
        # not line numbers are 1 indexed
        file = Path(filename)
        assert file.exists()

        logger.debug('Attempting to parse string in {}:{}.', filename, line_nr)
        with file.open('r') as fp:
            # move to position a few lines before given line
            read_lines(fp, max(line_nr - chunksize - 1, 0))
            # read chunk
            head = read_lines(fp, min(chunksize, line_nr - 1))

            # cursor position now at start of line containing the beginning the
            # string
            offset = fp.tell()

            # read next chunk
            lines = read_lines(fp, chunksize)

        match = RGX_PYSTRING.match(lines[0])
        if not match:
            raise ValueError(f'Could not find a string in {filename!r} at line '
                             f'{line_nr}.')

        if not has_code(match['pre']):
            # find the starting line of the current string
            if start := first_false_index(head[::-1], maybe_joined_str):
                lines = head[-start:] + lines

        block = ''.join(lines)
        for wrapper in cls.parse(block, offset):
            # disambiguate between multiple strings per line
            if (len(wrapper._matches) == 1) and wrapper.last.start('post') < width:
                #RGX_PYSTRING.match(wrapper.last['post']
                logger.debug("Going to next string since this one doesn't need "
                             "wrap.")
                continue
            
            return wrapper

        raise ValueError(f'Could not find any string in {filename!r} near line '
                         f'{line_nr}.')

    # alias
    fromfile = from_file

    def __init__(self, matches, offset=0):
        assert matches
        self._matches = list(matches)
        self._offset = int(offset)

    def __str__(self):
        sep = '\n|'
        return f'<{self.__class__.__name__}: span=[{self.start}:{self.end}]>{sep}{sep.join(map(repr, self.lines))}'

    __repr__ = __str__

    @property
    def opening(self):
        return self.marks + self.quotes

    @property
    def lines(self):
        return get_contents(self._matches)

    @property
    def first(self):
        return self._matches[0]

    @property
    def last(self):
        return self._matches[-1]

    @property
    def start(self):
        return self.first.start('marks') + self._offset

    @property
    def end(self):
        return self.last.start('post') + self._offset

    @property
    def indents(self):
        # Get indent for line from file. We have to make the first line break
        # earlier so we can use the result as a drop-in replacement
        indent = ' ' * (self.first.start('marks') - self.first.start())
        return [indent, indent]

    def is_fstring(self):
        return ('f' in self.first['marks'].lower())

    def is_raw(self):
        return ('r' in self.first['marks'].lower())

    # def _gen_split_points(self):
    #     for line in self:

    # def get_split_points(self, line, width):
    #     idx = current.rfind(' ', 0, width - len(opening))
    #     if idx != -1:
    #         yield line[:idx]
    #         opening = self.opening + line[idx:]
    #     else:
    #         '?'

    # def _wrap_fstring(self):

    # def iwrap(self, width, expand_tabs):
    #     # split_points = []
    #     # if self.is_fstring():
    #     # r = 'r' * self.is_raw()

    #     expander = str.expandtabs if expand_tabs else echo0

    #     opening = self.opening
    #     leftover = ''
    #     lines = map(expander, self.lines)
    #     while (line := next(lines, None)) is not None:
    #         current = opening + leftover + line
    #         if (w := len(current)) < width:
    #             continue

    #         idx = current.rfind(' ', 0, width - len(opening))
    #         if idx != -1:
    #             yield line[:idx]
    #             opening = self.opening + line[idx:]
    #         else:
    #             '?'
    #         # else:
    #         #     leftover = line

    #     yield leftover

    def wrap(self, width=DEFAULT_WIDTH, expand_tabs=True):

        lines = self.lines
        if expand_tabs:
            lines = map(str.expandtabs, lines)

        first = self.first
        if self.is_fstring():
            logger.debug('Hard wrapping fstring:\n  {}', 
                         '\n  '.join(map(repr, self.lines)))
            return wrap_fstring(''.join(lines), width,
                                first['marks'], first['quote'],
                                self.indents)

        logger.debug('Hard wrapping:\n  {}', '\n  '.join(map(repr, self.lines)))
        return wrap(self.lines, width,
                    first['marks'], first['quote'],
                    self.indents, expand_tabs)

    def wrap_in_file(self, filename, width, expand_tabs):
        width = int(width)
        assert width > 0

        file = Path(filename)
        assert file.exists()

        new = self.wrap(width, expand_tabs)

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


def rewrap(filename, line_nr, width=DEFAULT_WIDTH, expand_tabs=True):
    # hard wrap python strings in a file
    width = width or DEFAULT_WIDTH
    assert width > 0

    #
    wrapper = StringWrapper.from_file(filename, line_nr, width)
    wrapper.wrap_in_file(filename, width, expand_tabs)
    return wrapper

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
