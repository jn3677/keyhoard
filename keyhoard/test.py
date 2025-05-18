import keyboard

def on_enter():
    print("Enter pressed!")

keyboard.add_hotkey('enter', on_enter)
keyboard.wait()