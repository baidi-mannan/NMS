from flask import Flask, render_template,request
import sys
# import numpy as np

import json 


from SupportModules import mysqlcon,Password,Donor,Contact
mydbDetails = {
    'host':"nmsdb.czj2xnercmna.us-east-2.rds.amazonaws.com",
  'user':"admin",
  'password':"nmszka323",
  'database':"coredb"
}


app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/donor-login")
def donorLogin():
    return render_template("donorLogin.html", userType="donor")


@app.route("/manager-login")
def managerLogin():
    return render_template("managerLogin.html", userType="manager")


@app.route("/staff-login")
def staffLogin():
    return render_template("staffLogin.html", userType="staff")

@app.route("/logindonorpassword",methods=["POST"])
def checkPasswordFromUser():
    # logic login
    mysql = mysqlcon(mydbDetails)
    query = mysql.select(["select passwd,donorname from donors where username = %s",(request.form['username'],)])
    if(len(query)==0):
        return json.dumps({"statusCode":-1,"message":"User doesn't exist"})
    else:
        if(query[0][0] == Password(request.form['password']).getEncryptedPassword()):
            return json.dumps({"statusCode":1,"message":f"Successful Login {query[0][1]}"})
        else:
            return json.dumps({"statusCode":-2,"message":f"Wrong password"})

    print(request.form,file=sys.stderr)
    return json.dumps({"statusCode":1,"message":"Success"})

@app.route("/donorprofilepage")
def donorprofilepage():
    return json.dumps({"statusCode":1,"message":"Success"})

@app.route("/registerdonor",methods=["POST"])
def registerdonor():
    form = request.form
    d = Donor(form['name'],form['username'],Contact(form['emailid'],form['phone']),form['password'])
    mysql = mysqlcon(mydbDetails)
    query = mysql.select(["select username from donors where username = %s",(form['username'],)])
    if(len(query)==0):
        # ok add new user
        mysql.exeandcommit(d.getsqlandvalues())
        return json.dumps({"statusCode":1,"message":"Success"})
    else:
        return json.dumps({"statusCode":-2,"message":"User already exist"})

if __name__ == "__main__":
    app.run(debug=True)
