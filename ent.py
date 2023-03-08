# Alexandros Athanasopoulos AM: 4020 username : cse74020
# Vasileios  Sirpas         AM: 4174 username : cse74174

import math
import string
import sys

class Quad:
    def __init__(self, operator, operand1, operand2, operand3):
        self.operator = operator
        self.operand1 = operand1
        self.operand2 = operand2
        self.operand3 = operand3

#---------------------------

class Table:
    def __init__(self, scopes):
        self.scopes = scopes

class Scope:
    def __init__(self, level, entities):
        self.level = level
        self.entities = entities

class Entity:
    def __init__(self, name):
        self.name = name

class Variable(Entity):
    def __init__(self, name, datatype, offset):
        super().__init__(name)
        self.datatype = datatype
        self.offset = offset

class FormalParameter(Entity):
    def __init__(self, name, datatype, mode):
        super().__init__(name)
        self.datatype = datatype
        self.mode = mode  # in/ref/ret

class Parameter(FormalParameter):
    def __init__(self, name, datatype, mode, offset):
        super().__init__(name, datatype, mode)
        self.offset = offset

class Procedure(Entity):
    def __init__(self, name, startingQuad, framelength, formalParameters):
        super().__init__(name)
        self.startingQuad = startingQuad
        self.framelength = framelength
        self.formalParameters = formalParameters

class Function(Procedure):
    def __init__(self, name, datatype, startingQuad, framelength, formalParameters):
        super().__init__(name, startingQuad, framelength, formalParameters)
        self.datatype = datatype

class TemporaryVariable(Variable):
    def __init__(self, name, datatype, offset):
        super().__init__(name, datatype, offset)

class SymbolicConstant(Entity):
    def __init__(self, name, datatype, vallue):
        super().__init__(name)
        self.datatype = datatype
        self.vallue = vallue

quadz = [] #here we save the quadz

letters = list(string.ascii_letters)
numbers = list(string.digits)
mathSyms = ["+", "-", "*", "/","="]
specialChars = [",", ";", "(", ")", "{", "}", "[", "]"]
delimeters = [" ", "\t", "\n"]
relopes = ["=", "<", "<=", ">", ">=", "<>"]

ID = ""

expectation = ""

currentType = ""
currentWord = ""
lastWord = ""

statementWords = ["if", "while", "switchcase", "incase", "forcase", "call", "return", "input", "print"]

standardWords = ["program", "declare", "if", "else", "while", "switchcase", "forcase", "incase", "case", "default",
                 "not", "and", "or", "function", "procedure", "call", "return", "in", "inout", "input", "print"]

file = open(sys.argv[1], encoding="utf8")
filedata = list(file.read())

varNames = []

pos = 0  # position in file
line = 1  # line in file
inputChar = filedata[pos]

#endiamesus-------------
t_name = 0
labelslist = []
blocknames = []
currentCalling = []

flagForCfile = 0

#pinakas symb------------
myTable = Table([])
totaloffset = 0
offsetCheckPoint = []
symbFile = open('output.symb', 'w')

#telikos kodikas------------
finalFile = open('output.asm', 'w')
labelFlag = 1

def lex():
    global pos
    global inputChar
    global line
    global currentType
    global lastWord

    lastWord = currentWord
    currentType = ""
    comment = False
    state = 0
    word = ""  # Empty list to return word unit

    while state < 7:  # When state = 7 error, when state = 8 end of word unit
        if state == 0:
            if inputChar in letters:
                state = 1
            elif inputChar in numbers:
                state = 2
            elif (inputChar in mathSyms) or (inputChar in specialChars):
                state = 8  # END
            elif inputChar == "<":
                state = 3
            elif inputChar == ">":
                state = 4
            elif inputChar == ":":
                state = 5
            elif inputChar == "#":
                state = 6
            elif inputChar == ".":
                state = 8
            elif (inputChar != "\n") and (inputChar != " ") and (inputChar != "\t"):
                state = 7
                print("ERROR! at line " + str(line) + ". Unknown character: '" + inputChar + "'")
                exit()

        elif state == 1:  # This is a word, only letters and numbers allowed
            if not ((inputChar in numbers) or (inputChar in letters)):
                currentType = "Word"
                break

        elif state == 2:  # Number, only numbers allowed
            if not (inputChar in numbers):
                currentType = "Number"
                if float(word) > math.pow(2, 23) - 1 or float(word) < -(math.pow(2, 23) - 1):

                    print("Number out of boundaries in line " + str(line))
                    exit()
                break

        elif state == 3:  # means '<'
            if inputChar == "=" or inputChar == ">":
                state = 8
            else:
                break

        elif state == 4:  # means '>'
            if inputChar == "=":
                state = 8
            else:
                break

        elif state == 5:  # For :=

            if inputChar == "=":
                state = 8
            else:
                print("ERROR! at line " + str(line) + ". '=' was expected after ':'")
                exit()

        elif state == 6:  # For #comment#

            if pos == len(filedata):
                print("ERROR: a comment is never closed")
                exit()

            if inputChar == "#":
                state = 8
                comment = True


        if not inputChar in delimeters:
            word = word + inputChar

        if inputChar == "\n":  # Keep the current line
            line = line + 1

        pos = pos + 1
        if pos < len(filedata):
            inputChar = filedata[pos]

        elif pos > len(filedata):
            print("ERROR! at line " + str(line) + ". Code ended unexpectedly")
            exit()



    if not comment:
        return word
    else:
        return lex()

#Works like lex(), but after the "}." is found
def mk():
    global pos
    global inputChar
    global line
    global lastWord

    state = 0
    while True:# 2 = error, 3 = final
        if state == 0:
            if inputChar in delimeters:
                state = 0
            elif inputChar == "#":
                state = 1
            else:
                state = 2

        elif state == 1:
            if inputChar == "#":
                state = 0
            else:
                state = 1

        elif state == 2:
            print("WARNING: Unreachable code after the '}.' at the end of the program")
            return

        elif state == 3:
            return

        pos = pos + 1
        if pos < len(filedata):
            inputChar = filedata[pos]
        else:
            if state == 1:
                print("WARNING: Unreachable code after the '}.' at the end of the program")
                return
            else:
                state = 3

#prints some of the errors
def error():
    if expectation == "":
        print("Error in line " + str(line) + ": \"" + currentWord + "\" wasn't expected after \"" + lastWord + "\"")
    else:
        print("Error in line " + str(line) + ": \"" + expectation + "\" was expected after \"" + lastWord + "\" but found \"" + currentWord + "\"")
    exit()


def program():

    global standardWords
    global currentWord
    global ID
    global labelslist
    global blocknames
    global totaloffset

    if lex() != "program":
        print("ERROR! at line " + str(line) + ". The code must always start with 'program'")
        exit()  # false

    finalFile.write("\t.data\nstr_nl:\t.asciz \"\\n\"\n\t.text\n")
    finalFile.write("\tj L_main_\n")

    currentWord = lex()
    ID = currentWord
    blocknames = blocknames + [ID]

    addLayer()
    totaloffset = 8

    if currentWord in standardWords:
        print("ERROR! at line " + str(line) + ". Word " + currentWord + " can't be used as id")
        exit()  # false

    elif not currentType == "Word":
        print("ERROR! at line " + str(line) + ". Word " + currentWord + " can't be used as id")
        exit()  # false

    if block() == 1:
        error()
        exit()

    if lex() != ".":
        print("ERROR! at line " + str(line) + ". The program must always end with '.'")
        exit()

    mk()

    print("Program finished. No errors detected.")
    return 0  # Reached EOF ( "." found)


def block():
    global currentWord
    global labelslist
    global blocknames
    global totaloffset
    global offsetCheckPoint

    if lex() != "{":
        return 1

    currentWord = lex()

    if currentWord == "declare":
        if declarations() == 1:
            return 1

    if currentWord == "function" or currentWord == "procedure":
        if subprograms() == 1:
            return 1

    # endiamesos
    labelslist = labelslist + makeList(nextQuad())
    genQuad('begin_block', blocknames[-1], '_', '_')

    startBlock = labelslist[-1]-1

    if len(myTable.scopes) > 1:
        updateEntity(0, labelslist[-1]+1)

    if currentWord in statementWords or currentWord in varNames:
        if blockstatements() == 1:
            return 1

    # endiamesos
    if len(blocknames) == 1:
        labelslist = labelslist + makeList(nextQuad())
        genQuad('halt', '_', '_', '_')

    labelslist = labelslist + makeList(nextQuad())
    tmpname = blocknames.pop()
    genQuad('end_block', tmpname, '_', '_')

    endBlock = labelslist[-1]
    createFinalCode(startBlock, endBlock)

    if currentWord != "}":
        error()

    if len(myTable.scopes) > 1:
        totaloffset = totaloffset + 4
        updateEntity(1, totaloffset)

    removeLayer()

    return 0


def declarations():
    global currentWord
    global expectation

    retvar = varlist()

    if retvar == 1:
        return 1

    if currentWord != ";":
        expectation = ";"
        return 1

    currentWord = lex()
    if currentWord == "declare":
        if declarations() == 1:
            return 1
    elif currentWord == ";":
        return 1
    else:
        return 0


def varlist():

    global currentWord
    global totaloffset

    currentWord = lex()

    if currentType != "Word":
        return 0  # No variables

    # At least one

    while True:

        varNames.append(currentWord)

        totaloffset = totaloffset + 4
        addNewRegister("Variable", currentWord, totaloffset)

        currentWord = lex()

        if currentWord != ",":
            return 0

        currentWord = lex()

        if currentType != "Word":
            return 1


def subprograms():

    global currentWord
    if subprogram() == 1:
        return 1
    currentWord = lex()

    if currentWord == "function" or currentWord == "procedure":
        if subprograms() == 1:
            return 1

    return 0


def subprogram():
    global currentWord
    global expectation
    global labelslist
    global blocknames
    global totaloffset
    global offsetCheckPoint
    global flagForCfile

    flagForCfile = 1

    flag = currentWord

    currentWord = lex()

    if currentType != "Word":
        return 1

    blocknames = blocknames + [currentWord]  # endiamesos

    if flag == "function":
        addNewRegister("Function", currentWord, 0)
    else:
        addNewRegister("Procedure", currentWord, 0)

    addLayer()
    offsetCheckPoint = offsetCheckPoint + [totaloffset]
    totaloffset = 8

    currentWord = lex()

    if currentWord != "(":
        expectation = "("
        return 1

    if formalparlist() == 1:
        return 1

    if currentWord != ")":
        expectation = ")"
        return 1

    if block() == 1:
        return 1


    totaloffset = offsetCheckPoint.pop()

    return 0


def formalparlist():

    global currentWord

    currentWord = lex()

    if not (currentWord == "in" or currentWord == "inout"):
        return 0  # No variables

    # At least one variable

    if formalparitem() == 1:
        return 1

    while True:


        currentWord = lex()

        if currentWord != ",":
            return 0

        currentWord = lex()

        if formalparitem() == 1:
            return 1


def formalparitem():

    global currentWord
    global expectation
    global varNames
    global totaloffset

    if not (currentWord == "in" or currentWord == "inout"):
        expectation = "in or inout"
        return 1

    currentWord = lex()

    if (lastWord == "inout"):
        varNames = varNames + [currentWord]

    if currentType != "Word":
        return 1

    if lastWord == "in":
        mode = "cv"
    else:
        mode = "ref"

    totaloffset = totaloffset + 4
    addNewRegister("Parameter", currentWord, [mode, totaloffset])
    addParameter()



    return 0


def blockstatements():

    global currentWord
    global currentType
    global expectation

    if statement() == 1:
        return 1

    while True:
        if currentWord != ";":

            if currentWord != "}":
                expectation = ";\" or \"}"
                return 1
            return 0

        else:
            currentWord = lex()
            if currentWord == "}":
                return 0


        if statement() == 1:
            return 1



def statements():
    global currentWord
    global expectation

    if currentWord != '{':
        if statement() == 1:
            return 1

        if currentWord != ';':
            expectation = ";"
            return 1
        else:
            return 0

    # { was detected

    currentWord = lex()

    if statement() == 1:
        return 1

    while True:

        if currentWord != ";":

            if currentWord != "}":
                expectation = ";\" or \"}"
                return 1
            return 0

        else:
            currentWord = lex()
            if currentWord == "}":
                return 0

        if statement() == 1:
            return 1



def statement():
    global currentWord

    if currentWord in varNames:
        if assignstat() == 1:
            return 1

    elif currentWord == "if":
        if ifstat() == 1:
            return 1

    elif currentWord == "while":
        if whilestat() == 1:
            return 1

    elif currentWord == "switchcase":
        if switchcasestat() == 1:
            return 1

    elif currentWord == "forcase":
        if forcasestat() == 1:
            return 1

    elif currentWord == "incase":
        if incasestat() == 1:
            return 1

    elif currentWord == "call":
        if callstat() == 1:
            return 1

    elif currentWord == "return":
        if returnstat() == 1:
            return 1

    elif currentWord == "input":
        if inputstat() == 1:
            return 1

    elif currentWord == "print":
        if printstat() == 1:
            return 1

    else:
        return 1

    return 0


def assignstat():

    global currentWord
    global expectation
    global labelslist

    assignVar = currentWord

    currentWord = lex()

    if currentWord != ":=":
        expectation = ":="
        return 1

    currentWord = lex()

    E_place = expression()
    if E_place == 1:
        return 1

    # endiamesos
    labelslist = labelslist + makeList(nextQuad())
    genQuad(':=', E_place, '_', assignVar)

    return 0


def ifstat():
    global currentWord
    global expectation
    global labelslist
    currentWord = lex()

    if currentWord != "(":
        expectation = "("
        return 1

    currentWord = lex()

    condition_total = condition()
    if condition_total == 1:
        return 1

    condition_true = condition_total[0]
    condition_false = condition_total[1]

    if currentWord != ")":
        expectation = ")"
        return 1



    backpatch(condition_true, nextQuad())

    currentWord = lex()
    if statements() == 1:
        return 1

    labelslist = labelslist + makeList(nextQuad())
    ifList = makeList(nextQuad())
    genQuad('jump', '_', '_', '_')
    backpatch(condition_false, nextQuad())

    if elsepart() == 1:
        return 1

    backpatch(ifList, nextQuad())
    return 0


def elsepart():

    global currentWord
    currentWord = lex()
    if currentWord != "else":
        return 0

    currentWord = lex()

    if statements() == 1:
        return 1

    return 0


def whilestat():
    global currentWord
    global expectation
    global labelslist
    currentWord = lex()

    condQuad = nextQuad()

    if currentWord != "(":
        expectation = "("
        return 1

    currentWord = lex()

    condition_total = condition()
    if condition_total == 1:
        return 1

    condition_true = condition_total[0]
    condition_false= condition_total[1]

    if currentWord != ")":
        expectation = ")"
        return 1

    backpatch(condition_true, nextQuad())

    currentWord = lex()
    if statements() == 1:
        return 1

    labelslist = labelslist + makeList(nextQuad())
    genQuad('jump', '_', '_', condQuad)
    backpatch(condition_false, nextQuad())
    currentWord = lex()


    return 0


def switchcasestat():
    global currentWord
    global expectation
    global labelslist

    exitList = emptyList()
    currentWord = lex()

    while True:

        if currentWord != "case":

            if currentWord != "default":
                expectation = "default"
                return 1

            currentWord = lex()
            if statements() == 1:
                return 1

            backpatch(exitList, nextQuad())
            return 0

        currentWord = lex()

        if currentWord != "(":
            expectation = "("
            return 1

        currentWord = lex()

        condition_total = condition()
        if condition_total == 1:
            return 1

        condition_true = condition_total[0]
        condition_false= condition_total[1]

        if currentWord != ")":
            expectation = ")"
            return 1

        backpatch(condition_true, nextQuad())

        currentWord = lex()
        if statements() == 1:
            return 1

        labelslist = labelslist + makeList(nextQuad())
        t = makeList(nextQuad())
        genQuad('jump', '_', '_', '_')
        exitList = mergeList(exitList, t)
        backpatch(condition_false, nextQuad())

        currentWord = lex()


def forcasestat():
    global currentWord
    global expectation
    global labelslist
    currentWord = lex()

    exitList = emptyList()
    firstCondQuad = nextQuad()

    while True:

        if currentWord != "case":

            if currentWord != "default":
                expectation = "default"
                return 1

            currentWord = lex()
            if statements() == 1:
                return 1

            backpatch(exitList, firstCondQuad)
            return 0

        currentWord = lex()

        if currentWord != "(":
            expectation = "("
            return 1

        currentWord = lex()

        condition_total = condition()
        if condition_total == 1:
            return 1

        condition_true = condition_total[0]
        condition_false= condition_total[1]
        if currentWord != ")":
            expectation = ")"
            return 1

        backpatch(condition_true, nextQuad())

        currentWord = lex()
        if statements() == 1:
            return 1

        labelslist = labelslist + makeList(nextQuad())
        t = makeList(nextQuad())
        genQuad('jump', '_', '_', '_')
        exitList = mergeList(exitList, t)
        backpatch(condition_false, nextQuad())

        currentWord = lex()


def incasestat():
    global currentWord
    global expectation
    global labelslist

    currentWord = lex()

    flag = newTemp()
    labelslist = labelslist + makeList(nextQuad())
    firstCondQuad = nextQuad()
    genQuad(':=', 0, '_', flag)

    while True:

        if currentWord != "case":
            labelslist = labelslist + makeList(nextQuad())
            genQuad('=', 1, flag, firstCondQuad)
            return 0

        currentWord = lex()

        if currentWord != "(":
            expectation = "("
            return 1

        currentWord = lex()

        condition_total = condition()
        if condition_total == 1:
            return 1

        condition_true = condition_total[0]
        condition_false= condition_total[1]

        if currentWord != ")":
            expectation = ")"
            return 1

        backpatch(condition_true, nextQuad())

        currentWord = lex()
        if statements() == 1:
            return 1

        labelslist = labelslist + makeList(nextQuad())
        genQuad(':=', 0, '_', flag)
        backpatch(condition_false, nextQuad())

        currentWord = lex()


def returnstat():
    global currentWord
    global expectation
    global labelslist

    currentWord = lex()
    if currentWord != '(':
        expectation = "("
        return 1

    currentWord = lex()

    returnVal = expression()
    if returnVal == 1:
        return 1

    labelslist = labelslist + makeList(nextQuad())
    genQuad('ret', returnVal, '_', '_')

    if currentWord != ')':
        expectation = ")"
        return 1

    currentWord = lex()

    return 0


def callstat():
    global currentWord
    global expectation
    global currentCalling
    global labelslist

    currentWord = lex()

    if currentType != "Word":
        return 1

    check = searchEntity(currentWord)
    if check == -1:
        print("Error in line " + str(line) + ": No function found named \"" + currentWord + "\"")
        exit()
    elif check[0].__class__.__name__ != "Procedure":
        print("Error in line " + str(line) + ": Procedure type was expected after 'call'. \"" + currentWord + "\" is "+check[0].__class__.__name__+" type")
        exit()

    currentCalling = currentCalling + [currentWord]

    currentWord = lex()
    if currentWord != '(':
        expectation = "("
        return 1

    if actualparlist() == 1:
        return 1

    if currentWord != ')':
        expectation = ")"
        return 1

    labelslist = labelslist + makeList(nextQuad())
    callerName = currentCalling.pop()
    genQuad('call', callerName, '_', '_')

    currentWord = lex()

    return 0


def printstat():
    global currentWord
    global expectation
    global labelslist

    currentWord = lex()
    if currentWord != '(':
        expectation = "("
        return 1

    currentWord = lex()

    E_place = expression()
    if E_place == 1:
        return 1

    if currentWord != ')':
        expectation = ")"
        return 1

    labelslist = labelslist + makeList(nextQuad())
    genQuad('out', '_', '_', E_place)

    currentWord = lex()
    return 0


def inputstat():
    global currentWord
    global expectation
    global labelslist

    currentWord = lex()
    if currentWord != '(':
        expectation = "("
        return 1

    currentWord = lex()

    if currentType != "Word":
        return 1

    check = searchEntity(currentWord)
    if check == -1:
        print("Error in line " + str(line) + ": No variable found named \"" + currentWord + "\"")
        exit()
    elif check[0].__class__.__name__ != "Variable" and check[0].__class__.__name__ != "Parameter":
        print("Error in line " + str(line) + ": Variable type was expected after 'call'. \"" + currentWord + "\" is "+check[0].__class__.__name__+" type")
        exit()

    E_place = currentWord

    currentWord = lex()

    if currentWord != ')':
        expectation = ")"
        return 1

    # endiamesos
    labelslist = labelslist + makeList(nextQuad())
    genQuad('in', '_', '_', E_place)

    currentWord = lex()
    return 0


def actualparlist():
    global currentWord
    global labelslist
    global currentCalling
    global lastWord

    parNamesList = []
    parTypesList = []

    thisFunc = searchEntity(lastWord)
    currentWord = lex()

    if not (currentWord == "in" or currentWord == "inout"):
        return 0  # No variable

    if currentWord == "in":
        parType = "cv"
    else:
        parType = "ref"

    # At least one

    parTotal = actualparitem()
    if parTotal == 1:
        return 1

    parName = parTotal[0]

    parNamesList = parNamesList + [parName]
    parTypesList = parTypesList + [parType]



    while True:

        if currentWord != ",":

            if len(thisFunc[0].formalParameters) != len(parNamesList):
                print("ERROR at line " + str(line) + ": There must be "+str(len(thisFunc[0].formalParameters))+" parameters in '" + thisFunc[0].name + "'. ("+str(len(parNamesList))+" found)")
                exit()

            for i in range(0, len(parNamesList)):
                labelslist = labelslist + makeList(nextQuad())
                genQuad('par', parNamesList[i], parTypesList[i], '_')

                if parTypesList[i] != thisFunc[0].formalParameters[i].mode:
                    print("ERROR at line " + str(line) + ": Parameter at position "+str(i+1)+" must be '" + thisFunc[0].formalParameters[i].mode + "' type")
                    exit()

            return 0

        currentWord = lex()

        parTotal = actualparitem()
        if parTotal == 1:
            return 1

        parName = parTotal[0]
        parType = parTotal[1]

        parNamesList = parNamesList + [parName]
        parTypesList = parTypesList + [parType]



def actualparitem():
    global currentWord
    global currentType

    if currentWord == "in":
        currentWord = lex()
        parName = expression()
        return [parName,"cv"]

    elif currentWord == "inout":
        currentWord = lex()
        if currentType != "Word":
            return 1

        check = searchEntity(currentWord)
        if check == -1 or (check[0].__class__.__name__ != "Variable" and check[0].__class__.__name__ != "Parameter"):
            print("ERROR at line "+str(line)+": There is no variable '"+currentWord+"' to put as a inout type parameter")
            exit()

        currentWord = lex()
        return [lastWord,"ref"]

    else:
        return 1



def condition():
    global currentWord

    Q_total = boolterm()
    if Q_total == 1:
        return 1

    Q1_true = Q_total[0]
    Q1_false= Q_total[1]

    B_true = Q1_true
    B_false = Q1_false

    while True:
        if currentWord != "or":
            return [B_true, B_false]

        backpatch(B_false, nextQuad())

        currentWord = lex()

        Q_total = boolterm()
        if Q_total == 1:
            return 1

        Q2_true = Q_total[0]
        Q2_false = Q_total[1]

        B_true = mergeList(B_true, Q2_true)
        B_false= Q2_false


def boolterm():
    global currentWord

    R_total = boolfactor()
    if R_total == 1:
        return 1

    R1_true = R_total[0]
    R1_false = R_total[1]

    Q_true = R1_true
    Q_false= R1_false

    while True:
        if currentWord != "and":
            return [Q_true, Q_false]

        backpatch(Q_true, nextQuad())

        currentWord = lex()

        R_total = boolfactor()
        if R_total == 1:
            return 1

        R2_true = R_total[0]
        R2_false = R_total[1]

        Q_false= mergeList(Q_false, R2_false)
        Q_true = R2_true


def boolfactor():
    global currentWord
    global expectation
    global labelslist

    if currentWord == "not":
        currentWord = lex()

        if currentWord != '[':
            expectation = "["
            return 1

        currentWord = lex()

        B_total = condition()
        if B_total == 1:
            return 1

        B_true = B_total[0]
        B_false = B_total[1]

        if currentWord != ']':
            expectation = "]"
            return 1

        R_true = B_false
        R_false = B_true

        currentWord = lex()
        return [R_true, R_false]

    elif currentWord == '[':

        currentWord = lex()

        B_total = condition()
        if B_total == 1:
            return 1

        B_true = B_total[0]
        B_false= B_total[1]

        if currentWord != ']':
            expectation = "]"
            return 1

        R_true = B_true
        R_false= B_false

        currentWord = lex()
        return [R_true, R_false]

    else:
        E1_place = expression()
        if E1_place == 1:
            return 1

        if not currentWord in relopes:
            return 1

        currentRelopa = currentWord

        currentWord = lex()

        E2_place = expression()
        if E2_place == 1:
            return 1

        labelslist = labelslist + makeList(nextQuad())
        R_true = makeList(nextQuad())
        genQuad(currentRelopa, E1_place, E2_place, "_")
        labelslist = labelslist + makeList(nextQuad())
        R_false = makeList(nextQuad())
        genQuad('jump', '_', '_', '_')

        return [R_true, R_false]


def expression():
    global currentWord
    global labelslist

    flagSign = 0
    if currentWord == '+' or currentWord == '-':  # This is for optionalSign()
        if currentWord =='-':
            flagSign = -1
        currentWord = lex()

    T1_place = term()
    if T1_place == 1:
        return 1

    if flagSign == -1:
        tmp = newTemp()
        labelslist = labelslist + makeList(nextQuad())
        genQuad("*", T1_place, "-1", tmp)

        T1_place = tmp

    E_place = T1_place

    while True:
        if not(currentWord == '+' or currentWord == '-'):
            return E_place

        T1_place = E_place

        sign = currentWord # "-" or "+"
        currentWord = lex()

        T2_place = term()
        if T2_place == 1:
            return 1

        E_place = newTemp()
        labelslist = labelslist + makeList(nextQuad())
        genQuad(sign, T1_place, T2_place, E_place)


def term():
    global currentWord
    global labelslist

    F1_place = factor()
    if F1_place == 1:
        return 1

    T_place = F1_place

    while True:

        if not(currentWord == '*' or currentWord == '/'):
            return T_place

        F1_place = T_place

        sign = currentWord
        currentWord = lex()

        F2_place = factor()
        if F2_place == 1:
            return 1

        T_place = newTemp()
        labelslist = labelslist + makeList(nextQuad())
        genQuad(sign, F1_place, F2_place, T_place)


def factor():
    global currentWord
    global currentType
    global expectation
    global labelslist
    global currentCalling

    F_place = currentWord
    if currentType == "Number":
        currentWord = lex()
        return F_place

    elif currentWord == '(':

        currentWord = lex()
        F_place = expression()

        if F_place == 1:
            return 1

        if currentWord == ')':
            currentWord = lex()
            return F_place
        else:
            expectation = ")"
            return 1

    elif currentType == "Word":  # Variable or function name
        tmpName = currentWord
        check = searchEntity(tmpName)

        currentWord = lex()

        if currentWord == '(':
            if check == -1:
                print("Error in line " + str(line) + ": No procedure found named \"" + tmpName + "\"")
                exit()
            elif check[0].__class__.__name__ != "Function":
                print("Error in line " + str(line) + ": Function type was expected. \"" + tmpName + "\" is " + check[0].__class__.__name__ + " type")
                exit()


            currentCalling = currentCalling + [tmpName]



            if idtail()==1:
                return 1

            F_place = newTemp()

            labelslist = labelslist + makeList(nextQuad())
            genQuad('par', F_place, 'ret', '_')

            callerName = currentCalling.pop()
            labelslist = labelslist + makeList(nextQuad())
            genQuad('call', tmpName, '_', '_')

            return F_place
        else:

            if check == -1:
                print("Error in line " + str(line) + ": No variable found named \"" + tmpName + "\"")
                exit()
            elif check[0].__class__.__name__ != "Variable" and check[0].__class__.__name__ != "Parameter":
                print("Error in line " + str(
                    line) + ": Variable or Parameter type was expected after 'call'. \"" + tmpName + "\" is " + check[
                          0].__class__.__name__ + " type")
                exit()


            return F_place

    else:
        return 1


def idtail():
    global currentWord
    global currentType
    global expectation

    if actualparlist() == 1:
        return 1

    if currentWord != ')':
        expectation = ")"
        return 1

    currentWord = lex()

    return 0

#------------------------------------Endiamesos Kodikas---------------------

def genQuad(operator, operand1, operand2, operand3):
    quadz.append(Quad(operator, operand1, operand2, operand3))
    return 0

def nextQuad():
    return len(quadz) + 1

def newTemp():
    global t_name
    global totaloffset

    t_name = t_name + 1
    totaloffset = totaloffset + 4
    addNewRegister("TemporaryVariable", "T_" + str(t_name), totaloffset)
    return "T_" + str(t_name)

def emptyList():
    definitelyEmptyList = []
    return definitelyEmptyList

def makeList(label):
    definitelyLabel = [label]
    return definitelyLabel

def mergeList(list1, list2):
    mergedList = list1 + list2
    return mergedList

def backpatch(list,label):
    global labelslist, quadz

    counter = 0
    for i in quadz:
        for j in list:
            if labelslist[counter]==j:
                i.operand3 = label
        counter = counter + 1
    return 0

#--------------------------------------------------

def addNewRegister(entityType, name, extraOp):
    global myTable
    if entityType == "Variable":
        myTable.scopes[-1].entities.append(Variable(name, "Int", extraOp))
    elif entityType == "FormalParameter":
        myTable.scopes[-1].entities.append(FormalParameter(name, "Int", extraOp))
    elif entityType == "Procedure":
        # name, startingQuad, framelength, formalParameters
        myTable.scopes[-1].entities.append(Procedure(name, "", "", []))
    elif entityType == "Function":
        # name, datatype, startingQuad, framelength, formalParameters
        myTable.scopes[-1].entities.append(Function(name, "Int", "", "", []))
    elif entityType == "Parameter":
        # name, datatype, mode, offset):
        myTable.scopes[-1].entities.append(Parameter(name, "Int", extraOp[0], extraOp[1]))
    elif entityType == "TemporaryVariable":
        myTable.scopes[-1].entities.append(TemporaryVariable(name, "Int", extraOp))
    else:
        return 1

    return 0

def addLayer():
    global myTable

    if len(myTable.scopes) == 0:
        myTable.scopes = [Scope(0, [])]
    else:
        tmp = myTable.scopes[-1].level
        myTable.scopes.append(Scope(tmp+1, []))

    return 0

def removeLayer():
    global myTable

    printBoard()

    if len(myTable.scopes) == 0:
        return 0
    else:
        myTable.scopes.pop()

    return 0

def updateEntity(flag, value):
    global myTable

    if flag == 0:
        myTable.scopes[-2].entities[-1].startingQuad = value
    elif flag ==1:
        myTable.scopes[-2].entities[-1].framelength = value
    return 0

def addParameter():
    global myTable
    currentParameter = myTable.scopes[-1].entities[-1]
    myTable.scopes[-2].entities[-1].formalParameters.append(currentParameter)

    return 0

def searchEntity(ent_name):
    global myTable
    for i in range(len(myTable.scopes)-1, 0, -1):
        for j in myTable.scopes[i].entities:
            if j.name == ent_name:
                return [j, myTable.scopes[i].level]

    for j in myTable.scopes[0].entities:
        if j.name == ent_name:
            return [j, 0]

    return -1

def printBoard():
    symbFile.write("----------------------------------------------\n----------------------------------------------\n")
    for i in myTable.scopes:
        symbFile.write("\n-----Level "+str(i.level)+"------\n")
        for j in i.entities:
            tmpType = j.__class__.__name__
            if tmpType == "Function" or tmpType == "Procedure":
                symbFile.write("name: "+j.name + ", startingQuad: " +str(j.startingQuad)+", framelength: "+str(j.framelength))
                if tmpType == "Function":
                    symbFile.write(", datatype: "+j.datatype)

                symbFile.write(", formalParameters: ")

                commaCounter = 0
                for k in j.formalParameters:
                    symbFile.write(k.name)
                    symbFile.write("("+k.mode+")")
                    if commaCounter < len(j.formalParameters)-1:
                        symbFile.write(", ")
                    commaCounter = commaCounter + 1
                symbFile.write("\n")
            else:
                attrs = vars(j)
                symbFile.write(', '.join("%s: %s" % item for item in attrs.items()))
                symbFile.write("\n")

    symbFile.write("\n\n")
    return 0

#-----------final code----------------

def writeLabel():
    global labelFlag

    finalFile.write("L_"+str(labelFlag)+":\n")
    labelFlag = labelFlag + 1
    return labelFlag

def gnlvcode(v):
    check = searchEntity(v)

    if check == -1:
        print("ERROR at line "+str(line)+": variable '"+ v +"' doesn't exist")
        quit()

    if check[0].__class__.__name__ == "Procedure" or check[0].__class__.__name__ == "Function":
        print("ERROR at line " + str(line) + ": '" + v + "' is not a 'variable' type")
        quit()

    tmpEntity = check[0]
    tmpLevel = check[1]

    produce("lw", "t0", "-4(sp)", "")
    for i in range(tmpLevel+1, len(myTable.scopes)-1):
        produce("lw", "t0", "-4(t0)", "")

    produce("addi", "t0", "t0", "-" + str(tmpEntity.offset))

    return v

def loadvr(v, reg):

    if v.isdigit():
        produce("li", reg, v, "")
        return 0

    check = searchEntity(v)

    if check == -1:
        print("ERROR at line "+str(line)+": variable '"+ v +"' doesn't exist")
        quit()

    if check[0].__class__.__name__ == "Procedure" or check[0].__class__.__name__ == "Function":
        print("ERROR at line " + str(line) + ": '" + v + "' is not a variable type")
        quit()

    tmpEntity = check[0]
    tmpLevel = check[1]
    tmpType = tmpEntity.__class__.__name__

    if tmpLevel == len(myTable.scopes)-1:#belongs at the current function

        if tmpType != "Parameter" and tmpType != "FormalParameter":
            produce("lw", reg, "-" + str(tmpEntity.offset)+"(sp)", "")

        else:
            if tmpEntity.mode == "cv":#in x
                produce("lw", reg, "-" + str(tmpEntity.offset)+"(sp)", "")
            else:#inout x
                produce("lw", "t0", "-" + str(tmpEntity.offset) + "(sp)", "")
                produce("lw", reg, "(t0)", "")

    elif tmpLevel == 0:#is "global"
        produce("lw", reg, "-" + str(tmpEntity.offset)+"(gp)", "")

    else:#belongs to a (grand) parent
        if tmpType != "Parameter" and tmpType != "FormalParameter":
            gnlvcode(v)
            produce("lw", reg, "(t0)", "")

        else:
            if tmpEntity.mode == "cv":
                gnlvcode(v)
                produce("lw", reg, "(t0)", "")
            else:
                gnlvcode(v)
                produce("lw", "t0", "(t0)", "")
                produce("lw", reg, "(t0)", "")
    return 0

def storevr(reg, v):

    if v.isdigit():
        loadvr(v, reg)
        produce("si", reg, v, "")
        return 0

    check = searchEntity(v)

    if check == -1:
        print("ERROR at line "+str(line)+": variable "+ v +" doesn't exist")
        quit()

    if check[0].__class__.__name__ == "Procedure" or check[0].__class__.__name__ == "Function":
        print("ERROR at line " + str(line) + ": '" + v + "' is not a variable type")
        quit()

    tmpEntity = check[0]
    tmpLevel = check[1]
    tmpType = tmpEntity.__class__.__name__

    if tmpLevel == len(myTable.scopes)-1:

        if tmpType != "Parameter" and tmpType != "FormalParameter":
            produce("sw", reg, "-" + str(tmpEntity.offset)+"(sp)", "")

        else:
            if tmpEntity.mode == "cv":#in x
                produce("sw", reg, "-" + str(tmpEntity.offset)+"(sp)", "")
            else:#inout x
                produce("lw", "t0", "-" + str(tmpEntity.offset) + "(sp)", "")
                produce("sw", reg, "(t0)", "")

    elif tmpLevel == 0:
        produce("sw", reg, "-" + str(tmpEntity.offset)+"(gp)", "")

    else:
        if tmpType != "Parameter" and tmpType != "FormalParameter":
            gnlvcode(v)
            produce("sw", reg, "(t0)", "")

        else:
            if tmpEntity.mode == "cv":
                gnlvcode(v)
                produce("sw", reg, "(t0)", "")
            else:
                gnlvcode(v)
                produce("lw", "t0", "(t0)", "")
                produce("sw", reg, "(t0)", "")
    return 0

def produce(operator, operand1, operand2, operand3):

    finalFile.write("\t" + str(operator))

    if operand1 != "":
        finalFile.write(" " + str(operand1))

    if operand2 != "":
        finalFile.write(", " + str(operand2))

    if operand3 != "":
        finalFile.write(", " + str(operand3))

    finalFile.write("\n")
    return 0

def createFinalCode(start, end):
    global quadz

    parFlag = 0

    if quadz[-2].operator == "halt":
        finalFile.write("L_main_:\n")
    else:
        finalFile.write("L_"+quadz[start].operand1+":\n")

    for i in range(start, end):
        writeLabel()

        if str(quadz[i].operator) == ":=":

            loadvr(str(quadz[i].operand1), "t0")
            storevr("t0", str(quadz[i].operand3))

        elif str(quadz[i].operator) == "+":

            loadvr(str(quadz[i].operand1), "t1")
            loadvr(str(quadz[i].operand2), "t2")
            produce("add", "t1", "t2", "t1")
            storevr("t1", str(quadz[i].operand3))

        elif str(quadz[i].operator) == "-":

            loadvr(str(quadz[i].operand1), "t1")
            loadvr(str(quadz[i].operand2), "t2")
            produce("sub", "t1", "t2", "t1")
            storevr("t1", str(quadz[i].operand3))

        elif str(quadz[i].operator) == "*":

            loadvr(str(quadz[i].operand1), "t1")
            loadvr(str(quadz[i].operand2), "t2")
            produce("mul", "t1", "t2", "t1")
            storevr("t1", str(quadz[i].operand3))

        elif str(quadz[i].operator) == "/":

            loadvr(str(quadz[i].operand1), "t1")
            loadvr(str(quadz[i].operand2), "t2")
            produce("div", "t1", "t2", "t1")
            storevr("t1", str(quadz[i].operand3))

        elif str(quadz[i].operator) == "jump":
            produce("j", "L_"+str(quadz[i].operand3), "", "")

        elif str(quadz[i].operator) in relopes:

            if quadz[i].operator == "=":
                finalRelopa = "beq"
            elif quadz[i].operator == "<>":
                finalRelopa = "bne"
            elif quadz[i].operator == "<":
                finalRelopa = "blt"
            elif quadz[i].operator == ">":
                finalRelopa = "bgt"
            elif quadz[i].operator == "<=":
                finalRelopa = "ble"
            else:
                finalRelopa = "bge"

            loadvr(str(quadz[i].operand1), "t1")
            loadvr(str(quadz[i].operand2), "t2")
            produce(finalRelopa, "t1", "t2", "L_"+str(quadz[i].operand3))

        elif str(quadz[i].operator) == "par":
            currentFramelength = 12

            if len(myTable.scopes)>1:
                callerFunc = searchEntity(quadz[start].operand1)
                currentFramelength = callerFunc[0].framelength
            else:
                for j in myTable.scopes[-1].entities:
                    tmpType = j.__class__.__name__
                    if tmpType == "Variable" or tmpType == "TemporaryVariable":
                        currentFramelength = j.offset

            parNum = 0
            j = i

            while quadz[j].operator == "par":#counts for the position of the parameter
                j = j - 1
                parNum = parNum + 1

            d = 12 + (parNum - 1) * 4

            if parNum == 1:
                parFlag = 1
                produce("addi", "fp", "sp", str(currentFramelength))


            if quadz[i].operand2 == "cv":
                loadvr(quadz[i].operand1, "t0")
                produce("sw", "t0", "-" + str(d) +"(fp)", "")

            elif quadz[i].operand2 == "ref":

                check = searchEntity(quadz[i].operand1)

                case = 0
                if check[1]+1 == len(myTable.scopes) and check[1]!=0:
                    if check[0].__class__.__name__ == "Parameter" or check[0].__class__.__name__ == "FormalParameter":
                        if check[0].mode == "cv":
                            case = 1
                        else:
                            case = 4
                    else:
                        case = 1

                elif check[1]+1 < len(myTable.scopes) and check[1]!=0:
                    if check[0].__class__.__name__ == "Parameter" or check[0].__class__.__name__ == "FormalParameter":
                        if check[0].mode == "cv":
                            case = 2
                        else:
                            case = 5
                    else:
                        case = 2

                else:
                    case = 3

                if case == 1:

                    produce("addi", "t0", "sp", "-" + str(check[0].offset))
                    produce("sw", "t0", "-" + str(d)+"(fp)", "")

                elif case == 2:
                    gnlvcode(quadz[i].operand1)
                    produce("sw", "t0", "-" + str(d)+"(fp)", "")

                elif case == 3:
                    produce("addi", "t0", "gp", "-" + str(check[0].offset))
                    produce("sw", "t0", "-" + str(d) + "(gp)", "")

                elif case == 4:
                    produce("lw", "t0", "-" + str(check[0].offset)+"(sp)", "")
                    produce("sw", "t0", "-" + str(d) + "(fp)", "")

                elif case == 5:
                    gnlvcode(quadz[i].operand1)
                    produce("lw", "t0", "(t0)", "")
                    produce("sw", "t0", "-"+str(d)+"(fp)", "")

            else:#ret
                check = searchEntity(quadz[i].operand1)
                produce("addi", "t0", "sp", "-"+str(check[0].offset))
                produce("sw", "t0", "-8(fp)", "")

        elif str(quadz[i].operator) == "ret":
            loadvr(quadz[i].operand1, "t1")
            produce("lw", "t0", "-8(sp)", "")
            produce("sw", "t1", "(t0)", "")

        elif str(quadz[i].operator) == "call":
            checkCalling = searchEntity(quadz[i].operand1)

            if len(myTable.scopes) > 1:
                checkCaller = searchEntity(quadz[start].operand1)
            else:
                checkCaller = ["main_", -1]

            currentFramelength = 12

            if len(myTable.scopes) > 1:
                currentFramelength = checkCalling[0].framelength
            else:
                for j in myTable.scopes[-1].entities:
                    tmpType = j.__class__.__name__
                    if tmpType == "Variable" or tmpType == "TemporaryVariable":
                        currentFramelength = j.offset

            if parFlag == 0:
                produce("addi", "fp", "sp", str(currentFramelength))
            else:
                parFlag = 0

            if checkCalling[1]==checkCaller[1]:#they both have the same parent
                produce("lw", "t0", "-4(sp)", "")
                produce("sw", "t0", "-4(fp)", "")

            else: #caller is parent of calling
                produce("sw", "sp", "-4(fp)", "")

            produce("addi", "sp", "sp", str(currentFramelength))
            produce("jal", "L_"+checkCalling[0].name, "", "")
            produce("addi", "sp", "sp", "-" + str(currentFramelength))

        elif str(quadz[i].operator) == "begin_block":
            if quadz[-2].operator != "halt":
                produce("sw", "ra", "(sp)", "")
            else:
                currentFramelength = 12
                for j in myTable.scopes[-1].entities:
                    tmpType = j.__class__.__name__
                    if tmpType == "Variable" or tmpType == "TemporaryVariable":
                        currentFramelength = j.offset
                produce("addi", "sp", "sp", str(currentFramelength+4))
                produce("mv", "gp", "sp", "")

        elif str(quadz[i].operator) == "end_block":
            if quadz[-2].operator != "halt":
                produce("lw", "ra", "(sp)", "")
                produce("jr", "ra", "", "")
            else:
                produce("li", "a0", "0", "")
                produce("li", "a7", "93", "")
                produce("ecall", "", "", "")

        elif str(quadz[i].operator) == "in":
            produce("li","a7","5","")
            produce("ecall", "", "", "")
            storevr("a0", str(quadz[i].operand3))

        elif str(quadz[i].operator) == "out":
            loadvr(str(quadz[i].operand3), "a0")
            produce("li","a7","1","")
            produce("ecall", "", "", "")

            produce("la", "a0", "str_nl", "")
            produce("li", "a7", "4", "")
            produce("ecall", "", "", "")





    return 0

#-----------files------------------

def createCfile():
    global cFile
    cFile.write("#include <stdio.h>\n\n\n")
    cFile.write("int main()\n" + "{\n")

    fullVarList = varNames

    for i in range(t_name, 0, -1):
        fullVarList = fullVarList + ["T_"+str(i)]

    if len(fullVarList)!=0:
        cFile.write("\tint")
        for i in range(0, len(fullVarList)):
            cFile.write(" "+fullVarList[i])
            if i == len(fullVarList)-1:
                cFile.write(";\n")
            else:
                cFile.write(",")

    labNum = 0
    for i in quadz:
        cFile.write("\nL_"+str(labelslist[labNum])+":\t")
        if i.operator == "halt":
            cFile.write("{}")
            break

        elif i.operator == ":=":
            cFile.write(i.operand3+"="+str(i.operand1)+";")
            a = 1

        elif i.operator in ['+','-','*','/']:
            cFile.write(i.operand3 + "=" + str(i.operand1) + i.operator + str(i.operand2) + ";")

        elif i.operator == "jump":
            cFile.write("goto L_" + str(i.operand3) + ";")

        elif i.operator in relopes:
            if i.operator == '=':
                tmpRel = "=="
            elif i.operator == '<>':
                tmpRel = "!="
            else:
                tmpRel = i.operator

            cFile.write("if ("+str(i.operand1) + tmpRel + str(i.operand2) + ")\n\t\tgoto L_" + str(i.operand3) + ";")

        elif i.operator == "ret":
            cFile.write("return " + i.operand1 + ";")

        elif i.operator == "in":
            cFile.write('scanf(" %d", &' + str(i.operand3) + ");")

        elif i.operator == "out":
            cFile.write(r'printf("%d\n", ' + str(i.operand3) + ");")

        labNum = labNum + 1

    cFile.write("\n}")
    return 0

program()

intFile = open('output.int', 'w')
pos = 0
for i in quadz:
    intFile.write(str(labelslist[pos])+": "+str(i.operator)+", "+str(i.operand1)+", "+str(i.operand2)+", "+str(i.operand3)+"\n")
    pos = pos+1
print("output.int created")


if flagForCfile==0:
    cFile = open('output.c', 'w')
    createCfile()
    cFile.close()
    print("output.c created")
else:
    print("No output.c was created because there are functions in the code")

intFile.close()
symbFile.close()
finalFile.close()
print("output.symb created")
print("output.asm created")