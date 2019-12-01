import sqlite3
import datetime


class DB:
    def __init__(self, path):
        self.path = path
        self.db = None

    def conn(self):
        if not self.db:
            self.db = sqlite3.connect(self.path)
        return self.db

    def close(self):
        self.db.close()
        self.db = None

    def login(self, username, password):
        db = self.conn()
        c = db.cursor()
        gp = (username, password)
        c.execute('select id, coins from User where id = ? and password = ?', gp)
        res = c.fetchall()
        if len(res) > 0:
            c.execute('Update User set last_login_date=? where id=?', (datetime.datetime.now(), username))
            db.commit()
        self.close()
        return res

    def register(self, username, password):
        db = self.conn()
        c = db.cursor()
        gp = (username,)
        c.execute('select id from User where id = ?', gp)
        res = c.fetchall()
        if len(res) == 0:
            gp = (username, password, datetime.datetime.now(), 1000, 0)
            c.execute('insert into User (id, password, last_login_date, coins, playtimes) values (?, ?, ?, ?, ?)', gp)
            db.commit()
            self.close()
            return True
        self.close()
        return False

    def insert(self, usn, coins):
        db = self.conn()
        c = db.cursor()
        c.execute('select id, playtimes from User where id = ?', (usn, ))
        res = c.fetchall()
        if len(res) > 0:
            c.execute('Update User set coins=?, playtimes=? where id=?', (coins, res[0][1] + 1, usn))
            db.commit()
        self.close()

    def get_coins(self, ID):
        db = self.conn()
        c = db.cursor()
        c.execute('select id, coins from User where id = ?', (ID,))
        res = c.fetchall()
        self.close()
        if len(res) > 0:
            return res[0][1]
        return 0


if __name__ == '__main__':
    d = DB('test.db')
    d.insert('123', 1000)
