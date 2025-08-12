import math
import logging

COMMAND = "calc"
HELP = "A safe calculator for evaluating mathematical expressions.\nUsage: .calc <expression>"
TAGS = ['tools']

async def execute(m, args):
    """
    A safe calculator for evaluating mathematical expressions.
    """
    if not args:
        return "Please provide a mathematical expression to calculate."

    expression = ' '.join(args)

    # Sanitize and replace user-friendly symbols
    original_expression = expression
    expression = expression.replace('π', 'math.pi').replace('e', 'math.e')
    expression = expression.replace('×', '*').replace('÷', '/')

    # Whitelist of safe functions and constants
    safe_dict = {
        'math': math,
        'pi': math.pi,
        'e': math.e,
        'sqrt': math.sqrt,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'log': math.log,
        'log10': math.log10,
        'pow': pow,
        'abs': abs,
    }

    try:
        # Evaluate the expression in a restricted environment
        result = eval(expression, {"__builtins__": None}, safe_dict)
        return f"{original_expression} = {result}"
    except (SyntaxError, NameError, TypeError, ZeroDivisionError) as e:
        logging.error(f"Calculator error for expression '{expression}': {e}")
        return f"Invalid expression. Please use only numbers, basic operators (+, -, *, /), and constants (pi, e)."
    except Exception as e:
        logging.error(f"An unexpected error occurred in calculator: {e}")
        return "An unexpected error occurred."
