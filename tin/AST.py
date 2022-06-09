####   AST Classes    ####

class Expression:
    pass


class LiteralExpr(Expression):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        match self.value:
            case Paragraph() as p:
                return str(p)            
            case _:
                return repr(self.value)


class VariableExpr(Expression):

    def __init__(self, var_type, identifier):
        self.var_type = var_type
        self.identifier = identifier

    def __str__(self):
        match self.var_type:
            case None:
                return f'ijo {self.identifier}'
            case var_type:
                return f'ijo {var_type} {self.identifier}'


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


class ComparisonExpr(Expression):

    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

    def __str__(self):
        return f'{self.expr} li {self.op}'


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


class Sentence:

    def __init__(self, conditions, assignment, expr):
        self.conditions = conditions
        self.assignment = assignment
        self.expr = expr

    def __str__(self):
        conds = ''
        for cond in self.conditions:
            conds += f'{cond} la '
        match self.assignment:
            case None:
                return f'{conds}o {self.expr}.'
            case a:
                return f'{conds}{a} li {self.expr}.'


class Paragraph:

    def __init__(self, arguments, sentences):
        self.arguments = arguments
        self.sentences = sentences

    def __str__(self):
        if self.arguments:
            args = ('\npali ni li kepeken e ' +
                    ' e '.join(str(arg) for arg in self.arguments) +
                    '.\n')
        else:
            args = '\n'
        return (args +
                '\n'.join(str(s) for s in self.sentences) +
                '\npali sin li pini')
