from .AST import *
from random import randrange
from io import TextIOWrapper
from itertools import zip_longest


class Environment:

    def __init__(self, parent=None):
        self.parent = parent
        self.data = {}

    def get_local(self, k):
        if k in self.data:
            return self.data[k]
        else:
            return None

    def set_local(self, k, v):
        self.data[k] = v

    def get_first(self, k):
        if k in self.data:
            return self.data[k]
        elif self.parent is None:
            return None
        else:
            return self.parent.get_first(k)

    def set_first(self, k, v):
        if k in self.data or self.parent is None:
            self.data[k] = v
        else:
            self.parent.set_first(k, v)

    def get_global(self, k):
        if self.parent is not None:
            return self.parent.get_global(k)
        elif k in self.data:
            return self.data[k]
        else:
            return None

    def set_global(self, k, v):
        if self.parent is not None:
            self.parent.set_global(k)
        else:
            self.data[k] = v
        

class ReturnError(Exception):

    def __init__(self, value):
        self.value = value


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


def walk(expr, pali_ni=None, env=None):
##    print(expr)
    if env is None:
        env = Environment()
    match expr:
        case LiteralExpr():
            return expr.value
        case VariableExpr(var_type='lili'):
            return env.get_local(expr.identifier)
        case VariableExpr(var_type='suli'):
            return env.get_global(expr.identifier)
        case VariableExpr():
            return env.get_first(expr.identifier)
        case RandomExpr():
            return randrange(256)
        case RecursiveExpr():
            return pali_ni
        case NegateExpr():
            match walk(expr.expr, pali_ni, env):
                case bool() as b:
                    return not b
                case int() as i:
                    return -i
                case a:
                    return None
        case BinExpr(op='li'):
            return walk(expr.left, pali_ni, env) == walk(expr.right, pali_ni, env)
        case BinExpr(op='en'):
            match walk(expr.left, pali_ni, env), walk(expr.right, pali_ni, env):
                case str() as a, str() as b:
                    return a + b
                case int() as a, int() as b:
                    return a + b
                case _:
                    return None
        case BinExpr(op='pi'):
            match walk(expr.left, pali_ni, env), walk(expr.right, pali_ni, env):
                case dict() as a, b:
                    if b in a:
                        return a[b]
                    return None
                case str() as a, int() as b:
                    if 0 <= b < len(a):
                        return a[b]
                    return None
                case _:
                    return None
        case BinExpr(op=e):
            raise Exception(f'Wrong binary operator {e}')
        case ComparisonExpr(op='lili'):
            match walk(expr.expr, pali_ni, env):
                case int() as i:
                    return i < 0
                case _:
                    return False
        case ComparisonExpr(op='suli'):
            match walk(expr.expr, pali_ni, env):
                case int() as i:
                    return i > 0
                case _:
                    return False
        case ComparisonExpr(op=e):
            raise Exception(f'Wrong comparison operator {e}')
        case VerbExpr(verb='pana', first=first):
            raise ReturnError(walk(first, pali_ni, env))
        case VerbExpr(verb='lukin', first=first):
            match walk(first, pali_ni, env):
                case TextIOWrapper(closed=False):
                    if first.readable():
                        return first.readline()
                    else:
                        try:
                            return input() + '\n'
                        except EOFError as e:
                            return ''
                case _:
                    try:
                        return input() + '\n'
                    except EOFError as e:
                        return ''
        case VerbExpr(verb='sitelen', first=first, args=[dest, *rest]):
            match walk(dest, pali_ni, env), represent(walk(first, pali_ni, env)):
                case TextIOWrapper(closed=False) as dest, first:
                    if dest.writeable():
                        print(first, file=dest, end='')
                    else:
                        print(first, end='')
                case _, first:
                    print(first, end='')
        case VerbExpr(verb='sitelen', first=first):
            print(represent(walk(first, pali_ni, env)), end='')
        case VerbExpr(verb='kipisi', first=first, args=[start, stop, *rest]):
            match walk(first, pali_ni, env), walk(start, pali_ni, env), walk(stop, pali_ni, env):
                case str() as first, int() as start, int() as stop:
                    start = min(max(start, 0), len(first))
                    stop = min(max(stop, 0), len(first))
                    return first[start:stop]
                case str() as first, int() as start, _:
                    start = min(max(start, 0), len(first))
                    return first[start:]
                case str() as first, _, int() as stop:
                    stop = min(max(stop, 0), len(first))
                    return first[:stop]
                case str() as first, _, _:
                    return first
                case _:
                    return None
        case VerbExpr(verb='kipisi', first=first, args=[start, *rest]):
            match walk(first, pali_ni, env), walk(start, pali_ni, env):
                case str() as first, int() as start:
                    start = min(max(start, 0), len(first))
                    return first[start:]
                case str() as first, _:
                    return first
                case _:
                    return None
        case VerbExpr(verb='kipisi', first=first):
            match walk(first, pali_ni, env):
                case str() as first:
                    return first
                case _:
                    return None
        case VerbExpr(verb='open', first=first, args=[mode, *rest]):
            match walk(first, pali_ni, env), walk(mode, pali_ni, env):
                case str() as first, 'sitelen' as mode:
                    try:
                        return open(first, 'w')
                    except Exception:
                        return None
                case str() as first, _:
                    try:
                        return open(first, 'r')
                    except Exception:
                        return None
                case _:
                    return None
        case VerbExpr(verb='open', first=first):
            match walk(first, pali_ni, env):
                case str() as first:
                    try:
                        return open(first, 'r')
                    except Exception:
                        return None
                case _:
                    return None
        case VerbExpr(verb='pini', first=first):
            match walk(first, pali_ni, env):
                case TextIOWrapper(closed=False) as first:
                    first.close()
            return None
        case VerbExpr(verb='pali', first=first, args=args):
            match walk(first, pali_ni, env):
                case Paragraph() as p:
                    new_env = Environment(env)
                    for k, v in zip_longest(p.arguments, args[:len(p.arguments)]):
                        if v is None:
                            new_env.set_local(k.identifier, None)
                        else:
                            new_env.set_local(k.identifier, walk(v, pali_ni, env))
                    return walk(p.sentences, p, new_env)
                case _:
                    return None
        case Sentence(conditions=conditions,
                      assignment=assignment,
                      expr=subexpr):
            for cond in conditions:
                val = walk(cond, pali_ni, env)
                if val is False or val is None:
                    return None
            match assignment:
                case None:
                    return walk(subexpr, pali_ni, env)
                case VariableExpr(ver_type='lili', identifier=k):
                    env.set_local(k, walk(subexpr, pali_ni, env))
                case VariableExpr(ver_type='suli', identifier=k):
                    env.set_global(k, walk(subexpr, pali_ni, env))
                case VariableExpr(identifier=k):
                    env.set_first(k, walk(subexpr, pali_ni, env))
                case TableAssignment(table=table, index=index):
                    match walk(table, pali_ni, env):
                        case dict() as table:
                            table[walk(index, pali_ni, env)] = walk(subexpr, pali_ni, env)
                        case _:
                            return walk(subexpr, pali_ni, env)
        case [*sentences]:
            try:
                for s in sentences:
                    walk(s, pali_ni, env)
            except ReturnError as e:
                return e.value
        case None:
            return None
        case a:
            raise ValueError(a)
