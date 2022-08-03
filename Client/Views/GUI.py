import tkinter as tk
import tkinter.scrolledtext as tkst
from tkinter import simpledialog


def init():
    global root
    root = tk.Tk()
    root.title("Path")
    root.geometry("800x600")
    root.resizable(False, False)
    root.configure(background='#ffffff')
    root.iconbitmap('path.ico')
    root.mainloop()
