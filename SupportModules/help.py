from SupportModules import Item,ItemType,Inventory,NgoBank
import sys
import mysql.connector
import time

class Help():
    def __init__(self,mysql):
        self.mysql = mysql
    def SufficientFulfil(self,infoDict:dict):
        ngobank = NgoBank(self.mysql)
        inventory = Inventory(self.mysql)
        priceDict = inventory.getPriceDict()
        cursor = self.mysql.connection.cursor()
        cursor.execute(
           """select id, requirement_fees,requirement_book ,requirement_bag , requirement_shoes,  requirement_clothes    
           from studentlist 
           where requirement_bag + requirement_book + requirement_clothes + requirement_fees + requirement_shoes != 0
           order by requirement_bag*%s + requirement_book*%s + requirement_clothes*%s + requirement_fees + requirement_shoes*%s ;""",
            (priceDict['BAG'], priceDict['BOOK'], priceDict['CLOTHES'],priceDict['SHOES'],)
        )
        query = cursor.fetchall()
        cursor.execute(
            "SELECT coalesce(MAX(DONATIONID),0)+1 FROM completedhelp",
            ()
            )
        donationID = cursor.fetchall()[0][0]

        values = [ (donationID,row[0],) for row in query]
        valuesID = [ (row[0],) for row in query]
        cursor.executemany(
            """INSERT INTO completedhelp 
            (donationId, id, name, class, requirement_fees, requirement_book, requirement_bag, requirement_shoes, requirement_clothes, email, rollnumber, contactnumber, lastmarks, gender, familyincome)
             select %s ,id, name, class, requirement_fees, requirement_book, requirement_bag, requirement_shoes, requirement_clothes, email, rollnumber, contactnumber, lastmarks, gender, familyincome
            from studentlist where id = %s""",
            values
        )
        self.mysql.connection.commit()
        cursor.executemany(
            """update studentlist set 
                requirement_fees = 0,
                requirement_book = 0,
                requirement_bag = 0,
                requirement_shoes = 0,
                requirement_clothes = 0
                where id = %s;""",
                valuesID

        )
        self.mysql.connection.commit()
        giveFreq = {}
        for k,v in priceDict.items():
            if(infoDict[k]['FREQ_REQUIRED'] <= infoDict[k]['FREQ']):
                giveFreq[k] = infoDict[k]['FREQ_REQUIRED']
            else:
                giveFreq[k] = infoDict[k]['FREQ']
                ngobank.withdraw(infoDict['userName'],'manager',infoDict[k]['REQ'],f"Item {k} bought during donation id {donationID}")
        inventory.RemoveMultiple(giveFreq)
        ngobank.withdraw(infoDict['userName'],'manager',infoDict['FEES']['REQ'],f"fees Rs{infoDict['FEES']['REQ']} donated during donation id {donationID}")
        return donationID
