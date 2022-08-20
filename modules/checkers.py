import re

from kivy.animation import Animation
from kivy.garden.iconfonts import icon

from main import ScreenManagement
from modules.dbactions import closeDatabaseConnection, connectToDatabase


def checkDataCorrectness(login, password, errorBox, repeatPassword=None, fullName=None):
    """
    Checks whether data provided by user matches all patterns. If 'repeatPassword' is provided the function will
    check additional patterns for registering an account and then check whether login is already in use.

    Params
    ------------------
    login: string
        User's e-mail
    password: string
        User's password
    errorBox: ObjectProperty
        Object of errorBox; the container handling all error messages and showing them
    repeatPassword: string
        Repeated password in registration form. If not empty checks whether both password match
    fullName: string:
        Full name of new user. Needed for greeting user and to create his profile properly
    Return value
    ------------------
    False if:
        E-Mail does not meet requirments of regex
        Password is not in range of 8-64 characters long
        [Only for logging in] Login or password is incorrect
        [Only for registering] Password and repeated password do not match
        [Only for registering] Full name of user is not provided to function
        [Only for registering] Account already registered for this E-mail
    True if:
        Every pattern has been met and account info could have been retrieved or inserted from/to database
    """
    EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

    if not EMAIL_REGEX.fullmatch(login):
        ErrorBox().showError(errorBox=errorBox, reason="E-mail address is incorrect")
        return False
    elif len(password) < 8 or len(password) > 64:
        ErrorBox().showError(errorBox, "Password should be 8-64 characters long")
        return False
    elif repeatPassword is not None:
        if password != repeatPassword:
            ErrorBox().showError(errorBox=errorBox, reason="Passwords do not match")
            return False
        elif len(fullName) < 1:
            ErrorBox().showError(errorBox=errorBox, reason="You did not provide your full name")
            return False
        else:
            if doesAccountExist(login, errorBox) is False:
                db, cursor = connectToDatabase()
                cursor.execute("INSERT INTO accounts VALUES (null, %s, %s, %s, 0, NOW(), NOW())", ([login, password,
                                                                                                    fullName]))
                db.commit()
                print("SUCCESS. CREATED ACCOUNT. USER SHOULD LOG IN")
                return True
            else:
                ErrorBox().showError(errorBox=errorBox, reason="Account already registered for this E-mail")
                return False
    else:
        checkCredintialsInDatabase(login, password, errorBox)
        return True


def doesAccountExist(login, errorBox):
    """
    Checks whether provided E-Mail was ever used to register another account

    Params
    ------------------
    login: string
        E-Mail address of user
    errorBox: ObjectProperty
        Object of errorBox; the container handling all error messages and showing them

    Return value
    ------------------
    True: bool
        Account not found; login available
    False: bool
        Account found; can't create another one with the same login
    """
    db, cursor = connectToDatabase()
    print(cursor)
    cursor.execute("SELECT * FROM accounts WHERE login=%s", (login,))
    results = cursor.fetchone()
    print(cursor)
    print(results)
    if results is None:
        disableErrorMsg(errorBox)
        closeDatabaseConnection(db, cursor)
        return False
    else:
        closeDatabaseConnection(db, cursor)
        return True


def checkCredintialsInDatabase(login, password, errorBox):
    """
    Looks up in database for existing account with given data to log in user into service.

    Params
    ------------------
    login: string
        E-Mail address of user
    password: string
        Password of user
    errorBox: ObjectProperty
        Object of errorBox; the container handling all error messages and showing them

    Return value
    ------------------
    True: bool
        Credintials are valid; loggin in
    False: bool
        Invalid credintials; error shown
    """
    db, cursor = connectToDatabase()
    print(cursor)
    cursor.execute("SELECT * FROM accounts WHERE login=%s AND password=%s;", (login, password))
    results = cursor.fetchone()
    print(cursor)
    print(results)
    if results is not None:
        ScreenManagement().transition
        ScreenManagement().current = 'main_screen'
        disableErrorMsg(errorBox)
        print("SUCCESS. LOGGED IN. SHOULD SHOW MAIN SCREEN")
    else:
        ErrorBox().showError(errorBox, "Could not log in. Ensure the credentials match")
        closeDatabaseConnection(db, cursor)
        return False
    closeDatabaseConnection(db, cursor)
    return True


def disableErrorMsg(errorBox):
    """
    Disables error message box, called whenever all patterns in checking function are matched.
    Includes smooth animation of disabling

    Params
    --------------------
    errorBox: ObjectProperty
        Object of errorBox; the container handling all error messages and showing them
    """
    anim1 = Animation(opacity=0, duration=0.7)
    anim1.start(errorBox)
    anim1.bind(on_complete=ErrorBox().errorAnimationComplete)


class ErrorBox:
    errorBox = None

    def errorAnimationComplete(self, instance):
        self.errorBox.disabled = True

    def showError(self, errorBox, reason):
        errorBox.disabled = False
        errorBox.text = ("[size=40]%s[/size]\n" + reason) % icon('zmdi-alert-circle')
        anim1 = Animation(opacity=1, duration=0.7)
        anim1.start(errorBox)
        self.errorBox = errorBox
