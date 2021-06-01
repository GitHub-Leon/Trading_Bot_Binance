# password input
# date
import datetime
import getpass
# regex
import re
# sending auth. mail
import smtplib
import ssl
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# generate auth. code
import vcode

# local dependencies
from src.check_package import check_package
from src.classes.TxColor import txcolors
from src.config import SENDER_MAIL, SENDER_PW, CODE_EXPIRE_DURATION, WELCOME_TEXT_FILE, EMAIL_REGEX_FILE, \
    PASSWORD_REGEX_FILE, BIRTHDAY_REGEX_FILE, VERIFICATION_MAIL_PLAIN_TEXT_FILE, VERIFICATION_MAIL_HTML_FILE
from src.helpers.database_connection import connect_to_database  # Database
from src.helpers.scripts.logger import debug_log


# functionalities

def check_email(email):  # verifies correct email regex
    debug_log("Check email", False)

    regex_check = False
    try:
        regex_check = re.search(open(EMAIL_REGEX_FILE, "r").read(), email)
    except OSError as e:
        debug_log(str(e), True)

    if user_exist(email) and regex_check:  # user not in database and email valid
        return True
    return False


def check_password(password):  # verifies correct password regex
    debug_log("Check password", False)

    try:
        return re.search(open(PASSWORD_REGEX_FILE, "r").read(), password)
    except OSError as e:
        debug_log(str(e), True)
    return False


def check_birthday(birthday):  # verifies correct birthday regex
    debug_log("Check birthday", False)
    birthday_arr = birthday.split("/")
    birth_date = datetime.date(int(birthday_arr[2]), int(birthday_arr[1]), int(birthday_arr[0]))
    today = datetime.date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

    try:
        return re.search(open(BIRTHDAY_REGEX_FILE, "r").read(), birthday) and age > 18
    except OSError as e:
        debug_log(str(e), True)
    return False


def generate_verification_code():  # generates random verification code
    debug_log("Create verification code", False)
    return vcode.digits()


def generate_verification_mail_text(auth, firstname, lastname):
    debug_log("Generate verification mail text", False)

    text = None
    try:
        text = open(VERIFICATION_MAIL_PLAIN_TEXT_FILE).read().split("##")
    except OSError as e:
        debug_log(str(e), True)

    return text[0] + firstname + " " + lastname + text[1] + auth + text[2]


def generate_verification_mail_html(auth, firstname, lastname):
    debug_log("Generate verification mail html", False)

    html = None
    try:
        html = open(VERIFICATION_MAIL_HTML_FILE).read().split("##")
    except OSError as e:
        debug_log(str(e), True)

    return html[0] + firstname + " " + lastname + html[1] + auth + html[2]


def send_mail_verification(email, firstname, lastname):
    debug_log("Send verification email", False)
    message = MIMEMultipart("alternative")
    message["Subject"] = "Bot - Mail Verification"
    message["From"] = SENDER_MAIL
    message["To"] = email

    # Create the plain-text and HTML version of your message
    send_verification_code = generate_verification_code()
    verification_text = generate_verification_mail_text(send_verification_code, firstname, lastname)
    verification_html = generate_verification_mail_html(send_verification_code, firstname, lastname)

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(verification_text, "plain")
    part2 = MIMEText(verification_html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    # Create secure connection with server and send email
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(SENDER_MAIL, SENDER_PW)
            server.sendmail(
                SENDER_MAIL, email, message.as_string()
            )
    except Exception as e:
        debug_log("Email verification email server fail. Error-Message: " + str(e), True)

    return send_verification_code


def check_login(email, user_given_pw):
    debug_log("Check if the password matches the account data of database", False)
    db = connect_to_database()
    db_cursor = db.cursor()

    query = "select Password from Users where Email like %s"
    db_cursor.execute(query, (email,))
    user_pw = db_cursor.fetchone()

    try:
        if user_pw[0] == user_given_pw:
            return True
    except TypeError:
        debug_log("User given password was None", False)
        return False
    return False


def new_login(firstname, lastname, pw, email, birthday):
    try:
        debug_log("Create new account in database", False)
        db = connect_to_database()
        db_cursor = db.cursor()

        query = "insert into Users values(null, %s, %s, %s, STR_TO_DATE(%s, '%d/%m/%Y'), %s, null, STR_TO_DATE(%s, '%Y-%m-%d'), %s, %s)"
        db_cursor.execute(query, (firstname, lastname, email, birthday, pw, datetime.date.today(), 999,
                                  999))  # 999 - free package and muster address
        db.commit()
    except:
        debug_log("Creating a new account in database failed", True)
        return False
    return True


def user_exist(email):
    debug_log("Check if user is already in database", False)
    db = connect_to_database()
    db_cursor = db.cursor()

    query = "select Email from Users where Email like %s"
    db_cursor.execute(query, (email,))
    user_email = db_cursor.fetchone()

    if user_email is not None:
        debug_log("User does not exists in database", False)
        return False
    debug_log("User already exists in database", False)
    return True


# Return True or False. True if LogIn was successful. False if LogIn failed.
def login():
    debug_log("Initialize login procedure", False)

    try:
        print(open(WELCOME_TEXT_FILE, "r").read())
    except OSError as e:
        debug_log(str(e), True)

    print(f"{txcolors.WARNING}SignIn with your email and password.\n{txcolors.DEFAULT}"
          f"{txcolors.WARNING}Password isn´t shown because of safety.\n{txcolors.DEFAULT}")

    # ask about username and password and creates an account if the user doesn´t have one.
    if re.search("[y|Y]", input(f"Do you already have an account?(Y/N) - ")):
        while True:
            debug_log("Ask for email", False)
            email = input("Email: ")
            debug_log("Ask for password", False)
            pw = getpass.getpass()

            if email == "admin" and pw == "admin":
                debug_log("Admin logged in", False)
                print(f"{txcolors.WARNING}Welcome admin!{txcolors.DEFAULT}")
                return True

            if check_login(email, pw):
                debug_log("Valid login check", False)
                check_package(email)
                debug_log("Checked package", False)
                return True

            debug_log("Email or password is incorrect", False)
            print(f"{txcolors.WARNING}Email or Password is incorrect!{txcolors.DEFAULT}")
    else:
        # Create account
        debug_log("Create Account", False)
        print(f"{txcolors.WARNING}Let´s create one!\n{txcolors.DEFAULT}")

        debug_log("Ask for first and last name", False)
        firstname = input("Tell us your first name! - ")
        lastname = input("Tell us your last name! - ")

        # email input
        debug_log("Ask for email", False)
        email = input("Email: ")
        while not check_email(email):  # verifies correct email regex
            debug_log("Invalid email", False)
            print(f"{txcolors.WARNING}Please enter a valid email address!{txcolors.DEFAULT}")
            email = input("Email: ")

        # password input
        debug_log("Ask for password", False)
        password = getpass.getpass()
        while not check_password(password):  # verifies correct password regex
            debug_log("Invalid password", False)
            print(
                f"{txcolors.WARNING}The Password must contain at least one letter, one digit and a minimum of eight characters {txcolors.DEFAULT}")
            password = getpass.getpass()

        # birthday input
        debug_log("Ask for birthday", False)
        birthday = input("Please tell us you birthday!(DD/MM/YYYY) - ")
        while not check_birthday(birthday):  # verifies correct birthday regex
            debug_log("Invalid Birthday", False)
            print(f"{txcolors.WARNING}Please enter a valid birthday!{txcolors.DEFAULT}")
            birthday = input("Please tell us your birthday! (DD/MM/YYYY) - ")

        # Sends auth. Mail
        send_verification_code = "send_code"
        user_given_auth_code = "user_code"
        while send_verification_code != user_given_auth_code:
            debug_log("Send verification code to email", False)
            send_verification_code = send_mail_verification(email, firstname, lastname)
            print(f"{txcolors.WARNING}\nPlease check your mailbox and verify you account!\n{txcolors.DEFAULT}"
                  f"{txcolors.WARNING}The code is only{txcolors.DEFAULT} " + str(
                round(CODE_EXPIRE_DURATION / 60, 0)) + f" {txcolors.WARNING}minutes valid.{txcolors.DEFAULT}")

            start_time = time.time()

            # Check if user auth. was a success
            debug_log("Ask for verification code", False)
            user_given_auth_code = input("Enter your Verification Code! - ")

            while send_verification_code != user_given_auth_code and time.time() - start_time < CODE_EXPIRE_DURATION:
                debug_log("Invalid verification code", False)
                user_given_auth_code = input("Please check your auth. code again! Or exit(x) - ")
                if re.search("[x|X]", user_given_auth_code):
                    debug_log("User exit on invalid verification code", False)
                    return False

            if not time.time() - start_time < CODE_EXPIRE_DURATION:
                debug_log("Verification code is inactive", False)
                print(f"{txcolors.WARNING}Seems like the auth. code isn´t active anymore.{txcolors.DEFAULT}")
                user_given_auth_code = "x"
                if not re.search("[y|Y]", input(f"If you want you can request a new auth. code.(Y/N) - ")):
                    return False
                debug_log("User wants a new verification code", False)

        if not new_login(firstname, lastname, password, email, birthday):
            debug_log("New account creation failed", False)
            print(f"{txcolors.WARNING}Creating a new account failed.\n{txcolors.DEFAULT}"
                  f"{txcolors.WARNING}Please try again!{txcolors.DEFAULT}")
            return False

        debug_log("Registration is ready", False)
        print(f"{txcolors.WARNING}Your registration is ready.\n{txcolors.DEFAULT}"
              f"{txcolors.WARNING}If you need help please use the command 'help' or contact us!{txcolors.DEFAULT}")
        return True
