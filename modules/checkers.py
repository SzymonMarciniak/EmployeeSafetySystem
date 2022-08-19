import re

from kivy.animation import Animation
from kivy.garden.iconfonts import icon

from main import ScreenManagement
from modules.dbactions import closeDatabaseConnection, connectToDatabase


def checkDataCorrectness(login, password, errorBox, repeatPassword=None, fullName=None):
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
    else:
        checkCredintialsInDatabase(login, password, errorBox)
        return True


def doesAccountExist(login, errorBox):
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
        return False
    closeDatabaseConnection(db, cursor)
    return True


def disableErrorMsg(errorBox):
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
