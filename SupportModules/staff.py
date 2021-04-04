from SupportModules import Contact,Password
class Staff:
    def __init__(self,name:str, username:str,contact:Contact, passwd:str,ecrypted=False):
        self.name = name
        self.username = username
        self.contact = Contact(contact.emailid,contact.phone)
        if ecrypted is True:
            self.encryptedpassword = passwd
        else:
            self.password = Password(passwd)
    def __str__(self):
        return f"name:{self.name}\nemailid:{self.contact.emailid}\nphone:{self.contact.phone}"

    def getsqlandvalues(self):
        sql = "insert into stafflist (name,email,username,password,contactnumber,role) values(%s,%s,%s,%s,%s,'staff')"
        if(hasattr(self,'password')):
            # value = (self.name,self.contact.emailid,self.username, self.password.getEncryptedPassword(),self.contact.phone,)
            value = (self.name,self.contact.emailid,self.username, self.password.passwd,self.contact.phone,)
        else:
            value = (self.name,self.contact.emailid,self.username, self.encryptedpassword,self.contact.phone,)
        return [sql,value]
