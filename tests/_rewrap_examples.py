# pylint: disable=all

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