class Contact:
    def __init__(self,emailid:str,phone:str):
        self.emailid = emailid
        self.phone = phone
    
    def setAddress(self,emailid:str):
        self.emailid = emailid
    
    def getAddress(self):
        return self.emailid.copy()

    def setPhone(self,phone:str):
        self.phone = phone
    
    def getPhone(self):
        return self.phone.copy()

