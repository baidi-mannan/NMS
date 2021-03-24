from SupportModules import Contact,Password
class Donor:
    def __init__(self,name:str, username:str,contact:Contact, passwd:Password):
        self.name = name
        self.username = username
        self.contact = Contact(contact.emailid,contact.phone)
        self.passwd = Password(passwd)
    def __str__(self):
        return f"name:{self.name}\nemailid:{self.contact.emailid}\nphone:{self.contact.phone}"

    def getsqlandvalues(self):
        sql = "insert into donors values(%s,%s,%s,%s,%s,%s)"
        value = (self.username,self.contact.emailid,self.name,self.contact.phone,'DONOR', self.passwd.getEncryptedPassword(),)
        return [sql,value]
