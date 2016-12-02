
# Input
def split_lines(iInput):
    return [l.rstrip("\n") for l in iInput.split("\n") if l]

def merge_lines(iInput, iLines = 1):
    l = split_lines(iInput)
    o = []
    while l:
        o.append( ' '.join(l[:iLines]) )
        del l[:iLines]
    return o

# Output
def as_input():
    return lambda s, c: s

def split_input(i = 0):
    return lambda s, c: s.split()[i]

def optional_input(iVar, iIf, iElse = ""):
    return lambda s, c: iIf.format(**c) if iVar in c else iElse

class LineGenerator:
    def __init__(self, iFormat = "{}", iParams = []):
        self._format = iFormat
        self._params = iParams

    def process(self, s, c):
        aParams = []
        if self._params:
            aParams = [ f(s, c) for f in self._params ]
        else:
            aParams = [s]
        return self._format.format(*aParams, **c)

# Apply
def generate_lines(iInputLines, iGenerators, iContext={}):
    aGenerated = []
    for s in iInputLines:
        aGenerated += [ g.process(s, iContext) for g in iGenerators ]
    return aGenerated

