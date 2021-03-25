from flask import Flask, render_template, request, session, flash, redirect
from flask_mysqldb import MySQL
from SupportModules import mysqlcon,Password
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
    'host':app.config["MYSQL_HOST"],
  'user':app.config["MYSQL_USER"],
  'password':app.config["MYSQL_PASSWORD"],
  'database':app.config["MYSQL_DB"]
}


def staff_login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if ('User' in session) and (session['User']['type']=='staff'):
            return f(*args, **kwargs)
        else:
            print("You need to login first",file = sys.stderr)
            return redirect("/staff-login")
    return wrap

def donor_login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if ('User' in session) and (session['User']['type']=='donor'):
            return f(*args, **kwargs)
        else:
            print("You need to login first",file = sys.stderr)
            return redirect("/donor-login")
    return wrap

def manager_login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if ('User' in session) and (session['User']['type']=='manager'):
            return f(*args, **kwargs)
        else:
            print("You need to login first",file = sys.stderr)
            return redirect("/manager-login")
    return wrap

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/donor-login", methods=["GET", "POST"])
def donorLogin():
    global mysql
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
                
            if len(donorDetails["password"] < 8 ):
                return "<h5> PLEASE ENTER A PASSWORD OF LENGTH ATLEAST 8</h5>"
            
            u, l, n, s = 0, 0, 0, 0
            
            for i in donorDetails["password"]:
                if(i.isupper()):
                    u += 1
                if(i.islower()):
                    l += 1
                if(i.isdigit()):
                    n += 1
                if(i == '@' or i == '$' or i == '_'):
                    s += 1
                    
            if(u == 0 or l == 0 or n == 0 or s == 0):
                return "<h5> PASSWORD MUST HAVE ATLEAST 1 UPPER CASE LETTER, 1 LOWER CASE LETTER, 1 SPECIAL SYMBOL ($, @, _) AND 1 DIGIT</h5>"
            
            if(u+l+n+s != len(donorDetails["password"])):
                return "<h5> PASSWORD MUST ONLY CONTAIN LOWER CASE, UPPER CASE, DIGIT AND ($, @, _)</h5>"
                
                    
            if(len(donorDetails["userName"]) <6):
                return "<h5> PLEASE ENTER A USERNAME OF LENGTH ATLEAST 6</h5>"
            
            count = 0
            
            for i in donorDetails["userName"]:
                if(i.isupper() or i.ilower() or i.isdigit or i == '_'):
                    count += 1
            
            if(count != len(donorDetails["userName"])):
                return "<h5> USERNAME MUST ONLY CONTAIN LOWER CASE, UPPER CASE, DIGIT AND UNDERSCORE ('_')</h5>"
                
                
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
            session.pop('User', None)
            mysqlc = mysqlcon(mydbDetails)
            query = mysqlc.select(["select id,userName,name,password from donorList where username = %s",(userName,)])
            if(len(query)==0):
                return json.dumps({"statusCode":-1,"message":"User doesn't exist"})
            else:
                # if(query[0][3] == Password(password).getEncryptedPassword()):
                if(query[0][3] == password):
                    session['User']={'name':query[0][2],'userName':userName,'id':query[0][0],'type':'donor'}
                    return json.dumps({"statusCode":1,"message":f"Successful Login {query[0][2]}"})
                else:
                    return json.dumps({"statusCode":-2,"message":f"Wrong password"})
            return json.dumps({"statusCode":1,"message":"Success"})

    # return "Done!"
    # cur.execute("""CREATE TABLE donorList(id INTEGER , name VARCHAR(20))""")

    return render_template("donorLogin.html", userType="donor")


@app.route("/manager-login")
def managerLogin():
    return render_template("managerLogin.html", userType="manager")


@app.route("/staff-login")
def staffLogin():
    return render_template("staffLogin.html", userType="staff")

@app.route("/staffcheckpassword", methods = ["POST"])
def staffcheckpassword():
    staffDetails = request.form
    userName = staffDetails["userName"]
    password = staffDetails["password"]
    session.pop('User', None)
    mysqlc = mysqlcon(mydbDetails)
    query = mysqlc.select(["select id,username,name,password from stafflist where username = %s and role = %s",(userName,'staff',)])
    if(len(query)==0):
        return json.dumps({"statusCode":-1,"message":"User doesn't exist"})
    else:
        if(query[0][3] == Password(password).getEncryptedPassword()):
            session['User']={'name':query[0][2],'userName':userName,'id':query[0][0],'type':'staff'}


            return json.dumps({"statusCode":1,"message":f"Successful Login {query[0][2]}"})
        else:
            return json.dumps({"statusCode":-2,"message":f"Wrong password"})
    return json.dumps({"statusCode":1,"message":"Success"})

@app.route("/staffprofilepage")
@staff_login_required
def staffprofilepage():
    return f"Hello {session['User']['name']}"

@app.route("/stafflogout")
@staff_login_required
def stafflogout():
    session.pop('User',None)
    return redirect("/staff-login")
    

@app.route("/managercheckpassword", methods = ["POST"])
def managercheckpassword():
    managerDetails = request.form
    userName = managerDetails["userName"]
    password = managerDetails["password"]
    session.pop('User', None)
    mysqlc = mysqlcon(mydbDetails)
    query = mysqlc.select(["select id,username,name,password from stafflist where username = %s and role = %s",(userName,'manager',)])
    if(len(query)==0):
        return json.dumps({"statusCode":-1,"message":"User doesn't exist"})
    else:
        if(query[0][3] == Password(password).getEncryptedPassword()):
            session['User']={'name':query[0][2],'userName':userName,'id':query[0][0],'type':'manager'}


            return json.dumps({"statusCode":1,"message":f"Successful Login {query[0][2]}"})
        else:
            return json.dumps({"statusCode":-2,"message":f"Wrong password"})
    return json.dumps({"statusCode":1,"message":"Success"})

@app.route("/managerprofilepage")
@manager_login_required
def managerprofilepage():
    print(f"session['User'] = {session['User']}",file =sys.stderr)
    return f"Hello manager{session['User']['name']}"

@app.route("/managerlogout")
@manager_login_required
def managerlogout():
    session.pop('User',None)
    return redirect("/manager-login")

@app.route("/donorprofilepage")
@donor_login_required
def donorprofilepage():
    print(f"session['User'] = {session['User']}",file =sys.stderr)
    return f"Hello donor{session['User']['name']}"

@app.route("/donorlogout")
@donor_login_required
def donorlogout():
    session.pop('User',None)
    return redirect("/donor-login")



if __name__ == "__main__":
    app.run(debug=True)
