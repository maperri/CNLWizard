# CNLWizard

A tool for generating Controlled Natural Languages and the corresponding logic formalism.

## Install CNLWizard
In the root directory:

`pip install .`

### Dependencies

- lark

## Usage
Generate grammar and python functions
`python3 -g specification.yaml`

Compile the CNL
`python3 -c grammar.lark py_fn.py cnl_text.txt`
