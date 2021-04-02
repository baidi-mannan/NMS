from flask import Flask, render_template, request, session, flash, redirect, url_for
from flask_mysqldb import MySQL
from SupportModules import *
from functools import wraps
import json
import sys
import time 
app = Flask(__name__)
# app.config["MYSQL_USER"] = "sql6401232"
# app.config["MYSQL_PASSWORD"] = "un2P67tMei"
# app.config["MYSQL_HOST"] = "sql6.freemysqlhosting.net"
# app.config["MYSQL_DB"] = "sql6401232"
app.config["MYSQL_USER"] = "admin"
app.config["MYSQL_PASSWORD"] = "nmszka323"
app.config["MYSQL_HOST"] = "nmsdb.czj2xnercmna.us-east-2.rds.amazonaws.com"
app.config["MYSQL_DB"] = "coredb"
# app.config["MYSQL_CURSORCLASS"]

# for session
app.config["SECRET_KEY"] = "thisshouldbeasecret"

mysql = MySQL(app)
inventory = Inventory(mysql)
ngobank = NgoBank(mysql)


mydbDetails = {
    "host": app.config["MYSQL_HOST"],
    "user": app.config["MYSQL_USER"],
    "password": app.config["MYSQL_PASSWORD"],
    "database": app.config["MYSQL_DB"],
}
mysqlc = mysqlcon(mydbDetails)


def staff_login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if ("User" in session) and (session["User"]["type"] == "staff"):
            return f(*args, **kwargs)
        else:
            print("You need to login first", file=sys.stderr)
            return redirect("/staff-login")

    return wrap


def donor_login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if ("User" in session) and (session["User"]["type"] == "donor"):
            return f(*args, **kwargs)
        else:
            print("You need to login first", file=sys.stderr)
            return redirect("/donor-login")

    return wrap


def manager_login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if ("User" in session) and (session["User"]["type"] == "manager"):
            return f(*args, **kwargs)
        else:
            print("You need to login first", file=sys.stderr)
            return redirect("/manager-login")

    return wrap


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/donor-login", methods=["GET", "POST"])
def donorLogin():
    global mysql
    cur = mysql.connection.cursor()

    if request.method == "POST":
        donorDetails = request.form
        global mysqlc
        if request.form["button"] == "register":
            donorUserNames = mysqlc.userNameList("SELECT userName FROM donorList")
            result = checkNewData(donorDetails, donorUserNames)
            if not result["isValid"]:
                return result["message"]

            cur.execute(
                """INSERT INTO donorList(name,email,userName,password,contactNumber) VALUES(%s,%s,%s,%s,%s)""",
                (
                    donorDetails["name"],
                    donorDetails["email"],
                    donorDetails["userName"],
                    donorDetails["password"],
                    donorDetails["contactNumber"],
                ),
            )
            # cur.execute("""truncate donorList""")

            mysql.connection.commit()
            return render_template("donorRegister.html", userName=donorDetails["name"])

        if request.form["button"] == "login":
            userName = donorDetails["userName"]
            password = donorDetails["password"]
            session.pop("User", None)

            query = mysqlc.select(
                [
                    "select id,userName,name,password, membership,email,contactNumber from donorList where username = %s",
                    (userName,),
                ]
            )

            if len(query) == 0:
                return "<h5> NO SUCH USERNAME EXISTS<br> PLEASE TRY AGAIN</h5>"
            else:
                # if(query[0][3] == Password(password).getEncryptedPassword()):
                if query[0][3] == password:

                    session["User"] = {
                        "name": query[0][2],
                        "userName": userName,
                        "id": query[0][0],
                        "type": "donor",
                        "membership": query[0][4],
                        "email": query[0][5],
                        "contactNumber": query[0][6],
                        "pw": query[0][3],
                    }
                    return redirect(url_for("donorprofilepage"))
                else:
                    return "<h5> INCORRECT PASSWORD<br> PLEASE TRY AGAIN</h5>"

    return render_template("donor/donorLogin.html", userType="donor")


@app.route("/manager-login")
def managerLogin():
    return render_template("manager/managerLogin.html", userType="manager")


@app.route("/staff-login")
def staffLogin():
    return render_template("staff/staffLogin.html", userType="staff")


@app.route("/staffcheckpassword", methods=["POST"])
def staffcheckpassword():
    staffDetails = request.form
    userName = staffDetails["userName"]
    password = staffDetails["password"]
    session.pop("User", None)
    global mysqlc
    query = mysqlc.select(
        [
            "select id,username,name,password from stafflist where username = %s and role = %s",
            (
                userName,
                "staff",
            ),
        ]
    )
    if len(query) == 0:
        return json.dumps({"statusCode": -1, "message": "User doesn't exist"})
    else:
        if query[0][3] == Password(password).getEncryptedPassword():
            session["User"] = {
                "name": query[0][2],
                "userName": userName,
                "id": query[0][0],
                "type": "staff",
            }

            return json.dumps(
                {"statusCode": 1, "message": f"Successful Login {query[0][2]}"}
            )
        else:
            return json.dumps({"statusCode": -2, "message": f"Wrong password"})
    return json.dumps({"statusCode": 1, "message": "Success"})


@app.route("/staffprofilepage")
@staff_login_required
def staffprofilepage():
    return f"Hello {session['User']['name']}"


@app.route("/stafflogout")
@staff_login_required
def stafflogout():
    session.pop("User", None)
    return redirect("/staff-login")


@app.route("/managercheckpassword", methods=["POST"])
def managercheckpassword():
    managerDetails = request.form
    userName = managerDetails["userName"]
    password = managerDetails["password"]
    session.pop("User", None)
    global mysqlc 
    query = mysqlc.select(
        [
            "select id,username,name,password from stafflist where username = %s and role = %s",
            (
                userName,
                "manager",
            ),
        ]
    )
    if len(query) == 0:
        return json.dumps({"statusCode": -1, "message": "User doesn't exist"})
    else:
        if query[0][3] == Password(password).getEncryptedPassword():
            session["User"] = {
                "name": query[0][2],
                "userName": userName,
                "id": query[0][0],
                "type": "manager",
            }

            return redirect("/managerprofilepage")
        else:
            return json.dumps({"statusCode": -2, "message": f"Wrong password"})
    return json.dumps({"statusCode": 1, "message": "Success"})


@app.route("/managerprofilepage")
@manager_login_required
def managerprofilepage():
    return render_template("manager/managerProfilePage.html",Userdetails=session["User"])


@app.route("/manager-logout")
@manager_login_required
def managerlogout():
    session.pop("User", None)
    return redirect("/manager-login")


@app.route("/donorprofilepage")
@donor_login_required
def donorprofilepage():
    print(f"session['User'] = {session['User']}", file=sys.stderr)
    return render_template("donor/donorProfilePage.html", Userdetails=session["User"])


@app.route("/donor-logout")
@donor_login_required
def donorlogout():
    session.pop("User", None)
    return redirect("/donor-login")


@app.route("/donate-money", methods=["GET", "POST"])
@donor_login_required
def donateMoney():

    if request.method == "POST":
        amount = request.form["amount"]
        return redirect(url_for("makePayment", amount=amount))

    return render_template("donor/donateMoney.html")


@app.route("/make-payment", methods=["GET", "POST"])
@donor_login_required
def makePayment():
    amount = request.args["amount"]
    if request.method == "POST":
        cur = mysql.connection.cursor()
        cur.execute(
            """INSERT INTO funds (userName,userType,amount,status) VALUES (%s,%s, %s ,%s)""",
            (session["User"]["userName"], session["User"]["type"], amount, 1),
        )
        #cur.execute("commit")
        mysql.connection.commit()
        return "<h5>THANK YOU FOR CONTRIBUTING</h5>"

    return render_template("donor/makePayment.html")


@app.route("/donate-item", methods=["GET", "POST"])
@donor_login_required
def donateItem():

    if request.method == "POST":
        global inventory
        donation = request.form
        print(donation,file=sys.stderr)
        donated = False
        donationfreq = int(donation['book'])
        if(donationfreq>0):
            donated = True
            inventory.addItem(Item(ItemType['BOOK']),donationfreq)
        donationfreq = int(donation['bag'])
        if(donationfreq>0):
            donated = True
            inventory.addItem(Item(ItemType['BAG']),donationfreq)
        donationfreq = int(donation['shoes'])
        if(donationfreq>0):
            donated = True
            inventory.addItem(Item(ItemType['SHOES']),donationfreq)
        donationfreq = int(donation['clothes'])
        if(donationfreq>0):
            donated = True
            inventory.addItem(Item(ItemType['CLOTHES']),donationfreq)
        if(donated):
            return "<h5>Thank you your donation</h5>"
        else:
            return "<h5>No items donated! Please try again.</h5>"
    if request.method == "GET":
        return render_template("donor/donateItem.html")



@app.route("/update-donor-profile", methods=["GET", "POST"])
@donor_login_required
def updateDonorProfile():
    global mysql
    cur = mysql.connection.cursor()

    if request.method == "POST":

        userID = session["User"]["id"]
        if request.form["button"] == "save":
            donorDetails = request.form
            member = 1
            if donorDetails["membership"] == "full":
                member = 0

            cur.execute(
                """UPDATE donorList SET name=%s,email=%s,contactNumber=%s,membership=%s WHERE id=%s""",
                (
                    donorDetails["name"],
                    donorDetails["email"],
                    donorDetails["contactNumber"],
                    member,
                    userID,
                ),
            )

            mysql.connection.commit()
            session["User"]["name"] = donorDetails["name"]
            session["User"]["email"] = donorDetails["email"]
            session["User"]["contactNumber"] = donorDetails["contactNumber"]
            session["User"]["membership"] = member
            session.modified = True
            return "<h5> USER DEATILS CHANGED</h5>"
        if request.form["button"] == "changePassword":
            inputs = request.form
            if session["User"]["pw"] == inputs["oldPassword"]:
                output = checkPassword(inputs)
                if output["isValid"]:
                    cur.execute(
                        """UPDATE donorList SET password=%s WHERE id=%s""",
                        (
                            inputs["newPassword"],
                            userID,
                        ),
                    )
                    print(inputs["newPassword"])
                    mysql.connection.commit()
                    session.pop("User", None)
                    return redirect(url_for("donorLogin"))

                else:
                    return output["message"]
            else:
                return "<h5>YOU HAVE ENTERED WRONG PASSWORD<br>PLEASE TRY AGAIN</h5>"

    if request.method == "GET":
        # tick=time.time()
        # global mysqlc 
        # # mysqlc = mysqlcon(mydbDetails)
        # query = mysqlc.select(
        #         [
        #             "select id,userName,name,password, membership,email,contactNumber from donorList where username = %s",
        #             (session["User"]["userName"],),
        #         ]
        #     )
        # print(f"Query Took {time.time()-tick}",file=sys.stderr)
        # user={}
        # user['name']=query[0][2]
        # user['userName']=query[0][1]
        # user['email']=query[0][5]
        # user['contactNumber']=query[0][6]
        # user["membership"]=query[0][4]
        return render_template("donor/updateDonorProfile.html", user=session['User'])
    
# managers code starts here
@app.route("/manager-show-student-list")
@manager_login_required
def managershowstudentlist():
    headerName = ('Name','Class','Roll Number','Last Marks','Family Income','Contact Number','Help Required(Rs.)')
    global mysqlc
    priceList = mysqlc.select(
        [
            "select itemname,price from inventory",
            ()
        ]
    )
    
    priceDict = dict(priceList)
    print(priceDict,file = sys.stderr)
    query = mysqlc.select(
        [
            "select Name,Class,rollnumber,lastmarks,familyincome,contactnumber,(requirement_fees+%s*requirement_book + %s*requirement_bag + %s*requirement_shoes + %s*requirement_clothes)  from studentlist order by class",
            (priceDict['BOOK'],priceDict['BAG'],priceDict['SHOES'] , priceDict['CLOTHES'],)
        ]
        )
    
    
    print(query,file = sys.stderr)
    
    return render_template("manager/showStudent.html",headerName = headerName, query = query)

@app.route("/manager-show-staff-list")
@manager_login_required
def managershowstafflist():
    headerName = ('ID','Name','Email','Contact Number')
    global mysqlc
    query = mysqlc.select(
        [
            "select id,name,email,contactnumber from stafflist where role = 'staff'",
            ()
        ]
        )
    
    print(query,file = sys.stderr)
    
    return render_template("manager/showStaff.html",headerName = headerName, query = query)


@app.route("/manager-show-donor-list")
@manager_login_required
def managershowdonorlist():
    headerName = ('ID','Name','Email','Contact Number')
    global mysqlc
    query = mysqlc.select(
        [
            "select id,name,email,contactnumber from donorList",
            ()
        ]
        )
    
    print(query,file = sys.stderr)
    
    return render_template("manager/showDonor.html",headerName = headerName, query = query)




@app.route("/manager-show-funds")
@manager_login_required
def managershowfunds():
    global mysqlc
    query = mysqlc.select(
        [
            "SELECT sum(IF(`status`=1, `amount`, 0))-sum(IF(`status`=0, `amount`, 0)) AS    `Balance` FROM   funds",
            ()
        ]
        )
    
    print(query,file = sys.stderr)
    
    return render_template("manager/showFunds.html",BalanceFund = query[0][0])


@app.route("/manager-show-inventory-list")
@manager_login_required
def managershowinventorylist():
    headerName = ('Item Name','Available Units','Unit Price')
    global mysqlc
    query = mysqlc.select(
        [
            "select itemname,frequency,price from inventory order by itemid",
            ()
        ]
        )
    
    print(query,file = sys.stderr)
    
    return render_template("manager/showInventory.html",headerName = headerName, query = query)


@app.route("/manager-show-expenditures")
@manager_login_required
def managershowexpenditures():
    headerName = ('User Name','Amount (Rs.)','Remarks')
    global mysqlc
    query = mysqlc.select(
        [
            "select userName,amount,tranmessage from funds where status = 0 order by id",
            ()
        ]
        )
    
    print(query,file = sys.stderr)
    
    return render_template("manager/showExpenditures.html",headerName = headerName, query = query)

@app.route("/manager-show-requirement")
@manager_login_required
def managershowrequirement():
    req = Requirement(mysql)
    headerName,query = req()  
    return render_template("manager/showRequirement.html",headerName = headerName, query = query)

@app.route("/manager-update-price-list", methods=["GET", "POST"])
@manager_login_required
def managerupdatepricelist():
    # do some query 
    newPriceForm = request.form
    if request.method == "POST":
        newPrice= {
            'BOOK':newPriceForm['BookPrice'],
            'BAG':newPriceForm['BagPrice'],
            'SHOES':newPriceForm['ShoesPrice'],
            'CLOTHES':newPriceForm['ClothesPrice'],
        }
        global inventory
        inventory.UpdatePriceList(newPrice)
        return render_template("manager/managerUpdatePrice.html",oldprice = newPrice,saved=True)
    if request.method == "GET":
        global mysqlc
        priceList = mysqlc.select(
            [
                "select itemname,price from inventory",
                ()
            ]
        )
        priceDict = dict(priceList)
        return render_template("manager/managerUpdatePrice.html",oldprice = priceDict,saved=False)


@app.route("/manager-buy-item",methods=["GET", "POST"])
@manager_login_required
def managerbuyitem():
    global mysqlc
    priceList = mysqlc.select(
        [
            "select itemname,price from inventory",
            ()
        ]
    )
    priceDict = dict(priceList)
    global inventory
    global ngobank
    funds = ngobank.getFunds()
    if request.method == "POST":
        orderForm = request.form
        orderRequiredAmount = 0
        for k,v in priceDict.items():
            orderRequiredAmount+=(v*(int(orderForm[k])))
        if(funds<orderRequiredAmount):
            return redirect(url_for("managerbuyresultpage",bamount = orderRequiredAmount, status= -1, funds = funds))
            # return render_template("manager/managerBuyItem.html",priceDict = priceDict,status = -1,bamount = orderRequiredAmount, funds= funds)
        if(orderRequiredAmount <=0 ):
            return redirect(url_for("managerbuyresultpage",bamount = orderRequiredAmount, status= -2, funds = funds))
            # return render_template("manager/managerBuyItem.html",priceDict = priceDict,status = -2,bamount = orderRequiredAmount, funds= funds)
        print(orderForm, file= sys.stderr)
        inventory.AddMultiple(orderForm)
        ngobank.withdraw(session['User']['userName'],'manager',orderRequiredAmount,'Bought Items for NGO')
        return redirect(url_for("managerbuyresultpage",bamount = orderRequiredAmount, status= 1, funds = funds - orderRequiredAmount))
        # return render_template("manager/managerBuyItem.html",priceDict = priceDict,status = 1,bamount = orderRequiredAmount, funds = funds - orderRequiredAmount)
    if request.method == "GET":
        return render_template("manager/managerBuyItem.html",priceDict = priceDict,status = 0, funds = funds)

@app.route("/managerbuyresultpage")
@manager_login_required
def managerbuyresultpage():
    status = request.args.get('status')
    bamount = request.args.get('bamount')
    funds = request.args.get('funds')
    return render_template("manager/managerBuyResultPage.html",**request.args)


@app.route("/manager-check-records")
@manager_login_required
def managercheckrecords():
    return render_template("manager/managerCheckRecords.html")


if __name__ == "__main__":
    app.run(debug=True)