trafoschema = '''
$schema: "http://json-schema.org/schema#"

definitions:
  params:
    type: object
  parametrizedCall:
    type: object
    properties:
      value: {type: string}
      params: {$ref: "#/definitions/params"}
    additionalProperties: false
  for:
    type: object
    properties:
      path: {type: string}
      actions: {$ref: "#/definitions/actions"}
    additionalProperties: false
  simpleaction:
    type: [object, string, number, boolean, "null"]
  call:
    oneOf:
      - {$ref: "#/definitions/parametrizedCall"}
      - type: string
  action:
    type: object
    patternProperties:
      '^for$': {$ref: "#/definitions/for"}
      '^(write|print|exec)$': {$ref: "#/definitions/simpleaction"}
      '^(set)$': {type: object}
      '^call$': {$ref: "#/definitions/call"}
    additionalProperties: false
  actions:
    type: array
    items: {$ref: "#/definitions/action"}
    additionalItems: false
  routines:
    type: object
    patternProperties:
      '.*': {$ref: "#/definitions/actions"}
    additionalProperties: false
  sample:
    type: object
    properties:
      input:
        type: [object, array, string]
      output: {type: string}
    additionalProperties: false
    required: [input]
  samples:
    type: object
    patternProperties:
      '^.*$': {$ref: "#/definitions/sample"}
    additionalProperties: false
  constants:
    type: object
    patternProperties:
      '.*': {type: string}

type: object
properties:
  id: {type: string}
  actions: {$ref: "#/definitions/actions"}
  routines: {$ref: "#/definitions/routines"}
  samples: {$ref: "#/definitions/samples"}
  constants: {$ref: "#/definitions/constants"}
additionalProperties: false
required: [actions]
'''
