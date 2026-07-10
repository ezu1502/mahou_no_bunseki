from tkinter import filedialog as explorer, messagebox
from bunseki.analyzer import Analyzer
import logging
import os

logging.basicConfig(
    level = logging.DEBUG, 
    format = "%(levelname)-5s |  %(message)-30s -> CAST BY: \033[96m%(name)s\033[0m"
    )

def ask_file():
    while True:
        path = explorer.askopenfilename()

        if path == "":
            question = messagebox.askretrycancel(
                title = "Mahou no Bunseki warning:",
                message = "Explorer closed. Would you like to try again?"
            )

            if question:
                continue
            else:
                os._exit(0)
        else:
            return path

path = ask_file()

analysis = Analyzer(path)

analysis.show_list(analysis.get_fourier_spectrum)

print(f"\n{analysis.see_all_info()}")
print()