import mysql.connector
from mysql.connector import errorcode, MySQLConnection, CMySQLConnection
from mysql.connector.cursor_cext import CMySQLCursor

from modules import globals
from modules.globals import userID


def connectToDatabase(firstConnect=False):
    """
    Connect to the database with given data

    Parameters
    ---------------

    firstConnect: bool
        Indicates whether the connection is the first one to be made. First connections run additional
        table creation queries and validate the process.

    Raises
    ---------------
    db: CMySQLConnection
        The access was denied, login and/or password does not match

    db: CMySQLConnection
        The connection was not successful. Error reason is provided

    cursor: CMySQLCursor
        Table creation queries could not be processed. The reason for error is provided

    Returns
    ----------------
    db: CMySQLConnection
        Object of MySQL database connection. Opened and operating

    cursor: CMySQLCursor
        Object of MySQL database cursor. Needed for query processing
    """
    try:
        db = mysql.connector.connect(host='localhost', user='root', password='', database="employee_safety_system")
    except mysql.connector.Error as error:
        if error.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            raise ConnectionError(
                "Connection was not successful. The access was denied. Recheck the login and password.")
        else:
            raise ConnectionError("Cannot establish connection. Reason: %s" % error)
    else:
        cursor = db.cursor(buffered=True)
        if firstConnect:
            try:
                cursor.execute(
                    "CREATE TABLE IF NOT EXISTS accounts (id INT NOT NULL auto_increment PRIMARY KEY, "
                    "login VARCHAR(128), password VARCHAR(64), name VARCHAR(128), "
                    "type INT, creationDate INT, lastLogin INT);")
                cursor.execute(
                    "CREATE TABLE IF NOT EXISTS pswdResets (id INT NOT NULL auto_increment PRIMARY KEY, userID INT "
                    "NOT NULL, code VARCHAR(8), initDate INT, expDate INT, USED INT);")
                cursor.execute(
                    "CREATE TABLE IF NOT EXISTS workplaces (id INT NOT NULL auto_increment PRIMARY KEY, userID INT "
                    "NOT NULL, name VARCHAR(64), position INT, state_activation BOOLEAN, state_notifications BOOLEAN);"
                )
            except mysql.connector.Error as error:
                raise TimeoutError("Cannot process query. Reason: %s" % error)
        return db, cursor


def closeDatabaseConnection(db: CMySQLConnection, cursor: CMySQLCursor):
    """
    Closes connection to the database. Ensures closing of both handles; db and cursor

    Parameters
    -----------------
    db: CMySQLConnection
        Handle of database
    cursor: CMySQLCursor
        Handle of cursor - executive power

    Raises
    -----------------
    db: CMySQLConnection, cursor: CMySQLCursor
        Closing the connection not possible. Maybe the connection was never opened?
    """
    try:
        db.close()
        cursor.close()
    except mysql.connector.Error as error:
        raise Exception("Couldn't close connection. Maybe it is closed already or was never opened? Reason: %s" % error)


def checkIsEmailInDatabase(recoveryEmail):
    """
    Checks whether the provided E-mail address is located within the database.

    Return value
    ---------------------
    True: bool
        If address was found
    False: bool
        Otherwise
    """
    db, cursor = connectToDatabase()
    cursor.execute("SELECT * FROM accounts WHERE login=%s", (recoveryEmail,))
    results = cursor.fetchone()
    closeDatabaseConnection(db, cursor)
    if results is not None:
        return True
    else:
        return False


def setNewPassword(password):
    db, cursor = connectToDatabase()
    cursor.execute("UPDATE accounts SET password=%s WHERE id=%s", (password, globals.userID))
    db.commit()
    closeDatabaseConnection(db, cursor)


def insertNewWorkplace(name, notifications_status):
    db, cursor = connectToDatabase()
    cursor.execute("INSERT INTO workplaces VALUES(null, %s, %s, 1, 0, %s);", (globals.userID, name, notifications_status))
    db.commit()