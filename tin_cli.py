from tin.AST import VerbExpr, LiteralExpr
from tin.tree_walk import walk
from tin.parser import parser, ParsingError
from tin.compiler import compiler

from sys import argv


def parse_and_walk(p, args=None):
    if args is None:
        args = []
    match parser(p):
        case ParsingError() as e:
            print(e)
        case ast:
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
        '    -b <bytecode>\n'
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
                wlk = True
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
    if wlk and source is None:
        print('Option -w requires a source file passed with -s.\n'
              'See -h for help with options.')
        exit()
    if run and source is None and bytecode is None:
        print('Option -r requires either a source file passed with -s\n'
              'or a bytecode file passed with -b.\n'
              'See -h for help with options.')
        exit()
    if source is None and bytecode is None or \
       (source is None or bytecode is None) and not run and not wlk:
        print('You didn\'t give me anything to do!\n'
              'See -h for help with options.')
        exit()
    if wlk and run:
        print('You can\'t both walk and run the program in the same call.\n'
              'Only specify one of -r and -w.\n'
              'See -h for help with options.')
    if run:
        print('option -r has not been implemented yet.')
    if source is not None:
        with open(source, 'r') as f:
            AST = parser(f.read())
            if isinstance(AST, ParsingError):
                print(AST)
                exit()
        walkable = VerbExpr('pali', LiteralExpr(AST),
                            [LiteralExpr({i: v for i, v in enumerate(program_args)})])
        if wlk:
            ans = walk(walkable)
            print(f'Program exited with {ans}')
        if bytecode is not None or run:
            compiled = compiler(AST)
            if bytecode is not None:
                with open(bytecode, 'wb') as f:
                    f.write(compiled)
            if run:
                raise NotImplementedError()
    if bytecode is not None:
        with open(bytecode, 'rb') as f:
            compiled = f.read()
        if run:
            raise NotImplementedError()
