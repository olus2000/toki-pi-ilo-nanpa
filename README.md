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
It can be used to execute til programs and compile them into bytecode.

It takes arguments:

 - `-s <source>`

   A source file to be run or compiled.
 
 - `-b <source>`
   
   If -s was not specified:
   A bytecode source file to be executed with -r.
   
   If -s was specified:
   A destination for the compiled source to be saved in.
   

 - `-w`

   Requires -s and no -r.
   
   Runs the given source file with a tree-walking interpreter.
   Not efficient, will break on deep recursion.
 
 - `-r`
 
    Requires -s or -b and no -w.
    
    Runs the given/compiled bytecode with a virtual machine.

 - `--`
 
   Indicates that any further arguments should be passed to the executed program.
   They will be processed into a zero-indexed `kulupu` of strings.

### Example programs

 - FizzBuzz.tin

   Awaits a decimal number and prints the FizzBuzz sequence up to that number.
   Prints toki pona numbers instead of decimals. It's a pretty wide example,
   containing a mapping from digits to their values, a converter from strings
   to numbers and a converter from numbers to their toki pona representations,
   in addition to the FizzBuzz logic itself.

### toki pi ilo nanpa source code
Located in the "til/" folder it is composed of three files:

 - AST.py
 
   Classes describing the abstract syntax tree used as an intermediate representation
   between parsing and execution/compilation.
 
 - environment.py
 
   Contains the Environment class used for storing tin variables.

 - parser.py
 
   Functions for parsing strings into AST representation.

 - tree_walk.py

   Functions for walking the AST. Breaks on deep recursion.
 
 - compiler.py

   Functions for compiling the AST to bytecode.
   
 - virtual_machine.py
 
   A virtual machine capable of running bytecode compiled by compiler.py