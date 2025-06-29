from tkinter import *
from tkinter import ttk
from Crypto.Cipher import AES
from backports.pbkdf2 import pbkdf2_hmac
from lib.fragileBreak import fragile
from lib.helpers import *
import atexit
import os


passwordsLocation = os.path.join('.', 'data', 'passwords.txt')
passwordNonceLocation = os.path.join('.', 'data', 'passwordnonce.txt')
masterLocation = os.path.join('.', 'data', 'master.txt')
masterNonceLocation = os.path.join('.', 'data', 'masternonce.txt')
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
mainframe = ttk.Frame(root)
mainframe.pack(fill=BOTH, expand=1)
mainframe.grid(column=0, row=0, padx=padX, pady=padY)
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
s = ttk.Style()
# themes = ('winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')
s.theme_use('classic')


def exitApp():
    exit()


def removeAllWidgets(frame):
    try:
        for widget in frame.winfo_children():
            widget.destroy()
    except:
        print("Closing app.")
        # exitApp()


def validateMasterPassword(password, isNew):
    global unlocked, masterPass, nonce

    if isNew:
        correctPrint = 'Created Master Password.'
    else:
        correctPrint = 'Correct Password!'

    masterPass = ''
    masterBytes = b''
    decryptedMasterBytes = b''
    nonce = b''
    with fragile(open(masterLocation, 'rb')) as m:
        masterBytes = m.read()
        if len(masterBytes) == 0:
            masterPass = ''
            raise fragile.Break
        with open(masterNonceLocation, 'rb') as n:
            nonce = n.read()

        key = pbkdf2_hmac("sha256", password.encode(), password.encode(), 1024, 16)
        cipher = AES.new(key, AES.MODE_EAX, nonce)
        decryptedMasterBytes = cipher.decrypt(masterBytes)
        try:
            masterPass = decryptedMasterBytes.decode()
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
        with open(masterNonceLocation, 'wb') as n:
            n.write(nonce)
        unlocked = True
        masterPass = password
        ttk.Label(mainframe, text=correctPrint).grid(column=2, row=4, padx=padX, pady=padY)
    elif masterPass == password:
        unlocked = True
        ttk.Label(mainframe, text=correctPrint).grid(column=2, row=4, padx=padX, pady=padY)
    else:
        ttk.Label(mainframe, text='Incorrect Password.').grid(column=2, row=4, padx=padX, pady=padY)
    
    unlockedMenu()

    

def lockedMenu():
    global mainframe, root, unlocked, decrypted, masterPass

    unlocked = False
    decrypted = checkIfDecrypted(passwordsLocation)
    removeAllWidgets(mainframe)
    if decrypted:
        decrypted = encryptPasswords(passwordsLocation, passwordNonceLocation, masterPass, decrypted)
    masterPass = ''
    
    textprompt = ''
    if checkIfMasterExists(masterLocation):
        new = False
        textprompt = 'Enter Master Password: '
    else:
        new = True
        textprompt = 'Create Master Password: '
    masterPassVal = StringVar()
    ttk.Entry(mainframe, textvariable=masterPassVal).grid(column=2, row=2, sticky=(N, W, E, S), padx=padX, pady=padY)
    ttk.Label(mainframe, text=textprompt).grid(column=1, row=2, sticky=(W), padx=padX, pady=padY)
    ttk.Button(mainframe, text='Submit', command=lambda: validateMasterPassword(masterPassVal.get(), new)).grid(column=2, row=3, sticky=(S), padx=padX, pady=padY)
    root.mainloop()


def unlockedMenu(displayMessage=''):
    global root, mainframe, unlocked, decrypted, masterPass
    if not unlocked:
        lockedMenu()
    if not decrypted:
        decrypted = decryptPasswords(passwordsLocation, passwordNonceLocation, masterPass, decrypted)

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
    ttk.Label(mainframe, text='ITEM NAME', font=("Arial", 10, "bold"), borderwidth=2, relief='flat', padding='5 5 5 5').grid(column=1, row=1, padx=padX, pady=padY, sticky=(W))
    ttk.Label(mainframe, text='USERNAME', font=("Arial", 10, "bold"), borderwidth=2, relief='flat', padding='5 5 5 5').grid(column=2, row=1, padx=padX, pady=padY, sticky=(W))
    ttk.Label(mainframe, text='PASSWORD', font=("Arial", 10, "bold"), borderwidth=2, relief='flat', padding='5 5 5 5').grid(column=3, row=1, padx=padX, pady=padY, sticky=(W))
    for i in range(len(keys)):
            item = lines[i].split('--------')
            if len(item) < 3: continue
            ttk.Label(mainframe, text='  ' + str(i+1)+'. ').grid(column=0, row=i+2)
            ttk.Label(mainframe, text=keys[i], borderwidth=2, relief='flat', padding='5 5 5 5').grid(column=1, row=i+2, padx=padX, pady=padY, sticky=(W))
            ttk.Label(mainframe, text=items[keys[i]]['username'], borderwidth=2, relief='flat', padding='5 5 5 5').grid(column=2, row=i+2, padx=padX, pady=padY, sticky=(W))
            ttk.Label(mainframe, text=items[keys[i]]['password'], borderwidth=2, relief='flat', padding='5 5 5 5').grid(column=3, row=i+2, padx=padX, pady=padY, sticky=(W))
            
    c.close()


def searchMenu(displayMessage=''):
    global root, mainframe, unlocked
    if not unlocked:
        lockedMenu()

    removeAllWidgets(mainframe)

    ttk.Button(mainframe, text='Cancel', command=unlockedMenu).grid(column=2, row=0, sticky=(N), padx=padX, pady=padY)
    searchItem = StringVar()
    ttk.Label(mainframe, text='Enter item name to search for:').grid(column=2,row=1, padx=padX, pady=padY)
    ttk.Entry(mainframe, textvariable=searchItem).grid(column=2, row=2, padx=padX, pady=padY)
    if displayMessage != '':
        ttk.Label(mainframe, text=displayMessage).grid(column=2,row=5, padx=padX, pady=padY)
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
    searchMenu(displayMessage="Deleted " + itemToDel + " successfully.")



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
        searchMenu(displayMessage='Item does not exist.')



def exit_handler():
    global decrypted, masterPass
    removeAllWidgets(mainframe)
    decrypted = encryptPasswords(passwordsLocation, passwordNonceLocation, masterPass, decrypted)
atexit.register(exit_handler)


if __name__ == '__main__':
    
    createRequiredDataFiles(passwordsLocation, passwordNonceLocation, masterLocation, masterNonceLocation)

    lockedMenu()    
