
import sys
import re


# Parser

class sourceLineIter:
    def __init__(self, iLines):
        self._lines = iLines
        self._lineCount = len(iLines)
        self._currLineNb = 1

        self._previousLine = ''

        self._blockDepth = 0
        self._blockEnds = None

    # Iteration
    def get(self):
        if self._currLineNb > self._lineCount:
            return None
        else:
            return (self._currLineNb, self._lines[self._currLineNb - 1])

    def next(self):
        self._currLineNb += 1
        if self._currLineNb > self._lineCount:
            return None
        else:
            return self.get()

    def eof(self):
        return self._currLineNb > self._lineCount

    # Lines
    def getCmd(self):
        return self.get()[1].strip()

    def getFirstToken(self):
        aMatch = re.search('^(\w+)', self.getCmd())
        if aMatch:
            return aMatch.group(0)
        return None

    def isBlank(self):
        return self.getCmd() == ""

    def isComment(self):
        return self.getCmd().startswith('"')

    def isBlockBegin(self):
        aBlockEnd = {
                'function': 'endfunction',
                'if': 'endif',
                'augroup': 'augroup'}.get( self.getFirstToken() )
        if aBlockEnd:
            self._blockEnds = (self.getFirstToken(), aBlockEnd)
            self._blockDepth = 1
            return True
        return False

    def isBlockEnd(self):
        if self._blockDepth:
            if self.getFirstToken() == self._blockEnds[1]:
                self._blockDepth -= 1
                if not self._blockDepth:
                    self._blockEnds = None
                    return True
            if self.getFirstToken() == self._blockEnds[0]:
                self._blockDepth += 1
        return False

    # Public
    def consume(self):
        if self.eof():
            return None

        #print self.get()

        aComments = []

        while self.isBlank() or self.isComment():
            # Reset comment
            aComments = []

            # Find non empty line
            while self.isBlank():
                self.next()
                if self.eof():
                    return None

            # Find comment if any
            while self.isComment():
                aComments.append( self.get()[1] )
                self.next()
                if self.eof():
                    return None

        aLineNb, aCmd = self.get()

        # Handle functions
        if self.isBlockBegin():
            self.next()
            while not self.isBlockEnd():
                self.next()
        self.next()

        return (aLineNb, aCmd, aComments)

def getInstructions(iLines):
    aInstrs = []
    it = sourceLineIter(iLines)

    aInstr = it.consume()
    while aInstr:
        aLineNb, aCmd, aComments = aInstr

        # Merge multilines
        if aCmd.lstrip().startswith("\\") and aInstrs:
            aInstrs[-1][1].append(aCmd.lstrip())
        else:
            # Clean comments
            aInstrs.append( (aLineNb, [aCmd.lstrip()], [c.lstrip(' "') for c in aComments]) )

        aInstr = it.consume()

    return aInstrs


# Data

class VimType:
    def __init__(self, iPattern, iColumns = []):
        self._pattern = re.compile(iPattern)
        self._columns = iColumns
        self._found = []

    def collect(self, iInstr):
        aMatch = self._pattern.search(iInstr[1][0])
        if aMatch:
            self._found.append( aMatch.groupdict().items() + [('line',iInstr[0]), ('command',iInstr[1]), ('comment',iInstr[2])] )
            return True
        return False

    def get(self):
        aTable = [ self.getHeader() ]
        for f in self._found:
           aTable.append( self.getLine(f) )
        return aTable

    def getHeader(self):
        return self._columns

    def getLine(self, iFound):
        aFoundDict = dict(iFound)
        return [aFoundDict[c] for c in self._columns]

class Var(VimType):
    def __init__(self):
        VimType.__init__(self,
                r"^(?P<set>[sl]et)\s+(?P<var>\S+)(?:\s*\+?=\s*(?P<val>.*))?\s*$",
                ['line', 'set', 'var', 'comment'] )

class Map(VimType):
    def __init__(self):
        VimType.__init__(self,
                r"^(?P<map>.*map)\s+(?P<keys>\S+)\s+(?P<action>.*)\s*$",
                ['line', 'map', 'keys', 'comment'])

class AutoCmd(VimType):
    def __init__(self):
        VimType.__init__(self,
                r'^(?P<auto>au(?:tocmd)?\s+.*)\s*$',
                ['line', 'auto', 'comment'])

class Command(VimType):
    def __init__(self):
        VimType.__init__(self,
                r'^(?P<type>com(?:mand)?!)\s+(?P<cmd>\S+)\s+(?P<action>.*)\s*$',
                ['line', 'cmd', 'comment'])

class Function(VimType):
    def __init__(self):
        VimType.__init__(self,
                r'^(?P<type>fun(?:ction)?!)\s+(?P<function>\S+)\s*\(\s*(?P<args>.*)\s*\)\s*$',
                ['line', 'function', 'comment'])

class Abbrev(VimType):
    def __init__(self):
        VimType.__init__(self,
                r'^(?P<abbrev>\w*ab(?:brev)?\s+.*)\s*$',
                ['line', 'abbrev', 'comment'])

class Other(VimType):
    def __init__(self):
        VimType.__init__(self,
                r'^(?P<cmd>.*)\s*$',
                ['line', 'command', 'comment'])


# Output

def printOutput(iTypes):
    for n, t in iTypes:
        print n

        aTable = t.get()
        print aTable[0]
        print aTable[1:]

def htmlString(i):
    return str(i).replace("<", "&lt;").replace(">", "&gt;")

def htmlCell(i):
    if isinstance(i, list):
        return "<br>".join( [htmlString(e) for e in i] )
    else:
        return htmlString(i)

def htmlOutput(iTypes):
    print "<html>\n\
<head><title>Vimrc</title></head>\n\n\
<body>"
    for n, t in iTypes:
        print "<h4>{}</h4><table>".format(n)

        aTable = t.get()
        print "  <tr>{}</tr>".format( "".join(["<th>"+htmlCell(c)+"</th>" for c in aTable[0]]) )
        for r in aTable[1:]:
            print "  <tr>{}</tr>".format( "".join(["<td>"+htmlCell(c)+"</td>" for c in r]) )
        print "</table>"
    print "</body>\n\
</html>"

# Main

def main(aArgv):
    # Read file
    with open(".vimrc") as aFile:
        aContent = aFile.read()
    aLines = [l.rstrip("\n") for l in aContent.split("\n")]

    # Types
    aTypes = { 'map':Map(), 'var':Var(), 'autocmd':AutoCmd(), 'command':Command(), 'function':Function(), 'abbrev':Abbrev() }
    aOther = Other()

    # Collect
    for i in getInstructions(aLines):
        for t in aTypes.values() + [aOther]:
            if t.collect(i):
                # stop if found
                break

    # Output
    htmlOutput( aTypes.items() + [('other', aOther)] )

    return 0


if __name__ == "__main__":
    sys.exit( main(sys.argv) )

