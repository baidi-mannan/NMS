import mysql.connector
import sys
import time

# import numpy as np


class mysqlcon:
    def __init__(self, dblogin: dict):
        self.dblogin = dblogin
        self.db = mysql.connector.connect(
            host=dblogin["host"],
            user=dblogin["user"],
            password=dblogin["password"],
            database=dblogin["database"],
        )
        self.cursor = self.db.cursor()
        self.debug = True

    def __del__(self):
        self.db.close()

    def validate(self):
        tick = time.time()
        if self.db.is_connected():
            if self.debug:
                print(f"Validation check took{time.time() - tick}", file=sys.stderr)
            return 1
        else:
            self.db.close()
            self.db = mysql.connector.connect(
                host=self.dblogin["host"],
                user=self.dblogin["user"],
                password=self.dblogin["password"],
                database=self.dblogin["database"],
            )
            self.cursor = self.db.cursor()
            if self.debug:
                print(f"Reconnection  took{time.time() - tick}", file=sys.stderr)

            return 0

    def select(self, sqlandval: list):
        self.validate()
        self.cursor.execute(sqlandval[0], sqlandval[1])
        return self.cursor.fetchall()

    def exeandcommit(self, sqlandval: list):
        self.validate()
        self.cursor.execute(sqlandval[0], sqlandval[1])
        self.db.commit()
        return self.cursor.rowcount

    def userNameList(self, str):
        self.validate()
        self.cursor.execute(str)

        # arr = np.asarray(self.cursor.fetchall())
        arr = self.cursor.fetchall()
        strArr = []
        for i in range(len(arr)):
            strArr.append(arr[i][0])

        return strArr

    def registerStudent(self, details):
        print(details)
        self.cursor.execute(
            """INSERT INTO studentlist(name,class,requirement_fees,requirement_book,requirement_bag,requirement_shoes,requirement_clothes,email,rollnumber,contactnumber,lastmarks,gender,familyincome) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (
                details["name"],
                details["class"],
                details["fees"],
                details["books"],
                details["bags"],
                details["shoes"],
                details["clothes"],
                details["email"],
                details["rollNumber"],
                details["contactNumber"],
                details["lastMarks"],
                details["gender"],
                details["familyIncome"],
            ),
        )

        self.db.commit()