from flask import Flask, render_template, request, session, flash, redirect, url_for
from flask_mysqldb import MySQL
from SupportModules import mysqlcon, Password, checkNewData
from functools import wraps
import json
import sys

app = Flask(__name__)
app.config["MYSQL_USER"] = "sql6401232"
app.config["MYSQL_PASSWORD"] = "un2P67tMei"
app.config["MYSQL_HOST"] = "sql6.freemysqlhosting.net"
app.config["MYSQL_DB"] = "sql6401232"
# app.config["MYSQL_CURSORCLASS"]

# for session
app.config["SECRET_KEY"] = "thisshouldbeasecret"

mysql = MySQL(app)


mydbDetails = {
    "host": app.config["MYSQL_HOST"],
    "user": app.config["MYSQL_USER"],
    "password": app.config["MYSQL_PASSWORD"],
    "database": app.config["MYSQL_DB"],
}


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
        mysqlc = mysqlcon(mydbDetails)

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
                    "select id,userName,name,password from donorList where username = %s",
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
                    }
                    return redirect(url_for("donorprofilepage"))
                else:
                    return "<h5> INCORRECT PASSWORD<br> PLEASE TRY AGAIN</h5>"

    return render_template("donorLogin.html", userType="donor")


@app.route("/manager-login")
def managerLogin():
    return render_template("managerLogin.html", userType="manager")


@app.route("/staff-login")
def staffLogin():
    return render_template("staffLogin.html", userType="staff")


@app.route("/staffcheckpassword", methods=["POST"])
def staffcheckpassword():
    staffDetails = request.form
    userName = staffDetails["userName"]
    password = staffDetails["password"]
    session.pop("User", None)
    mysqlc = mysqlcon(mydbDetails)
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
    mysqlc = mysqlcon(mydbDetails)
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

            return json.dumps(
                {"statusCode": 1, "message": f"Successful Login {query[0][2]}"}
            )
        else:
            return json.dumps({"statusCode": -2, "message": f"Wrong password"})
    return json.dumps({"statusCode": 1, "message": "Success"})


@app.route("/managerprofilepage")
def managerprofilepage():
    print(f"session['User'] = {session['User']}", file=sys.stderr)
    return f"Hello manager{session['User']['name']}"


@app.route("/managerlogout")
@manager_login_required
def managerlogout():
    session.pop("User", None)
    return redirect("/manager-login")


@app.route("/donorprofilepage")
@donor_login_required
def donorprofilepage():
    # print(f"session['User'] = {session['User']}", file=sys.stderr)
    return render_template("donorProfilePage.html", Userdetails=session["User"])


@app.route("/donor-logout")
def donorlogout():
    session.pop("User", None)
    return redirect("/donor-login")


@app.route("/donate-money", methods=["GET", "POST"])
def donateMoney():

    if request.method == "POST":
        amount = request.form["amount"]
        return redirect(url_for("makePayment", amount=amount))

    return render_template("donateMoney.html")


@app.route("/make-payment", methods=["GET", "POST"])
def makePayment():
    amount = request.args["amount"]
    if request.method == "POST":
        cur = mysql.connection.cursor()
        cur.execute(
            """INSERT INTO funds (userName,userType,amount,status) VALUES (%s,%s, %s ,%s)""",
            (session["User"]["userName"], session["User"]["type"], amount, 1),
        )
        mysql.connection.commit()
        return "<h5>THANK YOU FOR CONTRIBUTING</h5>"

    return render_template("makePayment.html")


if __name__ == "__main__":
    app.run(debug=True)
