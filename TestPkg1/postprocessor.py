from util import Counter
import os
pythonKeywords = ['False', 'True', 'and', 'or', 'not', 'def',
                  'elif', 'else', 'if', 'while', 'for', 'in',
                  'range', 'return', 'print', 'import']

definedVars = Counter()

'''
save thing
'''
def proofread():
    #read in file
    myFile = open("test.txt", "r")
    lines = myFile.readlines()
    myFile.close()

    #populate definedVars
    declarePythonLanguage()
    declareVars(lines)

    #populate usedVars
    usedVars = findVariables(lines)
    proofread =  spellCheck(lines,usedVars)
    proofread = os.linesep.join([s for s in proofread.splitlines() if s])
    withTabs = addTabs(proofread,[1,2,3])
    print withTabs

def declarePythonLanguage():
    for word in pythonKeywords:
        definedVars[word] = -1

'''
This function extracts all declared variables from a text file.
Rules:
    1) variables can only be declared on the left hand side of an '=' character
    2) variables contain no spaces
    3) multiple variable declaration can be delimited by ',' or ' '
    4) for ease of parsing, imports are considered variables
'''
def declareVars(lines):
    lineNum = 0
    for line in lines:
        lineNum += 1
        if '=' in line:
            lhs = str.split(line, '=')[0].strip()
            if ',' in lhs:
                lhs = str.split(lhs, ',')
                for var in lhs:
                    addToDict(var.strip(),lineNum)
            elif ' ' in lhs:
                lhs = str.split(lhs, ' ')
                for var in lhs:
                    addToDict(var.strip(),lineNum)
            else:
                addToDict(lhs,lineNum)
        if 'import' in line:
            addToDict(str.split(line, 'import')[1].strip(),lineNum)
        if 'for' in line:
            rhs = str.split(line,'for')[1].strip()
            addToDict(str.split(rhs,' ')[0].strip(),lineNum)

'''
Adds item at a give line number to definedVars
'''
def addToDict(item,lineNum):
    if definedVars[item] == 0:
        definedVars[item] = lineNum

'''
This function collects and returns an ordered list of lists of all used variables mapped to their line.
Data will look like...
[[l1_var1, l1_var2, l1_var3, ...],
 [l2_var1, l2_var2, l2_var3, ...],
 [l3_var1, l3_var2, l3_var3, ...],
 [...,   , ...    , ...    , ...]]

Rules:
    1) variables cannot begin with a number
    2) variables cannot begin with either ' or "
    3) variables contain no spaces
    4) a variable appears before the '.' character
    5) variable(s) appear inside of a pair of the '(' and ')' characters, delimited by the ',' character
    6) variables can only be declared on the left hand side of an '=' character
'''
def findVariables(lines):
    toReturn = []
    for line in lines:
        curLine = []
        for arg1 in getInsideOfParenthesis(line.strip()):       #identify case for condition 5
            arg1 = str.split(arg1, ',')
            arg1 = [x for x in arg1 if x is not '']
            for arg2 in arg1:                                   #satisfy condition 5's parsing
                arg2 = str.split(arg2, '=')
                for arg3 in arg2:                               #don't have '=' in a variable name
                    arg3 = arg3.strip()
                    if (arg3[0].isalpha()):                     #satisfy condition 1,2
                        arg3 = str.split(arg3, '.')[0].strip()  #satisfy condition 4
                        for arg4 in str.split(arg3, ' '):       #satisfy condition 3
                            curLine.append(str.split(arg4,':')[0].strip())
        toReturn.append(curLine)
    return toReturn

'''
parses out arguments between parenthesis
that is, '45(23)(4)4' returns ['45','23',None,'4','4']
'''
def getInsideOfParenthesis(s):
    toReturn = []
    leftIndex = -1
    for index in range(0,len(s),1):
        if(s[index] == '(' or s[index] == ')'):
            toReturn.append(s[leftIndex+1:index])
            leftIndex = index
    if leftIndex != len(s)-1:
        toReturn.append(s[leftIndex+1:len(s)])
    return toReturn


'''
This function iterates through all usedVars in a parsed document.  It checks them against defined variables.
Variables that are used before their definition are deemed "wrong", and a spellcheck is attempted.  Specifically,
A getScore heuristic is evaluated on the "wrong" word.  If it's similar to a previously defined word, it is replaced.
While these iterations and replacements are happening, a final, return string is built and eventually returned.
'''
def spellCheck(lines, usedVars):
    toReturn = ""
    for i in range(len(lines)):
        leftIndex = 0
        lineGood = True
        for var in usedVars[i]:
            if definedVars[var] != 0:
                continue
            lineGood = False
            matchedLetters = 0
            match = getMatch(var,i+1)

            for letter in lines[i]:
                if(letter==var[matchedLetters]):
                    matchedLetters += 1
                else:
                    toReturn += lines[i][leftIndex:leftIndex+matchedLetters+1]
                    leftIndex += matchedLetters + 1
                    matchedLetters = 0

                if matchedLetters == len(var):
                    toReturn += match
                    leftIndex += matchedLetters
                    matchedLetters = 0
        if lineGood:
            toReturn += lines[i]
    return toReturn

'''
What makes two words similar?  This function returns an attempted mathematical answer
    +Number of same letters (num == count of same letters in 2nd arg, den == len of 2nd arg)
        (anteater,retaetna) = 8/8
        (fleas,flsea)       = 5/5
        (fleas,xxfxx)       = 1/5
        (clock,clocks)      = 5/6
        (clocks,clock)      = 5/5
    +Order of letters by neighbors (each letter in the 2nd word contained in the 1st word check left, right.
    matches make numerator++.  Denominator is 2*len(arg2).  Duplicate letters in first word are handled by averaging.
        (ten,txn)           = 4/6
        (ten,txxn)          = 4/8
        (txxn,ten)          = 4/6

if(aresimlilar):
    replace word with dictionary match
'''
def getScore(s1,s2):
    if abs(len(s1)-len(s2)) > 1:
        return 0

    summ = 0
    for letter in s2:
        if letter in s1:
            summ += 1
    n1 = summ/len(s2)

    tot = 0
    for j in range(len(s2)):
        if not s2[j] in s1:
            continue
        for i in range(len(s1)):
            if(s1[i] != s2[j]):
                continue
            if i == 0 or j == 0:
                tot += (i == 0 and j == 0)
            else:
                tot += s1[i-1] == s2[j-1]
            if i == len(s1)-1 or j == len(s2)-1:
                tot += (i == len(s1)-1 and j == len(s2)-1)
            else:
                tot += s1[i+1] == s2[j+1]
    n2 = tot/(2.*len(s2))

    if(n2 > 1):
        n2 = 1
    if(n1 > 1):
        n1 = 1
    return (n1+n2)/2

'''
calls the getScore function between every defined variable and the given variable, then returns the best match
'''
def getMatch(var,lineNum):
    toReturn = var
    maxx = 0
    for s in definedVars:
        if definedVars[s] == 0 or definedVars[s] >= lineNum:
            continue

        if getScore(s,var) > maxx:
            toReturn = s
            maxx = getScore(s,var)

    return toReturn

def addTabs(s,tabs):
    toReturn = ""
    lines = str.split(s,'\n')
    for i in range(min(len(tabs),len(lines))):
        toReturn += tabs[i]*"   " + lines[i] + "\n"

    return toReturn
