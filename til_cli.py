from til.AST import VerbExpr, LiteralExpr
from til.tree_walk import walk
from til.parser import parse_paragraph, ParsingError

from sys import argv


def parse_and_walk(p, args=None):
    if args is None:
        args = []
    match parse_paragraph(p, 0, 0, 0):
        case _, _, _, ParsingError() as e:
            print(e)
        case _, _, _, ast:
            return walk(VerbExpr('pali', LiteralExpr(ast), [LiteralExpr(v) for v in args]))


def help():
    print(
        'Command Line Interface for toki pi ilo nanpa.\n'
        'v1.0.0\n'
        '\n'
        'Arguments:\n'
        '\n'
        '    -h\n'
        '        Display this help and exit.\n'
        '\n'
        '    -s <source>\n'
        '        Path to the source file to be compiled/walked.\n'
        '        Should contain a valid toki pi ilo nanpa program.\n'
        '\n'
        '    -b <bytecode> UNIMPLEMENTED\n'
        '        If -s was passed: Path to a compilation destination file.\n'
        '        Otherwise path to a toki pi ilo nanpa bytecode file to be\n'
        '        executed.\n'
        '\n'
        '    -w\n'
        '        Requires -s.\n'
        '        The program passed with -s will be evaluated with a tree\n'
        '        walker algorithm. Note that this is not efficient and may\n'
        '        break on deep recursion.\n'
        '\n'
        '    -r UNIMPLEMENTED\n'
        '        Requires -s or -b\n'
        '        If -s was passed the program in it will be compiled and\n'
        '        executed. If both -s and -b were passed the compiled bytecode\n'
        '        will be saved in the file passed with -b.\n'
        '        If only -b was passed: execute the bytecode passed with -b.\n'
        '\n'
        '    --\n'
        '        Indicates end of til_cli arguments. Rest of the arguments will\n'
        '        be passed to the program as a 0-indexed kulupu of strings\n'
        '        if -r or -w were set.\n')


if __name__ == '__main__':
    args = argv[1:]
    w = False
    source = None
    bytecode = None
    run = False
    program_args = []
    while len(args) > 0:
        match args:
            case ['-w', *args]:
                w = True
            case ['-r', *args]:
                run = True
            case ['-s', str() as source, *args]:
                pass
            case ['-b', str() as bytecode, *args]:
                pass
            case ['-h', *args]:
                help()
                exit()
            case ['--', *program_args]:
                args = []
            case _:
                help()
                exit()
    if w and source is None:
        print('Option -w requires a source file passed with -s.\n'
              'See -h for help with options.')
        exit()
    if run and source is None and bytecode is None:
        print('Option -r requires either a source file passed with -s\n'
              'or a bytecode file passed with -b.\n'
              'See -h for help with options.')
        exit()
    if source is None and bytecode is None or \
       (source is None or bytecode is None) and not run and not w:
        print('You didn\'t give me anything to do!\n'
              'See -h for help with options.')
        exit()
    if bytecode is not None:
        print('Option -b has not been implemented yet.')
    if run:
        print('option -r has not been implemented yet.')
    if source is not None:
        with open(source, 'r') as f:
            _, _, _, AST = parse_paragraph(f.read(), 0, 0, 0)
            if isinstance(AST, ParsingError):
                print(AST)
                exit()
        AST = VerbExpr('pali', LiteralExpr(AST),
                       [LiteralExpr({i: v for i, v in enumerate(program_args)})])
        if w:
            ans = walk(AST)
            print(f'Program exited with {ans}')
    
