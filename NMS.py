from flask import Flask, render_template

import numpy as np


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


if __name__ == "__main__":
    app.run(debug=True)
