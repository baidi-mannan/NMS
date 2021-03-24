import hashlib
class Password:
    def __init__(self, passwd:str):
        self.passwd = passwd
    
    def getEncryptedPassword(self):
        result = hashlib.sha256(self.passwd.encode())
        return result.hexdigest()