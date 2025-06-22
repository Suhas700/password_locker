from tkinter import *
from tkinter import ttk


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
    unlocked = True
    unlockedMenu()
    print(password)


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


def addNewMenu():
    global root, mainframe, unlocked
    if not unlocked:
        lockedMenu()

    removeAllWidgets(mainframe)

    item_name = StringVar()
    ttk.Entry(mainframe, textvariable=item_name).grid(column=2, row=1, sticky=(N, W, E, S))
    ttk.Label(mainframe, text='Item Name: ').grid(column=1, row=1, sticky=(W))

    username = StringVar()
    ttk.Entry(mainframe, textvariable=username).grid(column=2, row=2, sticky=(N, W, E, S))
    ttk.Label(mainframe, text='Username: ').grid(column=1, row=2, sticky=(W))

    password = StringVar()
    ttk.Entry(mainframe, textvariable=password).grid(column=2, row=3, sticky=(N, W, E, S))
    ttk.Label(mainframe, text='Password: ').grid(column=1, row=3, sticky=(W))


    ttk.Button(mainframe, text='Save', command=lambda: saveItem(item_name.get(), username.get(), password.get())).grid(column=2, row=4, sticky=(S))
    

    def saveItem(item, username, password):
        print(item + username + password)


def viewAllMenu():
    global root, mainframe, unlocked
    if not unlocked:
        lockedMenu()

    removeAllWidgets(mainframe)


def searchMenu():
    global root, mainframe, unlocked
    if not unlocked:
        lockedMenu()

    removeAllWidgets(mainframe)



lockedMenu()











# def calculate(*args):
#     try:
#         value = float(feet.get())
#         meters.set(int(0.3048 * value * 10000.0 + 0.5)/10000.0)
#     except ValueError:
#         pass

# root = Tk()
# root.title("Feet to Meters")

# mainframe = ttk.Frame(root)
# mainframe.grid(column=0, row=0)
# root.columnconfigure(0, weight=1)
# root.rowconfigure(0, weight=1)

# feet = StringVar()
# feet_entry = ttk.Entry(mainframe, width=7, textvariable=feet)
# feet_entry.grid(column=2, row=1, sticky=(W, E))

# meters = StringVar()
# ttk.Label(mainframe, textvariable=meters).grid(column=2, row=2, sticky=(W, E))

# ttk.Button(mainframe, text="Calculate", command=calculate).grid(column=3, row=3, sticky=W)

# ttk.Label(mainframe, text="feet").grid(column=3, row=1, sticky=W)
# ttk.Label(mainframe, text="is equivalent to").grid(column=1, row=2, sticky=E)
# ttk.Label(mainframe, text="meters").grid(column=3, row=2, sticky=W)

# for child in mainframe.winfo_children(): 
#     child.grid_configure(padx=5, pady=5)

# feet_entry.focus()
# root.bind("<Return>", calculate)

# root.mainloop()