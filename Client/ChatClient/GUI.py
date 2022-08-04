import tkinter as tk
import tkinter.scrolledtext as tkst
from tkinter import simpledialog
from tkinter import messagebox


class UserInterface():
    def __init__(self, name_title: str):
        ui = tk.Tk()


def gui_loop():
    window = tk.Tk()
    window.configure(background="lightgray")

    chat_label = tk.Label(window, text="Chat:", bg="lightgray")
    chat_label.config(font=("Courier", 12))
    chat_label.pack(padx=20, pady=5)

    text_area = tk.scrolledtext.ScrolledText(window)
    text_area.pack(padx=20, pady=5)
    text_area.config(state='disabled')

    msg_label = tk.Label(window, text="Message:", bg="lightgray")
    msg_label.config(font=("Courier", 12))
    msg_label.pack(padx=20, pady=5)
