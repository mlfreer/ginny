import sys
import random

from wtforms.validators import ValidationError

def debug_print(message):
    raise ValidationError(message)

def int_or_float_or_string(s):
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return str(s)

sandbox_scope = {'__builtins__': {},
                'print': print,
                'random': random,
                'sorted': sorted,
                'len': len,
                'ifs': int_or_float_or_string}

def validate_code(form, field):
    code = field.data
    global_scope = sandbox_scope.copy()
    global_scope['debug_print'] = debug_print
    local_scope = {}
    try:
        exec(code, global_scope, local_scope)
        if 'define_variables' not in local_scope or not hasattr(local_scope['define_variables'], '__call__'):
            raise ValidationError("Function define_variables(*args, **kwargs) must be defined")
        if 'calculate_variables' not in local_scope or not hasattr(local_scope['calculate_variables'], '__call__'):
            raise ValidationError("Function calculate_variables(old_variables, actions, gamer_id, *args, **kwargs) must be defined")
        if 'is_next_round' not in local_scope or not hasattr(local_scope['is_next_round'], '__call__'):
            raise ValidationError("Function is_next_round(current_round, *args, **kwargs) must be defined")
        if 'show_variables' not in local_scope or not hasattr(local_scope['show_variables'], '__call__'):
            raise ValidationError("Function show_variables(old_variables, new_variables, actions, *args, **kwargs) must be defined")
        data = local_scope['define_variables']()
        if not isinstance(data, dict) :
            raise ValidationError("Function define_variables must return a dictionary of variables")
    except Exception as e:
        raise ValidationError(str(e))


