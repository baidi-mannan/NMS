from SupportModules import Contact,Password
class Manager:
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
        sql = "insert into stafflist (name,email,username,password,contactnumber,role) values(%s,%s,%s,%s,%s,%s)"
        if(hasattr(self,'password')):
            value = (self.name,self.contact.emailid,self.username, self.password.getEncryptedPassword(),self.contact.phone,'manager')
        else:
            value = (self.name,self.contact.emailid,self.username, self.encryptedpassword,self.contact.phone,'manager')
        return [sql,value]
    def updateInfosqlandvalues(self):
        sql = "update stafflist SET name=%s,email=%s,contactnumber=%s where username = %s"
        value = (self.name,self.contact.emailid, self.contact.phone,self.username)
        return [sql,value]
    def checkAndUpdatePasswordsqlandvalues(self,oldpw,newpw):
        if Password(oldpw).getEncryptedPassword() == self.encryptedpassword:
            sql = "update stafflist SET password=%s where username = %s"
            value = ( Password(newpw).getEncryptedPassword(),self.username)
            return [sql,value]
        else:
            return False