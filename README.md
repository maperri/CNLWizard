# CNLWizard

A tool for generating Controlled Natural Languages and the corresponding logic formalism.

### Dependencies

- lark: `pip install lark`
- yaml: `pip install PyYAML`
- ortools (for CP): `pip install ortools`
- z3 (for SMT): `pip install z3-solver`

Sat examples also require:
- python-sat: `pip install python-sat` 
- sympy: `pip install sympy`

## Usage
Generate grammar and python functions
```
python3 src/main.py -g {YAML}`
```
where YAML is the file containing the cnl specification in yaml format.

Compile the CNL
```
python3 src/main.py -c {GRAMMAR} {PY_FUNCTIONS} {CNL}
```
where GRAMMAR is the generated grammar in lark format, PY_FUNCTIONS is the file containing the implemented python functions and CNL is the CNL text that will be translated.


## Examples
In the example folder you can find several examples.
All the examples contains the yaml specification, the python functions, the generated grammar and some CNL texts that can be translated into formalisms.
Note that there are two python function files: those prefixed with 'generated' are the generated file by the tool (some functions might require to be implemented by the user), while those prefixed with 'implemented' are the final file with all the function implemented (by the user). 

The folders: 'asp', 'cp', 'sat' and 'smt'; contain examples of the corresponding language.
You can run: 
```
python3 src/main.py -c examples/{FOLDER_NAME}/grammar_{FOLDER_NAME}.lark examples/{FOLDER_NAME}/implemented_py_{FOLDER_NAME}.py examples/{FOLDER_NAME}/cnl_text/{CNL_NAME}
```
to compile the examples.

All these examples are grouped under a single specification file in the global folder, which contains a single yaml file that generated all the CNLs.
You can run: 
```
python3 src/main.py -c examples/global/grammar_{FORMALISM}.lark examples/global/implemented_py_{FORMALISM}.py examples/global/cnl_text/{FORMALISM}/{CNL_NAME}
```
where FORMALISM is one of: asp, cp, sat and smt.

The folders: pigeon_hole and employee_scheduling, contains an example of the same CNL translated into different target formalisms (asp, cp, smt).
You can run: 
```
python3 src/main.py -c examples/{FOLDER_NAME}/grammar_{FORMALISM}.lark examples/{FOLDER_NAME}/implemented_py_{FORMALISM}.py examples/{FOLDER_NAME}/cnl_text.cnl
```
where: 
- FOLDER_NAME is one of: pigeon_hole, employee_scheduling;
- FORMALISM is one of: asp, cp, smt

## Comparison with cnl2asp
The folder cnl2asp_comparison contains an experimental analysis in which we took CNL problems from the [cnl2asp](https://github.com/dodaro/cnl2asp) repository and we compared the necessary lines of code for cnl2asp and for CNLWizard to traslate them. 
The problems we considered are: graph_coloring, nsp, robot, cts.
Each folder contains a folder called cnl2asp which contains the minimum number of lines necessary to translate the corresponding problem, and the same in the wizard folder for CNLWizard. The "all" folder contains the code necessary to run all the problems under a single package, while the others can only translate the single problem.
In order to run cnl2asp:
```
python3 cnl2asp_comparison/{PROBLEM}/cnl2asp/src/main.py cnl2asp_comparison/inputs/{PROBLEM}.cnl
```
where PROBLEM can be one of: graph_coloring, nsp, robot, cts.
In order to run CNLWizard:
```
python3 src/main.py -c cnl2asp_comparison/nsp/wizard/grammar_asp.lark cnl2asp_comparison/{PROBLEM}/wizard/implemented_py_asp.py cnl2asp_comparison/inputs/{PROBLEM}.cnl 
```
where PROBLEM can be one of: graph_coloring, nsp, robot, cts.