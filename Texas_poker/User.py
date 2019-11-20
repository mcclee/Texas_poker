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
        c.execute('select id from User where id = ? and password = ?', gp)
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


if __name__ == '__main__':
    d = DB('test.db')
    print(d.login('Mcclee', '15801799809n'))
    print(d.register('Mcclee', '15801799809n'))