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

# Local dependencies
from src.check_package import check_package
from src.config import SENDER_MAIL, SENDER_PW, CODE_EXPIRE_DURATION, WELCOME_TEXT_FILE, EMAIL_REGEX_FILE, \
    PASSWORD_REGEX_FILE, BIRTHDAY_REGEX_FILE, VERIFICATION_MAIL_PLAIN_TEXT_FILE, VERIFICATION_MAIL_HTML_FILE
from src.helpers.database_connection import connect_to_database  # Database
from src.classes.TxColor import txcolors


# functionalities

def check_email(email):  # verifies correct email regex
    regex_check = re.search(open(EMAIL_REGEX_FILE, "r").read(), email)

    if user_exist(email) and regex_check:  # user not in database and email valid
        return True
    return False


def check_password(password):  # verifies correct password regex
    return re.search(open(PASSWORD_REGEX_FILE, "r").read(), password)


def check_birthday(birthday):  # verifies correct birthday regex
    birthday_arr = birthday.split("/")
    birth_date = datetime.date(int(birthday_arr[2]), int(birthday_arr[1]), int(birthday_arr[0]))
    today = datetime.date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return re.search(open(BIRTHDAY_REGEX_FILE, "r").read(), birthday) and age > 18


def generate_verification_code():  # generates random verification code
    return vcode.digits()


def generate_verification_mail_text(auth, firstname, lastname):
    text = open(VERIFICATION_MAIL_PLAIN_TEXT_FILE).read().split("##")
    return text[0] + firstname + " " + lastname + text[1] + auth + text[2]


def generate_verification_mail_html(auth, firstname, lastname):
    html = open(VERIFICATION_MAIL_HTML_FILE).read().split("##")
    return html[0] + firstname + " " + lastname + html[1] + auth + html[2]


def send_mail_verification(email, firstname, lastname):
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
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(SENDER_MAIL, SENDER_PW)
        server.sendmail(
            SENDER_MAIL, email, message.as_string()
        )

    return send_verification_code


def check_login(email, user_given_pw):
    db = connect_to_database()
    db_cursor = db.cursor()

    query = "select Password from Users where Email like %s"
    db_cursor.execute(query, (email,))
    user_pw = db_cursor.fetchone()

    if user_pw[0] == user_given_pw:
        return True
    return False


def new_login(firstname, lastname, pw, email, birthday):
    try:
        db = connect_to_database()
        db_cursor = db.cursor()

        query = "insert into Users values(null, %s, %s, %s, STR_TO_DATE(%s, '%d/%m/%Y'), %s, null, STR_TO_DATE(%s, '%Y-%m-%d'), %s, %s)"
        db_cursor.execute(query, (firstname, lastname, email, birthday, pw, datetime.date.today(), 999,
                                  999))  # 999 - free package and muster address
        db.commit()
    except:
        return False
    return True


def user_exist(email):
    db = connect_to_database()
    db_cursor = db.cursor()

    query = "select Email from Users where Email like %s"
    db_cursor.execute(query, (email,))
    user_email = db_cursor.fetchone()

    if user_email != None:
        return False
    return True


# Return True or False. True if LogIn was successful. False if LogIn failed.

def login():
    print(open(WELCOME_TEXT_FILE, "r").read())

    print(f"{txcolors.WARNING}SignIn with your email and password.\n{txcolors.DEFAULT}"
          f"{txcolors.WARNING}Password isn´t shown because of safety.\n{txcolors.DEFAULT}")

    # ask about username and password and creates an account if the user doesn´t have one.
    if re.search("[y|Y]", input(f"Do you already have an account?(Y/N) - ")):
        while True:
            email = input(f"Email: ")
            pw = getpass.getpass()

            if email == "admin" and pw == "admin":
                print(f"{txcolors.WARNING}Welcome admin!{txcolors.DEFAULT}")
                return True

            if check_login(email, pw):
                check_package(email)
                return True
            print(f"{txcolors.WARNING}Email or Password is incorrect!{txcolors.DEFAULT}")
    else:
        # Create account
        print(f"{txcolors.WARNING}Let´s create one!\n{txcolors.DEFAULT}")

        firstname = input(f"Tell us your first name! - ")
        lastname = input(f"Tell us your last name! - ")

        # email input
        email = input(f"Email: ")
        while not check_email(email):  # verifies correct email regex
            print(f"{txcolors.WARNING}Please enter a valid email address!{txcolors.DEFAULT}")
            email = input(f"Email: ")

        # password input
        password = getpass.getpass()
        while not check_password(password):  # verifies correct password regex
            print(f"{txcolors.WARNING}The Password must contain at least one letter, one digit and a minimum of eight characters {txcolors.DEFAULT}")
            password = getpass.getpass()

        # birthday input
        birthday = input(f"Please tell us you birthday!(DD/MM/YYYY) - ")
        while not check_birthday(birthday):  # verifies correct birthday regex
            print(f"{txcolors.WARNING}Please enter a valid birthday!{txcolors.DEFAULT}")
            birthday = input(f"Please tell us your birthday! (DD/MM/YYYY) - ")

        # Sends auth. Mail
        send_verification_code = "send_code"
        user_given_auth_code = "user_code"
        while send_verification_code != user_given_auth_code:
            send_verification_code = send_mail_verification(email, firstname, lastname)
            print(f"{txcolors.WARNING}\nPlease check your mailbox and verify you account!\n{txcolors.DEFAULT}"
                  f"{txcolors.WARNING}The code is only{txcolors.DEFAULT} " + str(round(CODE_EXPIRE_DURATION / 60, 0)) + f" {txcolors.WARNING}minutes valid.{txcolors.DEFAULT}")

            start_time = time.time()

            # Check if user auth. was a success
            user_given_auth_code = input(f"Enter your Verification Code! - ")

            while send_verification_code != user_given_auth_code and time.time() - start_time < CODE_EXPIRE_DURATION:
                user_given_auth_code = input(f"Please check your auth. code again! Or exit(x) - ")
                if re.search("[x|X]", user_given_auth_code):
                    return False

            if not time.time() - start_time < CODE_EXPIRE_DURATION:
                print(f"{txcolors.WARNING}Seems like the auth. code isn´t active anymore.{txcolors.DEFAULT}")
                user_given_auth_code = "x"
                if not re.search("[y|Y]", input(f"If you want you can request a new auth. code.(Y/N) - ")):
                    return False

        if not new_login(firstname, lastname, password, email, birthday):
            print(f"{txcolors.WARNING}Creating a new account failed.\n{txcolors.DEFAULT}"
                  f"{txcolors.WARNING}Please try again!{txcolors.DEFAULT}")
            return False
        print(f"{txcolors.WARNING}Your registration is ready.\n{txcolors.DEFAULT}"
              f"{txcolors.WARNING}If you need help please use the command 'help' or contact us!{txcolors.DEFAULT}")
        return True
