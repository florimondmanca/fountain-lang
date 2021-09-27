# Design

## Syntax

### Expressions

* Literals: booleans, numbers, strings, nil.
* Unary expressions: `not`, `-`.
* Binary expressions: arithmetic and comparison operators.
* Parentheses: for wrapping expressions.

```bash
expr    = literal | unary | binary | group;
literal = NUMBER | STRING | "true" | "false" | "nil";
unary   = ("-" | "not") expr;
binary  = expr op expr;
op      = "<" | "<=" | ">" | ">=" | "+" | "-" | "*" | "/";
group   = "(" expr ")";
```
