from flask import Flask, render_template, request
from flask_mysqldb import MySQL


app = Flask(__name__)
app.config["MYSQL_USER"] = "sql6401232"
app.config["MYSQL_PASSWORD"] = "un2P67tMei"
app.config["MYSQL_HOST"] = "sql6.freemysqlhosting.net"
app.config["MYSQL_DB"] = "sql6401232"
# app.config["MYSQL_CURSORCLASS"]

mysql = MySQL(app)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/donor-login", methods=["GET", "POST"])
def donorLogin():
    cur = mysql.connection.cursor()
    stmt = "SHOW TABLES LIKE 'donorList'"
    cur.execute(stmt)
    result = cur.fetchone()

    if not result:
        cur.execute(
            """CREATE TABLE donorList(id INT NOT NULL AUTO_INCREMENT , 
            name VARCHAR(20) DEFAULT "Unamed",
            email VARCHAR(50),
            userName VARCHAR(50),
            password VARCHAR(50),
            contactNumber VARCHAR(20),
            PRIMARY KEY(id))"""
        )

    if request.method == "POST":
        donorDetails = request.form
        if request.form["button"] == "register":

            if donorDetails["password"] != donorDetails["rePassword"]:
                return "<h5> THE PASSWORD DOES NOT MATCH<br> PLEASE TRY AGAIN</h5>"
            if donorDetails["userName"] == "" or donorDetails["password"] == "":
                return "<h5> PLEASE ENTER A VALID USERNAME OR PASSWORD</h5>"
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

            val = cur.execute("""SELECT * FROM donorList""")
            if val > 0:
                pri = cur.fetchall()
                print(pri)
        if request.form["button"] == "login":
            userName = donorDetails["userName"]
            password = donorDetails["password"]

    # return "Done!"
    # cur.execute("""CREATE TABLE donorList(id INTEGER , name VARCHAR(20))""")

    return render_template("donorLogin.html", userType="donor")


@app.route("/manager-login")
def managerLogin():
    return render_template("managerLogin.html", userType="manager")


@app.route("/staff-login")
def staffLogin():
    return render_template("staffLogin.html", userType="staff")


if __name__ == "__main__":
    app.run(debug=True)
