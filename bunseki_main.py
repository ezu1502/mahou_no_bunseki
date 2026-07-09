from tkinter import filedialog as explorer
from bunseki.analyzer import Analyzer
import logging

logging.basicConfig(
    level = logging.DEBUG, 
    format = "%(levelname)-5s |  %(message)-30s -> CAST BY: \033[96m%(name)s\033[0m"
    )

def ask_file():
    while True:
        path = explorer.askopenfilename()

        if path == "":
            continue
        else:
            return path

path = ask_file()

analysis = Analyzer(path)


print(f"\n{analysis.see_all_info()}")
print()