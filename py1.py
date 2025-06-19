import os

def master():
    if not os.path.exists("master.txt"):
        master_password=input("enter your master password: ")
        with open("master.txt",mode='w') as a:
            a.write(master_password)
        print("master password created successfully!!")
    else:
        login()



def login():
    master_p=input("enter the master password:")
    with open("master.txt",mode='r') as b:
        Mp=b.read()
        if master_p!=Mp:
            print("wrong password entered!")
            exit()


def all_passwords():
    website=input("enter the name of the website for which you want to save the password:")
    username=input("enter the username:")
    password=input("enter the password:")

    with open("passwords.txt",mode='a') as c:
        c.write(f"{website}--------{username}--------{password}\n")
    print("The password has been saved successfully!")


def view_all():
    with open("passwords.txt",mode='r') as d:
        read=d.read()
        print("The details are:")
        print(read)


def search_password():
    search=input("enter the website whose password u want to know:")
    with open("passwords.txt",mode='r') as s:
        for line in s:
            if search in line:
                print(line)


def main_menu():
    print("----------PASSWORD LOCKER----------")
    print("1.store new password\n 2.view all passwords\n 3.Search for password\n 4.exit")
    option=int(input("enter the option you want to select: "))
    if option==1:
        all_passwords()
    elif option==2:
        view_all()
    elif option==3:
        search_password()
    elif option==4:
        print("Exiting successfully..")
        exit()
    else:
        print("Wrong choice!!")
        exit()

master()
while True:
    main_menu()
    print("\n\n")


               