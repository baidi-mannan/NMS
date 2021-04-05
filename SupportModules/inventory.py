from SupportModules import Item,ItemType
import sys
import mysql.connector
import time
class Inventory:
    # def __init__(self,dblogin:dict):
    def __init__(self, mysql):
        self.debug =False
        self.__freq = {}
        for itm in ItemType:
            self.__freq[itm.name] = 0
        # self.db = mysql.connector.connect(
        #     host = dblogin['host'],
        #     user = dblogin['user'],
        #     password = dblogin['password'],
        #     database = dblogin['database']
        # )
        # self.cursor = self.db.cursor()
        self.mysql = mysql
    
    def __del__(self):
        # self.db.close()
        pass
    def getItemFreq(self,item:Item)->int:
        self.cursor = self.mysql.connection.cursor()
        sql = "select frequency from inventory where itemid = %s"
        itemid = (item.class_, )
        self.cursor.execute(sql,itemid)
        query = self.cursor.fetchone()
        return query[0]
    
    def addItem(self, item:Item, number:int)->int:
        self.cursor = self.mysql.connection.cursor()
        if number<0: raise ValueError("Positive value expected")
        self.__freq[item.itemType.name] = self.__freq[item.itemType.name] + number
        sql = "update inventory set frequency = %s + frequency where itemid = %s"
        val = (number, item.class_,)
        self.cursor.execute(sql,val)
        self.mysql.connection.commit()
        query = self.cursor.rowcount
        # print(f"{query} Row(s) updated successfully",file=sys.stderr)
        return 1
        # showing success
    
    def removeItem(self, item:Item, number:int)->int:
        curfreq = self.getItemFreq(item)
        if(curfreq >= number):
            self.cursor = self.mysql.connection.cursor()
            sql = "update inventory set frequency = frequency - %s where itemid = %s"
            val = (number, item.class_,)
            self.cursor.execute(sql,val)
            self.mysql.connection.commit()
            query = self.cursor.rowcount
            # print(f"{query} Row(s) updated successfully",file=sys.stderr)
            return 1
        else:
            raise ValueError(f"Inventory Underflow, have {curfreq} but requested to remove {number}")
            return 0

    def trynow(self):
        self.cursor = self.mysql.connection.cursor()
        self.cursor.execute("SELECT * FROM inventory")
        myresult = self.cursor.fetchall()

        # for x in myresult:
            # print(f"{x[1]} : {x[2]}")

    def UpdatePriceList(self, priceList:dict):
        tick = time.time()
        listOfTuples = [(v,k) for k,v in priceList.items()]
        stmt = """update inventory SET price = %s where itemname = %s"""
        self.cursor = self.mysql.connection.cursor()
        self.cursor.executemany(stmt,listOfTuples)
        self.mysql.connection.commit()
        if(self.debug):
            print(f"Time taken to update Price {time.time() - tick}",file = sys.stderr)
        return self.cursor.rowcount
    def AddMultiple(self, freq:dict):
        # need perfect key as itemname
        tick = time.time()
        listOfTuples = [(v,k) for k,v in freq.items()]
        stmt = """update inventory SET frequency = %s + frequency where itemname = %s"""
        self.cursor = self.mysql.connection.cursor()
        self.cursor.executemany(stmt,listOfTuples)
        self.mysql.connection.commit()
        if(self.debug):
            print(f"Time taken to Add {time.time() - tick}",file = sys.stderr)
        return self.cursor.rowcount
    def RemoveMultiple(self, freq:dict):
        # need perfect key as itemname
        tick = time.time()
        listOfTuples = [(v,k) for k,v in freq.items()]
        stmt = """update inventory SET frequency = frequency - %s where itemname = %s"""
        self.cursor = self.mysql.connection.cursor()
        self.cursor.executemany(stmt,listOfTuples)
        self.mysql.connection.commit()
        if(self.debug):
            print(f"Time taken to Remove {time.time() - tick}",file = sys.stderr)
        return self.cursor.rowcount

    def getPriceDict(self):
        self.cursor = self.mysql.connection.cursor()
        self.cursor.execute(
            "select itemname,price from inventory",
            ()
        )
        priceList = self.cursor.fetchall()
        priceDict = dict(priceList)
        return priceDict
