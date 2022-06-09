import re
from .AST import *


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

ValueError is raised in the case of an
unexhaustive match-case.

The way some parsing is grouped into functions
may look a bit janky. Some of it is to make
error reporting better.
'''


####   Parsing helpers   ####

class ParsingError:

    def __init__(self, line, column, message):
        self.message = message
        self.line = line
        self.column = column

    def __str__(self):
        return f'Parsing error at line {self.line+1} column {self.column+1}:\n'\
               f'{self.message}'

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
                case a:
                    raise ValueError(a)
        return oi, ol, oc, oe
    return f


def parse_many(parser):
    def f(p, i, l, c):
        ans = []
        while True:
            match parser(p, i, l, c):
                case _, _, _, ParsingError():
                    return i, l, c, ans
                case i, l, c, value:
                    ans.append(value)
                case a:
                    raise ValueError(a)
    return f


def option(parser):
    def f(p, i, l, c):
        match parser(p, i, l, c):
            case _, _, _, ParsingError():
                return i, l, c, None
            case i, l, c, val:
                return i, l, c, val
            case a:
                raise ValueError(a)
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
        return i, l, c, ParsingError(l, c, f'Expected "{char}"')
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
        return i, l, c, ParsingError(l, c, f'Expected one of {repr(chars)}')
    return f


def parse_word(word):
    parsers = [parse_char(c) for c in word]
    def f(p, i, l, c):
        ni, nl, nc = i, l, c
        for parser in parsers:
            match parser(p, ni, nl, nc):
                case _, _, _, ParsingError():
                    return i, l, c, ParsingError(l, c, f'Expected "{word}"')
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
        return i, l, c, ParsingError(l, c,
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


def parse_words(*words):
    parsers = [parse_word(words[0])] + [parse_separated(parse_word(w)) for w in words[1:]]
    return chain(*parsers)

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
                    return i, l, c, ParsingError(l, c,
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
        return i, l, c, ParsingError(l, c,
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
                    return i, l, c, ParsingError(l, c,
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
id_pattern = re.compile('(?:(?:[AEIOU])|(?:[JKLMNPSTW][aeiou]))(?:n?(?![aeiou]))?(?:[jklmnpstw][aeiou](?:n(?![aeiou]))?)*')
def parse_identifier(p, i, l, c):
    m = id_pattern.match(p, i)
    if not m:
        return i, l, c, ParsingError(l, c, f'Expected an identifier')
    m = m[0]
    return i + len(m), l, c + len(m), m


def parse_variable(p, i, l, c):
    parser = chain(parse_word('ijo'),
                   option(alter(parse_separated(parse_word('lili')),
                                parse_separated(parse_word('suli')))),
                   parse_separated(parse_identifier))
    match parser(p, i, l, c):
        case i, l, c, ParsingError() as e:
            return i, l, c, e
        case i, l, c, ['ijo', var_type, str() as identifier]:
            return i, l, c, VariableExpr(var_type, identifier)
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
            return i, l, c, LiteralExpr(None)
        case 'lon':
            return i, l, c, LiteralExpr(True)
        case 'kulupu':
            return i, l, c, LiteralExpr({})
        case ['pali', 'ni']:
            return i, l, c, Recursion
        case Expression():
            return i, l, c, value
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


def parse_ala_expression(p, i, l, c):
    i, l, c, value = parse_pi_expression(p, i, l, c)
    if isinstance(value, ParsingError):
        return i, l, c, value
    while True:
        match parse_separated(parse_word('ala'))(p, i, l, c):
            case _, _, _, ParsingError():
                return i, l, c, value
            case i, l, c, 'ala':
                value = NegateExpr(value)
            case a:
                raise ValueError(a)


def parse_expression(p, i, l, c):
    i, l, c, value = parse_ala_expression(p, i, l, c)
    if isinstance(value, ParsingError):
        return i, l, c, value
    en_parser = parse_separated(parse_word('en'))
    next_expr_parser = parse_separated(parse_ala_expression)
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
    match parse_arguments(p, i, l, c):
        case i, l, c, ParsingError() as e:
            return i, l, c, e
        case i, l, c, args:
            return i, l, c, VerbExpr(verb, first, args)
        case a:
            raise ValueError(a)


def parse_arguments(p, i, l, c):
    args = []
    while True:
        match parse_separated(parse_word('kepeken'))(p, i, l, c):
            case _, _, _, ParsingError() as e:
                return i, l, c, args
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
            

def parse_condition(p, i, l, c):
    match parse_expression(p, i, l, c):
        case i, l, c, ParsingError() as e:
            return i, l, c, e
        case i, l, c, Expression() as expr:
            pass
        case a:
            raise ValueError(a)
    match chain(parse_separated(parse_word('li')),
                parse_separated(alter(parse_word('lili'),
                                      parse_word('suli'),
                                      parse_expression)))(p, i, l, c):
        case _, _, _, ParsingError() as e:
            return i, l, c, expr
        case i, l, c, ['li', 'lili']:
            return i, l, c, ComparisonExpr('lili', expr)
        case i, l, c, ['li', 'suli']:
            return i, l, c, ComparisonExpr('suli', expr)
        case i, l, c, ['li', Expression() as right]:
            return i, l, c, BinExpr('li', expr, right)
        case a:
            raise ValueError(a)


def parse_paragraph(p, i, l, c):
    match parse_words('pali', 'ni')(p, i, l, c):
        case _, _, _, ParsingError():
            arguments = []
        case i, l, c, ['pali', 'ni']:
            match parse_separated(chain(
                                parse_words('li', 'kepeken', 'e', 'ijo'),
                                parse_separated(parse_identifier)))(p, i, l, c):
                case i, l, c, ParsingError() as e:
                    return i, l, c, e
                case i, l, c, [['li', 'kepeken', 'e', 'ijo'], str() as identifier]:
                    arguments = [VariableExpr(None, identifier)]
                case a:
                    raise ValueError(a)
            while True:
                match alter(chain(parse_whitespace, parse_char('.')),
                            chain(parse_separated(parse_words('e', 'ijo')),
                                  parse_separated(parse_identifier)))(p, i, l, c):
                    case i, l, c, ParsingError() as e:
                        return i, l, c, e
                    case i, l, c, [_, '.']:
                        break
                    case i, l, c, [['e', 'ijo'], str() as identifier]:
                        arguments.append(VariableExpr(None, identifier))
                    case a:
                        raise ValueError(a)
        case a:
            raise ValueError(a)
    if arguments:
        match parse_whitespace_separator(p, i, l, c):
            case i, l, c, ParsingError() as e:
                return i, l, c, e
            case i, l, c, _:
                pass
            case a:
                raise ValueError(a)
    sentences = []
    while i < len(p):
        match alter(parse_words('pali', 'sin', 'li', 'pini'),
                    parse_sentence)(p, i, l, c):
            case i, l, c, ParsingError() as e:
                return i, l, c, e
            case i, l, c, ['pali', 'sin', 'li', 'pini']:
                break
            case i, l, c, Sentence() as s:
                sentences.append(s)
            case a:
                raise ValueError(a)
        if i == len(p):
            break
        match parse_whitespace_separator(p, i, l, c):
            case i, l, c, ParsingError() as e:
                return i, l, c, e
            case i, l, c, _:
                pass
            case a:
                raise ValueError(a)
    return i, l, c, Paragraph(arguments, sentences)


def parse_sentence(p, i, l, c):
    conditions = []
    while True:
        match chain(parse_condition, parse_separated(parse_word('la')))(p, i, l, c):
            case _, _, _, ParsingError():
                break
            case i, l, c, [Expression() as cond, 'la']:
                conditions.append(cond)
            case a:
                raise ValueError(a)
        i, l, c, _ = parse_whitespace_separator(p, i, l, c)
    match alter(parse_word('o'),
                chain(parse_assignment, parse_separated(parse_word('li'))))(p, i, l, c):
        case i, l, c, ParsingError() as e:
            return i, l, c, e
        case i, l, c, 'o':
            assignment = None
        case i, l, c, [VariableExpr() | TableAssignment() as assignment, 'li']:
            pass
        case a:
            raise ValueError(a)
    match parse_separated(alter(parse_words('pali', 'sin'),
                                parse_words('pali', 'e', 'pali', 'sin'),
                                parse_sentence_body))(p, i, l, c):
        case i, l, c, ParsingError() as e:
            return i, l, c, e
        case i, l, c, ['pali', 'sin']:
            match chain(parse_whitespace, parse_char('.'),
                        parse_separated(parse_paragraph))(p, i, l, c):
                case i, l, c, ParsingError() as e:
                    return i, l, c, e
                case i, l, c, [_, '.', Paragraph() as par]:
                    expr = LiteralExpr(par)
                case a:
                    raise ValueError(a)
        case i, l ,c, ['pali', 'e', 'pali', 'sin']:
            match parse_arguments(p, i, l, c):
                case i, l, c, ParsingError() as e:
                    return i, l, c, e
                case i, l, c, args:
                    pass
                case a:
                    raise ValueError(a)
            match chain(parse_whitespace, parse_char('.'),
                        parse_separated(parse_paragraph))(p, i, l, c):
                case i, l, c, ParsingError() as e:
                    return i, l, c, e
                case i, l, c, [_, '.', Paragraph() as par]:
                    expr = VerbExpr('pali', LiteralExpr(par), args)
                case a:
                    raise ValueError(a)
        case i, l, c, Expression() as expr:
            pass
        case a:
            raise ValueError(a)
    match chain(parse_whitespace, parse_char('.'))(p, i, l, c):
        case i, l, c, ParsingError() as e:
            return i, l, c, e
        case i, l, c, [_, '.']:
            return i, l, c, Sentence(conditions, assignment, expr)
        case a:
            raise ValueError(a)


def parser(p):
    match chain(parse_whitespace, parse_paragraph)(p, 0, 0, 0):
        case _, _, _, ParsingError() as e:
            return e
        case _, _, _, [_, Paragraph() as p]:
            return p
        case a:
            raise ValueError(a)
