from tkinter import filedialog as explorer
from bunseki.analyzer import Analyzer

def ask_file():
    while True:
        path = explorer.askopenfilename()

        if path == "":
            continue
        else:
            return path

path = ask_file()

analysis = Analyzer(path)

print()
print(analysis.see_all_info())
print()