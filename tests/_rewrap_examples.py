# pylint: disable=all
# type: ignore
# sourcery skip

# ---------------------------------------------------------------------------- #

('hello '  # comment
 # more comment
 'world' # 'commented string'
 # bla
 '!'
 )

# ---------------------------------------------------------------------------- #
if True:
    if len(set(ncols)) != 1:
        raise ValueError(f'Cannot stack tables with unequal number of columns: {ncols}')

# ---------------------------------------------------------------------------- #


class Trigger:
    """
    Class representing the trigger time and mechanism starting CCD exposure
    """

    FLAG_INFO = {
        'flag':
            {'*': 'GPS Trigger',
             INACCURATE_TIME_FLAG: 'GPSSTART missing - timestamp may be inaccurate'},
        'loop_flag':
            {'*': 'GPS Repeat'}
    }


# ---------------------------------------------------------------------------- #
def foo():
    if not callable(func):
        raise TypeError(f'Parameter `func` should be callable. Received {type(func)}')


# ---------------------------------------------------------------------------- #
def __init__(self, a, b):

    data = dict(a=a, b=b)
    for k, v in data.items():
        if isinstance(v, shocObsGroups):
            data[k] = v.to_list()
        elif not isinstance(v, shocCampaign):
            raise ValueError(
                f'Cannot match objects of type {type(a)} and {type(b)}. Please ensure you pass `shocCampaign` or `shocObsGroups` instances to this class.')

    self.a, self.b = data.values()
    self.matches = {}
    self.deltas = {}
    #  dict of distance matrices between 'closest' attributes


# ---------------------------------------------------------------------------- #
def get_hash():
    if isinstance(val, abc.Hashable):
        # even though we have hashable types for our function arguments, the
        # actual hashing might not still work, so we catch any potential
        # exceptions here
        try:
            hash(val)
        except TypeError as err:
            warnings.warn(
                f'Hashing failed for {describe(self.func)}: {name!r} = '
                f'{val!r} due to:\n{err!s}'
            )
            #
            return False

    ignore = isinstance(val, Ignore)
    if ignore:
        if not val.silent:
            # line below should get f' prefix
            warnings.warn('Ignoring argument in '
                          f'{describe(self.func)}: {name!r} = {val!r}'
                          )
        continue


# ---------------------------------------------------------------------------- #

class foo:
    def null(a):
        if a:
            # emit warning and break out if we receive a rejection sentinel or
            # unhashable type
            what = ('unhashable argument',
                    'rejection sentinel')[isinstance(val, Reject)]
            warnings.warn(f'{describe(self.func).capitalize()} received {what}: '
                          f'{name!r} = {val!r}\n'
                          'Return value for call will not be cached.',
                          CacheRejectionWarning)


# ---------------------------------------------------------------------------- #
if True:
    if len(set(ncols)) != 1:
        raise ValueError(f'Cannot stack tables with unequal number of columns: {ncols}')


# ---------------------------------------------------------------------------- #
def foo():
    if not callable(func):
        raise TypeError(f'Parameter `func` should be callable. Received {type(func)}')


# ---------------------------------------------------------------------------- #
class x:
    def y():
        if missing:
            raise ValueError(
                f'Can\'t map method {name!r} over group. Right group is missing '
                'values for the following keys: ' + '\n'.join(map(str, missing))
            )


# ---------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    'spec',
    {'Bla {:*^100|B,r,_/teal}':
        'Bla \x1b[;1;31;4;48;2;0;128;128m********************************************Hello world!********************************************\x1b[0m',
    '{:|rBI_/k}':
        '\x1b[;31;1;3;4;40mHello world!\x1b[0m',
    '{:|red,B,I,_/k}':
        '\x1b[;38;2;127;255;212;3;48;2;211;211;211mHello world!\x1b[0m',
    '{:|aquamarine,I/lightgrey}':
        '\x1b[;38;2;122;0;0;1;3;4;40mHello world!\x1b[0m',
    '{:|[122,0,0],B,I,_/k}': ''
        }.keys()
)
def test_ext_format(spec, s='Hello world!'):
    print(repr(formatter.format(spec, s)))


# ---------------------------------------------------------------------------- #
class x:
    def y(self):
        if module is self.module:
            logger.info('Import statements are already well sorted for \'{}\' style!',
                        sort)


# ---------------------------------------------------------------------------- #
        if key != entry.key:
            logger.warning(
                f'Adding entry to {self.__class__.__name__} with '
                f'keys that don\'t match. Ignoring {key!r} and using'
                f' {entry.key}')


# ---------------------------------------------------------------------------- #


class _:
    def _():
        logger.opt(
            lazy=True).info(
            '{}',
            lambda:
            f'Found {len(data):d} {bands}-band SkyMapper DR1 images for coordinates {ra_dec_string(coords)} '
            f'spanning dates {t.min().iso.split()[0]} to {t.max().iso.split()[0]}.',)

    return columns, data
