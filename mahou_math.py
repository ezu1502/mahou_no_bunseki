

def mean(*args: int, ndigits: int | None = None) -> float:
    default_digits = 3
    if ndigits is None:
        return round(sum(args) / len(args), default_digits)
    elif ndigits == 0:
        return sum(args) // len(args)
    
    return round(sum(args) / len(args), ndigits)


