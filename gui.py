from tkinter import *
from tkinter import ttk
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
paddingVal = 10
padX = (paddingVal, paddingVal)
padY = (paddingVal, paddingVal)

root = Tk()
root.title("Password Locker")
root.resizable(0, 0)
# root.geometry("300x350")
mainframe = ttk.Frame(root)
# mainframe.pack_propagate(0)
mainframe.pack(fill=BOTH, expand=1)
mainframe.grid(column=0, row=0, padx=padX, pady=padY)
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
s = ttk.Style()
s.theme_use('alt')


def exitApp():
    exit()


def removeAllWidgets(frame):
    try:
        for widget in frame.winfo_children():
            widget.destroy()
    except:
        print("Closing app.")
        # exitApp()


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
            ttk.Label(mainframe, text='Incorrect Password.').grid(column=2, row=4, padx=padX, pady=padY)
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
        ttk.Label(mainframe, text='Correct Password!').grid(column=2, row=4, padx=padX, pady=padY)
    elif masterPass == password:
        unlocked = True
        ttk.Label(mainframe, text='Correct Password!').grid(column=2, row=4, padx=padX, pady=padY)
    else:
        ttk.Label(mainframe, text='Incorrect Password.').grid(column=2, row=4, padx=padX, pady=padY)

    unlockedMenu()


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
    

def lockedMenu():
    global mainframe, root, unlocked, decrypted, masterPass

    unlocked = False
    checkIfDecrypted()
    removeAllWidgets(mainframe)
    if decrypted:
        encryptPasswords()
    masterPass = ''
    
    masterPassVal = StringVar()
    ttk.Entry(mainframe, textvariable=masterPassVal).grid(column=2, row=2, sticky=(N, W, E, S), padx=padX, pady=padY)
    ttk.Label(mainframe, text='Master Password: ').grid(column=1, row=2, sticky=(W), padx=padX, pady=padY)
    ttk.Button(mainframe, text='Submit', command=lambda: validateMasterPassword(masterPassVal.get())).grid(column=2, row=3, sticky=(S), padx=padX, pady=padY)
    root.mainloop()


def unlockedMenu(displayMessage=''):
    global root, mainframe, unlocked, decrypted
    if not unlocked:
        lockedMenu()
    if not decrypted:
        decryptPasswords()

    removeAllWidgets(mainframe)
    ttk.Button(mainframe, text='Add', command=addNewMenu).grid(column=2, row=1, padx=padX, pady=padY)
    ttk.Button(mainframe, text='View All', command=viewAllMenu).grid(column=2, row=2, padx=padX, pady=padY)
    ttk.Button(mainframe, text='Search', command=searchMenu).grid(column=2, row=3, padx=padX, pady=padY)
    ttk.Button(mainframe, text='Lock', command=lockedMenu).grid(column=2, row=4, padx=padX, pady=padY)
    ttk.Button(mainframe, text='Exit', command=exitApp).grid(column=2, row=5, padx=padX, pady=padY)
    if displayMessage != '':
        ttk.Label(mainframe, text=displayMessage).grid(column=2,row=6, padx=padX, pady=padY)


def addNewMenu(i='', u='', p='', overwrite=''):
    global root, mainframe, unlocked
    if not unlocked:
        lockedMenu()

    removeAllWidgets(mainframe)

    item_name = StringVar(value=i)
    ttk.Entry(mainframe, textvariable=item_name).grid(column=2, row=1, sticky=(N, W, E, S), padx=padX, pady=padY)
    ttk.Label(mainframe, text='Item Name: ').grid(column=1, row=1, sticky=(W), padx=padX, pady=padY)

    username = StringVar(value=u)
    ttk.Entry(mainframe, textvariable=username).grid(column=2, row=2, sticky=(N, W, E, S), padx=padX, pady=padY)
    ttk.Label(mainframe, text='Username: ').grid(column=1, row=2, sticky=(W), padx=padX, pady=padY)

    password = StringVar(value=p)
    ttk.Entry(mainframe, textvariable=password).grid(column=2, row=3, sticky=(N, W, E, S), padx=padX, pady=padY)
    ttk.Label(mainframe, text='Password: ').grid(column=1, row=3, sticky=(W), padx=padX, pady=padY)

    ttk.Button(mainframe, text='Save', command=lambda: saveItem(item_name.get(), username.get(), password.get(), overwrite=overwrite)).grid(column=2, row=4, sticky=(S), padx=padX, pady=padY)
    ttk.Button(mainframe, text='Cancel', command=unlockedMenu).grid(column=2, row=5, sticky=(S), padx=padX, pady=padY)
    

def saveItem(item, username, password, overwrite=''):
    global root, mainframe, unlocked
    items = []
    with open(passwordsLocation, mode='r') as c:
        items = c.readlines()
    items = parseToDict(items)
    if overwrite == '' and item in items.keys():
        ttk.Label(mainframe, text='Item with this item name already exists.').grid(column=2, row=7, padx=padX, pady=padY)
        return
    if overwrite != '':
        items.pop(overwrite)
    
    items[item] = {'username':username, 'password':password}

    with open(passwordsLocation, mode='w') as c:
        for item in items.keys():
            c.write(f"{item}--------{items[item]['username']}--------{items[item]['password']}\n")
    
    unlockedMenu(displayMessage='Saved ' + item + ' successfully.')


def parseToDict(items):
    adict = {}
    for item in items:
        item_split = item.split('--------')
        if len(item_split) < 3: continue
        adict[item_split[0]] = {'username':item_split[1], 'password':item_split[2][:len(item_split[2]) - 1]}
    return adict


def viewAllMenu():
    global root, mainframe, unlocked
    if not unlocked:
        lockedMenu()

    removeAllWidgets(mainframe)
    ttk.Button(mainframe, text='Cancel', command=unlockedMenu).grid(column=2, row=0, padx=padX, pady=padY)
    c = open(passwordsLocation, mode='r')
    lines = c.readlines()
    items = parseToDict(lines)
    keys = list(items.keys())
    ttk.Label(mainframe, text='ITEM NAME' + '\t').grid(column=1, row=1, padx=padX, pady=padY)
    ttk.Label(mainframe, text='USERNAME' + '\t').grid(column=2, row=1, padx=padX, pady=padY)
    ttk.Label(mainframe, text='PASSWORD' + '\t').grid(column=3, row=1, padx=padX, pady=padY)
    for i in range(len(keys)):
            item = lines[i].split('--------')
            if len(item) < 3: continue
            ttk.Label(mainframe, text=keys[i] + '\t').grid(column=1, row=i+2, padx=padX, pady=padY)
            ttk.Label(mainframe, text=items[keys[i]]['username'] + '\t').grid(column=2, row=i+2, padx=padX, pady=padY)
            ttk.Label(mainframe, text=items[keys[i]]['password'] + '\t').grid(column=3, row=i+2, padx=padX, pady=padY)
            
    c.close()


def searchMenu(deleted=False, deletedItem=''):
    global root, mainframe, unlocked
    if not unlocked:
        lockedMenu()

    removeAllWidgets(mainframe)

    ttk.Button(mainframe, text='Cancel', command=unlockedMenu).grid(column=2, row=0, sticky=(N), padx=padX, pady=padY)
    searchItem = StringVar()
    ttk.Label(mainframe, text='Enter item name to search for:').grid(column=2,row=1, padx=padX, pady=padY)
    ttk.Entry(mainframe, textvariable=searchItem).grid(column=2, row=2, padx=padX, pady=padY)
    if deleted:
        ttk.Label(mainframe, text='Deleted ' + deletedItem + ' successfully.').grid(column=2,row=5, padx=padX, pady=padY)
    ttk.Button(mainframe, text='Search', command=lambda: search(searchItem.get())).grid(column=2, row=3, padx=padX, pady=padY)


def deleteItem(itemToDel):
    items = []
    with open(passwordsLocation, 'r') as p:
        items = p.readlines()
    items = parseToDict(items)
    if itemToDel not in items.keys():
        ttk.Label(mainframe, text="The item (" + itemToDel + ") does not exist.").grid(column=2,row=5, padx=padX, pady=padY)
        return

    with open(passwordsLocation, 'w') as p:
        for item in items.keys():
            if item == itemToDel:
                continue
            p.write(f"{item}--------{items[item]['username']}--------{items[item]['password']}\n")
    searchMenu(deleted=True, deletedItem=itemToDel)



def search(searchItem):
    items = []
    with open(passwordsLocation, mode='r') as c:
        items = c.readlines()
    
    items = parseToDict(items)
    
    if searchItem in items.keys():
        username = items[searchItem]['username']
        password = items[searchItem]['password']
        ttk.Label(mainframe, text='Item Name: ' + searchItem + '\t').grid(column=1, row=4, padx=padX, pady=padY)
        ttk.Label(mainframe, text='Username: ' + username + '\t').grid(column=2, row=4, padx=padX, pady=padY)
        ttk.Label(mainframe, text='Password: ' + password + '\t').grid(column=3, row=4, padx=padX, pady=padY)
        ttk.Button(mainframe, text='Edit', command=lambda: addNewMenu(searchItem, username, password, overwrite=searchItem)).grid(column=4, row=4, padx=padX, pady=padY)
        ttk.Button(mainframe, text='Delete', command=lambda: deleteItem(searchItem)).grid(column=5, row=4, padx=padX, pady=padY)
    else:
        ttk.Label(mainframe, text='Item does not exist.').grid(column=2, row=4, padx=padX, pady=padY)



def exit_handler():
    removeAllWidgets(mainframe)
    encryptPasswords()
atexit.register(exit_handler)


if __name__ == '__main__':
    lockedMenu()    
