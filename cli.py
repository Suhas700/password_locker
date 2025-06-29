import os
from lib.helpers import *
import atexit


passwordsLocation = '.\\data\\passwords.txt'
passwordNonceLocation = '.\\data\\passwordnonce.txt'
masterLocation = '.\\data\\master.txt'
masterNonceLocation = '.\\data\\masternonce.txt'
unlocked = False
decrypted = False
masterPass = ''
nonce = ''



def locked_menu():
    global masterPass, unlocked, decrypted

    decrypted = checkIfDecrypted(passwordsLocation)
    if unlocked:
        main_menu()
    if decrypted:
        decrypted = encryptPasswords(passwordsLocation, passwordNonceLocation, masterPass, decrypted)
    unlocked = False
    textprompt = ''
    if checkIfMasterExists(masterLocation):
        new = False
        textprompt = 'Enter Master Password: '
    else:
        new = True
        textprompt = 'Create Master Password: '
    password = input(textprompt)
    unlocked = validateMasterPassword(masterLocation, masterNonceLocation, password)
    if (unlocked):
        if (new): print('Master Password successfully created.')
        else: print('Correct Password!')
        masterPass = password
    else:
        print('Incorrect Password.')


def add_or_edit_password():
    item=input("enter item name: ")
    username=input("enter username: ")
    password=input("enter password: ")

    saveItem(item, username, password)
    print("The password has been saved successfully!")


def saveItem(item, username, password):
    global unlocked
    items = []
    with open(passwordsLocation, mode='r') as c:
        items = c.readlines()
    items = parseToDict(items)
    
    items[item] = {'username':username, 'password':password}

    with open(passwordsLocation, mode='w') as c:
        for item in items.keys():
            c.write(f"{item}--------{items[item]['username']}--------{items[item]['password']}\n")



def view_all():
    with open(passwordsLocation, mode='r') as d:
        items = d.readlines()
        if len(items) == 0:
            print('No passwords have been stored.')
            return
        items = parseToDict(items)
        print("The details are:")
        justification = 0
        for key in items.keys():
            justification = max(justification, len(key), len(items[key]['username']), len(items[key]['password']), 8) + 2
        print('ITEM'.ljust(justification) +
            'USERNAME'.center(justification) +
            'PASSWORD'.rjust(justification))
        for key in items.keys():
            print(key.ljust(justification) +
                items[key]['username'].center(justification) +
                items[key]['password'].rjust(justification))          


def search_password():
    search=input("enter the item name: ")
    print('\n search results:\n')
    with open(passwordsLocation, mode='r') as s:
        items = parseToDict(s.readlines())
        if search in items.keys():
            justification = max(len(search), len(items[search]['username']), len(items[search]['password']), 8) + 2
            print('ITEM'.ljust(justification) +
                  'USERNAME'.center(justification) +
                  'PASSWORD'.rjust(justification))
            print(search.ljust(justification) +
                  items[search]['username'].center(justification) +
                  items[search]['password'].rjust(justification))                
        else:
            print("No such item has been saved.")


def delete_password(itemToDel):
    items = []
    with open(passwordsLocation, 'r') as p:
        items = p.readlines()
    items = parseToDict(items)
    if itemToDel not in items.keys():
        print("The item:", itemToDel, "- does not exist.")
        return

    with open(passwordsLocation, 'w') as p:
        for item in items.keys():
            if item == itemToDel:
                continue
            p.write(f"{item}--------{items[item]['username']}--------{items[item]['password']}\n")
    print('Deleted:', itemToDel, 'successfully.')

def main_menu():
    global unlocked, decrypted
    if not unlocked:
        locked_menu()
    if not decrypted:
        decrypted = decryptPasswords(passwordsLocation, passwordNonceLocation, masterPass, decrypted)
    print("\n----------PASSWORD LOCKER----------")
    print(" 1. Add/Edit password\n 2. View all passwords\n 3. Search for password\n 4. Delete a password\n 5. Exit")
    option=input("Enter the option you want to select: ")
    print('------------------------------------\n\n\n')
    if option=='1':
        add_or_edit_password()
    elif option=='2':
        view_all()
    elif option=='3':
        search_password()
    elif option=='4':
        itemToDel = input('Enter item name to delete: ')
        delete_password(itemToDel)
    elif option=='5':
        print("Exiting..")
        exit()
    else:
        print("Invalid option.")

def exit_handler():
    global decrypted
    decrypted = encryptPasswords(passwordsLocation, passwordNonceLocation, masterPass, decrypted)
atexit.register(exit_handler)



if __name__ == '__main__':
    
    createRequiredDataFiles(passwordsLocation, passwordNonceLocation, masterLocation, masterNonceLocation)

    locked_menu()
    while True:
        main_menu()
        print("\n\n")


               
