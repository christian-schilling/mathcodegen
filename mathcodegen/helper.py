# evaluates function recursively on elements
# in nested lists
def map_recursively(function, value):
    if type(value) is list:
        return [map_recursively(function, v) for v in value]
    else:
        return function(value)
