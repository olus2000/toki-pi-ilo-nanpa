# toki pi ilo nanpa
Toki pi ilo nanpa is a esoteric programming language based on a constructed human
language toki pona and instpired by a scripted language Lua. It was invented
by [me](https://esolangs.org/wiki/User:Olus2000) and its specification is
described on it's [esolangs wiki page](https://esolangs.org/wiki/Toki_pi_ilo_nanpa).

If the behavior of this interpreter differs from what is written on the wiki
please create an issue.

This repo offers a bunch of tools related to interpreting the language:
a parser, a class for parsing, compiling, decompiling and running toki code,
and an interface to use in a command line. Maybe the latter would make more sense
if I learned how to build python modules.

### Command Line Interface for toki pi ilo nanpa
It's a small tool for working with til programs located in the file "til_cli.py".
It can be used to execute til programs and ~~compile them into bytecode~~ (unimplemented).

It takes arguments:

 - `-s <source>`

   A source file to be run ~~or compiled~~.

 - `-w`

   Requires -s.
   Runs the given source file with a tree-walking interpreter.
   Not efficient, will break on deep recursion.

### Example programs
Ha ha! You thought I had time to make any good examples? Go to the esolangs wiki
and try to run the code I posted there.

### toki pi ilo nanpa source code
Located in the "til/" folder it is composed of three files:

 - AST.py
 
   Classes describing the abstract syntax tree used as an intermediate representation
   between parsing and execution/compilation.

 - parser.py
 
   Functions for parsing strings into AST representation.

 - tree_walk.py

   Functions for walking the AST. Breaks on deep recursion.
