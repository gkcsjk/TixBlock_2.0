import sqlite3


class mySql:
    def __init__(self):
        self.db = "database.db"
        with sqlite3.connect(self.db) as conn:
            cursor = conn.cursor()
            sqls = ["DROP TABLE IF EXISTS events",
                    "CREATE TABLE IF NOT EXISTS users(ID VARCHAR PRIMARY KEY , first_name VARCHAR, last_name VARCHAR, role INTEGER)",
                    'CREATE TABLE IF NOT EXISTS blockchain(hash VARCHAR, prev_hash VARCHAR)',
                    'CREATE TABLE IF NOT EXISTS blocks (ID INTEGER PRIMARY KEY AUTOINCREMENT, place VARCHAR, time VARCHAR, seat VARCHAR, price REAL, author VARCHAR, answer VARCHAR, hash VARCHAR, prev_hash VARCHAR)',
                    'CREATE TABLE IF NOT EXISTS temp (place VARCHAR, time VARCHAR, seat VARCHAR, price REAL)',
                    'CREATE TABLE IF NOT EXISTS events (ID INTEGER PRIMARY KEY AUTOINCREMENT, place VARCHAR, time VARCHAR, seat VARCHAR, price REAL)',
                    'CREATE TABLE IF NOT EXISTS tickets(hash VARCHAR, place VARCHAR, time VARCHAR, seat VARCHAR, price VARCHAR)', ]
            for sql in sqls:
                cursor.execute(sql)
            """
            if(self.getCountBlockchain() == 0):
                self.insertToBlockchain()
            """

    def runExample(self):
        eventsDict = {"Ed Sheeran - Melbourne Town Hall": {"27 - 11 - 2017 11:00 pm": {"1A": 109, "2A": 110, "3Z": 999},
                                                           "09 - 12 - 2017 11:00 pm": {"2B": 200, "2C": 210,
                                                                                       "2Z": 1100},
                                                           "19 - 01 - 2018 11:00 pm": {"3B": 300, "3C": 339,
                                                                                       "4B": 440}},

                      "Choppin Live - Melbourne Aquarium Center": {
                          "1 - 1 - 2011 11:00 pm": {"1B": 200, "9B": 900, "2A": 999},
                          "01 - 2 - 2012 11:00 pm": {"1A": 100},
                          "1 - 03 - 2012 11:00 pm": {"3C": 900, "4A": 899}},

                      "P!nk - Broken Life": {"13 - 13 - 2013 11:00 pm": {"9D": 200, "4D": 200},
                                             "03 - 11 - 2013 13:00 pm": {"45D": 19020, "44A": 10999},
                                             "13 - 03 - 2013 11:00 pm": {"3D": 9001, "22D": 4903}}
                      }
        self.parseEventDict(eventsDict)

    def parseEventDict(self, theDict):
        for eventName, data in theDict.items():
            for date, seatPrice in data.items():
                for seat, price in seatPrice.items():
                    self.insertToEvents(eventName, date, seat, price)

    def dropTempTable(self):
        with sqlite3.connect(self.db) as conn:
            cursor = conn.cursor()
            # Only drop the table temporary after cust paid all the tickets
            sql = 'DELETE FROM temp'
            cursor.execute(sql)

    def insertUser(self, first_name, last_name, account):
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()
            cur.execute("INSERT INTO users (first_name, last_name, ID, role) VALUES (?,?,?,0)", (first_name, last_name, account))
            con.commit()

    def getUsers(self):
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM users")
            return cur.fetchall()

    def getUser(self, ID):
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE ID=:ID", {"ID": ID})
            return cur.fetchone()

    def deleteUsers(self):
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()
            cur.execute("DELETE FROM users")
            cur.execute("INSERT INTO users (ID, first_name, last_name, role) values ('info@tixblock.com','admin','admin', 1)")

    def insertData(self, temp, place, time, seat, price):
        # Inserting data into database
        # Param:
        # temp is boolean. True if we are inserting to temporary table.
        # Place, time, seat and price are the params required.
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()
            if temp:
                cur.execute("INSERT INTO temp (place, time, seat, price) VALUES (?,?,?,?)", (place, time, seat, price))
            else:
                cur.execute("INSERT INTO blocks (place, time, seat, price) VALUES (?,?,?,?)",
                            (place, time, seat, price))

            con.commit()
            self.deleteBoughtTicket()

    def insertDataFromTemp(self):
        # Inserting data into database from temporary table to blocks.

        with sqlite3.connect(self.db) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM temp")
            rows = cur.fetchall()

            for row in rows:
                place = row[0]
                time = row[1]
                seat = row[2]
                price = row[3]

                sql = 'INSERT INTO blocks (place, time, seat, price) VALUES ({},{},{},{})'.format('\"' + place + '\"',
                                                                                                  '\"' + time + '\"',
                                                                                                  '\"' + seat + '\"',
                                                                                                  price)
                cur.execute(sql)
                con.commit()

            return rows  # Returning all the rows.

    def select_ticket(self, temp, params=()):
        # Param:
        # Temp is boolean. True for temporary table
        # Params is conditions.
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()
            if params == ():
                if temp:
                    cur.execute("SELECT * FROM temp")
                else:
                    cur.execute("SELECT * FROM blocks")
                return cur.fetchall()
            else:
                # No usage!!!
                string = "SELECT"
                for i in range(len(params) - 1):
                    string += "%s,"
                string += "%s"
                if (temp):
                    string += "FROM temp"
                else:
                    string += " FROM blocks"
                result = cur.execute(string)
                return result.fetchall()

    def totalPrice(self):
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()
            cur.execute("SELECT sum(price) FROM temp")
            return cur.fetchall()

    def delBlockchain(self):
        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM blockchain")

    def insertToEvents(self, place, time, seat, price):
        # Insert event details into events table
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()
            # sql = 'INSERT INTO events(place, time, seat, price) VALUES ({},{},{},{})'.format(cplace, ctime, cseat, cprice)
            # cur.execute(sql)
            cur.execute("INSERT INTO events (place, time, seat, price) VALUES (?,?,?,?)", (place, time, seat, price))
            con.commit()

    def insertToTemp(self, place, time, seat, price):
        # !!! No usage
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()
            sql = 'INSERT INTO temp(place, time, seat, price) VALUES ({},{},{},{})'.format(place, time, seat, price)
            cur.execute(sql)
            con.commit()
            self.deleteBoughtTicket()

    def retrieveFromEvents(self, param=(), whereclause=()):
        # To get distinct values, param = 'DISTINCT [fieldname]'
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()
            if (param == ()):
                if (whereclause != ()):
                    cur.execute("SELECT place,time,seat,price FROM events WHERE " + whereclause)
                else:
                    cur.execute("SELECT place,time,seat,price FROM events")
            else:
                str = 'SELECT ' + param
                str += ' FROM events'
                if (whereclause != ()):
                    cur.execute(str + ' WHERE ' + whereclause)
                else:
                    cur.execute(str)
            return cur.fetchall()

    def retrieveFromTemp(self, param=(), whereclause=()):
        # No usage
        # To get distinct values, param = 'DISTINCT [fieldname]'
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()
            if (param == ()):
                if (whereclause != ()):
                    cur.execute("SELECT place,time,seat,price FROM temp WHERE " + whereclause)
                else:
                    cur.execute("SELECT place,time,seat,price FROM temp")
            else:
                str = 'SELECT ' + param
                str += ' FROM temp'
                if (whereclause != ()):
                    cur.execute(str + ' WHERE ' + whereclause)
                else:
                    cur.execute(str)
            return cur.fetchall()

    def deleteBoughtTicket(self):
        # This would be trigerred if:
        # 1. Data in temp table matches the events table AT ANY TIME --> Meaning after every insert into temp table.
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()

            # For every rcord in temp table, delete the same record in events

            # First, find all the duplicate values.
            sql = 'SELECT e.place, e.time, e.seat, e.price FROM events e INNER JOIN temp t ON e.place = t.place AND e.time = t.time AND e.seat = t.seat AND e.price = t.price'
            cur.execute(
                'SELECT e.place, e.time, e.seat, e.price FROM events e INNER JOIN temp t ON e.place = t.place AND e.time = t.time AND e.seat = t.seat AND e.price = t.price')

            # Second, delete those values from events
            rows = cur.fetchall()
            for row in rows:
                place = row[0]
                time = row[1]
                seat = row[2]
                price = row[3]

                sql = 'DELETE FROM events WHERE place = \"{}\" AND time = \"{}\" AND seat = \"{}\" AND price = \"{}\"'.format(
                    place, time, seat, price)
                cur.execute(sql)
                con.commit()

    def rollbackBoughtTicket(self):
        # Rollback bought ticket or almost bought ticket.
        # This triggered when customer click :
        # 1. Cancel.
        # 2. Leaving the site.
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()

            # First, find all values in temp.
            sql = 'SELECT * FROM temp'
            cur.execute(sql)

            # Second, insert those values BACK to the events table
            rows = cur.fetchall()
            for row in rows:
                place = row[0]
                time = row[1]
                seat = row[2]
                price = row[3]

                sql = 'INSERT INTO events (place, time, seat, price) VALUES ({},{},{},{})'.format('\"' + place + '\"',
                                                                                                  '\"' + time + '\"',
                                                                                                  '\"' + seat + '\"',
                                                                                                  price)
                cur.execute(sql)
                con.commit()

    def dropTemp(self):
        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()

            sqls = ['DELETE FROM temp', ]
            for sql in sqls:
                cur.execute(sql)

    def checkCountEventTable(self):
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()
            sql = 'SELECT COUNT(*) FROM events'
            cur.execute(sql)
            rows = cur.fetchone()

            return rows[0]

    def insertToBlockchain(self, _hash='', _prev_hash=''):
        # MUST GET THE HASH AND PREV_HASH OF THE BLOCK.

        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()

            # If _prev_hash and prev_hash on the database matched:

            # 1. Add the hash and prev_hash to the blockchain.
            sql = 'SELECT COUNT(*) FROM blockchain WHERE prev_hash = \"' + _prev_hash + '\"'
            cur.execute(sql)
            rowsCount = cur.fetchone()
            if (rowsCount[0] == 1):  # If there is a match...
                sql = 'INSERT INTO blockchain(hash, prev_hash) VALUES ({},{})'.format(_hash, _prev_hash)
            elif (_prev_hash == 0):  # If there is not a match but genesis is found..
                sql = 'INSERT INTO blockchain(hash, prev_hash) VALUES ({},0)'.format(_hash)
            elif (rowsCount[0] == 0):
                sql = 'INSERT INTO blockchain(hash, prev_hash) VALUES (0,0)'  # No blocks found, make a genesis block.
            cur.execute(sql)
            conn.commit()

    def getBlockchain(self):
        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            sql = 'SELECT * FROM BLOCKCHAIN'
            cur.execute(sql)
            return cur.fetchall()

    def getCountBlockchain(self):
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()
            sql = 'SELECT COUNT(*) FROM blockchain'
            cur.execute(sql)
            rows = cur.fetchone()

            return rows[0]

    # Connect this with Blockchain.
    # Pass a list of blocks from here to blockchain
    # Pass back the list from blockchain to here.
    # Let's just assume all the blockchain are not COMPROMISED!
    def testBlockchain(self, place='', time='', seat='', price=0, _hash='', _prevH=''):
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()
            # Make the genesis block.
            sql = 'INSERT INTO blockchain VALUES ({},{})'.format('\"' + _hash + '\"', '\"' + _prevH + '\"')
            cur.execute(sql)
            con.commit()


    """
    Admin Database Operations
    """
    def admin_get_users(self):
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM users")
            return cur.fetchall()

    def admin_get_events(self):
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM events")
            return cur.fetchall()

    def admin_delete_event(self, ID):
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()
            cur.execute("DELETE FROM events WHERE ID=:ID", {"ID": ID})
            con.commit()

    def admin_add_event(self, place, time, seat, price):
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()
            cur.execute("INSERT INTO events(place, time, seat, price) VALUES (?,?,?,?)", (place, time, seat, price))
            con.commit()


if __name__ == "__main__":
    mySql = mySql()

    # mySql.runSQL()

    place = "Event 1"
    time = "11-10-2019 11:43pm"
    seat = "E9"
    price = "10923"
    mySql.insertData(place, time, seat, price)

    mySql.select_ticket()
