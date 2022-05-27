
# pylint: disable-all
# type: ignore


if isinstance(other, TimeSeries):
    # Can only really do time series if they are simultaneous
    if self.n != other.n:
        raise ValueError('Arithmetic on %s objects with different '
                         'sizes not permitted' % self.__class__)
# ---------------------------------------------------------------------------- #


if n > N_MAX_TS_SAFETY:
    raise TooManyToPlot(
        'Received %i time series to plot. This is probably not what you wanted. Refusing since safety limit '
        'is currently set to %i to avoid accidental compute intensive '
        'commands from overwhelming system resources.'
        % (n, N_MAX_TS_SAFETY))

# ---------------------------------------------------------------------------- #

if (colours is not None) and (len(colours) < n):
    logger.warning('Colour sequence has too few colours ({:d} < {:d}). Colours '
                   'will repeat' % (len(colours), n))
# ---------------------------------------------------------------------------- #

n = len(data)
if 4 < n < 1:
    raise ValueError('Invalid number of arguments: %i' % n)
# ---------------------------------------------------------------------------- #


if len(times) != len(signals):
    raise ValueError('Number of time and signal vectors do not correspond. Please provide explicit time stamps for all signal vectors when plotting ragged time series.'
                        )
# ---------------------------------------------------------------------------- #
    
    
def invert(d, convertion={list: tuple}):
    inverted = type(d)()
    for key, val in d.items():
        kls = type(val)
        if kls in convertion:
            val = convertion[kls](val)
        
        if not isinstance(val, Hashable):
            raise ValueError(f'Cannot invert dictionary with non-hashable item: {val} of type {type(val)}. You may wish to pass a convertion mapping to this function to aid invertion of dicts containing non-hashable items.')
        
        inverted[val] = key
    return inverted


def pformat(dict_, name='', key_repr=str, val_repr=str, sep=':', item_sep=',',
            brackets='{}'): pass

# ---------------------------------------------------------------------------- #

class Thing:
    def thing(self):
        if result is ECHO:
            if kws:
                raise ValueError('ECHO sentinel cannot be used with keyword arguments')
        
        
# ---------------------------------------------------------------------------- #
    def get(self, run, kind, master=True):
        att = MATCH[kind]
        which = 'master' if master else 'raw'
        if which not in self.db[kind]:
            self.load(kind, master)

        db = self.db[kind]
        filenames = []
        for key in set(run.attrs(*att[0])):
            # key = str(key)
            if str(key) not in db:
                try:
                    logger.warning(
                        'No %s files available in database for '
                        'observational setup:\n%s',
                        kind, '; '.join(('{a} = {v}' for a, v in zip(att[0], key)))
                        )
                except Exception as err:
                    from IPython import embed
                    
# ---------------------------------------------------------------------------- #
class X:
    def y():
        if not_found:    
            logger.warning(
                'No %s files available in database for '
                'observational setup:\n%s',
                kind, Table(not_found, col_headers=att[0])
                )
            
