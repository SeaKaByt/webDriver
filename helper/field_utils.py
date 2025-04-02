from pywinauto.keyboard import send_keys

def send_keys_tab(keys):
    send_keys(keys)
    send_keys('{TAB}')

