import re
import math

# Includes methods for analyzing class and output settings
class proposition:

    _minimum_row_width = 5 # Width for output of cells in truth table
    _row_padding = 2 # Default left and right padding in each cell 
    _separator_char = "#" # Character to use to construct horizontal borders 
    _column_char = "#" # Character to use between cells

    def __init__(self, text, extended=False):
        text = proposition.process_special_chars(text.lower())
        variables = sorted(set(re.findall(r"\b([a-z])\b", text)))
        formulas = list(variables)
        f = proposition.split(
            [text] if extended is False else proposition.format_strict(text))
        print("Interpreted Input: ", proposition.format_strict(text))
        formulas.extend(f)
        self._formula = text
        self._variables = variables
        self._formulas = formulas

    @staticmethod
    def process_special_chars(text):
        text = [ord(x) for x in text]
        formula = ""
        i = 0
        while i < len(text):
            unit = text[i]

            map = {
                172: "not",
                8743: "and",
                8744: "or",
                8660: "biimplies",
                8658: "implies",
                8593: "nand",
                8853: "xor"
            }

            if unit in map.keys():
                formula += " " + map[unit] + " "
            else:
                formula += chr(unit)
            i += 1
        return formula

    def display_truth_table(self):
        variables = self._variables

        def p_row(vars):
            # 			evaluate (formula, vars)
            j = 0
            row = proposition._column_char
            for f in self._formulas:
                l = (lengths[j] - 1) / 2.0
                row += " ".join(["" for i in range(0,
                                                   1 + int(math.floor(l)))]) + ("1" if proposition.evaluate(f,
                                                                                                            vars) == "TRUE" else "0") + " ".join(["" for i in range(0,
                                                                                                                                                                    1 + int(math.ceil(l)))]) + proposition._column_char
                j += 1
            print(row)

        row = proposition._column_char
        separator = proposition._separator_char
        lengths = []
        for x in self._formulas:
            n = len(x)
            m = (n + proposition._row_padding * 2) if n + proposition._row_padding * \
                2 >= proposition._minimum_row_width else proposition._minimum_row_width
            l = (m - n) / 2.0
            lengths.append(m)
            row += " ".join(["" for i in range(0, 1 + int(math.floor(l)))]) + x + " ".join(
                ["" for i in range(0, 1 + int(math.ceil(l)))]) + proposition._column_char
            separator += proposition._separator_char.join(
                ["" for i in range(0, 2 + m)])
        print(separator + "\n" + (row) + "\n" + separator)

        def rec(i=0, arr={}):
            if i + 1 < len(self._variables):
                arr[self._variables[i]] = False
                rec(i + 1, arr)
                arr[self._variables[i]] = True
                rec(i + 1, arr)
            else:
                arr[self._variables[i]] = False
                p_row(arr)
                arr[self._variables[i]] = True
                p_row(arr)
        rec()

        print(separator)

    def display_strict_format(self):
        print("Original Formula:  " + self._formula)
        print("Strict format   :  " + self.format_strict(self._formula))

    def display_properties(self):
        print("Original Formula:  " + self._formula)
        print("Variables:         " + str(self._variables))
        print("Subformula:        " + str(self._formulas))

    display_options = {
        "Calculate truth table": display_truth_table,
        "Display strict format": display_strict_format,
        "Display properties": display_properties
    }

    def display(self, option):
        if option in self.display_options:
            return self.display_options[option](self)
        else:
            raise ValueError("Error: Invalid display option")

    class iter:
        def __init__(self):
            self.counter = -1

        def next(self):
            self.counter += 1
            return int(self.counter / 2)

    rand = 0

    @staticmethod
    def get_id():
        proposition.rand += 1
        return proposition.rand

    class logic:
        @staticmethod
        def _not(p1):
            return not p1

        @staticmethod
        def _and(p1, p2):
            return True if (p1 is True and p2 is True) else False

        @staticmethod
        def _or(p1, p2):
            return p1 is True or p2 is True

        @staticmethod
        def _xor(p1, p2):
            return True if (
                (p1 is True and p2 is False) or (
                    p1 is False and p2 is True)) else False

        @staticmethod
        def _implies(p1, p2):
            return False if (p1 is True and p2 is False) else True

        @staticmethod
        def _biimplies(p1, p2):
            return True if p1 == p2 else False

        @staticmethod
        def _nand(p1, p2):
            return False if (p1 is True and p2 is True) else True

    operations = {
        "#not": logic._not,
        "and": logic._and,
        "or": logic._or,
        "xor": logic._xor,
        "implies": logic._implies,
        "biimplies": logic._biimplies,
        "nand": logic._nand
    }
    operations_names = [
        "#not",
        "and",
        "or",
        "xor",
        "implies",
        "biimplies",
        "nand"]

    @staticmethod
    def split(formula, negate=False):
        result = []
        not_found = False
        parenthesis_index = 0
        sub = ""

        i = 0
        while i < len(formula):
            unit = formula[i]
            if unit == "(":
                parenthesis_index += 1
                if not_found == 1:
                    not_found = 2
            elif unit == ")":
                parenthesis_index -= 1
                if parenthesis_index == 0:
                    result.extend(
                        proposition.split(
                            sub, (True if not_found == 2 else False)))
                    not_found = 0
                    sub = ""
            elif not_found == 1 and re.match("[a-z]", unit):
                result.append("not " + unit)
                not_found = 0

            if parenthesis_index > 0 and (
                    parenthesis_index != 1 or unit != "("):
                sub += unit
            elif i + 3 < len(formula) and parenthesis_index == 0 and formula[i:i + 4] == "not ":
                not_found = 1
                i += 3

            i += 1

        if parenthesis_index != 0:
            raise ValueError("Error: Unmatched parenthesis")

        result.append(formula if negate is False else ("not (" + formula + ")"))
        result = [proposition.clean(x) for x in result]

        i = 0
        while i < len(result) - 1:
            j = i + 1
            while j < len(result):
                if result[i] == result[j] or re.match(
                        "^\([ ]*" + re.escape(result[i]) + "[ ]*\)$", result[j]):
                    del result[j]
                    break
                elif re.match("^\([ ]*" + re.escape(result[j]) + "[ ]*\)$", result[i]):
                    result[i] = result[j]
                    del result[j]
                    break
                j += 1
            i += 1

        return result

    @staticmethod
    def format_add(map, x):
        i = str(proposition.get_id())
        map[i] = x
        return i

    @staticmethod
    def strip_outer_parenthesis(str):
        if str[0] != "(":
            return str
        index = 1
        i = 1
        while i < len(str):
            unit = str[i]
            if unit == "(":
                index += 1
            elif unit == ")":
                index -= 1
            if index == 0 and i != len(str) - 1:
                return str
            else:
                return str[1:-1]
            i += 1

    @staticmethod
    def remove_duplicate_parenthesis(formula):
        dio = []
        dic = []
        pairs = {}

        index = -1
        count = 0
        found = False
        forward = -1

        starts = []
        ends = []
        for i in range(0, len(formula)):
            unit = formula[i]
            if unit == "(":
                if found and forward:
                    dio.append(index)
                index = i
                found = True
                forward = True

                count += 1
                starts.append([count, i])

            elif unit == ")":
                if found and forward == False:
                    dic.append(i)
                index = i
                found = True
                forward = False

                ends.append([count, i])
                count -= 1
            elif unit != " ":
                found = False
        ends_bk = list(ends)

        for p in starts:
            i = 0
            while ends[i][0] != p[0]:
                i += 1
                if i >= len(ends):
                    raise ValueError("Error: Unmatched parenthesis")
            pairs[p[1]] = ends[i][1]
            del ends[i]

# 		print("starts: ", starts
# 		print("ends: ", ends_bk
# 		print("pairs: ", pairs
# 		print("dio: ", dio
# 		print("dic: ", dic
# 		print(" ".join(["%02d" % (i,) for i in range(0, len(formula))])
# 		print(" ".join([i + " " for i in formula])

        for x in dio:
            partner = pairs[x]
            if partner in dic:
                i = 0
                while i < len(starts) and starts[i][1] != x:
                    i += 1
                if i >= len(starts):
                    raise ValueError("Error: Something weird happened")
                flag = False
                if i + 1 < len(starts):
                    i = pairs[starts[i + 1][1]]
                    j = 0

                    while j < len(ends_bk) and ends_bk[j][1] != partner:
                        j += 1

                    if j < len(ends_bk) and j > 0 and ends_bk[j - 1][1] == i:
                        flag = True
                if flag is True:
                    formula = formula[0:x] + " " + formula[x +
                                                           1:partner] + " " + formula[partner + 1:]

        return formula

    @staticmethod
    def remove_empty_parenthesis(formula):
        flag = True
        while flag is True:
            flag = False
            start = -1
            found = False
            l = len(formula)
            i = 0
            while i < l:
                unit = formula[i]
                if unit == "(":
                    start = i
                    found = True
                elif unit == ")" and found:
                    found = False
                    formula = formula[0:start] + formula[i + 1:]
                    i = start - 1
                    l = len(formula)
                    flag = True
                elif unit != " ":
                    found = False
                i += 1
        return formula

    @staticmethod
    def remove_spaces(formula):
        return " ".join(re.findall("[^ ]+", formula))

    @staticmethod
    def clean(formula):
        map = [
            proposition.remove_empty_parenthesis,
            proposition.remove_duplicate_parenthesis,
            proposition.remove_spaces
        ]
        i = proposition.iter()

        def c(x): return c(map[i.next()](x)) if i.next() < len(map) else x
        return c(formula)

    @staticmethod
    def format_strict(formula):
        map = {}

        def add(x): return proposition.format_add(map, x)

        def strip(x): return proposition.strip_outer_parenthesis(x)
        while formula.find("(") != -1:
            sub = ""
            start = -1
            i = 0
            while i < len(formula):
                unit = formula[i]
                if unit == "(":
                    sub = ""
                    start = i
                elif unit == ")" and start != -1:
                    terp = formula
                    formula = formula[0:start] + \
                        add(strip(proposition.format_strict(sub))) + formula[i + 1:]
                    i = start + len(str(len(map) - 1)) - 1
                    sub = ""
                    start = -1
                else:
                    sub += unit
                i += 1
        for op in proposition.operations_names:
            if op[0] == "#":
                op = op[1:]
                flag = True
                while flag is True:
                    flag = False
                    i = 0
                    while i < len(formula):
                        temp_flag = False
                        if i + \
                                len(op) < len(formula) and formula[i:i + (len(op)) + 1] == op + " ":
                            if flag is True:
                                temp_flag = True
                                flag = False
                            j = i + len(op)
                            space_found = False
                            alphanum_found = False
                            start = 0
                            while j < len(formula) and (
                                    not space_found or not alphanum_found):
                                if re.match(
                                        "^[a-z0-9]$", formula[j]) and not alphanum_found:
                                    alphanum_found = True
                                    start = j
                                elif alphanum_found and formula[j] == " ":
                                    if ("#" + formula[start:j]
                                            ) in proposition.operations_names:
                                        i = start - 1
                                        flag = True
                                        break
                                    space_found = True
                                    j -= 1
                                j += 1
                            if not flag:
                                formula = formula[0:i] + \
                                    add(formula[i:j]) + formula[j:]
                            if temp_flag:
                                flag = True
                        i += 1
            else:
                while formula.find(" " + op + " ") != -1:
                    i = len(formula) - 1
                    while i >= 0:
                        if i - \
                                len(op) - 1 >= 0 and formula[i - len(op) - 1:i + 1] == " " + op + " ":
                            j = i + 1
                            space_found = False
                            alphanum_found = False
                            while j < len(formula) and (
                                    not space_found or not alphanum_found):
                                if re.match(
                                        "^[a-z0-9]$", formula[j]) and not alphanum_found:
                                    alphanum_found = True
                                elif alphanum_found and formula[j] == " ":
                                    space_found = True
                                    j -= 1
                                j += 1
                            end = j

                            j = i - len(op) - 2
                            space_found = False
                            alphanum_found = False
                            while j >= 0 and (
                                    not space_found or not alphanum_found):
                                if re.match(
                                        "^[a-z0-9]$", formula[j]) and not alphanum_found:
                                    alphanum_found = True
                                elif alphanum_found and formula[j] == " ":
                                    space_found = True
                                    j += 1
                                j -= 1
                            start = j
                            formula = formula[0:start + 1] + \
                                add(formula[start + 1:end]) + formula[end:]
                        i -= 1

        def generate_list(): return [
            x for x in re.findall(
                "[0-9]+", formula) if x in map.keys()]
        list = generate_list()

        def find_map(x): return (
            "( " + str(map[x]) + " )") if re.match("^[0-9]+$", x) and x in map else x
        while len(list) > 0:
            formula = " ".join([find_map(x) for x in formula.split()])
            list = generate_list()
        e = proposition.clean(formula)
        if len(e) == 1:
            return "( " + e + " )"
        return e

    @staticmethod
    def evaluate_connective(command, p1, p2=False):
        key = (
            "#" +
            command) if (
            "#" +
            command) in proposition.operations else command
        p1 = True if p1 == "TRUE" else False
        if p2 is False:
            if command == "":
                return p1
            return proposition.operations[key](p1)
        else:
            p2 = True if p2 == "TRUE" else False
            return proposition.operations[key](p1, p2)

    @staticmethod
    def evaluate(formula, vars):
        def ev(p):
            if p != "TRUE" and p != "FALSE":
                if p not in vars:
                    raise ValueError("Error: Variable not defined")
                else:
                    p = "TRUE" if vars[p] is True else "FALSE"
            return p

        formula = proposition.format_strict(formula.lower())
        i = formula.find(")")
        while i != -1:
            j = i - 1
            while j >= 0 and formula[j] != "(":
                j -= 1
            if j < 0:
                raise ValueError("Error: I don't even know how this happened")
            sub = re.findall("[^ ]+", formula[j + 1:i])
            l = len(sub)
            cmd = ""
            p1 = False
            p2 = False
            if l == 1:
                cmd = ""
                p1 = ev(sub[0])
            elif l == 2:
                cmd = sub[0]
                p1 = ev(sub[1])
            elif l == 3:
                cmd = sub[1]
                p1 = ev(sub[0])
                p2 = ev(sub[2])
            else:
                raise ValueError("Error: What even is this " + formula[j + 1:i])
            e = "TRUE" if proposition.evaluate_connective(
                cmd, p1, p2) is True else "FALSE"
            formula = formula[0:j] + e + formula[i + 1:]
            i = formula.find(")")
        return formula

# Request user input for proposition
user_input = input("Proposition: ")

# Process proposition
# Class constructor automatically reads proposition
# and generates truth table
prop = proposition(user_input, True)

# Call method to print truth table
prop.display("Calculate truth table")
