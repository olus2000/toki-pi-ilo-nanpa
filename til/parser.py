import re


####   Variable naming conventions   ####

'''
In this file:
    p - program string
    i - position of the parser in the string
    l - line number for error reporting
    c - column number for error reporting
    e - Parsing Error
    value - value of the parsed string
Parsers are functions of type:
(p, i, l, c) -> (i, l, c, e | value)
'''


####   AST Classes    ####

class Expression:
    pass


class LiteralExpr(Expression):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class VariableExpr(Expression):

    def __init__(self, identifier):
        self.identifier = identifier

    def __str__(self):
        return f'ijo {self.identifier}'


class RandomExpr(Expression):

    def __str__(self):
        return 'nanpa nasa'

Random = RandomExpr()


class RecursiveExpr(Expression):

    def __str__(self):
        return 'pali ni'

Recursion = RecursiveExpr()


class NegateExpr(Expression):

    def __init__(self, expr):
        self.expr = expr

    def __str__(self):
        return f'{self.expr} ala'


class BinExpr(Expression):

    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def __str__(self):
        return f'{self.left} {self.op} {self.right}'


class VerbExpr(Expression):

    def __init__(self, verb, first, args):
        self.verb = verb
        self.first = first
        self.args = args

    def __str__(self):
        ans = f'{self.verb}'
        if self.first:
            ans += f' e {self.first}'
        for arg in self.args:
            ans += f' kepeken {arg}'
        return ans


class TableAssignment:

    def __init__(self, table, index):
        self.table = table
        self.index = index

    def __str__(self):
        return f'{self.table} pi {self.index}'


####   Parsing helpers   ####

class ParsingError:

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

    # A trick to make max(None, ParsingError) return ParsingError in alter
    def __lt__(self, v):
        return False


def chain(*parsers):
    def f(p, i, l, c):
        ans = []
        for parser in parsers:
            match parser(p, i, l, c):
                case i, l, c, ParsingError() as e:
                    return i, l, c, e
                case i, l, c, parsed:
                    ans.append(parsed)
        return i, l, c, ans
    return f


def alter(*parsers):
    def f(p, i, l, c):
        for parser in parsers:
            oi, ol, oc, oe = i, l, c, None
            match parser(p, i, l, c):
                case ni, nl, nc, ParsingError() as ne:
                    oi, ol, oc, oe = max((ni, nl, nc, ne), (oi, ol, oc, oe))
                case i, l, c, parsed:
                    return i, l, c, parsed
        return oi, ol, oc, oe
    return f


def parse_many(parser):
    def f(p, i, l, c):
        ans = []
        while True:
            match parser(p, i, l, c):
                case _, _, _, ParsingError():
                    return ans
                case (i, l, c, value):
                    ans.append(value)
    return f


####   Lexing   ####

def parse_char(char):
    def f(p, i, l, c):
        if i < len(p) and p[i] == char:
            if char == '\n':
                c = 0
                l += 1
            else:
                c += 1
            return i + 1, l, c, char
        return i, l, c, ParsingError(
            f'Parsing Error at line {l} column {c}:\n'
            f'Expected "{char}"')
    return f


def parse_any_char(chars):
    parsers = [parse_char(c) for c in chars]
    def f(p, i, l, c):
        for parser in parsers:
            match parser(p, i, l, c):
                case _, _, _, ParsingError():
                    pass
                case parsed:
                    return parsed
        return i, l, c, ParsingError(
            f'Parsing Error at line {l} column {c}:\n'
            f'Expected one of {repr(chars)}')
    return f


def parse_word(word):
    parsers = [parse_char(c) for c in word]
    def f(p, i, l, c):
        ni, nl, nc = i, l, c
        for parser in parsers:
            match parser(p, ni, nl, nc):
                case _, _, _, ParsingError():
                    return i, l, c, ParsingError(
                        f'ParseingError at line {l} column {c}:\n'
                        f'Expected "{word}"')
                case ni, nl, nc, _:
                    pass
        return ni, nl, nc, word
    return f


def parse_any_word(words):
    parsers = [parse_word(s) for s in words]
    def f(p, i, l, c):
        for parser in parsers:
            match parser(p, i, l, c):
                case _, _, _, ParsingError():
                    pass
                case parsed:
                    return parsed
        return i, l, c, ParsingError(
            f'Parsing Error at line {l} column {c}:\n'
            f'Expected one of [{", ".join([repr(s) for s in words])}]')
    return f


parse_one_whitespace = parse_any_char('\n\r\t ')


parse_whitespace = parse_many(parse_one_whitespace)


parse_whitespace_separator = chain(parse_one_whitespace, parse_whitespace)


def parse_separated(parser):
    parser = chain(parse_whitespace_separator, parser)
    def f(p, i, l, c):
        match parser(p, i, l, c):
            case i, l, c, ParsingError() as e:
                return i, l, c, e
            case i, l, c, [_, value]:
                return i, l, c, value
            case a:
                raise ValueError(a)
    return f

####   Parsing (and some lexing also)   ####

escapes = {'\\': '\\', '"': '"', 'n': '\n'}
def parse_string_body(p, i, l, c):
    ans = ''
    try:
        while p[i] != '"':
            if p[i] == '\\':
                i += 1
                c += 1
                if p[i] not in escapes:
                    return i, l, c, ParsingError(
                        f'Parsing Error at line {l} column {c}:\n'
                        f'Incorrect escape sequence. Did you mean "\\\\"?')
                ans += escapes[p[i]]
            else:
                ans += p[i]
            if p[i] == '\n':
                l += 1
                c = 0
            else:
                c += 1
            i += 1
    except IndexError:
        return i, l, c, ParsingError(
            f'Parsing Error at line {l} column {c}:\n'
            f'Unexpected EOF while parsing a string')
    return i + 1, l, c + 1, ans


def parse_string(p, i, l, c):
    parser = chain(parse_word('nimi'),
                   parse_whitespace_separator,
                   parse_char('"'),
                   parse_string_body)
    match parser(p, i, l, c):
        case i, l, c, ['nimi', _, '"', value]:
            return i, l, c, LiteralExpr(value)
        case i, l, c, ParsingError() as e:
            return i, l, c, e
        case a:
            raise ValueError(str(a))


numbers = {'ali': 100, 'ale': 100, 'mute': 20, 'luka': 5, 'tu': 2, 'wan': 1}
nonzero_number_parser = parse_any_word(list(numbers))
def parse_int_body(p, i, l, c):
    i, l, c, word = parse_any_word(list(numbers) + ['ala', 'nasa'])(p, i, l, c)
    match word:
        case ParsingError():
            return i, l, c, word
        case 'ala':
            return i, l, c, 0
        case 'nasa':
            return i, l, c, Random
    ans = numbers[word]
    while True:
        prev = numbers[word]
        match parse_separated(nonzero_number_parser)(p, i, l, c):
            case _, _, _, ParsingError() as e:
                return i, l, c, ans
            case ni, nl, nc, word:
                if numbers[word] > prev:
                    return i, l, c, ParsingError(
                        f'Parsing Error at line {l} column {c}:\n'
                        f'Number words must be in a non-increasing order')
                ans += numbers[word]
                i, l, c = ni, nl, nc
            case a:
                raise ValueError(a)


def parse_int(p, i, l, c):
    parser = chain(parse_word('nanpa'),
                   parse_whitespace_separator,
                   parse_int_body)
    match parser(p, i, l, c):
        case i, l, c, ['nanpa', _, RandomExpr() as value]:
            return i, l, c, value
        case i, l, c, ['nanpa', _, int() as value]:
            return i, l, c, LiteralExpr(value)
        case i, l, c, ParsingError() as e:
            return i, l, c, e
        case a:
            raise ValueError(str(a))


# I got really annoyed by trying to make a parser for tp names.
id_pattern = re.compile('(([AEIOU]n?)|([JKLMNPSTW][aeiou]n?))([jklmnpstw][aeiou]n?)*')
def parse_identifier(p, i, l, c):
    m = id_pattern.match(p, i)
    if not m:
        return i, l, c, ParsingError(
            f'Parsing Error at line {l} column {c}:\n'
            f'Expected an identifier')
    m = m[0]
    return i + len(m), l, c + len(m), m


def parse_variable(p, i, l, c):
    parser = chain(parse_word('ijo'),
                   parse_separated(parse_identifier))
    match parser(p, i, l, c):
        case i, l, c, ParsingError() as e:
            return i, l, c, e
        case i, l, c, ['ijo', str() as identifier]:
            return i, l, c, VariableExpr(identifier)
        case a:
            raise ValueError(a)


def parse_simple_expression(p, i, l, c):
    parser = alter(parse_int, parse_string, parse_word('ala'),
                   parse_word('lon'), parse_word('kulupu'),
                   chain(parse_word('pali'), parse_separated(parse_word('ni'))),
                   parse_variable)
    i, l, c, value = parser(p, i, l, c)
    match value:
        case ParsingError() as e:
            return i, l, c, e
        case 'ala':
            value = LiteralExpr(None)
        case 'lon':
            value = LiteralExpr(True)
        case 'kulupu':
            value = LiteralExpr({})
        case ['pali', 'ni']:
            value = Recursion
        case Expression():
            pass
        case a:
            raise ValueError(a)
    ala_parser = parse_separated(parse_word('ala'))
    while True:
        match ala_parser(p, i, l, c):
            case ni, nl, nc, ParsingError():
                return i, l, c, value
            case i, l, c, 'ala':
                value = NegateExpr(value)
            case a:
                raise ValueError(a)


def parse_pi_expression(p, i, l, c):
    i, l, c, value = parse_simple_expression(p, i, l, c)
    if isinstance(value, ParsingError):
        return i, l, c, value
    pi_parser = parse_separated(parse_word('pi'))
    next_expr_parser = parse_separated(parse_simple_expression)
    while True:
        match pi_parser(p, i, l, c):
            case _, _, _, ParsingError():
                return i, l, c, value
            case i, l, c, 'pi':
                pass
            case a:
                raise ValueError(a)
        match next_expr_parser(p, i, l, c):
            case i, l, c, ParsingError() as e:
                return i, l, c, e
            case i, l, c, next_expr:
                value = BinExpr('pi', value, next_expr)
            case a:
                raise ValueError(a)


def parse_expression(p, i, l, c):
    i, l, c, value = parse_pi_expression(p, i, l, c)
    if isinstance(value, ParsingError):
        return i, l, c, value
    en_parser = parse_separated(parse_word('en'))
    next_expr_parser = parse_separated(parse_pi_expression)
    while True:
        match en_parser(p, i, l, c):
            case _, _, _, ParsingError():
                return i, l, c, value
            case i, l, c, 'en':
                pass
            case a:
                raise ValueError(a)
        match next_expr_parser(p, i, l, c):
            case i, l, c, ParsingError() as e:
                return i, l, c, e
            case i, l, c, next_expr:
                value = BinExpr('en', value, next_expr)
            case a:
                raise ValueError(a)


parse_verb = parse_any_word(['pali', 'pana', 'lukin', 'sitelen', 'kipisi',
                              'open', 'pini'])

def parse_sentence_body(p, i, l, c):
    verb = None
    first = None
    args = []
    match alter(parse_verb, parse_expression)(p, i, l, c):
        case i, l, c, ParsingError() as e:
            return i, l, c, e
        case i, l, c, Expression() as expr:
            return i, l, c, expr
        case i, l, c, str() as verb:
            pass
        case a:
            raise ValueError(a)
    match parse_separated(parse_word('e'))(p, i, l, c):
        case _, _, _, ParsingError() as e:
            return i, l, c, VerbExpr(verb, first, args)
        case i, l, c, 'e':
            pass
        case a:
            ValueError(a)
    match parse_separated(parse_expression)(p, i, l, c):
        case i, l, c, ParsingError() as e:
            return i, l, c, e
        case i, l, c, Expression() as first:
            pass
        case a:
            raise ValueError(a)
    while True:
        match parse_separated(parse_word('kepeken'))(p, i, l, c):
            case _, _, _, ParsingError() as e:
                return i, l, c, VerbExpr(verb, first, args)
            case i, l, c, 'kepeken':
                pass
            case a:
                raise ValueError(a)
        match parse_separated(parse_expression)(p, i, l, c):
            case i, l, c, ParsingError() as e:
                return i, l, c, e
            case i, l, c, Expression() as arg:
                args.append(arg)
            case a:
                raise ValueError(a)
    

def parse_assignment(p, i, l, c):
    i, l, c, var = parse_variable(p, i, l, c)
    match var:
        case ParsingError():
            return i, l, c, var
        case VariableExpr():
            pass
        case a:
            raise ValueError(a)
    match parse_separated(parse_word('pi'))(p, i, l, c):
        case _, _, _, ParsingError():
            return i, l, c, var
        case i, l, c, 'pi':
            pass
        case a:
            raise ValueError(a)
    match parse_separated(parse_simple_expression)(p, i, l, c):
        case i, l, c, ParsingError() as e:
            return i, l, c, e
        case i, l, c, Expression() as index:
            pass
        case a:
            raise ValueError(a)
    while True:
        match parse_separated(parse_word('pi'))(p, i, l, c):
            case _, _, _, ParsingError():
                return i, l, c, TableAssignment(var, index)
            case i, l, c, 'pi':
                pass
            case a:
                raise ValueError(a)
        match parse_separated(parse_simple_expression)(p, i, l, c):
            case i, l, c, ParsingError() as e:
                return i, l, c, e
            case i, l, c, Expression() as e:
                var = BinExpr('pi', var, index)
                index = e
            case a:
                raise ValueError(a)
            
