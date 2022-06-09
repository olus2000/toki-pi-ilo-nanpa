'''
Header:
    - 1 byte version (this file is v0)
    - 1 byte length of variable identifiers minus 1

TIL encoding:
 00XXXXXX: literal unsigned integer spread over XXXXXX bytes.
 01XXXXXX: literal unsigned integer which length is described by the next
           XXXXXX+1 bytes.
 100XXXXX: literal string stored in the next XXXXX bytes.
 101XXXXX: literal string which length is stored in the next XXXXX+1 bytes.
 11XXXXXX: command with the opcode XXXXXX

All numbers (literals and lengths) are stored big-endian.
This allows for storing literal integers up to 2^64 bytes (a ton),
and literal strings up to 2^32 bytes.

Opcodes:
     00 - Literal True
     01 - Literal table
     10 - Literal None
     11 - 
    100 - First variable  |
    101 - Local variable  | Followed by an identifier (length defined in header)
    110 - Global variable |
    111 -
   1000 - Random
   1001 - Recurse
   1010 - Negate
   1011 -
   1100 - Bigger than zero
   1101 - Smaller than zero
   1110 -
'''


SHORT_INT = 0b00000000
LONG_INT  = 0b01000000
SHORT_STR = 0b10000000
LONG_STR  = 0b10100000
COMMAND   = 0b11000000


# big-endian
def int_to_bytes(n):
    encoded = []
    while n:
        encoded.append(n % 256)
        n //= 256
    return bytearray(reversed(encoded))


def make_dictionary(ast, dictionary=None):
    if dictionary is None:
        dictionary = {}
    match ast:
        case LiteralExpr():
            pass
        case VariableExpr(identifier = identifier):
            if identifier not in dictionary:
                dictionary[identifier] = len(dictionary)
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
            for expr in conditions:
                make_dictionary(expr, dictionary)
            make_dictionary(assignment, dictionary)
            make_dictionary(expr, dictionary)
        case Paragraph(arguments = arguments, sentences = sentences):
            for expr in arguments:
                make_dictionary(expr, dictionary)
            for expr in sentences:
                make_dictionary(expr, dictionary)
    return dictionary


def compile_ast(ast, compiled, dictionary):
    match ast:
        case LiteralExpr(value = True):
            compiled.append(byte((0 + COMMAND,)))
        case LiteralExpr(value = dict()):
            compiled.append(byte((1 + COMMAND,)))
        case LiteralExpr(value = None):
            compiled.append(byte((2 + COMMAND,)))
        case LiteralExpr(value = str() as s):
            s = bytearray(s, 'utf-8')
            if len(s) < 32:
                compiled.append(byte((len(s) + SHORT_STR,)))
            else:
                encoded = int_to_bytes(len(s))
                compiled.append(byte((len(encoded) - 1 + LONG_STR,)))
                compiled += encoded
            compiled += s
        case LiteralExpr(value = int() as i):
            i = int_to_bytes(i)
            if len(i) < 64:
                compilated.append(byte((len(i) + SHORT_INT,)))
            else:
                encoded = int_to_bytes(len(i))
                compiled.append(byte((len(encoded) - 1 + LONG_INT,)))
                compiled += encoded
            compiled += i
        case VariableExpr(var_type=var_type, identifier=identifier):
            match var_type:
                case None:
                    compiled.append(byte((4 + COMMAND,)))
                case 'lili':
                    compiled.append(byte((5 + COMMAND,)))
                case 'suli':
                    compiled.append(byte((6 + COMMAND,)))
                case a:
                    raise ValueError(a)
            identifier = dictionary[identifier]
            var_len = compiled[1] + 1
            encoded = int_to_bytes(identifier)
            compiled += bytearray(b'\x00' * (var_len - len(encoded))) + encoded
        case RandomExpr():
            compiled.append(byte((8 + COMMAND,)))
        case RecursiveExpr():
            compiled.append(byte((9 + COMMAND,)))
        case 
            

def compile(ast):
    dictionary = make_dictionary(ast)
    var_len = 0
    n = len(dictionary - 1)
    while n:
        var_len += 1
        n //= 256
    return compile_ast(ast, bytearray(0, var_len-1), dictionary)
