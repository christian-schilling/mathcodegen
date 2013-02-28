from sympy import N

def resultParser(result):
    if type(result) is list:
        newres = []
        for i in range(len(result)):
            res = resultParser(result[i])
            newres.append(res)
        result = newres

    else:
        result = N(result)
    return result
