
import gen

## helper
def _():
    return gen.as_input()

def _sub(i = 0):
    return gen.split_input(i)

def _opt(v, i, e = ""):
    return gen.optional_input(v, i, e)

class Line(gen.LineGenerator):
    def __init__(self, f, p):
        gen.LineGenerator.__init__(self, f, p)

def generate(iInputLines=[], iGenerators=[], iContext=[]):
    global input
    if not iInputLines:
        iInputLines = gen.split_lines(input)

    global generators
    if not iGenerators:
        iGenerators = generators

    global context
    if not iContext:
        iContext = context

    for s in gen.generate_lines(iInputLines, iGenerators, iContext):
        print s

## generate
input = """
ATPCO
RES302
EXCESS
LH01417
"""

context = {
'bp': 'MUC',
'oc': 'LH'
}

generators = [
Line( "delete from T_ACT where name = '{0}' and operating_carrier = '{oc}' and {1};", [_(), _opt("hc", "handling_carrier = '{hc}'", "handling_carrier is null")] ),
Line( "insert T_ACT(name, operating_carrier, {1}activated) values('{0}', '{oc}',{2} Y);", [_(), _opt("hc", " handling_carrier,"), _opt("hc", " '{hc}',")] )
]


print "-- LH"
generate()

print "\n-- OS"
context['oc'] = 'OS';
context['hc'] = 'LX';
generate()

