from .environment import Environment
from random import randrange
from io import TextIOWrapper


'''
Compatible with til bytecode version 0.
For more info see the docs folder.
'''


OPCODE_CHECK = 0b10000000
OPCODE_MASK  = 0b01111111
LENCODE_MASK = 0b01111000
LENGTH_MASK  = 0b00000111


class Paragraph:

    def __init__(self, id):
        self.id = id


def represent(val):
    match val:
        case True:
            return '[lon]'
        case False:
            return '[lon ala]'
        case int():
            return '[nanpa]'
        case str():
            return val
        case Paragraph():
            return '[pali]'
        case dict():
            return '[kulupu]'
        case TextIOWrapper():
            return '[lipu]'
        case None:
            return '[ala]'
        case a:
            raise ValueError(a)


def consume(compiled: bytearray, start: int, length: int) -> (int, int):
    ans = 0
    for _ in range(length):
        ans *= 256
        ans += compiled[start]
        start += 1
    return ans, start


def virtual_machine(compiled: bytearray, args):
    version = compiled[0]
    assert version <= 0
    var_len = compiled[1]
    adr_len = compiled[2]
    par_len = compiled[3]
    par_tab_len, ip = consume(compiled, 4, par_len)
    par_adr_tab = []
    for _ in range(par_tab_len):
        par_adr, ip = consume(compiled, ip, adr_len)
        par_adr_tab.append(par_adr)
    pars = [compiled[ip + adr : ip + end] for adr, end
            in zip(par_adr_tab, par_adr_tab[1:] + [len(compiled) - ip])]
    data = []
    ret = []
    par = 0
    ip = 0
    env = Environment()
    while True:
        if par > len(pars):
            print(ret)
            return
        com, ip = consume(pars[par], ip, 1)
##        print(len(ret), par, com)
        if com & OPCODE_CHECK != 0:
            match com & OPCODE_MASK:
                case 0:
                    data.append(True)
                case 1:
                    data.append({})
                case 2:
                    data.append(None)
                case 3:
                    identifier, ip = consume(pars[par], ip, par_len)
                    data.append(Paragraph(identifier))
                case 4:
                    identifier, ip = consume(pars[par], ip, var_len)
                    data.append(env.get_first(identifier))
                case 5:
                    identifier, ip = consume(pars[par], ip, var_len)
                    data.append(env.get_local(identifier))
                case 6:
                    identifier, ip = consume(pars[par], ip, var_len)
                    data.append(env.get_global(identifier))
                case 8:
                    data.append(randrange(256))
                case 9:
                    data.append(Paragraph(par))
                case 10:
                    a = data.pop()
                    match a:
                        case bool():
                            data.append(False)
                        case int():
                            data.append(a > 0)
                        case _:
                            data.append(False)
                case 11:
                    a = data.pop()
                    match a:
                        case bool():
                            data.append(False)
                        case int():
                            data.append(a < 0)
                        case _:
                            data.append(False)
                case 12:
                    a, b = data.pop(), data.pop()
                    data.append(a == b and type(a) is type(b))
                case 13:
                    a = data.pop()
                    match a:
                        case bool():
                            data.append(not a)
                        case int():
                            data.append(-a)
                        case _:
                            data.append(None)
                case 14:
                    a, b = data.pop(), data.pop()
                    match a, b:
                        case int(), int() if type(a) is not bool \
                             and type(b) is not bool:
                            data.append(b + a)
                        case str(), str():
                            data.append(b + a)
                case 15:
                    a, b = data.pop(), data.pop()
                    match a, b:
                        case _, dict():
                            if a in b:
                                data.append(b[a])
                            else:
                                data.append(None)
                        case int(), str() if type(a) is not bool:
                            if 0 <= a < len(b):
                                data.append(b[a])
                            else:
                                data.append(None)
                        case _:
                            data.append(None)
                case 16:
                    i, t, v = data.pop(), data.pop(), data.pop()
                    match i, t, v:
                        case _, dict(), _:
                            t[i] = v
                case 17:
                    a = data.pop()
                    identifier, ip = consume(pars[par], ip, var_len)
                    env.set_first(identifier, a)
                case 18:
                    if data:
                        a = data.pop()
                    else:
                        a = None
                    identifier, ip = consume(pars[par], ip, var_len)
                    env.set_local(identifier, a)
                case 19:
                    a = data.pop()
                    identifier, ip = consume(pars[par], ip, var_len)
                    env.set_global(identifier, a)
                case 22:
                    data.pop()
                case 23:
                    data = []
                case 48:
                    match data.pop():
                        case Paragraph(id=identifier):
                            ret.append((par, ip, env))
                            par, ip, env = identifier, 0, Environment(env)
                        case _:
                            data = [None]
                case 49:
                    data = [data.pop()]
                    if ret:
                        par, ip, env = ret.pop()
                    else:
                        break
                case 50:
                    first = data.pop()
                    match first:
                        case TextIOWrapper(closed=False) if first.readable():
                            data = [first.readline()]
                        case _:
                            try:
                                data = [input() + '\n']
                            except EOFError as e:
                                data = ['']
                case 51:
                    first = data.pop()
                    if data:
                        arg = data.pop()
                    else:
                        arg = None
                    match arg:
                        case TextIOWrapper(closed=False) if arg.writeable():
                            print(represent(first), file=arg, end='')
                        case _:
                            print(represent(first), end='')
                    data = [None]
                case 52:
                    first = data.pop()
                    match first:
                        case str():
                            if data:
                                start = data.pop()
                                match start:
                                    case int() if type(start) is not bool:
                                        start = min(max(0, start), len(first))
                                    case _:
                                        start = 0
                            else:
                                start = 0
                            if data:
                                end = data.pop()
                                match end:
                                    case int() if type(end) is not bool:
                                        end = max(min(len(first), end), start)
                                    case _:
                                        end = len(first), start
                            else:
                                end = len(first)
                            data = [first[start:end]]
                        case _:
                            data = [None]
                case 53:
                    first = data.pop()
                    if data:
                        mode = data.pop()
                    else:
                        mode = None
                    match first, mode:
                        case str(), 'sitelen':
                            try:
                                data = [open(first, 'w')]
                            except Exception:
                                data = [None]
                        case str(), _:
                            try:
                                data = [open(first, 'r')]
                            except Exception:
                                data = [None]
                        case _:
                            data = [None]
                case 54:
                    match data.pop():
                        case TextIOWrapper(colsed=False) as first:
                            first.close()
                    data = [None]
                case i:
                    raise ValueError((par, ip, i))
        else:
            match com & LENCODE_MASK, com & LENGTH_MASK:
                case 0, length:
                    val, ip = consume(pars[par], ip, length)
                    data.append(val)
                case 8, length:
                    length, ip = consume(pars[par], ip, length)
                    val = pars[par][ip:ip + length].decode('utf-8')
                    ip += length
                    data.append(val)
                case 16, length:
                    val, ip = consume(pars[par], ip, length)
                    ip += val
                case 24, length:
                    val, ip = consume(pars[par], ip, length)
                    pred = data.pop()
                    if pred is None or pred is False:
                        ip += val
                case a:
                    raise ValueError((par, ip, a))
    print('Program exited with', data[-1])
