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

analysis.show_list(analysis.properties.get_fourier_spectrum)


def test_freq_to_note():
    for i in range (1, 12):

        factor = 440*(2**((1/12)*i))
        note = analysis.freq_to_note(factor)
        print(note)



print(f"\n{analysis.see_all_info()}")
print()