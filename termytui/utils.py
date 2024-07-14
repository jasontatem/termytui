def average(numbers):
    return sum(numbers) / len(numbers)

def pass_func(*args, **kwargs):
    pass

def null_content_func(panel):
   pass
    

allowed_inputs = {
    'alpha_lower': 'abcdefghijklmnopqrstuvwxyz',
    'alpha_upper': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
    'numbers': '0123456789',
    'python_sym': '[]()+-*/',
    'punctuation': '`~!@#$%^&*()-_[]{};:\'"/?.,><\\|',
    'space': ' '
}

allowed_inputs['alpha'] = allowed_inputs['alpha_upper'] + allowed_inputs['alpha_lower']
allowed_inputs['alphanum'] = allowed_inputs['alpha'] + allowed_inputs['numbers']
allowed_inputs['alphapunct'] = allowed_inputs['alphanum'] + allowed_inputs['punctuation']
