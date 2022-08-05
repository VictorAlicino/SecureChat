import keyboard
from turtle import *

string = ""
while True:
    key = keyboard.read_key(True)
    if key == "enter":
        break
    elif key == "backspace":
        string = string[:-1]
        print(string)
        continue
    else:
        string += key[0]
        print(string)
        continue
