import re
from typing import NamedTuple

class Token:
    def __init__(self, token_name, token_value):
        self.token_name = token_name
        self.token_value = token_value

    def __repr__(self):
        return f"{self.token_name} ::= {self.token_value}"

class States(NamedTuple):
    H: str
    COMM: str
    ID: str
    ERR: str
    NM: str
    DLM: str

class Tokens(NamedTuple):
    KWORD: str
    IDENT: str
    NUM: str
    OPER: str
    DELIM: str
    NUM2: str
    NUM8: str
    NUM10: str
    NUM16: str
    REAL: str
    TYPE: str
    ARITH: str

class Current:
    def __init__(self, symbol: str = "", eof_state: bool = False, line_number: int = 0, pos_number: int = 0,
                 state: str = ""):
        self.symbol = symbol
        self.eof_state = eof_state
        self.line_number = line_number
        self.pos_number = pos_number
        self.state = state

    def re_assign(self, symbol: str, eof_state: bool, line_number: int, pos_number: int):
        self.symbol = symbol
        self.eof_state = eof_state
        self.line_number = line_number
        self.pos_number = pos_number

class Error:
    def __init__(self, filename: str, symbol: str = "", line: int = 0, pos_in_line: int = 0):
        self.filename = filename
        self.symbol = symbol
        self.line = line
        self.pos_in_line = pos_in_line

def fgetc_generator(filename: str):
    with open(filename) as fin:
        s = list(fin.read())
        s.append('\n')
        counter_pos, counter_line = 1, 1
        for i in range(len(s)):
            yield s[i], s[i] == "@", counter_line, counter_pos
            if s[i] == "\n":
                counter_pos = 0
                counter_line += 1
            else:
                counter_pos += 1

class LexicalAnalyzer:
    def __init__(self, filename: str, identifiersTable):
        self.identifiersTable = identifiersTable
        self.states = States("H", "COMM", "ID", "ERR", "NM", "DLM")
        self.token_names = Tokens("KWORD", "IDENT", "NUM", "OPER", "DELIM", "NUM2", "NUM8", "NUM10", "NUM16", "REAL",
                                  "TYPE", "ARITH")
        self.keywords = {"or": 1, "and": 2, "not": 3, "{": 4, "}": 5, "as": 6, "if": 7,
                         "then": 8, "else": 9, "for": 10, "to": 11, "do": 12, "while": 13, "read": 14, "write": 15,
                         "true": 16, "false": 17}
        self.types = {"integer", "boolean", "real"}  # +
        self.arith = {"+", '-', '*', '/'}  # +
        self.operators = {"<>", "=", "<", "<=", ">", ">="}  # +
        self.delimiters = {";", ",", ":", "[", "]", "(", ")"}
        self.fgetc = fgetc_generator(filename)
        self.current = Current(state=self.states.H)
        self.error = Error(filename)
        self.lexeme_table = []

    def analysis(self):
        self.current.state = self.states.H
        self.current.re_assign(*next(self.fgetc))
        while not self.current.eof_state:
            if self.current.state == self.states.H:
                self.h_state_processing()
            elif self.current.state == self.states.COMM:
                self.comm_state_processing()
            elif self.current.state == self.states.ID:
                self.id_state_processing()
            elif self.current.state == self.states.ERR:
                self.err_state_processing()
            elif self.current.state == self.states.NM:
                self.nm_state_processing()
            elif self.current.state == self.states.DLM:
                self.dlm_state_processing()

    def h_state_processing(self):
        while not self.current.eof_state and self.current.symbol in {" ", "\n", "\t"}:
            self.current.re_assign(*next(self.fgetc))
        if self.current.symbol.isalpha():  # переход в состояние идентификаторов
            self.current.state = self.states.ID
        elif self.current.symbol in set(list("0123456789.")):  # переход в состояние чисел
            self.current.state = self.states.NM
        elif self.current.symbol in (self.delimiters | self.operators | self.types | self.arith):
            self.current.state = self.states.DLM
        elif self.current.symbol == "{":
            self.add_token(self.token_names.KWORD, "{")
            if not self.current.eof_state:
                self.current.re_assign(*next(self.fgetc))
        elif self.current.symbol == "}":
            self.add_token(self.token_names.KWORD, "}")
            if not self.current.eof_state:
                self.current.re_assign(*next(self.fgetc))
        elif self.current.symbol == "#":
            self.current.state = self.states.COMM
            if not self.current.eof_state:
                self.current.re_assign(*next(self.fgetc))
        else:
            self.current.state = self.states.ERR

    def comm_state_processing(self):
        while not self.current.eof_state and self.current.symbol != "#":
            self.current.re_assign(*next(self.fgetc))
        if self.current.symbol == "#":
            self.current.state = self.states.H
            if not self.current.eof_state:
                self.current.re_assign(*next(self.fgetc))
        else:
            self.error.symbol = self.current.symbol
            self.current.state = self.states.ERR

    def dlm_state_processing(self):
        if self.current.symbol in self.delimiters | self.arith | self.types:
            if self.current.symbol in self.delimiters:
                self.add_token(self.token_names.DELIM, self.current.symbol)
            elif self.current.symbol in self.types:
                self.add_token(self.token_names.TYPE, self.current.symbol)
            else:
                self.add_token(self.token_names.ARITH, self.current.symbol)
            if not self.current.eof_state:
                self.current.re_assign(*next(self.fgetc))
        else:
            temp_symbol = self.current.symbol
            if not self.current.eof_state:
                self.current.re_assign(*next(self.fgetc))
                if temp_symbol + self.current.symbol in self.operators:
                    self.add_token(self.token_names.OPER, temp_symbol + self.current.symbol)
                    if not self.current.eof_state:
                        self.current.re_assign(*next(self.fgetc))
                else:
                    self.add_token(self.token_names.OPER, temp_symbol)
            else:
                self.add_token(self.token_names.OPER, self.current.symbol)
        self.current.state = self.states.H

    def err_state_processing(self):
        raise Exception(
            f"\nUnknown: '{self.error.symbol}' in file {self.error.filename} \nline: {self.current.line_number} and pos: {self.current.pos_number}")

    def id_state_processing(self):  # Completed
        buf = [self.current.symbol]
        if not self.current.eof_state:
            self.current.re_assign(*next(self.fgetc))
        while not self.current.eof_state and (
                self.current.symbol.isalpha() or self.current.symbol.isdigit()):  # ([a-zA-Z]|[0-9])+
            buf.append(self.current.symbol)
            self.current.re_assign(*next(self.fgetc))
        buf = ''.join(buf)
        if buf in self.keywords:
            self.add_token(self.token_names.KWORD, buf)
        elif buf in self.types:  # Check if it's a type identifier
            self.add_token(self.token_names.TYPE, buf)
        else:
            self.add_token(self.token_names.KWORD, buf)
            if buf not in self.keywords:
                self.identifiersTable.add(buf) #put
        self.current.state = self.states.H

    def nm_state_processing(self):
        buf = []
        buf.append(self.current.symbol)
        if not self.current.eof_state:
            self.current.re_assign(*next(self.fgetc))
        while not self.current.eof_state and (self.current.symbol in set(list("ABCDEFabcdefoOdDhH0123456789.eE+-"))):
            buf.append(self.current.symbol)
            self.current.re_assign(*next(self.fgetc))

        buf = ''.join(buf)
        is_n, token_num = self.is_num(buf)
        if is_n:
            self.add_token(token_num, buf)
            self.current.state = self.states.H
        else:
            self.error.symbol = buf

            self.current.state = self.states.ERR

    def is_num(self, digit):
        if re.match(r"(^\d+[Ee][+-]?\d+$|^\d*\.\d+([Ee][+-]?\d+)?$)", digit):
            return True, self.token_names.REAL
        elif re.match(r"^[01]+[Bb]$", digit):
            return True, self.token_names.NUM2
        elif re.match(r"^[01234567]+[Oo]$", digit):
            return True, self.token_names.NUM8
        elif re.match(r"^\d+[dD]?$", digit):
            return True, self.token_names.NUM10
        elif re.match(r"^\d[0-9ABCDEFabcdef]*[Hh]$", digit):
            return True, self.token_names.NUM16

        return False, False

    def is_keyword(self, word):
        if word in self.keywords:
            return True
        return False

    def add_token(self, token_name, token_value):
        self.lexeme_table.append(Token(token_name, token_value))