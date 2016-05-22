from voluptuous import Schema, Required

RECORD_FN_NAME = '_record_state_fn_hidden_123'
RETVAL_NAME = '_retval_hidden_123'
MANGLED_FN_NAME = '_record_modified_original_fn_hidden_123'


LINE_STATE_SCHEMA = Schema({
    Required('lineno'): int,
    Required('state'): dict
})
EXECUTION_DUMP_SCHEMA = Schema({
    Required('data'): Schema([LINE_STATE_SCHEMA])
})

SOURCE_DUMP_SCHEMA = Schema({
    Required('source'): basestring
})
