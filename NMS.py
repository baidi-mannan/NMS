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
# app.config["MYSQL_USER"] = "admin"
# app.config["MYSQL_PASSWORD"] = "nmszka323"
# app.config["MYSQL_HOST"] = "nmsdb.czj2xnercmna.us-east-2.rds.amazonaws.com"
# app.config["MYSQL_DB"] = "coredb"
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
            # print("You need to login first", file=sys.stderr)
            return redirect("/staff-login")

    return wrap


def donor_login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if ("User" in session) and (session["User"]["type"] == "donor"):
            return f(*args, **kwargs)
        else:
            # print("You need to login first", file=sys.stderr)
            return redirect("/donor-login")

    return wrap


def manager_login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if ("User" in session) and (session["User"]["type"] == "manager"):
            return f(*args, **kwargs)
        else:
            # print("You need to login first", file=sys.stderr)
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
            return render_template(
                "donor/donorRegister.html", userName=donorDetails["name"]
            )

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
                # return "<h5> NO SUCH USERNAME EXISTS<br> PLEASE TRY AGAIN</h5>"
                return render_template("GeneralMessage.html",message="NO SUCH USERNAME EXISTS PLEASE TRY AGAIN")

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
                    # return "<h5> INCORRECT PASSWORD<br> PLEASE TRY AGAIN</h5>"
                    return render_template("GeneralMessage.html",message="INCORRECT PASSWORD PLEASE TRY AGAIN")
    return render_template("donor/donorLogin.html", userType="donor")


@app.route("/manager-login")
def managerLogin():
    return render_template("manager/managerLogin.html", userType="manager")


@app.route("/staff-login", methods=["GET", "POST"])
def staffLogin():
    staffDetails = request.form
    if request.method == "POST":
        userName = staffDetails["userName"]
        password = staffDetails["password"]
        session.pop("User", None)

        query = mysqlc.select(
            [
                "select id,username,name,password,email,contactnumber from stafflist where username = %s",
                (userName,),
            ]
        )
        # print(query)
        if len(query) == 0:
            # return "<h5> NO SUCH USERNAME EXISTS<br> PLEASE TRY AGAIN</h5>"
            return render_template("GeneralMessage.html",message="NO SUCH USERNAME EXISTS! PLEASE TRY AGAIN")
        else:
            # if(query[0][3] == Password(password).getEncryptedPassword()):
            if query[0][3] == password:

                session["User"] = {
                    "name": query[0][2],
                    "userName": userName,
                    "id": query[0][0],
                    "type": "staff",
                    "email": query[0][4],
                    "contactNumber": query[0][5],
                    "pw": query[0][3],
                }
                return redirect(url_for("staffprofilepage"))

            else:
                # return "<h5> INCORRECT PASSWORD<br> PLEASE TRY AGAIN</h5>"
                return render_template("GeneralMessage.html",message="INCORRECT PASSWORD! PLEASE TRY AGAIN")
    return render_template("staff/staffLogin.html", userType="staff")


@app.route("/staffprofilepage")
@staff_login_required
def staffprofilepage():
    return render_template("staff/staffProfilePage.html", userDetails=session["User"])


@app.route("/update-staff-profile", methods=["GET", "POST"])
def updateStaffProfile():
    global mysql
    cur = mysql.connection.cursor()

    if request.method == "POST":

        userID = session["User"]["id"]
        if request.form["button"] == "save":
            staffDetails = request.form

            cur.execute(
                """UPDATE stafflist SET name=%s,email=%s,contactnumber=%s WHERE id=%s""",
                (
                    staffDetails["name"],
                    staffDetails["email"],
                    staffDetails["contactNumber"],
                    userID,
                ),
            )

            mysql.connection.commit()
            session["User"]["name"] = staffDetails["name"]
            session["User"]["email"] = staffDetails["email"]
            session["User"]["contactNumber"] = staffDetails["contactNumber"]

            session.modified = True
            # return "<h5> USER DEATILS CHANGED</h5>"
            return render_template("GeneralMessage",message = "USER DEATILS CHANGED")
        if request.form["button"] == "changePassword":
            inputs = request.form
            if session["User"]["pw"] == inputs["oldPassword"]:
                output = checkPassword(inputs)
                if output["isValid"]:
                    cur.execute(
                        """UPDATE stafflist SET password=%s WHERE id=%s""",
                        (
                            inputs["newPassword"],
                            userID,
                        ),
                    )
                    # print(inputs["newPassword"])
                    mysql.connection.commit()
                    session.pop("User", None)
                    return redirect(url_for("staffLogin"))

                else:
                    return output["message"]
            else:
                return "<h5>YOU HAVE ENTERED WRONG PASSWORD<br>PLEASE TRY AGAIN</h5>"

    return render_template("staff/updateStaffProfile.html", user=session["User"])


@app.route("/register-student", methods=["GET", "POST"])
def registerStudent():
    global mysqlc
    if request.method == "POST":
        sinfo = request.form
        # return request.form
        query = mysqlc.select(
            [
                """select 
                COALESCE(sum(email = %s),0) ,COALESCE(sum(contactnumber = %s),0)
                from studentlist 
                where (email = %s or contactnumber = %s)  ;
                """,
                (
                    sinfo["email"],
                    sinfo["contactNumber"],
                    sinfo["email"],
                    sinfo["contactNumber"],
                ),
            ]
        )
        if query[0][0] + query[0][1] > 0:
            errorMessage = ""
            if query[0][0] > 0:
                errorMessage = errorMessage + "email Already present in database,"
            if query[0][1] > 0:
                errorMessage = errorMessage + "Phone number present in database,"
            errorMessage = errorMessage + " Please give new details"
            # return errorMessage
            return render_template("GeneralMessage.html", message= errorMessage)
        mysqlc.registerStudent(request.form, session["User"]["userName"])

        # return "STUDENT REGISTERED"
        return render_template("GeneralMessage.html", message= "STUDENT REGISTERED")
    return render_template("staff/registerStudent.html", user=session["User"])


@app.route("/donate-staff", methods=["GET", "POST"])
def donateStaff():
    if request.method == "POST":
        amount = request.form["amount"]
        donorName = request.form["donorName"]
        return redirect(
            url_for("makePaymentbyStaff", amount=amount, donorName=donorName)
        )

    return render_template(
        "staff/donateStaff.html",
    )


@app.route("/make-payment-staff", methods=["GET", "POST"])
@staff_login_required
def makePaymentbyStaff():
    amount = request.args["amount"]
    donorName = request.args["donorName"]
    if request.method == "POST":
        cur = mysql.connection.cursor()
        cur.execute(
            """INSERT INTO funds (userName,userType,amount,status,tranmessage) VALUES (%s,%s, %s ,%s,%s)""",
            (
                session["User"]["userName"],
                session["User"]["type"],
                amount,
                1,
                f"{donorName} donated Rs. {amount}",
            ),
        )
        # cur.execute("commit")
        mysql.connection.commit()
        return "<h5>THANK YOU FOR CONTRIBUTING</h5>"
    return render_template("donor/makePayment.html")

@app.route("/staff-update-student", methods=["GET", "POST"])
@staff_login_required
def staffupdatestudent():
    global mysqlc
    query = mysqlc.select(["select id,name from studentlist", ()])
    inputs = [[row[0], row[1]] for row in query]

    if request.method == "POST":
        if request.form["formName"] == "chooseStudent":
            query = mysqlc.select(
                [
                    """select 
                    id,
                    name,
                    class,
                    requirement_fees,
                    requirement_book,
                    requirement_bag,
                    requirement_shoes,
                    requirement_clothes,
                    email,
                    rollnumber,
                    contactnumber,
                    lastmarks,
                    gender,
                    familyincome 
                    from studentlist where id = %s""",
                    (request.form["studentID"],),
                ]
            )

            user = {
                "id": query[0][0],
                "name": query[0][1],
                "class": query[0][2],
                "requirement_fees": query[0][3],
                "requirement_book": query[0][4],
                "requirement_bag": query[0][5],
                "requirement_shoes": query[0][6],
                "requirement_clothes": query[0][7],
                "email": query[0][8],
                "rollnumber": query[0][9],
                "contactnumber": query[0][10],
                "lastmarks": query[0][11],
                "gender": query[0][12],
                "familyincome": query[0][13],
            }
            return render_template(
                "staff/staffUpdateStudent.html", inputs=inputs, user=user
            )
        if request.form["formName"] == "updateProfile":
            userInfo = request.form
            sinfo = request.form
            query = mysqlc.select(
                [
                    """select 
                    COALESCE(sum(email = %s),0) ,COALESCE(sum(contactnumber = %s),0)
                    from studentlist 
                    where (email = %s or contactnumber = %s) and id != %s ;
                    """,
                    (
                        sinfo["email"],
                        sinfo["contactnumber"],
                        sinfo["email"],
                        sinfo["contactnumber"],
                        int(sinfo["id"]),
                    ),
                ]
            )
            if query[0][0] + query[0][1] > 0:
                errorMessage = ""
                if query[0][0] > 0:
                    errorMessage = errorMessage + "email Already present in database,"
                if query[0][1] > 0:
                    errorMessage = errorMessage + "Phone number present in database,"
                errorMessage = errorMessage + " Please give new details"
                # return errorMessage
                return render_template("GeneralMessage.html", message = errorMessage)
            mysqlc.updateStudent(request.form)
            # return "Profile Updated Successfully"
            return render_template("GeneralMessage.html", message = "Profile Updated Successfully")
    return render_template(
        "staff/staffUpdateStudent.html", inputs=inputs, user=None
    )


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
        # return json.dumps({"statusCode": -1, "message": "User doesn't exist"})
        return render_template("GeneralMessage.html", message = "User doesn't exist")
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
            # return json.dumps({"statusCode": -2, "message": f"Wrong password"})
            return render_template("GeneralMessage.html", message = "Wrong password")
    return json.dumps({"statusCode": 1, "message": "Success"})


@app.route("/managerprofilepage")
@manager_login_required
def managerprofilepage():
    return render_template(
        "manager/managerProfilePage.html", Userdetails=session["User"]
    )


@app.route("/manager-logout")
@manager_login_required
def managerlogout():
    session.pop("User", None)
    return redirect("/manager-login")


@app.route("/donorprofilepage")
@donor_login_required
def donorprofilepage():
    # print(f"session['User'] = {session['User']}", file=sys.stderr)
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


@app.route("/make-payment-donor", methods=["GET", "POST"])
@donor_login_required
def makePayment():
    amount = request.args["amount"]
    if request.method == "POST":
        cur = mysql.connection.cursor()
        cur.execute(
            """INSERT INTO funds (userName,userType,amount,status,tranmessage) VALUES (%s,%s, %s ,%s,%s)""",
            (
                session["User"]["userName"],
                session["User"]["type"],
                amount,
                1,
                f"{session['User']['userName']} donated Rs. {amount}",
            ),
        )
        # cur.execute("commit")
        mysql.connection.commit()
        # return "<h5>THANK YOU FOR CONTRIBUTING</h5>"
        return render_template("GeneralMessage.html",message="THANK YOU FOR CONTRIBUTING")
    return render_template("donor/makePayment.html")


@app.route("/donate-item", methods=["GET", "POST"])
@donor_login_required
def donateItem():

    if request.method == "POST":
        global inventory
        donation = request.form
        # print(donation, file=sys.stderr)
        donated = False
        donationfreq = int(donation["book"])
        if donationfreq > 0:
            donated = True
            inventory.addItem(Item(ItemType["BOOK"]), donationfreq)
        donationfreq = int(donation["bag"])
        if donationfreq > 0:
            donated = True
            inventory.addItem(Item(ItemType["BAG"]), donationfreq)
        donationfreq = int(donation["shoes"])
        if donationfreq > 0:
            donated = True
            inventory.addItem(Item(ItemType["SHOES"]), donationfreq)
        donationfreq = int(donation["clothes"])
        if donationfreq > 0:
            donated = True
            inventory.addItem(Item(ItemType["CLOTHES"]), donationfreq)
        if donated:
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
            # return "<h5> USER DEATILS CHANGED</h5>"
            return render_template("GeneralMessage.html", message = "USER DEATILS CHANGED")
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
                    # print(inputs["newPassword"])
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
        # # print(f"Query Took {time.time()-tick}",file=sys.stderr)
        # user={}
        # user['name']=query[0][2]
        # user['userName']=query[0][1]
        # user['email']=query[0][5]
        # user['contactNumber']=query[0][6]
        # user["membership"]=query[0][4]
        return render_template("donor/updateDonorProfile.html", user=session["User"])


# managers code starts here
@app.route("/manager-show-student-list")
@manager_login_required
def managershowstudentlist():
    headerName = (
        "ID",
        "Name",
        "Class",
        "Roll Number",
        "Last Marks",
        "Family Income",
        "Contact Number",
        "Registered By",
        "Help Required(Rs.)",
    )
    global mysqlc
    priceList = mysqlc.select(["select itemname,price from inventory", ()])

    priceDict = dict(priceList)
    # print(priceDict, file=sys.stderr)
    query = mysqlc.select(
        [
            "select id,Name,Class,rollnumber,lastmarks,familyincome,contactnumber,registeredBy,(requirement_fees+%s*requirement_book + %s*requirement_bag + %s*requirement_shoes + %s*requirement_clothes)  from studentlist order by id",
            (
                priceDict["BOOK"],
                priceDict["BAG"],
                priceDict["SHOES"],
                priceDict["CLOTHES"],
            ),
        ]
    )

    # print(query, file=sys.stderr)

    return render_template(
        "manager/showStudent.html", headerName=headerName, query=query
    )


@app.route("/manager-show-staff-list")
@manager_login_required
def managershowstafflist():
    headerName = ("ID", "Name", "Email", "Contact Number")
    global mysqlc
    query = mysqlc.select(
        ["select id,name,email,contactnumber from stafflist where role = 'staff'", ()]
    )

    # print(query, file=sys.stderr)

    return render_template("manager/showStaff.html", headerName=headerName, query=query)


@app.route("/manager-show-donor-list")
@manager_login_required
def managershowdonorlist():
    headerName = ("ID", "Name", "Email", "Contact Number", "Membership")
    global mysqlc
    query = mysqlc.select(
        [
            """select id,name,email,contactnumber,
                case
                    when membership = 1 then 'Semi-Anually'
                    when membership = 0 then 'Anually'
                    else 'N/A'
                end as mtype
             from donorList""",
            (),
        ]
    )

    # print(query, file=sys.stderr)

    return render_template("manager/showDonor.html", headerName=headerName, query=query)

    # print(query, file=sys.stderr)

    return render_template("manager/showStaff.html", headerName=headerName, query=query)


@app.route("/manager-show-funds")
@manager_login_required
def managershowfunds():
    global mysqlc
    query = mysqlc.select(
        [
            "SELECT sum(IF(`status`=1, `amount`, 0))-sum(IF(`status`=0, `amount`, 0)) AS    `Balance` FROM   funds",
            (),
        ]
    )

    # print(query, file=sys.stderr)

    return render_template("manager/showFunds.html", BalanceFund=query[0][0])


@app.route("/manager-show-inventory-list")
@manager_login_required
def managershowinventorylist():
    headerName = ("Item Name", "Available Units", "Unit Price")
    global mysqlc
    query = mysqlc.select(
        ["select itemname,frequency,price from inventory order by itemid", ()]
    )

    # print(query, file=sys.stderr)

    return render_template(
        "manager/showInventory.html", headerName=headerName, query=query
    )


@app.route("/manager-show-expenditures", methods=["GET", "POST"])
@manager_login_required
def managershowexpenditures():
    headerName = ("TransactionID", "User Name", "Amount (Rs.)", "Remarks")
    global mysqlc
    title = "Expenditures"
    if request.method == "POST":
        if request.form["type"] == "Expenditures":
            query = mysqlc.select(
                [
                    "select id,userName,amount,tranmessage from funds where status = 0 order by id",
                    (),
                ]
            )
        else:
            query = mysqlc.select(
                [
                    "select id,userName,amount,tranmessage from funds where status = 1 order by id",
                    (),
                ]
            )
            title = "Income"
    else:
        query = mysqlc.select(
            [
                "select id,userName,amount,tranmessage from funds where status = 0 order by id",
                (),
            ]
        )

    return render_template(
        "manager/showExpenditures.html", headerName=headerName, query=query, title=title
    )


@app.route("/manager-show-requirement")
@manager_login_required
def managershowrequirement():
    req = Requirement(mysql)
    headerName, query = req()
    return render_template(
        "manager/showRequirement.html", headerName=headerName, query=query
    )


@app.route("/manager-update-price-list", methods=["GET", "POST"])
@manager_login_required
def managerupdatepricelist():
    # do some query
    newPriceForm = request.form
    if request.method == "POST":
        # return request.form
        newPrice = {
            "BOOK": newPriceForm["BookPrice"],
            "BAG": newPriceForm["BagPrice"],
            "SHOES": newPriceForm["ShoesPrice"],
            "CLOTHES": newPriceForm["ClothesPrice"],
        }
        global inventory
        inventory.UpdatePriceList(newPrice)
        return render_template(
            "manager/managerUpdatePrice.html", oldprice=newPrice, saved=True
        )
    if request.method == "GET":
        global mysqlc
        priceList = mysqlc.select(["select itemname,price from inventory", ()])
        priceDict = dict(priceList)
        return render_template(
            "manager/managerUpdatePrice.html", oldprice=priceDict, saved=False
        )


@app.route("/manager-buy-item", methods=["GET", "POST"])
@manager_login_required
def managerbuyitem():
    global mysqlc
    priceList = mysqlc.select(["select itemname,price from inventory", ()])
    priceDict = dict(priceList)
    global inventory
    global ngobank
    funds = ngobank.getFunds()
    if request.method == "POST":
        orderForm = request.form
        orderRequiredAmount = 0
        for k, v in priceDict.items():
            orderRequiredAmount += v * (int(orderForm[k]))
        if funds < orderRequiredAmount:
            return redirect(
                url_for(
                    "managerbuyresultpage",
                    bamount=orderRequiredAmount,
                    status=-1,
                    funds=funds,
                )
            )
            # return render_template("manager/managerBuyItem.html",priceDict = priceDict,status = -1,bamount = orderRequiredAmount, funds= funds)
        if orderRequiredAmount <= 0:
            return redirect(
                url_for(
                    "managerbuyresultpage",
                    bamount=orderRequiredAmount,
                    status=-2,
                    funds=funds,
                )
            )
            # return render_template("manager/managerBuyItem.html",priceDict = priceDict,status = -2,bamount = orderRequiredAmount, funds= funds)
        # print(orderForm, file=sys.stderr)
        inventory.AddMultiple(orderForm)
        ngobank.withdraw(
            session["User"]["userName"],
            "manager",
            orderRequiredAmount,
            "Bought Items for NGO",
        )
        return redirect(
            url_for(
                "managerbuyresultpage",
                bamount=orderRequiredAmount,
                status=1,
                funds=funds - orderRequiredAmount,
            )
        )
        # return render_template("manager/managerBuyItem.html",priceDict = priceDict,status = 1,bamount = orderRequiredAmount, funds = funds - orderRequiredAmount)
    if request.method == "GET":
        return render_template(
            "manager/managerBuyItem.html", priceDict=priceDict, status=0, funds=funds
        )


@app.route("/managerbuyresultpage")
@manager_login_required
def managerbuyresultpage():
    status = request.args.get("status")
    bamount = request.args.get("bamount")
    funds = request.args.get("funds")
    return render_template("manager/managerBuyResultPage.html", **request.args)


@app.route("/manager-check-records")
@manager_login_required
def managercheckrecords():
    return render_template("manager/managerCheckRecords.html")


@app.route("/update-manager-profile", methods=["GET", "POST"])
@manager_login_required
def updatemanagerprofile():
    global mysqlc
    query = mysqlc.select(
        [
            "select name,email,contactnumber,password from stafflist where username = %s",
            (session["User"]["userName"],),
        ]
    )

    user = {
        "name": query[0][0],
        "userName": session["User"]["userName"],
        "email": query[0][1],
        "phone": query[0][2],
    }

    if request.method == "POST":
        # return request.form
        if request.form["formName"] == "changePassword":
            manager = Manager(
                user["name"],
                user["userName"],
                Contact(user["email"], user["phone"]),
                query[0][3],
                True,
            )
            slqandval = manager.checkAndUpdatePasswordsqlandvalues(
                request.form["oldPassword"], request.form["newPassword"]
            )

            if slqandval is not False:
                mysqlc.exeandcommit(slqandval)
                # print((request.form["newPassword"], slqandval), file=sys.stderr)
                return redirect(url_for("managerlogout"))
            else:
                return "Wrong Password"
        if request.form["formName"] == "updateProfile":
            userInfo = request.form
            manager = Manager(
                userInfo["name"],
                user["userName"],
                Contact(userInfo["email"], userInfo["phone"]),
                query[0][3],
                True,
            )
            mysqlc.exeandcommit(manager.updateInfosqlandvalues())
            session["User"]["name"] = userInfo["name"]
            session.modified = True
            return redirect(url_for("managerprofilepage"))

    return render_template("manager/updateManagerProfile.html", user=user)


@app.route("/manager-update-donor", methods=["GET", "POST"])
@manager_login_required
def managerupdatedonor():
    global mysqlc
    query = mysqlc.select(["select userName from donorList", ()])
    inputs = [row[0] for row in query]

    if request.method == "POST":
        if request.form["formName"] == "chooseDonor":
            query = mysqlc.select(
                [
                    "select name,email,contactnumber,userName,membership,password from donorList where username = %s",
                    (request.form["donorUserName"],),
                ]
            )

            user = {
                "name": query[0][0],
                "email": query[0][1],
                "phone": query[0][2],
                "userName": query[0][3],
                "membership": query[0][4],
            }
            return render_template(
                "manager/managerUpdateDonorProfile.html", inputs=inputs, user=user
            )
        if request.form["formName"] == "updateProfile":
            userInfo = request.form
            query = mysqlc.select(
                [
                    "select name,email,contactnumber,userName,membership,password from donorList where username = %s",
                    (userInfo["userName"],),
                ]
            )
            donor = Donor(
                userInfo["name"],
                userInfo["userName"],
                Contact(userInfo["email"], userInfo["phone"]),
                query[0][5],
                int(userInfo["membership"]),
            )
            mysqlc.exeandcommit(donor.updateInfosqlandvalues())

            return "Profile Updated Successfully"
        if request.form["formName"] == "changePassword":
            userInfo = request.form
            query = mysqlc.select(
                [
                    "select name,email,contactnumber,userName,membership,password from donorList where username = %s",
                    (userInfo["userName"],),
                ]
            )
            user = {
                "name": query[0][0],
                "email": query[0][1],
                "phone": query[0][2],
                "userName": query[0][3],
                "membership": query[0][4],
            }
            donor = Donor(
                user["name"],
                user["userName"],
                Contact(user["email"], user["phone"]),
                query[0][5],
                int(user["membership"]),
            )
            # return str(query[0][5] == userInfo['oldPassword'])
            stmt = donor.checkAndUpdatePasswordsqlandvalues(
                userInfo["oldPassword"], userInfo["newPassword"]
            )
            if stmt is not False:
                mysqlc.exeandcommit(stmt)
                return "Password chaned Successfully"
            else:
                return "wrong password"
        return request.form
    return render_template(
        "manager/managerUpdateDonorProfile.html", inputs=inputs, user=None
    )


@app.route("/manager-help-students", methods=["POST", "GET"])
@manager_login_required
def managerhelpstudents():
    req = Requirement(mysql)
    infoDict = req(forPrinting=False)
    AvailFunds = ngobank.getFunds()
    infoDict["AVA"] = AvailFunds
    infoDict["userName"] = session["User"]["userName"]
    # return str(infoDict)
    if request.method == "POST":
        if request.form["DONATION"] == "Sufficient":
            donationid = Help(mysql).SufficientFulfil(infoDict)

            # query = mysqlc.select(
            #     [
            #     """select
            #     id,
            #     name,
            #     rollnumber,
            #     requirement_fees ,
            #     requirement_book ,
            #     requirement_bag ,
            #     requirement_shoes ,
            #     requirement_clothes
            #     from studentlist
            #      """,
            #      ()
            #      ]
            # )
            # headerName = ('ID', 'Name', 'Roll Number', 'Fees Donated', 'Book(s) Donated', 'Bag(s) Donated', 'Shoe(s) Donated', 'Dress(s) Donated')

            # mysqlc.exeandcommit(
            #     [
            #         """update studentlist set
            #             requirement_fees = 0,
            #             requirement_book = 0,
            #             requirement_bag = 0,
            #             requirement_shoes = 0,
            #             requirement_clothes = 0
            #             where id = 1;""",
            #             ()
            #     ]
            # )

            return redirect(url_for("managershowhelp", donationid=donationid))
        if request.form.get("DONATION") == "Insufficient":
            donationid = Help(mysql).InSufficientFulfil(
                infoDict, request.form["Priority"]
            )
            return redirect(url_for("managershowhelp", donationid=donationid))
    if infoDict["REQ"] == 0:
        return render_template(
            "manager/managerHelpStudents.html",
            title="All helps fulfilled",
            infoDict=infoDict,
        )
    if infoDict["REQ"] <= AvailFunds:
        return render_template(
            "manager/managerHelpStudents.html",
            title="Sufficient Funds",
            infoDict=infoDict,
        )
    else:
        return render_template(
            "manager/managerHelpStudents.html",
            title="Insufficient Funds",
            infoDict=infoDict,
        )


@app.route("/manager-show-help")
@manager_login_required
def managershowhelp():

    donationid = request.args.get("donationid")

    headerName = (
        "Donation Id",
        "Student Id",
        "Name",
        "Gender",
        "Family Income",
        "Last Marks",
        "Fess Donated(Rs.)",
        "Books Donated",
        "Bags Donated",
        "Shoes Donated",
        "Dresses Donated",
        "Date Of Donation",
    )
    global mysqlc
    query = mysqlc.select(
        [
            """select 
                donationId,
                id,
                name,
                gender,
                familyincome,
                lastmarks,
                requirement_fees, 
                requirement_book, 
                requirement_bag,
                requirement_shoes,
                requirement_clothes,
                date(processedTimestamp)

                from completedhelp order by donationid desc,id
                ;""",
            (),
        ]
    )

    return render_template(
        "manager/managerShowHelps.html",
        query=query,
        headerName=headerName,
        donationid=donationid,
    )


@app.route("/manager-manage-staff", methods=["GET", "POST"])
@manager_login_required
def managermanagestaff():
    global mysqlc
    if request.method == "POST":
        if (
            request.form.get("formName") == None
            and request.form.get("pageOption") != "Remove Staff"
        ):
            return render_template(
                "manager/managerManageStaff.html",
                user=None,
                status=1,
                option=request.form,
            )
        if (
            request.form.get("formName") == None
            and request.form.get("pageOption") == "Remove Staff"
        ):
            query = mysqlc.select(
                ["select userName from stafflist where role = 'staff';", ()]
            )
            if len(query) == 0:
                return "No staff(s) in NGO"
            staffuserNameList = [row[0] for row in query]
            return render_template(
                "manager/managerManageStaff.html",
                user=staffuserNameList,
                status=1,
                option=request.form,
            )

        if request.form.get("formName") == "Register Staff":
            sinfo = request.form
            query = mysqlc.select(
                [
                    """select 
                    COALESCE(sum(userName=%s),0), COALESCE(sum(email = %s),0) ,COALESCE(sum(contactnumber = %s),0)
                    from stafflist 
                    where userName = %s or email = %s or contactnumber = %s;
                    """,
                    (
                        sinfo["userName"],
                        sinfo["email"],
                        sinfo["phone"],
                        sinfo["userName"],
                        sinfo["email"],
                        sinfo["phone"],
                    ),
                ]
            )
            if query[0][0] + query[0][1] + query[0][2] > 0:
                errorMessage = ""
                if query[0][0] > 0:
                    errorMessage = errorMessage + "userName Already taken,"
                if query[0][1] > 0:
                    errorMessage = errorMessage + "email Already present in database,"
                if query[0][2] > 0:
                    errorMessage = errorMessage + "Phone number present in database,"
                errorMessage = errorMessage + " Please give new details"
                return errorMessage
            s = Staff(
                sinfo["name"],
                sinfo["userName"],
                Contact(sinfo["email"], sinfo["phone"]),
                sinfo["password_1"],
            )
            mysqlc.exeandcommit(s.getsqlandvalues())
            return "Successful Staff registration"
        if request.form.get("formName") == "Remove Staff":
            query = mysqlc.select(
                [
                    "select userName from stafflist where userName = %s;",
                    (request.form.get("staffUserName"),),
                ]
            )
            if len(query) == 0:
                return "Staff Already Removed from NGO"
            mysqlc.exeandcommit(
                [
                    "DELETE FROM stafflist WHERE userName = %s",
                    (request.form.get("staffUserName"),),
                ]
            )
            return f"{request.form.get('staffUserName')} Removed from NGO!"
    return render_template("manager/managerManageStaff.html", user=None, status=None)


@app.route("/manager-register-student", methods=["GET", "POST"])
@manager_login_required
def managerregisterStudent():
    global mysqlc
    if request.method == "POST":
        sinfo = request.form
        query = mysqlc.select(
            [
                """select 
                COALESCE(sum(email = %s),0) ,COALESCE(sum(contactnumber = %s),0)
                from studentlist 
                where (email = %s or contactnumber = %s) ;
                """,
                (
                    sinfo["email"],
                    sinfo["contactNumber"],
                    sinfo["email"],
                    sinfo["contactNumber"],
                ),
            ]
        )
        if query[0][0] + query[0][1] > 0:
            errorMessage = ""
            if query[0][0] > 0:
                errorMessage = errorMessage + "email Already present in database,"
            if query[0][1] > 0:
                errorMessage = errorMessage + "Phone number present in database,"
            errorMessage = errorMessage + " Please give new details"
            # return errorMessage
            return render_template("GeneralMessage.html", message= errorMessage)
        mysqlc.registerStudent(request.form,session['User']['userName'])

        # return "STUDENT REGISTERED"
        return render_template("GeneralMessage.html", message= "STUDENT REGISTERED")
    return render_template("staff/registerStudent.html", user=session["User"])


@app.route("/manager-manage-student")
@manager_login_required
def managermanagestudent():
    return render_template("manager/managerManageStudent.html")


@app.route("/manager-update-student", methods=["GET", "POST"])
@manager_login_required
def managerupdatestudent():
    global mysqlc
    query = mysqlc.select(["select id,name from studentlist", ()])
    inputs = [[row[0], row[1]] for row in query]

    if request.method == "POST":
        if request.form["formName"] == "chooseStudent":
            query = mysqlc.select(
                [
                    """select 
                    id,
                    name,
                    class,
                    requirement_fees,
                    requirement_book,
                    requirement_bag,
                    requirement_shoes,
                    requirement_clothes,
                    email,
                    rollnumber,
                    contactnumber,
                    lastmarks,
                    gender,
                    familyincome 
                    from studentlist where id = %s""",
                    (request.form["studentID"],),
                ]
            )

            user = {
                "id": query[0][0],
                "name": query[0][1],
                "class": query[0][2],
                "requirement_fees": query[0][3],
                "requirement_book": query[0][4],
                "requirement_bag": query[0][5],
                "requirement_shoes": query[0][6],
                "requirement_clothes": query[0][7],
                "email": query[0][8],
                "rollnumber": query[0][9],
                "contactnumber": query[0][10],
                "lastmarks": query[0][11],
                "gender": query[0][12],
                "familyincome": query[0][13],
            }
            return render_template(
                "manager/managerUpdateStudent.html", inputs=inputs, user=user
            )
        if request.form["formName"] == "updateProfile":
            userInfo = request.form
            sinfo = request.form
            query = mysqlc.select(
                [
                    """select 
                    COALESCE(sum(email = %s),0) ,COALESCE(sum(contactnumber = %s),0)
                    from studentlist 
                    where (email = %s or contactnumber = %s) and id != %s ;
                    """,
                    (
                        sinfo["email"],
                        sinfo["contactnumber"],
                        sinfo["email"],
                        sinfo["contactnumber"],
                        int(sinfo["id"]),
                    ),
                ]
            )
            if query[0][0] + query[0][1] > 0:
                errorMessage = ""
                if query[0][0] > 0:
                    errorMessage = errorMessage + "email Already present in database,"
                if query[0][1] > 0:
                    errorMessage = errorMessage + "Phone number present in database,"
                errorMessage = errorMessage + " Please give new details"
                # return errorMessage
                return render_template("GeneralMessage.html", message = errorMessage)
            mysqlc.updateStudent(request.form)
            # return "Profile Updated Successfully"
            return render_template("GeneralMessage.html", message = "Profile Updated Successfully")
    return render_template(
        "manager/managerUpdateStudent.html", inputs=inputs, user=None
    )


if __name__ == "__main__":
    app.run(debug=True)
