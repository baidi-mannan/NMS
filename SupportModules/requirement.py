class Requirement:
    def __init__(self, mysql):
        self.mysql = mysql
    def __call__(self):
        cur = self.mysql.connection.cursor()
        cur.execute(
            "select itemname,price from inventory",
            ()
        )
        priceList = cur.fetchall()
        priceDict = dict(priceList)
        cur.execute(
            "select itemname,frequency from inventory",
            ()
        )
        freqDict = dict(cur.fetchall())
        cur.execute(
            "select sum(requirement_fees),sum(requirement_book),sum(requirement_bag), sum(requirement_shoes), sum(requirement_clothes) from studentlist;",
            ()
        )
        # (priceDict['BOOK'],priceDict['BAG'],priceDict['SHOES'],priceDict['CLOTHES'],)
        requirements = cur.fetchall()[0]
        cur.execute(
            "SELECT sum(IF(`status`=1, `amount`, 0))-sum(IF(`status`=0, `amount`, 0)) AS    `Balance` FROM   funds",
            ()
        )
        funds = cur.fetchall() [0][0]
        # myTable = [[entityname, required units, how many i have, how much i need to pay]]
        myTable = []
        totalAmount = 0
        # first row Fees
        row = ['Fees',f"Rs.{requirements[0]}","-",f"Rs.{requirements[0]}"]
        myTable.append(row)
        totalAmount += requirements[0]
        
        #second row BOOK
        reqPrice = 0
        if requirements[1] > freqDict['BOOK'] :
            reqPrice = (requirements[1]-freqDict['BOOK'])*priceDict['BOOK']
            
        row = ["Books", requirements[1], freqDict['BOOK'], f"Rs.{reqPrice}"]
        totalAmount += reqPrice
        myTable.append(row)

        #third row BAG
        reqPrice = 0
        if requirements[2] > freqDict['BAG'] :
            reqPrice = (requirements[2]-freqDict['BAG'])*priceDict['BAG']
            
        row = ["Bags", requirements[2], freqDict['BAG'], f"Rs.{reqPrice}"]
        totalAmount += reqPrice
        myTable.append(row)

        #fourth row SHOES
        reqPrice = 0
        if requirements[3] > freqDict['SHOES'] :
            reqPrice = (requirements[3]-freqDict['SHOES'])*priceDict['SHOES']
            
        row = ["Shoes", requirements[3], freqDict['SHOES'], f"Rs.{reqPrice}"]
        totalAmount += reqPrice
        myTable.append(row)

        #FIFTH row CLOTHES
        reqPrice = 0
        if requirements[4] > freqDict['CLOTHES'] :
            reqPrice = (requirements[4]-freqDict['CLOTHES'])*priceDict['CLOTHES']
            
        row = ["Clothes", requirements[4], freqDict['CLOTHES'], f"Rs.{reqPrice}"]
        totalAmount += reqPrice
        myTable.append(row)

        #FINAL row Total Amount
        row = ["Total Amount", "", "", f"Rs.{totalAmount}"]
        myTable.append(row)

        headerName = ["Particulars", "Required","Available","Amount Required"]

        return headerName, myTable


        

        