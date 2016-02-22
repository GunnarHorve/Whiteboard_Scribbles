import keyword

from util import Counter

definedVars = Counter()


def proofread_from_file(file_path, tabs):
    """
    Proofreads the given file for correct Python.
    :param file_path: the path to the file to read
    """
    with open(file_path, "r") as my_file:
        lines = my_file.readlines()
        my_file.close()
        return proofread(lines, tabs)


def proofread(lines, tabs):
    """
    Proofresd the given list of lines for correct Python
    :param lines: the list of lines to proofread
    :param tabs: a list of integers defining the tab levels of the lines
    """
    # populate definedVars
    _declare_python_language()
    _declare_vars(lines)

    # populate used_vars
    used_vars = _find_variables(lines)
    proof = _check_spelling(lines, used_vars)
    # proof = os.linesep.join([s for s in proof.splitlines() if s])
    with_tabs = _add_tabs(proof, tabs)

    return with_tabs


def _declare_python_language():
    for word in keyword.kwlist + dir(__builtins__):
        definedVars[word] = -1


def _declare_vars(lines):
    """
    This function extracts all declared variables from a text file.
    Rules:
        1) variables can only be declared on the left hand side of an '=' character
        2) variables contain no spaces
        3) multiple variable declaration can be delimited by ',' or ' '
        4) for ease of parsing, imports are considered variables
    """
    line_num = 0
    for line in lines:
        line_num += 1
        if '"""' in line:
            # TODO: find matching triple-quote, take everything in between as a literal
            pass
        if "'''" in line:
            # same
            pass
        if '"' in line:
            # TODO: find matching quote, take everything in between as a literal
            # GOTCHA if future work: escaped quotes
            pass
        if "'" in line:
            # same
            pass
        if '[' in line:
            # TODO: treat the letters connected to this on the left as a variable
            # this may go better in findVars
            pass
        if '{' in line:
            # same
            pass

        if '=' in line:
            lhs = str.split(line, '=')[0].strip()
            if ',' in lhs:
                lhs = str.split(lhs, ',')
                for var in lhs:
                    _add_to_dict(var.strip(), line_num)
            elif ' ' in lhs:
                lhs = str.split(lhs, ' ')
                for var in lhs:
                    _add_to_dict(var.strip(), line_num)
            else:
                _add_to_dict(lhs, line_num)
        if 'import' in line:
            _add_to_dict(str.split(line, 'import')[1].strip(), line_num)
        if 'for' in line:
            rhs = str.split(line, 'for')[1].strip()
            _add_to_dict(str.split(rhs, ' ')[0].strip(), line_num)
        if 'def' in line:
            try:
                var = line[line.index('def') + 4: line.index('(')]
                _add_to_dict(var, line_num)
            except:
                pass
        if 'class' in line:
            try:
                var = line[line.index('class') + 6: line.index('(')]
                _add_to_dict(var, line_num)
            except:
                pass


def _add_to_dict(item, line_num):
    """
    Adds item at a give line number to definedVars
    """
    if definedVars[item] == 0:
        definedVars[item] = line_num


def _find_variables(lines):
    """
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
    """
    to_return = []
    for line in lines:
        cur_line = []
        for arg1 in _get_inside_of_parenthesis(line.strip()):  # identify case for condition 5
            arg1 = str.split(arg1, ',')
            arg1 = [x for x in arg1 if x is not '']
            for arg2 in arg1:  # satisfy condition 5's parsing
                arg2 = str.split(arg2, '=')
                for arg3 in arg2:  # don't have '=' in a variable name
                    arg3 = arg3.strip()
                    if arg3 != '' and arg3[0].isalpha():  # satisfy condition 1,2
                        arg3 = str.split(arg3, '.')[0].strip()  # satisfy condition 4
                        for arg4 in str.split(arg3, ' '):  # satisfy condition 3
                            cur_line.append(str.split(arg4, ':')[0].strip())
        to_return.append(cur_line)
    return to_return


def _get_inside_of_parenthesis(string):
    """
    parses out arguments between parenthesis
    that is, '45(23)(4)4' returns ['45','23',None,'4','4']
    """
    to_return = []
    left_index = -1
    for index in range(0, len(string), 1):
        if string[index] == '(' or string[index] == ')':
            to_return.append(string[left_index + 1:index])
            left_index = index
    if left_index != len(string) - 1:
        to_return.append(string[left_index + 1:len(string)])
    return to_return


def _check_spelling(lines, used_vars):
    """
    This function iterates through all usedVars in a parsed document.  It checks them against defined variables.
    Variables that are used before their definition are deemed "wrong", and a spellcheck is attempted.  Specifically,
    A getScore heuristic is evaluated on the "wrong" word. If it's similar to a previously defined word, it is replaced.
    While these iterations and replacements are happening, a final, return string is built and eventually returned.
    """
    to_return = ""
    for i in range(len(lines)):
        left_index = 0
        is_line_good = True
        for var in used_vars[i]:
            if definedVars[var] != 0 or len(var) == 0:
                continue
            is_line_good = False
            matched_letters = 0
            match = _get_match(var, i + 1)

            for letter in lines[i]:
                if letter == var[matched_letters]:
                    matched_letters += 1
                else:
                    to_return += lines[i][left_index:left_index + matched_letters + 1]
                    left_index += matched_letters + 1
                    matched_letters = 0

                if matched_letters == len(var):
                    to_return += match
                    left_index += matched_letters
                    matched_letters = 0
        if is_line_good:
            to_return += lines[i] + '\n'
        else:
            to_return += '\n'
    return to_return


def _get_score(s1, s2):
    """
    What makes two words similar?  This function returns an attempted mathematical answer
        +Number of same letters (num == count of same letters in 2nd arg, den == len of 2nd arg)
            (anteater,retaetna) = 8/8
            (fleas,flsea)       = 5/5
            (fleas,xxfxx)       = 1/5
            (clock,clocks)      = 5/6
            (clocks,clock)      = 5/5
        +Order of letters by neighbors (each letter in the 2nd word contained in the 1st word check left, right.
        matches make numerator++. Denominator is 2*len(arg2). Duplicate letters in first word are handled by averaging.
            (ten,txn)           = 4/6
            (ten,txxn)          = 4/8
            (txxn,ten)          = 4/6

    if(aresimlilar):
        replace word with dictionary match
    """
    if abs(len(s1) - len(s2)) > 1 or len(s1) == 0 or len(s2) == 0:
        return 0

    letter_sum = 0
    for letter in s2:
        if letter in s1:
            letter_sum += 1
    n1 = letter_sum / len(s2)

    tot = 0
    for j in range(len(s2)):
        if not s2[j] in s1:
            continue
        for i in range(len(s1)):
            if s1[i] != s2[j]:
                continue
            if i == 0 or j == 0:
                tot += (i == 0 and j == 0)
            else:
                tot += s1[i - 1] == s2[j - 1]
            if i == len(s1) - 1 or j == len(s2) - 1:
                tot += (i == len(s1) - 1 and j == len(s2) - 1)
            else:
                tot += s1[i + 1] == s2[j + 1]
    n2 = tot / (2. * len(s2))

    if n2 > 1:
        n2 = 1
    if n1 > 1:
        n1 = 1
    return (n1 + n2) / 2


def _get_match(var, line_num):
    """
    calls the getScore function between every defined variable and the given variable, then returns the best match
    """
    to_return = var
    score_max = 0
    for s in definedVars:
        if definedVars[s] == 0 or definedVars[s] >= line_num:
            continue

        if _get_score(s, var) > score_max:
            to_return = s
            score_max = _get_score(s, var)

    return to_return


def _add_tabs(s, tabs):
    to_return = ""
    lines = str.split(s, '\n')
    j = 0
    for i in range(min(len(tabs), len(lines))):
        if i + j >= len(lines):
            break
        line = lines[i + j]
        while line == '':
            to_return += '\n'
            j += 1
            if i + j >= len(lines):
                break
            line = lines[i + j]
        to_return += tabs[i] * "  " + line + "\n"

    return to_return


def main():
    with open('./generate_training_data.py', 'r') as my_file:
        lines = my_file.readlines()
        for i in range(len(lines)):
            lines[i] = lines[i].replace('\t', '').strip(' ').replace('\n', '').replace('\r', '')

        print proofread(lines,
                        [0, 0, 0, 1, 1, 2, 2, 3, 4, 0, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2, 2, 3, 2, 3, 2, 2, 2, 2,
                         2, 2,
                         1, 0, 1])


if __name__ == "__main__":
    main()
