# fountain-lang

An interpreted programming language, written in Python.

```console
$ fountain app.ft
```

Based on https://www.craftinginterpreters.com/, inspired by Lua.

## Features

### High-level language

#### Dynamic typing

#### Automatic memory management

### Data types

* Booleans. A dedicated `Bool` type with two values: `true` and `false`.

```
true  -- The "true" value.
false  -- The "not true" value.
```

* Numbers. The type is `Number`. In Fountain, all numbers are double-precision floating point value, although they may be represented as integers in code.

```
12  -- An integer.
12.34  -- A decimal number.
```

* Strings. Represented in single or double quotes.

```
"This is a string"  -- A string.
""  -- The empty string.
'123'  -- A string, not a number, using single quotes.
```

* Nil. The "no value" value, spelled `nil`.

### Expressions

```lua
-- Arithmetic
x + y
x - y
x * y
x / y
-x

-- Comparisons and equality
x > y
x >= y
x < y
x <= y
1 == 2  -- false
"cat" != "dog"  -- true
123 == "123"  -- false, No implicit conversions.

-- Logic
not true  -- false
not false -- true

true and false  -- false
true or false -- true
```

### Statements

### Variables

### Control flow

Conditionals:

```lua
-- If blocks
if ... then
  ...
elif ... then
  ...
else
  ...
end

-- Inline conditional evaluation
s = "yes" if true else "no"  -- "yes"
```

Loops:

```lua
-- Infinite loop.
for do
  ...
end

-- Iterator-based loop.
for n in {1, 2, 3} do
  print(n)
end

-- While-like loop.
for do
  if ... then
    break
  end
  ...
end

-- Repeat-like loop
for do
  ...
  if ... then
    break
  end
end
```

### Functions

```lua
fun f(x, y)
  return x + y
end

f(1, 2)  -- Basic function call.
f(x=1, y=2)  -- Named arguments.
f(1, y=2)  -- Positional and named arguments.
f(y=2, 1)  -- Error! Positional must come first.
```

### Tables

Fountain only has one built-in datastructure: tables.

Tables are general key-value stores which can be used as hashmaps or lists.

```lua
nums = {1, 2, 3}
nums[0]  -- 1
nums[1]  -- 2
nums[2]  -- 3
nums  -- {[0] = 1, [1] = 2, [2] = 3}

sprite = {x = 5, y = 10, vx = 2, vy = -1}
sprite.x  -- 5. Same as sprite["x"]
sprite.y += sprite.vy
sprite.y  -- 9
sprite  -- {[x] = 5, [y] = 10, [vx] = 2, [vy] = -1}
```

### Import system

### Standard library

* High-level language.
* Dynamic typing.
* Automatic memory management.
* Data types: `bool`, `number`, `str`, `table`, `nil`.
* Expressions: arithmetic (`+`, `-`, `*`, `/`), comparison and equality, logic, precedence and grouping.

* Control flow: if/elif/else/end, while/do/end, for/end, 

## License

Apache 2.0
