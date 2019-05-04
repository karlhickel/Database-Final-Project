# This class creates a SQLite OR MySQL connection and allows for easy use
# of SQLite in Python given a database
import sqlite3
from sqlite3 import OperationalError
import mysql.connector
from mysql.connector import errorcode
import pandas as pd
import os


class SQLManager:
    # Constructor
    # TODO replace config with actual variables
    def __init__(self, config, db, host=None, user=None, password=None, debug=None):
        self.conn = None
        self.cursor = None
        self.config = config
        if debug == None:
            self.debug = False
        else:
            self.debug = debug
        # Set connection to give database
        if config == "sqlite":
            self.conn = sqlite3.connect(db)
            self.cursor = self.conn.cursor()
            print("Connected to SQLite3")
        else:
            if db[-3:] == ".db":
                db = db[:-3]
            try:
                if host == None:
                    host = '127.0.0.1'
                if user == None:
                    user = "root"
                if password == None:
                    password = "password"
                self.conn = mysql.connector.connect(user=user, password=password, host=host)
                self.cursor = self.conn.cursor()
                self.cursor.execute("CREATE DATABASE IF NOT EXISTS " + db)
                self.cursor.execute("USE " + db)
                print("Connected to MySQL\nDATABASE:", db)
            except mysql.connector.Error as err:
                print(err)

    # Deconstructor
    def __del__(self):
        if self.conn != None:
            self.close()

    # Close db conn
    def close(self):
        self.conn.close()

    # Query SQL data to pandas df
    def query(self, query, commandNo=None, display=None):
        # if query is a sql file
        if query[len(query)-4:] == ".sql":
            # https://stackoverflow.com/questions/19472922/reading-external-sql-script-in-python
            # Open and read the file as a single buffer
            fd = open(query, 'r')
            sqlFile = fd.read()
            fd.close()

            # all SQL commands (split on ';')
            sqlCommands = sqlFile.split(';')

            # remove commented commands
            temp = sqlCommands
            sqlCommands = []
            for index, command in enumerate(temp):
                command = command.strip()
                if not command.startswith("--") and not command.startswith("\n--") and not command == '':
                    sqlCommands.append(command)

            if commandNo == None:
                # Execute every command from the input file
                for index, command in enumerate(sqlCommands):
                    # This will skip and report errors
                    # For example, if the tables do not yet exist, this will skip over
                    # the DROP TABLE commands
                    return self.runSQL(command, display=display)
            else:
                return self.runSQL(sqlCommands[commandNo], display=display)
        else:
            return self.runSQL(query, display=display)

    def runSQL(self, command, display=None):
        try:
            df = pd.read_sql_query(command, self.conn)
            if display == True:
                print(df)
            return df
        except OperationalError as msg:
            print("Command skipped: ", msg)

    def execute(self, commands, commandNo=None):
        if commands[len(commands)-4:] == ".sql":
            # https://stackoverflow.com/questions/19472922/reading-external-sql-script-in-python
            # Open and read the file as a single buffer
            fd = open(commands, 'r')
            sqlFile = fd.read()
            fd.close()

            # all SQL commands (split on ';')
            sqlCommands = sqlFile.split(';')

            # remove commented commands
            temp = sqlCommands
            sqlCommands = []
            for index, command in enumerate(temp):
                command = command.strip()
                if not command.startswith("--") and not command.startswith("\n--") and not command == '':
                    sqlCommands.append(command)

            if self.debug:
                for index, command in enumerate(sqlCommands):
                    print("Command", index,":", command)

            if commandNo == None:
                # Execute every command from the input file
                for command in sqlCommands:
                    # dont run empty lines as commands
                    if len(command.strip()) > 0:
                        if not command.startswith("--"):
                            self.cursor.execute(command)
                            self.conn.commit()
            else:
                # Execute a command given its index
                self.cursor.execute(sqlCommands[commandNo])
                self.conn.commit()
        # if just string SQL statement
        else:
            self.cursor.execute(commands)
            self.conn.commit()

    # call stored procedure
    def callproc(self, proc, columns, *args, isDML=None, display=None):
        argv = []
        for arg in args:
            argv.append(arg)

        self.cursor.callproc(proc, argv)
        for i in self.cursor.stored_results():
            results = i.fetchall()
        if not isDML:
            df = pd.DataFrame(results, columns=columns)

            if display:
                print(df)

            return df
        else:
            return

    # Create table from csv
    def readCSV(self, csv, name=None):
        df = pd.read_csv(csv)

        # if table name is given, make a table
        if name != None:
            df.to_sql(name, self.conn)

        return df

    # Drop a given table
    def dropTable(self, table):
        try:
            statement = "DROP TABLE " + table
            self.cursor.execute(statement)
            print("Table", table, "dropped.")
        except:
            table = "'" + table + "'"
            print("Table", table, "not found.")

    # Drop a given Database
    def dropDB(self, db):
        if self.config == "sqlite":
            if db[len(db)-3:] != ".db":
                try:
                    os.remove(db+".db")
                except Exception as err:
                    print(err)
            else:
                os.remove(db)
                print("DB", db, "deleted.")
        else:
            try:
                if db[-3:] == ".db":
                    db = db[:-3]
                self.cursor.execute("DROP DATABASE " + db)
                print("Database", db, "dropped.")
            except:
                table = "'" + db + "'"
                print("Database", db, "not found.")

    # Clear all DB
    def dropAll(self):
        # Check for SQLite databases
        for filename in os.listdir(os.getcwd()):
            if filename[-3:] == ".db":
                os.remove(filename)
                print("Database", filename, "dropped.")

    # Accessor for cursor
    def getCursor(self):
        return self.cursor

    # Accessor for connection
    def getConn(self):
        return self.conn
