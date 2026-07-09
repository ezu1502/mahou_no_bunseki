from enum import StrEnum

def check_valid_hex(code: str) -> None:
    if len(code) != 7:
        raise ValueError(
            f"Invalid hexadecimal color: {code!r}. #RRGGBB format expected"
        )
    valid_chars = "abcdefABCDEF1234567890"
    for char in code[1:]:
        if char not in valid_chars:
            raise ValueError(
                f"Invalid hex: {code!r}. {char!r} is not a valid hexadecimal character"
            )
                    
def ansi(code: str) -> str:
    if code.startswith("#"):
        check_valid_hex(code)
        hexa_alphabet: list[str] = ["A", "B", "C", "D", "E", "F"]
        values: list[int] = [10, 11, 12, 13, 14, 15]

        R = code[1:3]
        G = code[3:5]
        B = code[5:7]

        def hex_to_dec(string: str) -> int:
            string = string.upper()
            sixteens, units = string[0], string[1]
            for indx, text in enumerate(hexa_alphabet):
                if sixteens == text:
                    sixteens = values[indx]

                if units == text:
                    units = values[indx]

            Rsixteens = int(sixteens)
            Runits = int(units)
            
            decimal = 16*(Rsixteens) + 1*(Runits) 
            return decimal

        dec_R = hex_to_dec(R)
        dec_G = hex_to_dec(G)
        dec_B = hex_to_dec(B)

        return f"\033[38;2;{dec_R};{dec_G};{dec_B}m"
    
    return f"\033[{code}"

class COLORS(StrEnum):
    RESET = ansi("0m")
    WHITE = ansi("37m")
    RED = ansi("31m")
    GREEN = ansi("32m")
    BLUE = ansi("34m")
    MAGENTA = ansi ("35m")
    ORANGE = ansi("#FF9900")
    PURPLE = ansi("#6200FF")
    
        
def painted_string(string: str, color: COLORS | str = COLORS.WHITE) -> str:
    if isinstance(color, COLORS):
        return f"{color}{string}{COLORS.RESET}"

    ansi_code = ansi(color)
    return f"{ansi_code}{string}{COLORS.RESET}"