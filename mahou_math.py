from functools import wraps

def check_args(function):
    @wraps
    def wrapper(*args):
        if not args:
            raise ValueError("median requires at least one value")
        else:
            function(*args)
    
    return wrapper


#region BASICS

def is_even(number):
    even = ((number % 2) == 0)
    return True if even else False


#region STATISTIC

@check_args
def mean(*args: int| float) -> float:
    return sum(args) / len(args)

@check_args
def median(*args):
    arg_list = [*args]
    arg_list.sort()
    
    length = len(arg_list)
    if not is_even(length):
        index = length // 2

        median = arg_list[index]
        return median
    else:
        index = length // 2
        median = mean(arg_list[index-1], arg_list[index])
        return median

@check_args
def mode(*args):
    final_list = []
    for each in set(args):
        each_ocurrence = 0
        for arg in args:
            if each == arg:
                each_ocurrence += 1
        final_list.append((each, each_ocurrence))

    freq_list = [item[1] for item in final_list]

    if len(final_list) > 1 and len(set(freq_list)) == 1:
        return None
    
    final_list.sort(key = lambda item: item[1], reverse = True)
    mode = final_list[0][0]

    return mode













@check_args
def mean_deviation(*args: int | float) -> float:
    args_mean = mean(*args)
    deviation_sum = 0
    for arg in args:
        deviation = abs(args_mean - arg)
        deviation_sum += deviation

    return deviation_sum / len(args)

@check_args        
def standard_deviation(*args):
    args_mean = mean(*args)
    squared_deviations = 0
    for arg in args:
        deviation = (arg - args_mean)**2
        squared_deviations += deviation

    variancy = squared_deviations / len(args)

    return sqrt(variancy)
#endregion
#region ARITHMETICS

def sqrt(number: int | float) -> float:
    return number ** (1/2)

def power(number, exponent):
    return number**exponent

def squared(number):
    return number**2

def tetration(a, b):
    result = 1
    for _ in range(b):
        result = a ** result

    return result

def pentation(a, b):
    result = 1
    for _ in range(b):
        result = tetration(a, result)

    return result

def hexation(a, b):
    result = 1
    for _ in range(b):
        result = pentation(a, result)

    return result
#endregion