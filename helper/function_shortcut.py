from pywinauto.keyboard import send_keys

def enter_to_function_view(function=None):
    if function == 'Container Details':
        send_keys("{F12}")
        send_keys("{F8}")
        send_keys("{F2}")
        send_keys("{F1}")