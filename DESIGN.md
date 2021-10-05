# Design

## Syntax

### Expressions

* Literals: booleans, numbers, strings, nil.
* Unary expressions: `not`, `-`.
* Binary expressions: arithmetic and comparison operators.
* Parentheses: for wrapping expressions.
* Take precedence and associativity (left- or right-associative, LA or LA) rules into account: equality (`==`, `!=`; LA), comparison (`>`, `>=`, `<`, `<=`, `and`, `or`; LA), term (`+`, `-`; LA), factor (`*`, `/`; LA), unary (`not`, `-`; RA). A rule must only match expressions at its precedence level or higher.

```bash
# Top-level
program:
  | stmt* EOF

# Statements
stmt:
  | simple_stmt ";"?
simple_stmt:
  | block
  | if_stmt
  | for_stmt
  | "break"
  | "continue"
  | fn_stmt
  | "return" expression?
  | assert_stmt
  | assign_stmt
  | expr_stmt
block:
  | "do" stmt* "end"
if_stmt:
  | "if" (expression "do" stmt*) | (expression "do" stmt* "else" stmt*) "end"
for_stmt:
  | "for" "do" stmt* "end"
fn_stmt:
  | "fn" IDENTIFIER "(" parameters? ")" stmt* "end"
parameters:
  | param_no_default+ param_with_default*
  | param_with_default+
param_no_default:
  | IDENTIFIER
param_with_default:
  | IDENTIFIER "=" expression
assert_stmt:
  | "assert" expression ("," expression)?
assign_stmt:
  | IDENTIFIER "=" expression
expr_stmt:
  | expression

# Expressions
expression:
  | disjunction
disjunction:
  | conjunction ("or" conjunction)+
  | conjunction
conjunction:
  | equality ("and" equality)+
  | equality
equality:
  |  comparison ( ( "==" | "!=" ) comparison )*
comparison:
  | term ( ( ">" | ">=" | "<" | "<=" | "and" | "or" ) term )*
term:
  | factor ( ( "+" | "-" ) factor )*
factor:
  | unary ( ( "*" | "/" ) unary )*
unary:
  | ( "-" | "not" ) unary
  | call
call:
  | expression "(" arguments? ")"
  | primary
arguments:
  | pos_args ("," kw_args)?
  | kw_args
pos_args:
  | expression ("," expression)*
kw_args:
  | kw_arg ("," kw_arg)*
kw_arg:
  | IDENTIFIER "=" expression
primary:
  | IDENTIFIER
  | TRUE
  | FALSE
  | NIL
  | NUMBER
  | STRING
  | "(" expression ")"
```

### Resources

- On avoiding semicolons: [How Lua avoids semicolons](https://www.seventeencups.net/posts/how-lua-avoids-semicolons/)
- [Lua grammar reference](http://lua-users.org/wiki/LuaGrammar)
- [Python grammar reference](https://docs.python.org/3/reference/grammar.html)
- [Pinecone](https://github.com/wmww/Pinecone) | [I wrote a programming language: Here's how you can, too](https://www.freecodecamp.org/news/the-programming-language-pipeline-91d3f449c919/)
- [Create your own programming language with Rust](https://createlang.rs/)
