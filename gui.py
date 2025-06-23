from tkinter import *
from tkinter import ttk


passwordsLocation = 'passwords.txt'
masterLocation = 'master.txt'


root = Tk()

unlocked = False
root.title("Password Locker")
mainframe = ttk.Frame(root)
mainframe.grid(column=0, row=0)
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)


def exitApp():
    exit()


def removeAllWidgets(frame):
    for widget in frame.winfo_children():
        widget.destroy()


def validateMasterPassword(password):
    global unlocked

    masterPass = ''
    with open(masterLocation, 'r') as m:
        masterPass = m.readline()

    if masterPass == '':
        with open(masterLocation, 'w') as m:
            m.write(password)
        unlocked = True
    elif masterPass == password:
        unlocked = True

    unlockedMenu()
    

def lockedMenu():
    global mainframe, root, unlocked

    unlocked = False
    removeAllWidgets(mainframe)
    masterPass = StringVar()
    ttk.Entry(mainframe, textvariable=masterPass).grid(column=2, row=2, sticky=(N, W, E, S))
    ttk.Label(mainframe, text='Master Password: ').grid(column=1, row=2, sticky=(W))
    ttk.Button(mainframe, text='Submit', command=lambda: validateMasterPassword(masterPass.get())).grid(column=2, row=3, sticky=(S))
    root.mainloop()


def unlockedMenu():
    global root, mainframe, unlocked
    if not unlocked:
        lockedMenu()
    removeAllWidgets(mainframe)
    ttk.Button(mainframe, text='Add New', command=addNewMenu).grid(column=2, row=1)
    ttk.Button(mainframe, text='View All', command=viewAllMenu).grid(column=2, row=2)
    ttk.Button(mainframe, text='Search', command=searchMenu).grid(column=2, row=3)
    ttk.Button(mainframe, text='Lock', command=lockedMenu).grid(column=2, row=4)
    ttk.Button(mainframe, text='Exit', command=exitApp).grid(column=2, row=5)


def addNewMenu(i='', u='', p='', overwrite=False):
    global root, mainframe, unlocked
    if not unlocked:
        lockedMenu()

    removeAllWidgets(mainframe)

    item_name = StringVar(value=i)
    ttk.Entry(mainframe, textvariable=item_name).grid(column=2, row=1, sticky=(N, W, E, S))
    ttk.Label(mainframe, text='Item Name: ').grid(column=1, row=1, sticky=(W))

    username = StringVar(value=u)
    ttk.Entry(mainframe, textvariable=username).grid(column=2, row=2, sticky=(N, W, E, S))
    ttk.Label(mainframe, text='Username: ').grid(column=1, row=2, sticky=(W))

    password = StringVar(value=p)
    ttk.Entry(mainframe, textvariable=password).grid(column=2, row=3, sticky=(N, W, E, S))
    ttk.Label(mainframe, text='Password: ').grid(column=1, row=3, sticky=(W))

    ttk.Button(mainframe, text='Save', command=lambda: saveItem(item_name.get(), username.get(), password.get(), overwrite=overwrite)).grid(column=2, row=4, sticky=(S))
    ttk.Button(mainframe, text='Cancel', command=unlockedMenu).grid(column=2, row=5, sticky=(S))
    

def saveItem(item, username, password, overwrite=False):
    global root, mainframe, unlocked
    items = []
    with open(passwordsLocation, mode='r') as c:
        items = c.readlines()
    items = parseToDict(items)
    if not overwrite and item in items.keys():
        ttk.Label(mainframe, text='Item with this item name already exists.').grid(column=2, row=7)
        return
    
    items[item] = {'username':username, 'password':password}

    with open(passwordsLocation, mode='w') as c:
        for item in items.keys():
            c.write(f"{item}--------{items[item]['username']}--------{items[item]['password']}")
    
    unlockedMenu()


def parseToDict(items):
    adict = {}
    for item in items:
        item_split = item.split('--------')
        adict[item_split[0]] = {'username':item_split[1], 'password':item_split[2]}
    return adict


def viewAllMenu():
    global root, mainframe, unlocked
    if not unlocked:
        lockedMenu()

    removeAllWidgets(mainframe)
    ttk.Button(mainframe, text='Cancel', command=unlockedMenu).grid(column=2, row=0, sticky=(N))
    c = open(passwordsLocation, mode='r')
    lines = c.readlines()
    for i in range(len(lines)):
            item = lines[i].split('--------')
            ttk.Label(mainframe, text='Item Name: ' + item[0] + '\t').grid(column=1, row=i+1)
            ttk.Label(mainframe, text='Username: ' + item[1] + '\t').grid(column=2, row=i+1)
            ttk.Label(mainframe, text='Password: ' + item[2] + '\t').grid(column=3, row=i+1)
            ttk.Button(mainframe, text='Edit', command=lambda: addNewMenu(item[0], item[1], item[2], overwrite=True)).grid(column=4, row=i+1)
    
    c.close()


def searchMenu():
    global root, mainframe, unlocked
    if not unlocked:
        lockedMenu()

    removeAllWidgets(mainframe)

    ttk.Button(mainframe, text='Cancel', command=unlockedMenu).grid(column=2, row=0, sticky=(N))
    searchItem = StringVar()
    ttk.Label(mainframe, text='Enter item name to search for:').grid(column=2,row=1)
    ttk.Entry(mainframe, textvariable=searchItem).grid(column=2, row=2)
    ttk.Button(mainframe, text='Search', command=lambda: search(searchItem.get())).grid(column=2, row=3)


def search(searchItem):
    items = []
    with open(passwordsLocation, mode='r') as c:
        items = c.readlines()
    
    items = parseToDict(items)
    
    if searchItem in items.keys():
        username = items[searchItem]['username']
        password = items[searchItem]['password']
        ttk.Label(mainframe, text='Item Name: ' + searchItem + '\t').grid(column=1, row=4)
        ttk.Label(mainframe, text='Username: ' + username + '\t').grid(column=2, row=4)
        ttk.Label(mainframe, text='Password: ' + password + '\t').grid(column=3, row=4)
        ttk.Button(mainframe, text='Edit', command=lambda: addNewMenu(searchItem, username, password, overwrite=True)).grid(column=4, row=4)
    else:
        ttk.Label(mainframe, text='Item does not exist.').grid(column=2, row=4)



if __name__ == '__main__':
    lockedMenu()    
