class SafeDict(dict):
    def __missing__(self, key):
        return "${" + key + "}"


def parse_expression(expression, process_variables):
    # Check if expression is a string
    if not isinstance(expression, str):
        raise TypeError(f"Expected expression to be a string, but got {type(expression)} with value {expression}")

    # Extract the key from the expression
    key = expression.replace("${", "").replace("}", "")

    # If the key is in process_variables, return the corresponding value
    if key in process_variables:
        return process_variables[key]
    
    # If not, try to format the entire expression
    try:
        return expression.replace("${", "{").format_map(SafeDict(process_variables))
    except Exception as e:
        # Handle or raise appropriate exception here, e.g.:
        raise ValueError(f"Failed to format expression '{expression}' with provided variables. Original error: {e}")



if __name__ == "__main__":
    test = "___${a[nice]}___"
    print(parse_expression(test, {"a": {"nice": ["OK"]}}))
