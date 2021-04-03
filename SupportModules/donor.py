from SupportModules import Contact,Password
import sys
class Donor:
    def __init__(self,name:str, username:str,contact:Contact, passwd:str,membership = 1,ecrypted=False):
        self.debug = True
        self.name = name
        self.username = username
        self.contact = Contact(contact.emailid,contact.phone)
        self.membership = membership
        if ecrypted is True:
            self.encryptedpassword = passwd
        else:
            self.password = Password(passwd)
    def __str__(self):
        return f"name:{self.name}\nemailid:{self.contact.emailid}\nphone:{self.contact.phone}"

    def getsqlandvalues(self):
        sql = "insert into donorList (name,email,userName,password,contactnumber,membership) values(%s,%s,%s,%s,%s,%s)"
        if(hasattr(self,'password')):
            value = (self.name,self.contact.emailid,self.username, self.password.getEncryptedPassword(),self.contact.phone,self.membership)
        else:
            value = (self.name,self.contact.emailid,self.username, self.encryptedpassword,self.contact.phone,self.membership)
        return [sql,value]
    def updateInfosqlandvalues(self):
        sql = "update donorList SET name=%s,email=%s,contactnumber=%s, membership =%s where username = %s"
        value = (self.name,self.contact.emailid, self.contact.phone,self.membership,self.username,)
        return [sql,value]
    def checkAndUpdatePasswordsqlandvalues(self,oldpw,newpw):
        if(hasattr(self,'encryptedpassword')):
            if Password(oldpw).getEncryptedPassword() == self.encryptedpassword:
                sql = "update donorList SET password=%s where username = %s"
                value = ( Password(newpw).getEncryptedPassword(),self.username,)
                return [sql,value]
            else:
                return False
        else:
            if oldpw == self.password.passwd:
                sql = "update donorList SET password=%s where username = %s"
                value = (newpw,self.username,)
                return [sql,value]
            else:
                if(self.debug):
                    print((oldpw,self.password,oldpw==self.password),file =sys.stderr)
                return False