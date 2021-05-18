# password input
import getpass

# regex
import re

# sending auth. mail
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# generate auth. code
import vcode

# date
import datetime
import time

# async func
import asyncio

from .helpers import parameters

# Load arguments then parse settings
args = parameters.parse_args()

DEFAULT_CONFIG_MAIL_FILE = 'config_mail.yml'

config_file = args.config if args.config else DEFAULT_CONFIG_MAIL_FILE
parsed_config = parameters.load_config(config_file)

# Load vars
SENDER_MAIL = parsed_config['auth-options']['SENDER_MAIL']
SENDER_PW = parsed_config['auth-options']['SENDER_MAIL_PW']
CODE_EXPIRE_DURATION = parsed_config['auth-options']['CODE_EXPIRE_TIME']


# functionalities

def check_email(email):  # verifies correct email regex
    return re.search(open("./src/helpers/email_regex.txt", "r").read(), email)


def check_password(password):  # verifies correct password regex
    return re.search(open("./src/helpers/password_regex.txt", "r").read(), password)


def check_birthday(birthday):  # verifies correct birthday regex
    birthday_arr = birthday.split("/")
    birth_date = datetime.date(int(birthday_arr[2]), int(birthday_arr[1]), int(birthday_arr[0]))
    today = datetime.date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return re.search(open("./src/helpers/birthday_regex.txt", "r").read(), birthday) and age > 18


def generate_verification_code():  # generates random verification code
    return vcode.digits()


def generate_verification_mail_text(auth, firstname, lastname):
    text = open("./src/helpers/mail_verification_plain.txt").read().split("##")
    return text[0] + firstname + " " + lastname + text[1] + auth + text[2]


def generate_verification_mail_html(auth, firstname, lastname):
    html = open("./src/helpers/mail_verification_html.html").read().split("##")
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


# Return True or False. True if LogIn was successful. False if LogIn failed.

def login():
    print(open("./src/helpers/welcome.txt", "r").read())

    print("SignIn with your email and password.\n"
          "Password isn´t shown because of safety.\n")

    # ask about username and password and creates an account if the user doesn´t have one.
    if re.search("[y|Y]", input("Do you already have an account?(Y/N) - ")):
        email = input("Email: ")
        pw = getpass.getpass()

        if email == "admin" and pw == "admin":
            print("Welcome admin!")
            return True
    else:
        # Create account
        print("Let´s create one!\n")

        firstname = input("Tell us your first name! - ")
        lastname = input("Tell us your last name! - ")

        # email input
        email = input("Email: ")
        while not check_email(email):  # verifies correct email regex
            print("Please enter a valid email address!")
            email = input("email: ")

        # password input
        password = getpass.getpass()
        while not check_password(password):  # verifies correct password regex
            print("The Password must contain at least one letter, one digit and a minimum of eight characters ")
            password = getpass.getpass()

        # birthday input
        birthday = input("Please tell us you birthday!(DD/MM/YYYY) - ")
        while not check_birthday(birthday):  # verifies correct birthday regex
            print("Please enter a valid birthday!")
            birthday = input("Please tell us your birthday! (DD/MM/YYYY) - ")

        # Sends auth. Mail
        send_verification_code = "send_code"
        user_given_auth_code = "user_code"
        while send_verification_code != user_given_auth_code:
            send_verification_code = send_mail_verification(email, firstname, lastname)
            print("\nPlease check your mailbox and verify you account!\n"
                  "The code is only " + str(round(CODE_EXPIRE_DURATION / 60, 0)) + " minutes valid.")

            start_time = time.time()

            # Check if user auth. was a success
            user_given_auth_code = input("Enter your Verification Code! - ")

            while send_verification_code != user_given_auth_code and time.time() - start_time < CODE_EXPIRE_DURATION:
                user_given_auth_code = input("Please check your auth. code again! Or exit(x) - ")
                if re.search("[x|X]", user_given_auth_code):
                    return False

            if not time.time() - start_time < CODE_EXPIRE_DURATION:
                print("Seems like the auth. code isn´t active anymore.")
                user_given_auth_code = "x"
                if not re.search("[y|Y]", input("If you want you can request a new auth. code.(Y/N) - ")):
                    return False

        print("Your registration is ready.\n"
              "If you need help please use the command 'help' or contact us!")
        return True
