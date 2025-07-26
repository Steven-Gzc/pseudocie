# pseudocie

A Python-based interpreter for CIE A-Level Computer Science pseudocode, designed to parse and execute pseudocode programs following the Cambridge International Examinations 9618 specification. Built with Lark parser generator and an AST tree-walking interpreter.

## ⚠️ Important Note

**This is a demonstration project that implements only a subset of the full CIE 9618 pseudocode specification.** It supports basic language constructs like variable declarations, assignments, arithmetic operations, and input/output, but does not implement advanced features such as:

- Arrays and complex data structures
- Procedures and functions
- Control flow statements (IF/THEN/ELSE, loops)
- File handling operations
- Advanced string operations
- Error handling constructs

For the complete official specification, refer to the [CIE 9618 Pseudocode Guide for Teachers](697401-2026-pseudocode-guide-for-teachers.pdf).

## Features

Currently supported pseudocode features:

- **Data Types**: `INTEGER`, `REAL`, `STRING`, `BOOLEAN`
- **Variable Declarations**: `DECLARE variable : TYPE`
- **Constants**: `CONSTANT name = value`
- **Assignments**: `variable <- expression`
- **Arithmetic Operations**: `+`, `-`, `*`, `/`, `DIV` (integer division), `MOD`
- **Logical Operations**: `AND`, `OR`, `NOT`
- **Comparison Operations**: `>`, `<`, `>=`, `<=`, `=`, `<>`
- **Input/Output**: `INPUT variable`, `OUTPUT expression[, expression, ...]`
- **Comments**: `// comment text`

## Installation

1. Clone this repository:
```bash
git clone github.com/Steven-Gzc/pseudocie.git
cd pseudocie
```

2. Install dependencies (requires Python 3.8+):
```bash
pip install lark
```

## Usage

### Command Line Interface

Run a pseudocode file:
```bash
python cli.py path\to\file.cie
```

Additional options:
```bash
python cli.py path\to\file.cie -t        # Print parse tree
python cli.py path\to\file.cie -e        # Show environment after execution
python cli.py path\to\file.cie -d        # Dump parse tree to file
```

### Example

```bash
python cli.py tests\hello.cie
```

## Project Structures

```
pseudocie/
├── cli.py                 # Command-line interface
├── grammar.lark          # Lark grammar definition for CIE pseudocode
├── parse_utils.py        # Parsing utilities
├── cie_runtime/          # Runtime execution engine
│   ├── __init__.py
│   ├── environment.py    # Variable environment management
│   └── evaluator.py      # Expression evaluation and program execution
├── tests/                # Example pseudocode programs
│   ├── hello.cie
│   ├── expressions.cie
│   ├── div_mod.cie
│   └── constants_and_reals.cie
└── README.md
```

## Limitations

This interpreter is a **demonstration/educational tool** and implements only basic pseudocode constructs. Missing features include:

- **Uncommon Types**:  `DATE`, `CHAR`
- **Control Structures**: `IF...THEN...ELSE`, `WHILE`, `FOR`, `REPEAT...UNTIL`
- **Subprograms**: `PROCEDURE`, `FUNCTION`
- **Data Structures**: Arrays (`ARRAY[1:10] OF INTEGER`), records
- **Advanced I/O**: File operations, formatted output
- **String Manipulation**: Advanced string functions
- **Type Checking**: Runtime type validation
- **Error Handling**: `TRY...EXCEPT` blocks

## Contributing

This project is intended as an educational demonstration. If you're working on extending CIE pseudocode support, consider:

### Language Features
1. Adding control flow statements (IF/WHILE/FOR)
2. Implementing procedures and functions
3. Adding array and record support
4. Improving error messages and debugging features

### Development Tools
5. Editor support (VS Code extension, syntax highlighting)
6. Auto-completion for CIE pseudocode keywords and constructs
7. Integration with popular IDEs
8. Hand-written paper OCR for digitizing pseudocode from exam papers
9. AI-generated exam-style questions and solutions for practice

## License

This project is provided for educational purposes. Please refer to the official CIE documentation for complete pseudocode specifications.
