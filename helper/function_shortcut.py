import time

from pywinauto.keyboard import send_keys

def enter_to_function_view(module=None):
    # Enter to Container Details
    if module == 'CD':
        send_keys("{F12}")
        send_keys("{F8}")
        send_keys("{F2}")
        send_keys("{F1}")

    # Enter to Discharge Container
    elif module == 'DC':
        send_keys("{F12}")
        send_keys("{F7}")
        send_keys("{F2}")