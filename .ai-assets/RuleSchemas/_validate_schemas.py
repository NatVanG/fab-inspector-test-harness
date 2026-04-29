from jsonschema import Draft202012Validator
import json

with open('fab-inspector-jsonlogic.schema.json') as f:
    jl_schema = json.load(f)
Draft202012Validator.check_schema(jl_schema)
print('jsonlogic schema: valid Draft 2020-12 schema')

with open('fab-inspector-rules.schema.json') as f:
    rules_schema = json.load(f)
Draft202012Validator.check_schema(rules_schema)
print('rules schema: valid Draft 2020-12 schema')

validator = Draft202012Validator(jl_schema)
tests = [
    ({'==':[1,1]}, True, 'simple equality'),
    ({'and':[{'>':[3,1]},True]}, True, 'compound and/gt'),
    ({'var':'a.b'}, True, 'var with dot path'),
    ({'filter':[{'var':'integers'}, {'>=':[{'var':''},2]}]}, True, 'filter op'),
    ({'reduce':[{'var':'integers'},{'+':[{'var':'current'},{'var':'accumulator'}]},0]}, True, 'reduce'),
    ({'count':[{'var':'items'}]}, True, 'Ric: count'),
    ({'let':[{'x':{'+':[1,2]}}, {'*':[{'var':'x'},3]}]}, True, 'Ric: let'),
    ({'diff':[[1,2,3],[2,3,4]]}, True, 'Ric: diff'),
    ({'apiget':'https://api.fabric.microsoft.com/v1/workspaces'}, True, 'FabInsp: apiget string'),
    ({'daxquery':['EVALUATE VALUES(Table)']}, True, 'FabInsp: daxquery'),
    ({'strjoin':[['a','b'],',']}, True, 'Ric: strjoin'),
    ({'torecord':['key1','val1','key2','val2']}, True, 'Ric: torecord'),
    ({'typeof':[{'var':'x'}]}, True, 'Ric: typeof'),
    ({'badop':[1,2]}, False, 'unknown operator rejected'),
    (True, True, 'literal true'),
    ('hello', True, 'literal string'),
    (None, True, 'literal null'),
]
for expr, should_pass, name in tests:
    errs = list(validator.iter_errors(expr))
    ok = (len(errs)==0) == should_pass
    status = "PASS" if ok else "FAIL"
    detail = ""
    if not ok:
        detail = " errors=" + str([e.message[:60] for e in errs])
    print(f'  {status}: {name}{detail}')

print('Done with expression tests.\n')

# Test rule envelope schema against actual DocsExamples rule files
import os, glob
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

# Build a registry that resolves the $ref to the jsonlogic schema
jl_resource = Resource.from_contents(jl_schema, default_specification=DRAFT202012)
registry = Registry().with_resource(
    "fab-inspector-jsonlogic.schema.json", jl_resource
)

rules_validator = Draft202012Validator(rules_schema, registry=registry)

rule_files = ["DocsExamples/Example-join-split-count-rule.json"]
print(f'Validating {len(rule_files)} rule files against envelope schema:')
for rf in rule_files:
    with open(rf) as f:
        data = json.load(f)
    errs = list(rules_validator.iter_errors(data))
    if errs:
        for e in errs:
            print(f'  ERROR path={list(e.absolute_path)}: {e.message[:120]}')
    else:
        print(f'  OK: {os.path.basename(rf)}')

print('\nAll validation complete.')
