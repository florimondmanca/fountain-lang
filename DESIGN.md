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
  | assign_stmt
  | expr_stmt
  | print_stmt
  | block
assign_stmt:
  | IDENTIFIER "=" expression
expr_stmt:
  | expression
print_stmt:
  | "print" expression
block:
  | "do" stmt* "end"

# Expressions
expression:
  | conditional
conditional:
  | equality ("if" equality "else" equality)?
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
