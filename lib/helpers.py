from Crypto.Cipher import AES
from backports.pbkdf2 import pbkdf2_hmac
from lib.fragileBreak import fragile
import os


def createRequiredDataFiles(passwordsLocation, passwordNonceLocation, masterLocation, masterNonceLocation):
    if not os.path.exists(passwordsLocation):
        os.makedirs(os.path.dirname(passwordsLocation), exist_ok=True)
        with open(passwordsLocation, 'w'):
            print('Created passwords file.')
    if not os.path.exists(masterLocation):
        os.makedirs(os.path.dirname(masterLocation), exist_ok=True)
        with open(masterLocation, 'w'):
            print('Created master file.')
    if not os.path.exists(passwordNonceLocation):
        os.makedirs(os.path.dirname(passwordNonceLocation), exist_ok=True)
        with open(passwordNonceLocation, 'w'):
            print('Created passwords nonce file.')
    if not os.path.exists(masterNonceLocation):
        os.makedirs(os.path.dirname(masterNonceLocation), exist_ok=True)
        with open(masterNonceLocation, 'w'):
            print('Created master nonce file.')
    print('\n\n')    
    

def encryptPasswords(passwordsLocation, passwordNonceLocation, masterPass, decrypted, override=False):
    if not override and not decrypted:
        return False
    key = pbkdf2_hmac("sha256", masterPass.encode(), masterPass.encode(), 1024, 16)
    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce
    encryptedFile = []
    
    with open(passwordNonceLocation, 'wb') as m:
        m.write(nonce)

    with open(passwordsLocation, 'rb') as c:
        items = parseToDict(c.readlines(), bytesMode=True)

    with open(passwordsLocation, 'wb') as c:
        for key in items.keys():
            item = cipher.encrypt(key) + b'--------' + cipher.encrypt(items[key]['username']) + b'--------' + cipher.encrypt(items[key]['password'])
            c.write(item)
            c.write(b'==-----==')

    return False


def decryptPasswords(passwordsLocation, passwordNonceLocation, masterPass, decrypted, override=False):
    if not override and decrypted:
        return True
    with open(passwordsLocation, 'rb') as p:
        if len(p.readlines()) == 0:
            return True
    key = pbkdf2_hmac("sha256", masterPass.encode(), masterPass.encode(), 1024, 16)
    nonce = b''

    with open(passwordNonceLocation, 'rb') as m:
        nonce = m.read()

    cipher = AES.new(key, AES.MODE_EAX, nonce)

    decryptedFile = []
    with open(passwordsLocation, 'rb') as c:
        items = c.read()

    items = items.split(b'==-----==')

    with open(passwordsLocation, 'wb') as c:
        for item in items:
            data = item.split(b'--------')
            if (len(data) < 3): continue
            decrypted_item = cipher.decrypt(data[0]) + b'--------' + cipher.decrypt(data[1]) + b'--------' + cipher.decrypt(data[2])
            c.write(decrypted_item)
            c.write(b'\n')
    
    return True


def checkIfMasterExists(masterLocation):
    lines = ''
    with open(masterLocation, 'rb') as m:
        lines = m.readlines()
    
    if len(lines) == 0:
        return False
    else:
        return True


def validateMasterPassword(masterLocation, masterNonceLocation, password):

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
            return False

    if masterPass == '':
        key = pbkdf2_hmac("sha256", password.encode(), password.encode(), 1024, 16)
        cipher = AES.new(key, AES.MODE_EAX)
        nonce = cipher.nonce
        encryptedPassword = cipher.encrypt(password.encode())
        with open(masterLocation, 'wb') as m:
            m.write(encryptedPassword)
        with open(masterNonceLocation, 'wb') as n:
            n.write(nonce)
        return True
    elif masterPass == password:
        return True
    else:
        return False


def checkIfDecrypted(passwordsLocation):
    item = ''
    try:
        with open(passwordsLocation, 'r') as c:
            item = c.readline()
    except:
        return False
    if item.count('==-----==') == 0 and len(item) > 0:
        return True
    else:
        return False
    

def parseToDict(items, bytesMode=False):
    adict = {}
    if bytesMode:
        seperator = b'--------'
    else: 
        seperator = '--------'
    for item in items:
        item_split = item.split(seperator)
        if len(item_split) < 3: continue
        adict[item_split[0]] = {'username':item_split[1], 'password':item_split[2][:len(item_split[2]) - 1]}
    return adict