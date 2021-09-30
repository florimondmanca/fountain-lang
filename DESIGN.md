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
  | print_stmt
  | if_stmt
  | for_stmt
  | assert_stmt
  | assign_stmt
  | expr_stmt
  | "break"
  | "continue"
block:
  | "do" stmt* "end"
print_stmt:
  | "print" expression
if_stmt:
  | "if" (expression "do" stmt*) | (expression "do" stmt* "else" stmt*) "end"
for_stmt:
  | "for" "do" stmt* "end"
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
  | primary;
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
