import os
#import sys
# this module is only made for linux and posix.


all_keys_pressed = []
def handled_input():
    if os.name == 'posix' or os.name == 'linux':
        from pynput import keyboard
        def on_press(key):
            try:
                k = key.char  
                all_keys_pressed.append(k)
                print(all_keys_pressed)
            except:
                k = key.name 
                all_keys_pressed.append(k)
                print(all_keys_pressed)

        while True:
            os.system("stty -echo")
            listener = keyboard.Listener(on_press=on_press)
            listener.start() 
            listener.join() 



#handled_input()