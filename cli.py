import os
from Crypto.Cipher import AES
from backports.pbkdf2 import pbkdf2_hmac
from fragileBreak import fragile
import atexit


passwordsLocation = 'passwords.txt'
masterLocation = 'master.txt'
unlocked = False
decrypted = False
masterPass = ''
nonce = ''


def checkIfMasterExists():
    lines = ''
    with open(masterLocation, 'rb') as m:
        lines = m.readlines()
    
    if len(lines) == 0:
        return False
    else:
        return True


def encryptPasswords(override=False):
    global decrypted
    if not override and not decrypted:
        return
    key = pbkdf2_hmac("sha256", masterPass.encode(), masterPass.encode(), 1024, 16)
    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce
    encryptedFile = []
    masterData = []
    firstTime = False

    with open(masterLocation, 'rb') as m:
        masterData = m.readlines()
    if len(masterData) == 2:
        masterData.append(nonce)
        firstTime = True
    else:
        masterData[2] = nonce
    with open(masterLocation, 'wb') as m:
        m.write(masterData[0])
        m.write(masterData[1])
        if firstTime:
            m.write(b'\n')
        m.write(masterData[2])

    with open(passwordsLocation, 'rb') as c:
        for line in c:
            if len(line.split(b'--------')) < 3: continue
            i = len(line) - 1
            while line[i] == 10 or line[i] == 13: i-=1
            encryptedFile.append(cipher.encrypt(line[:i+1]))

    with open(passwordsLocation, 'wb') as c:
        for line in encryptedFile:
            c.write(line)
            c.write(b'\n')

    decrypted = False


def decryptPasswords(override=False):
    global decrypted
    if not override and decrypted:
        return

    key = pbkdf2_hmac("sha256", masterPass.encode(), masterPass.encode(), 1024, 16)
    nonce = b''
    with open(masterLocation, 'rb') as m:
        masterData = m.readlines()

    if (len(masterData) < 3):
        encryptPasswords(override=True)
        with open(masterLocation, 'rb') as m:
            masterData = m.readlines()
    nonce = masterData[2]

    cipher = AES.new(key, AES.MODE_EAX, nonce)

    decryptedFile = []
    with open(passwordsLocation, 'rb') as c:
        for line in c:
            decryptedFile.append(cipher.decrypt(line[:len(line)-1]))

    with open(passwordsLocation, 'wb') as c:
        for line in decryptedFile:
            i = len(line) - 1
            while line[i] == 10 or line[i] == 13: i-=1
            c.write(line)
            c.write(b'\n')
    
    decrypted = True


def validateMasterPassword(password):
    global unlocked, masterPass, nonce

    masterPass = ''
    masterBytes = b''
    decryptedMasterBytes = b''
    with fragile(open(masterLocation, 'rb')) as m:
        masterBytes = m.readline()
        nonce = m.readline()
        nonce = nonce[:len(nonce) - 1]
        if nonce == b'' or masterBytes == b'':
            masterPass = ''
            raise fragile.Break
        key = pbkdf2_hmac("sha256", password.encode(), password.encode(), 1024, 16)
        cipher = AES.new(key, AES.MODE_EAX, nonce)
        decryptedMasterBytes = cipher.decrypt(masterBytes)
        try:
            masterPass = decryptedMasterBytes.decode()
            masterPass = masterPass[:len(masterPass) - 1]
        except:
            print('Incorrect Password.')
            return

    if masterPass == '':
        key = pbkdf2_hmac("sha256", password.encode(), password.encode(), 1024, 16)
        cipher = AES.new(key, AES.MODE_EAX)
        nonce = cipher.nonce
        encryptedPassword = cipher.encrypt(password.encode())
        with open(masterLocation, 'wb') as m:
            m.write(encryptedPassword)
            m.write(b'\n')
            m.write(nonce)
        unlocked = True
        print('Correct Password!')
    elif masterPass == password:
        unlocked = True
        print('Correct Password!')
    else:
        print('Incorrect Password.')


def checkIfDecrypted():
    global decrypted
    item = ''
    try:
        with open(passwordsLocation, 'r') as c:
            item = c.readline()
    except:
        decrypted = False
        return
    if len(item.split('--------')) == 3:
        decrypted = True


def locked_menu():
    global masterPass, unlocked
    checkIfDecrypted()
    if unlocked:
        main_menu()
    if decrypted:
        encryptPasswords()
    unlocked = False
    textprompt = ''
    if checkIfMasterExists():
        textprompt = 'Enter Master Password: '
    else:
        textprompt = 'Create Master Password: '
    password = input(textprompt)
    validateMasterPassword(password)


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



def parseToDict(items):
    adict = {}
    for item in items:
        item_split = item.split('--------')
        if len(item_split) < 3: continue
        adict[item_split[0]] = {'username':item_split[1], 'password':item_split[2][:len(item_split[2]) - 1]}
    return adict


def view_all():
    with open("passwords.txt",mode='r') as d:
        items = parseToDict(d.readlines())
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
    with open("passwords.txt",mode='r') as s:
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
    if not unlocked:
        locked_menu()
    if not decrypted:
        decryptPasswords()
    print("----------PASSWORD LOCKER----------")
    print(" 1. Add/Edit password\n 2. View all passwords\n 3. Search for password\n 4. Delete a password\n 5. Exit")
    option=int(input("Enter the option you want to select: "))
    print('------------------------------------\n\n\n')
    if option==1:
        add_or_edit_password()
    elif option==2:
        view_all()
    elif option==3:
        search_password()
    elif option==4:
        itemToDel = input('Enter item name to delete: ')
        delete_password(itemToDel)
    elif option==5:
        print("Exiting..")
        exit()
    else:
        print("Invalid option.")
    
atexit.register(encryptPasswords)


if __name__ == '__main__':
    if not os.path.exists(passwordsLocation):
        with open(passwordsLocation, 'w'):
            print('Created passwords file.')
    if not os.path.exists(masterLocation):
        with open(masterLocation, 'w'):
            print('Created master file.')
    locked_menu()
    while True:
        main_menu()
        print("\n\n")


               
