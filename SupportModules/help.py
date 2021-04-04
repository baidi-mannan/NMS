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
    def InSufficientFulfil(self,infoDict:dict,priority:str):
        ngobank = NgoBank(self.mysql)
        inventory = Inventory(self.mysql)
        priceDict = inventory.getPriceDict()
        cursor = self.mysql.connection.cursor()
        sqlDict = {
            'Male':"""select id, requirement_fees,requirement_book ,requirement_bag , requirement_shoes,  requirement_clothes    
           from studentlist 
           where requirement_bag + requirement_book + requirement_clothes + requirement_fees + requirement_shoes != 0 
           order by gender DESC, requirement_bag*%s + requirement_book*%s + requirement_clothes*%s + requirement_fees + requirement_shoes*%s ;""",

           'Female':"""select id, requirement_fees,requirement_book ,requirement_bag , requirement_shoes,  requirement_clothes    
           from studentlist 
           where requirement_bag + requirement_book + requirement_clothes + requirement_fees + requirement_shoes != 0 
           order by gender , requirement_bag*%s + requirement_book*%s + requirement_clothes*%s + requirement_fees + requirement_shoes*%s ;""",

           'StudentPerformance':"""select id, requirement_fees,requirement_book ,requirement_bag , requirement_shoes,  requirement_clothes    
           from studentlist 
           where requirement_bag + requirement_book + requirement_clothes + requirement_fees + requirement_shoes != 0 
           order by lastmarks DESC, requirement_bag*%s + requirement_book*%s + requirement_clothes*%s + requirement_fees + requirement_shoes*%s ;""",

           'FamilyIncome':"""select id, requirement_fees,requirement_book ,requirement_bag , requirement_shoes,  requirement_clothes    
           from studentlist 
           where requirement_bag + requirement_book + requirement_clothes + requirement_fees + requirement_shoes != 0 
           order by familyincome, requirement_bag*%s + requirement_book*%s + requirement_clothes*%s + requirement_fees + requirement_shoes*%s ;""",
        }
        cursor.execute(
           sqlDict[priority],
            (priceDict['BAG'], priceDict['BOOK'], priceDict['CLOTHES'],priceDict['SHOES'],)
        )
        query = cursor.fetchall()
        cursor.execute(
            "SELECT coalesce(MAX(DONATIONID),0)+1 FROM completedhelp",
            ()
            )
        donationID = cursor.fetchall()[0][0]

        ngodata = {
            'AVA':infoDict['AVA'],
            'BOOK':infoDict['BOOK']['FREQ'],
            'BAG' :infoDict['BAG']['FREQ'],
            'SHOES':infoDict['SHOES']['FREQ'],
            'CLOTHES':infoDict['CLOTHES']['FREQ'],
        }
        # CHOOSE VALUES CORRECTLY
        values = []
        valuesID = []
        feepayment = 0
        bookbought = 0
        bagbought = 0
        shoesbought = 0
        clothesbought = 0
        ngodonated = {
            'BOOK':0,
            'BAG' :0,
            'SHOES':0,
            'CLOTHES':0,
        }
        for row in query:
            STUDENTFEESREQ = row[1]
            STUDENTBOOKREQ = row[2]  
            STUDENTBAGREQ = row[3]
            STUDENTSHOESREQ = row[4]  
            STUDENTCLOTHESREQ = row[5]
            # can i give him
            canigive = True
            STUDENTTOTAL = 0
            STUDENTTOTAL += STUDENTFEESREQ
            if ngodata['BOOK']>= STUDENTBOOKREQ:
                pass
            else:
                STUDENTTOTAL += (STUDENTBOOKREQ-ngodata['BOOK']) * priceDict['BOOK']
            
            if ngodata['BAG']>= STUDENTBAGREQ:
                pass
            else:
                STUDENTTOTAL += (STUDENTBAGREQ-ngodata['BAG']) * priceDict['BAG']
            
            if ngodata['SHOES']>= STUDENTSHOESREQ:
                pass
            else:
                STUDENTTOTAL += (STUDENTSHOESREQ-ngodata['SHOES']) * priceDict['SHOES']
            
            if ngodata['CLOTHES']>= STUDENTCLOTHESREQ:
                pass
            else:
                STUDENTTOTAL += (STUDENTCLOTHESREQ-ngodata['CLOTHES']) * priceDict['CLOTHES']
            if(STUDENTTOTAL > ngodata['AVA']):
                canigive = False
            
            
            if canigive == False:
                continue
            
            # give
            ngodata['AVA']-=STUDENTTOTAL
            values.append((donationID,row[0],))
            valuesID.append((row[0],))
            feepayment += STUDENTFEESREQ
            
            if ngodata['BOOK']>= STUDENTBOOKREQ:
                ngodata['BOOK'] -= STUDENTBOOKREQ
                ngodonated['BOOK'] += STUDENTBOOKREQ
            else:
                bookbought += (STUDENTBOOKREQ-ngodata['BOOK']) * priceDict['BOOK']
                ngodonated['BOOK'] += ngodata['BOOK']
                ngodata['BOOK'] = 0
            
            if ngodata['BAG']>= STUDENTBAGREQ:
                ngodata['BAG'] -= STUDENTBAGREQ
                ngodonated['BAG'] += STUDENTBAGREQ
            else:
                bagbought += (STUDENTBAGREQ-ngodata['BAG']) * priceDict['BAG']
                ngodonated['BAG'] += ngodata['BAG']
                ngodata['BAG'] = 0
            
            if ngodata['SHOES']>= STUDENTSHOESREQ:
                ngodata['SHOES'] -= STUDENTSHOESREQ
                ngodonated['SHOES'] += STUDENTSHOESREQ
            else:
                shoesbought += (STUDENTSHOESREQ-ngodata['SHOES']) * priceDict['SHOES']
                ngodonated['SHOES'] += ngodata['SHOES']
                ngodata['SHOES'] = 0
            
            if ngodata['CLOTHES']>= STUDENTCLOTHESREQ:
                ngodata['CLOTHES'] -= STUDENTCLOTHESREQ
                ngodonated['CLOTHES'] += STUDENTCLOTHESREQ
            else:
                clothesbought += (STUDENTCLOTHESREQ-ngodata['CLOTHES']) * priceDict['CLOTHES']
                ngodonated['CLOTHES'] += ngodata['CLOTHES']
                ngodata['CLOTHES'] = 0
        if(len(values) == 0):
            return -1
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


        # do here
        inventory.RemoveMultiple(ngodonated)
        if(feepayment>0):
            ngobank.withdraw(infoDict['userName'],'manager',feepayment,f"fees Rs{feepayment} donated during donation id {donationID}")
        if(bookbought>0):
            ngobank.withdraw(infoDict['userName'],'manager',bookbought,f"Item Book bought during donation id {donationID}")
        if(bagbought>0):
            ngobank.withdraw(infoDict['userName'],'manager',bagbought,f"Item Bag bought during donation id {donationID}")
        if(shoesbought>0):
            ngobank.withdraw(infoDict['userName'],'manager',shoesbought,f"Item Shoes bought during donation id {donationID}")
        if(clothesbought>0):
            ngobank.withdraw(infoDict['userName'],'manager',clothesbought,f"Item Clothes bought during donation id {donationID}")

        return donationID
