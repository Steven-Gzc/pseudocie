# CIE A‑Level Pseudocode – Quick Syntax Reference

A one‑page cheat‑sheet distilled from the 2026 *Pseudocode Guide for Teachers*.

---

## 1  Building blocks

| Concept            | Syntax                                |
| ------------------ | ------------------------------------- |
| **Comment**        | `// this is a comment`                |
| **Assignment**     | `variable ← expression`               |
| **Declaration**    | `DECLARE name : TYPE`                 |
| **Input / Output** | `INPUT var`, `OUTPUT item1 , item2 …` |

---

## 2  Primitive data types

`INTEGER`, `REAL`, `BOOLEAN`, `CHAR`, `STRING`, `DATE`

Complex structures:

* **Array**  `ARRAY[start…end] OF TYPE`
* **Record**  `RECORD … ENDRECORD`

---

## 3  Operators

| Category   | Operators                 |
| ---------- | ------------------------- |
| Arithmetic | `+  -  *  /  DIV  MOD  ^` |
| Relational | `=  <>  <  >  <=  >=`     |
| Logical    | `AND  OR  NOT`            |

---

## 4  Selection

```text
IF condition THEN
    statements
[ELSEIF condition THEN …]
[ELSE
    statements]
ENDIF
```

---

## 5  Iteration

```text
WHILE condition
    statements
ENDWHILE

REPEAT
    statements
UNTIL condition

FOR i ← start TO end [STEP s]
    statements
NEXT i
```

---

## 6  Subprograms

```text
PROCEDURE ProcName(parameter list)
    statements
ENDPROCEDURE

FUNCTION FuncName(parameter list) RETURNS TYPE
    statements
    RETURN value
ENDFUNCTION
```

Call with `CALL ProcName(args)` or simply `result ← FuncName(args)`.

---

## 7  Arrays & records

```text
DECLARE scores : ARRAY[1:50] OF INTEGER
DECLARE person : RECORD
    Firstname : STRING
    Age       : INTEGER
ENDRECORD

scores[25] ← 100
OUTPUT person.Firstname
```

---

## 8  Built‑in procedures / functions (core set)

| Category              | Name                                             | Example                            |
| --------------------- | ------------------------------------------------ | ---------------------------------- |
| Random                | `RANDOMINT(a,b)`                                 | `score ← RANDOMINT(1,100)`         |
| String length / slice | `LENGTH`, `SUBSTRING`, `LEFT`, `RIGHT`           | `len ← LENGTH(name)`               |
| Case conversion       | `TOUPPER`, `TOLOWER`                             | `caps ← TOUPPER(name)`             |
| Rounding              | `ROUND`, `TRUNC`                                 | `r ← ROUND(π, 2)`                  |
| ASCII ↔ char          | `ASCII`, `CHR`                                   | `code ← ASCII('A')`                |
| Files                 | `OPENFILE`, `READFILE`, `WRITEFILE`, `CLOSEFILE` | `OPENFILE(f, "scores.txt", WRITE)` |

---

## 9  Error messages in your interpreter

Report *line number* + concise description, e.g.:

```
Runtime error on line 14: Expected INTEGER but got STRING
```

---

### Tips for students

* Indent consistently; the parser ignores spaces, but humans don’t.
* Arrays are **1‑based** by default (index starts at 1).
* Use `ELSEIF` (not `ELIF`) to chain conditions.
* Always `RETURN` a value before `ENDFUNCTION`.

*(End of file)*
