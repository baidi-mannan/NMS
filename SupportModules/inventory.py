from SupportModules import Item,ItemType
import mysql.connector
class Inventory:
    def __init__(self,dblogin:dict):
        self.__freq = {}
        for itm in ItemType:
            self.__freq[itm.name] = 0
        self.db = mysql.connector.connect(
            host = dblogin['host'],
            user = dblogin['user'],
            password = dblogin['password'],
            database = dblogin['database']
        )
        self.cursor = self.db.cursor()
    
    def __del__(self):
        self.db.close()

    def getItemFreq(self,item:Item)->int:
        sql = "select frequency from inventory where itemid = %s"
        itemid = (item.class_, )
        self.cursor.execute(sql,itemid)
        query = self.cursor.fetchone()
        return query[0]
    
    def addItem(self, item:Item, number:int)->int:
        if number<0: raise ValueError("Positive value expected")
        self.__freq[item.itemType.name] = self.__freq[item.itemType.name] + number
        sql = "update inventory set frequency = %s + frequency where itemid = %s"
        val = (number, item.class_,)
        self.cursor.execute(sql,val)
        self.db.commit()
        query = self.cursor.rowcount
        print(f"{query} Row(s) updated successfully")
        return 1
        # showing success
    
    def removeItem(self, item:Item, number:int)->int:
        curfreq = self.getItemFreq(item)
        if(curfreq >= number):
            sql = "update inventory set frequency = frequency - %s where itemid = %s"
            val = (number, item.class_,)
            self.cursor.execute(sql,val)
            self.db.commit()
            query = self.cursor.rowcount
            print(f"{query} Row(s) updated successfully")
            return 1
        else:
            raise ValueError(f"Inventory Underflow, have {curfreq} but requested to remove {number}")
            return 0

    def trynow(self):
        self.cursor.execute("SELECT * FROM inventory")
        myresult = self.cursor.fetchall()

        for x in myresult:
            print(f"{x[1]} : {x[2]}")

