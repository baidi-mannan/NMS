import sys
import mysql.connector
import time
class NgoBank:
    # def __init__(self,dblogin:dict):
    def __init__(self, mysql):
        self.debug =True
        self.mysql = mysql
    def deposit(self, userName,userType, amount, message=""):
        tick = time.time()
        cur = self.mysql.connection.cursor()
        cur.execute(
            """INSERT INTO funds (userName,userType,amount,status,tranmessage) VALUES (%s,%s, %s ,%s,%s)""",
            (userName, userType, amount, 1,message),
        )
        self.mysql.connection.commit()
        if self.debug:
            print(f"Deposit took{time.time() - tick}",file = sys.stderr)
        return True
    def withdraw(self, userName,userType, amount, message=""):
        tick = time.time()
        cur = self.mysql.connection.cursor()
        cur.execute(
            """INSERT INTO funds (userName,userType,amount,status,tranmessage) VALUES (%s,%s, %s ,%s,%s)""",
            (userName, userType, amount, 0,message),
        )
        self.mysql.connection.commit()
        if self.debug:
            print(f"Withdraw took{time.time() - tick}",file = sys.stderr)
        return True
    def getFunds(self):
        tick = time.time()
        cur = self.mysql.connection.cursor()
        cur.execute(
            "SELECT sum(IF(`status`=1, `amount`, 0))-sum(IF(`status`=0, `amount`, 0)) AS    `Balance` FROM   funds",
            ()
        )
        if self.debug:
            print(f"Funds calculation took{time.time() - tick}",file = sys.stderr)
        return cur.fetchall()[0][0]