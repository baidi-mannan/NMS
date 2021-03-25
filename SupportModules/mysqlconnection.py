import mysql.connector
class mysqlcon:

    def __init__(self, dblogin:dict):
        self.db = mysql.connector.connect(
            host = dblogin['host'],
            user = dblogin['user'],
            password = dblogin['password'],
            database = dblogin['database']
        )
        self.cursor = self.db.cursor()
    def __del__(self):
        self.db.close()
    
    def select(self, sqlandval:list):
        self.cursor.execute(sqlandval[0],sqlandval[1])
        return self.cursor.fetchall()
    def exeandcommit(self,sqlandval:list):
        self.cursor.execute(sqlandval[0],sqlandval[1])
        self.db.commit()
        return self.cursor.rowcount

