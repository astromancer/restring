from .core import *



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