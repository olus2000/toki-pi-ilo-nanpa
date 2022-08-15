from .AST import *


'''
Compatible with til bytecode version 0.
For more info see the docs folder.
'''

VARIABLE = {
    None  : 4,
    'lili': 5,
    'suli': 6,
}

ASSIGNMENT = {
    None  : 17,
    'lili': 18,
    'suli': 19,
}

OPCODE = {
    'suli'   : 10,
    'lili'   : 11,
    'li'     : 12,
    'en'     : 14,
    'pi'     : 15,
    'pali'   : 48,
    'pana'   : 49,
    'lukin'  : 50,
    'sitelen': 51,
    'kipisi' : 52,
    'open'   : 53,
    'pini'   : 54,
}


INT = 0b00000000
STR = 0b00001000
JMP = 0b00010000
JEZ = 0b00011000
COMMAND = 0b10000000


# big-endian
def int_to_bytes(n):
    encoded = []
    while n:
        encoded.append(n % 256)
        n //= 256
    return bytearray(reversed(encoded))


def get_var_len(dictionary):
    var_len = 0
    n = len(dictionary)
    while n:
        var_len += 1
        n //= 256
    return var_len


class Dictionary:

    def __init__(self):
        self.vars = {}
        self.pars = {}


def make_dictionary(ast, dictionary=None):
    if dictionary is None:
        dictionary = Dictionary()
    match ast:
        case LiteralExpr(value = Paragraph() as par):
            make_dictionary(par, dictionary)
        case LiteralExpr():
            pass
        case VariableExpr(identifier = identifier):
            if identifier not in dictionary.vars:
                dictionary.vars[identifier] = len(dictionary.vars)
        case RandomExpr():
            pass
        case RecursiveExpr():
            pass
        case NegateExpr(expr = expr):
            make_dictionary(expr, dictionary)
        case BinExpr(left = left, right = right):
            make_dictionary(left, dictionary)
            make_dictionary(right, dictionary)
        case ComparisonExpr(expr = expr):
            make_dictionary(expr, dictionary)
        case VerbExpr(first = first, args = args):
            make_dictionary(first, dictionary)
            for expr in args:
                make_dictionary(expr, dictionary)
        case TableAssignment(table = table, index = index):
            make_dictionary(table, dictionary)
            make_dictionary(index, dictionary)
        case Sentence(conditions = conditions, assignment = assignment, expr = expr):
            for cond in conditions:
                make_dictionary(cond, dictionary)
            if assignment is not None:
                make_dictionary(assignment, dictionary)
            make_dictionary(expr, dictionary)
        case Paragraph(arguments = arguments, sentences = sentences):
            dictionary.pars[ast] = len(dictionary.pars)
            for arg in arguments:
                make_dictionary(arg, dictionary)
            for expr in sentences:
                make_dictionary(expr, dictionary)
        case a:
            raise ValueError(a)
    return dictionary


def compile_ast(ast, dictionary) -> bytearray:
    match ast:
        case LiteralExpr(value = True):
            return bytearray((0 + COMMAND,))
        case LiteralExpr(value = dict()):
            return bytearray((1 + COMMAND,))
        case LiteralExpr(value = None):
            return bytearray((2 + COMMAND,))
        case LiteralExpr(value = str() as s):
            s = bytearray(s, 'utf-8')
            encoded = int_to_bytes(len(s))
            assert len(encoded) <= 7
            return bytearray((len(encoded) + STR,)) + encoded + s
        case LiteralExpr(value = int() as i) if type(i) is not bool:
            encoded = int_to_bytes(i)
            assert len(encoded) <= 7
            return bytearray((len(encoded) + INT,)) + encoded
        case LiteralExpr(value = Paragraph() as par):
            par_len = get_var_len(dictionary.pars)
            par = dictionary.pars[par]
            encoded = int_to_bytes(par)
            assert len(encoded) <= par_len
            compiled = bytearray((3 + COMMAND,))
            compiled += bytearray(par_len - len(encoded)) + encoded
            return compiled
        case VariableExpr(var_type=var_type, identifier=identifier):
            compiled = bytearray((VARIABLE[var_type] + COMMAND,))
            identifier = dictionary.vars[identifier]
            var_len = get_var_len(dictionary.vars)
            encoded = int_to_bytes(identifier)
            assert len(encoded) <= var_len
            compiled += bytearray(var_len - len(encoded)) + encoded
            return compiled
        case RandomExpr():
            return bytearray((8 + COMMAND,))
        case RecursiveExpr():
            return bytearray((9 + COMMAND,))
        case NegateExpr(expr = expr):
            return compile_ast(expr, dictionary) + bytearray((13 + COMMAND,))
        case BinExpr(left = left, right = right, op = op):
            compiled = compile_ast(left, dictionary)
            compiled += compile_ast(right, dictionary)
            return compiled + bytearray((OPCODE[op] + COMMAND,))
        case ComparisonExpr(op = op, expr = expr):
            compiled = compile_ast(expr, dictionary)
            return compiled + bytearray((OPCODE[op] + COMMAND,))
        case VerbExpr(verb = verb, first = first, args = args):
            compiled = bytearray()
            for arg in args[::-1]:
                compiled += compile_ast(arg, dictionary)
            if first is not None:
                compiled += compile_ast(first, dictionary)
            else:
                compiled.append(2 + COMMAND)
            return compiled + bytearray((OPCODE[verb] + COMMAND,))
        case TableAssignment(table = table, index = index):
            compiled = compile_ast(table, dictionary)
            compiled += compile_ast(index, dictionary)
            return compiled + bytearray((16 + COMMAND,))
        case Sentence(conditions = conditions, assignment = assignment, expr = expr):
            compiled_conds = []
            for cond in conditions:
                compiled_conds.append(compile_ast(cond, dictionary))
            compiled = compile_ast(expr, dictionary)
            match assignment:
                case TableAssignment():
                    compiled += compile_ast(assignment, dictionary)
                case VariableExpr(var_type = var_type, identifier = identifier):
                    compiled += bytearray((ASSIGNMENT[var_type] + COMMAND,))
                    identifier = dictionary.vars[identifier]
                    var_len = get_var_len(dictionary.vars)
                    encoded = int_to_bytes(identifier)
                    assert len(encoded) <= var_len
                    compiled += bytearray(var_len - len(encoded)) + encoded
                case None:
                    compiled.append(22 + COMMAND)
            for cond in compiled_conds[::-1]:
                jump_dist = len(compiled)
                encoded = int_to_bytes(jump_dist)
                assert len(encoded) <= 7
                cond.append(len(encoded) + JEZ)
                compiled = cond + encoded + compiled
            return compiled
        case Paragraph(arguments = arguments, sentences = sentences):
            compiled = bytearray()
            for arg in arguments:
                compiled += bytearray((ASSIGNMENT['lili'] + COMMAND,))
                identifier = dictionary.vars[arg.identifier]
                var_len = get_var_len(dictionary.vars)
                encoded = int_to_bytes(identifier)
                assert len(encoded) <= var_len
                compiled += bytearray(var_len - len(encoded)) + encoded
            compiled.append(23 + COMMAND)
            for sentence in sentences:
                compiled += compile_ast(sentence, dictionary)
            compiled += compile_ast(
                Sentence([], None, VerbExpr('pana', None, [])),
                dictionary
            )
            return compiled
        case a:
            raise ValueError(a)
            
            

def compiler(ast: Paragraph) -> bytearray:
    dictionary = make_dictionary(ast)
    var_len = get_var_len(dictionary.vars)
    assert var_len < 256
    par_len = max(get_var_len(dictionary.pars), 1)
    assert par_len < 256
    pars = [x[1] for x in sorted([(v, k) for k, v in dictionary.pars.items()])]
    compiled = bytearray()
    addresses = []
    for par in pars:
        addresses.append(len(compiled))
        compiled += compile_ast(par, dictionary)
    adr_len = get_var_len(compiled)
    assert adr_len < 256
    par_table = bytearray()
    for adr in addresses:
        encoded = int_to_bytes(adr)
        par_table += bytearray(adr_len - len(encoded)) + encoded
    header = bytearray((0, var_len, adr_len, par_len))
    encoded_par_num = int_to_bytes(len(addresses))
##    print(par_len, len(encoded_par_num))
    assert par_len == len(encoded_par_num)
    return header + \
           encoded_par_num + \
           par_table + \
           compiled
