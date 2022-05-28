from til.AST import VerbExpr, LiteralExpr
from til.tree_walk import walk
from til.parser import parse_paragraph, ParsingError


def parse_and_walk(p, args=None):
    if args is None:
        args = []
    match parse_paragraph(p, 0, 0, 0):
        case _, _, _, ParsingError() as e:
            print(e)
        case _, _, _, ast:
            return walk(VerbExpr('pali', LiteralExpr(ast), [LiteralExpr(v) for v in args]))
    
