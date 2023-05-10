import re
import string

from prettytable import PrettyTable


class State:
    def __init__(self, position, name, state_transitions: dict[list, int]):
        self.position = position
        self.name = name
        self.state_transitions = state_transitions

    def get_next_state(self, letter):
        for state in self.state_transitions.keys():
            if letter in list(state):
                return self.state_transitions[state]
        return -1

    def set_name(self, name):
        self.name = name


class Analyzer:

    def __init__(self):
        self.table = PrettyTable()
        self.table.field_names = ["Lexeme", "Lexeme\'s type", "Value"]
        self.names = ["", "Identificator", "Constant", "", "Operator", "Assignment statement", "Comment"]
        self.states = []
        self.identifiers = {}
        self.id_num = 1
        self.dividers = "();><=: \t\n%"
        self.operators = "();><="
        self.keywords = ['for', 'do']
        self.reg_for_num = "[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"
        self.reg_for_id = "[A-Za-z_]{1,16}"
        self.ident_alph = string.ascii_letters + string.digits + "_"
        self.num_alph = string.digits + "." + "+" + "-" + "e" + "E"
        self.delta = [
            {" \t\n": 0, string.ascii_letters + "_": 1, string.digits + "+" + "-": 2,
             ":": 3, self.operators: 4, "%": 6},
            {self.dividers: 0, self.ident_alph: 1},
            {self.dividers: 0, self.num_alph: 2},
            {"=": 5},
            {self.ident_alph.join(self.num_alph) + " \t\n%": 0},
            {self.ident_alph.join(self.num_alph) + " \t\n%": 0},
            {"\n": 0, string.ascii_letters + string.digits + string.punctuation + "_ ": 6}
        ]
        for i in range(len(self.delta)):
            self.states.append(State(i, self.names[i], self.delta[i]))

    def add_lexeme_to_table(self, name, value, type_):
        self.table.add_row([name, type_, value])

    def get_value(self, current_state, oper):
        value = ""
        if current_state == 1:
            if oper in self.keywords:
                self.states[current_state].set_name("Key word")
                if oper == 'for':
                    value = "KW1"
                else:
                    value = "KW2"
            else:
                self.states[current_state].set_name("Identificator")
                if oper not in self.identifiers.keys():
                    self.identifiers[oper] = self.id_num
                    self.id_num += 1
                value = oper + ":" + str(self.identifiers[oper])
        elif current_state == 2:
            value = oper
        return value

    def print_table(self):
        print(self.table)

    def check_the_pattern(self, current_state, oper):
        if current_state == 1:
            return re.match(self.reg_for_id, oper)
        elif current_state == 2:
            return re.match(self.reg_for_num, oper)
        else:
            return True

    def analyze(self, path):
        current_state = 0
        file = open(path, 'r')
        file_lines = file.readlines()
        file.close()
        oper = ""
        for line in file_lines:
            for c in line:
                next_state = self.states[current_state].get_next_state(c)
                if next_state == -1:
                    print("Error occurred on line: " + line + "Maybe you used the forbidden symbol!")
                    return
                elif next_state == current_state:
                    oper += c
                else:
                    if len(oper) > 16 and current_state != 6:
                        print("The " + oper.casefold() + " is too long!")
                        print("Error occurred on line: " + line)
                        return
                    if next_state == 0:
                        if self.check_the_pattern(current_state, oper):
                            self.add_lexeme_to_table(oper, self.get_value(current_state, oper),
                                                     self.states[current_state].name)
                        else:
                            print("The symbol " + oper + " cannot be added to the table!")
                        current_state = self.states[next_state].get_next_state(c)
                        if current_state == -1:
                            print("Error occurred on line: " + line + "Maybe you used the forbidden symbol!")
                            return
                        oper = (c, '')[current_state == 0]
                    else:
                        oper += c
                        current_state = next_state
        print("Seems like no error occurred!")
