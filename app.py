from flask import Flask, jsonify, redirect, send_file, request
from flask_cors import CORS
import bill_tracker_core as core
import db_interactions
import email_sender
import logging
import random
import string

app = Flask(__name__)
logger = logging.getLogger()
CORS(app)
# Get config from core
CONFIG = core.CONFIG
database = db_interactions.DBAgent("bill_app_db")  # initialises database pool as a global variable

# example call: database.interact("INSERT INTO bills_db VALUES (1,3,'large bill text')")


# region Bill actions.
# Todo: These could be placed in Bill class, or in core file?
# Returns n in upper case
def cap(n):
    return n.upper()  # TODO remove


# Returns n with spaces between each character.
def space(n):
    return " ".join(n)  # TODO remove


# Returns the bill with given id in JSON form
def find_bill(bill_id):
    bill = core.Bill(
        "3",
        "Yet Another Sample bill",
        "This is a 3rd, different sample bill: an example, for testing purposes.",
        "1/2/2121",
        "2/1/2122",
        "inactive",
        short_desc="Different Sample Bill"
    )
    return bill.to_dict()  # TODO REMOVE


def get_top_bills():
    bill1 = core.Bill(
        "1",
        "Sample Title",
        "Sample Description of a sample bill",
        "1/1/2021",
        "1/1/2030",
        "active"
    )
    bill2 = core.Bill(
        "id_2",
        "Another Sample bill",
        "This is a different sample bill: an example. Probably for testing purposes.",
        "1/2/2121",
        "2/1/2122",
        "inactive",
        short_desc="Different Sample Bill"
    )

    return [bill1.to_dict(), bill2.to_dict()]  # TODO Change to work with top 50 bills


# endregion


# Sample private function
# We don't want private functions to be accessible from the internet, so this function should NOT be put in the actions
#   array.
def unsafe_function(n):
    # Do something that shouldn't be accessible publicly
    print("oh dear!")


# # Perform action on given bill TODO REMOVE
# @app.route('/b/<bill_id>/<action>')
# def handle_request(bill_id, action):
#     # not case-sensitive
#     action = action.lower()
#
#     # Run requested action if valid
#     if action in safe_actions:
#         result = safe_actions[action](bill_id)
#     else:
#         result = f"unknown or forbidden action: {action}"
#
#     # Construct output
#     output = {
#         "bill_id": bill_id,
#         "action": action,
#         "result": result
#     }
#
#     # Convert to json and return
#     return jsonify(output)


@app.route('/bill/<bill_id>')
def get_bill(bill_id):
    response = database.select(f"SELECT * FROM Bills WHERE billID='{bill_id}';")
    if not response:
        return jsonify({"error": "query_error"})
    return jsonify(str(response))


@app.route('/bills')
def get_bills():
    response = database.select("SELECT * FROM Bills;")
    if not response:
        return jsonify({"error": "query_error"})
    return jsonify(str(response))


@app.route('/top')
def top():
    result = get_top_bills()
    # Construct output
    output = {
        "result": result
    }

    # Convert to json and return
    return jsonify(output)


@app.route('/')
def landing_page():
    return redirect(CONFIG["default_url"])  # TODO remove


@app.route('/testdb')
def db_testing():
    # TODO REMOVE
    response = database.select("SELECT * FROM Users;")
    if response is None:
        return "None"
    else:
        return str(response)


@app.route('/login', methods=['POST'])
def login():
    """
    Log in to the application using the user's password. Checks if the email address is used, and checks the password.
    :return: Message with the user's unique token if successful, or an error message explaining why login failed.
    """
    # Get form information:
    email = request.form['email']
    password = request.form['password']
    if is_new_address(email):
        return jsonify({"error": "new_email_error"})  # Email does not correspond to a User
    # Get user from database using username, check if user is valid.
    user = fetch_user(email)  # Construct the user object
    if user.verify_password(password):
        # Send email to user address informing of new login
        email_sender.send_email(user.email, "Insight: new login", "A new device signed in to your Insight account. We'"
                                                                  "re sending you this email to make sure it was you!"
                                                                  " If it wasn't, please respond to this email to let "
                                                                  "us know!\n\n-The Insight team")
        return jsonify({"session_token": user.session_token})  # Return the session token
    # Return the session token
    return jsonify({"error": "incorrect_password_error"})  # Given wrong password


@app.route('/login_with_token', methods=['POST'])
def login_with_token():
    """
    Log in to the application using the user's token. Checks if the email address is used, and validates the token.
    :return: Message indicating the login was successful, or an error message explaining why it was not successful.
    """
    # Get form information:
    email = request.form['email']
    session_token = request.form['session_token']
    if verify_user(email, session_token):  # Verify the user using email and session token
        return jsonify({"success": "login_successful"})  # Return success message
    return jsonify({"error": "login_unsuccessful"})  # Given the wrong token


@app.route('/register', methods=['POST'])
def register():
    """
    Register new User. Creates a new User object, updates the database and returns the session token.
    :return: Session token if successful, an Error otherwise.
    """
    # Get new User details from form:
    email = request.form['email']
    password = request.form['password']  # The given password is already hashed
    notification_token = request.form['notification_token']
    postcode = request.form['postcode']
    # Check for errors:
    if type(password) is not str or not password:
        return jsonify({"error": "password_error"})
    if type(notification_token) is not str or "ExponentPushToken[" not in notification_token:
        return jsonify({"error": "notification_token_error"})
    if type(postcode) is not str or len(postcode) < 6 or len(postcode) > 8:  # Check that the postcode is valid
        return jsonify({"error": "postcode_error"})
    if not email_sender.is_valid_email(email):  # Check that the given email is a valid email address
        return jsonify({"error": "email_error"})

    if not is_new_address(email):  # Check if the given email is already in use
        return jsonify({"error": "email_in_use_error"})

    # Add new user to the database:
    new_user = core.User(email, password, notification_token, postcode, create_session_token())  # Create new user
    add_user_to_database(new_user)  # Add new User to the database
    # Send email to user's email address
    email_sender.send_email(new_user.email, "Insight: Registration", "Thanks for registering to use the Insight app!"
                                                                     "\n\n-The Insight team")
    # Return the session token
    return jsonify({"session_token": new_user.session_token})


@app.route('/message', methods=['POST'])
def send_message():
    """
    Sends an email to a member of parliament specified by the user.
    Requires user verification, MP id and the message itself.
    :return: A success message, if the email was sent successfully, otherwise an error message
    """
    # Get user info for verification
    email = request.form['email']
    session_token = request.form['session_token']
    # Get information to send email
    mp_id = request.form['mp_id']
    message = request.form['message']
    # Verify the user:
    if not verify_user(email, session_token):  # Verify the user
        return jsonify({"error": "invalid_credentials"})  # Verification unsuccessful

    mp = fetch_mp(mp_id)  # Construct and return the parliament member by following given id

    if mp:  # If the MP was successfully constructed
        try:
            email_sender.send_email(mp.email, "Insight Update!", message)  # Send the email
            return jsonify({"success": "email_sent"})  # If sent without errors, return success message
        except Exception as e:
            return jsonify({"error": "email_failed_to_send"})  # Error with mail sending

    return jsonify({"error": "mp_database_error"})  # Could not build ParliamentMember


# Deliver requested resource.
# todo: generalise so works with filetypes other than image
@app.route('/res/' + CONFIG["external_res_path"] + '/<name>')
def get_res(name):
    # print(request.mimetype)
    # todo: sort out mimetype. This might affect retrieving images in the future.
    return send_file(CONFIG["img_dir"] + name)

    # return send_file("CONFIG["img_dir"] + core.CONFIG["invalid_img"], mimetype='image/gif')


# Start of helper functions


def create_session_token() -> str:
    """
    Generate a unique token using a combination of random digits, lowercase and uppercase letters.
    :return: The unique, generated token.
    """
    token = ''.join(random.SystemRandom().choice(string.digits + string.ascii_lowercase + string.ascii_uppercase)
                    for _ in range(8))  # Use digits, lowercase and uppercase letters, length 8
    # Look if it's unique i.e. does not appear already in the db (if not repeat the process)
    if database.select(f"SELECT * FROM Users WHERE sessionToken='{token}';"):  # Check if the token is in use
        return create_session_token()  # Repeat the process until a unique token is generated
    return token  # Return the unique token


def is_new_address(email_address: str) -> bool:
    """
    Checks the database to see if the given email address is already in use.
    :param email_address: The email address to look up.
    :return: True if the email address is not being used, false otherwise.
    """
    query = database.select(f"SELECT * FROM Users WHERE email='{email_address}';")  # Get the user(s) with the given email
    if query:
        return False  # If the query returns a populated list, return False
    return True  # If the query returns an empty list return True


def add_user_to_database(user: core.User) -> None:
    """
    Add the given User to the database.
    :param user: User object
    :return: None
    """
    if not user:  # Ignore None
        return
    # The SQL statement to add the user into the Users table:
    statement = f"INSERT INTO Users (email,password,postcode,sessionToken,notificationToken) VALUES ('{user.email}','" \
                f"{user.password_hash}','{user.postcode}','{user.session_token}','{user.notification_token}');"
    database.interact(statement)  # Carry out the SQL statement
    return


def fetch_user(email_address: str) -> core.User or None:
    """
    Finds the user with the given email address, constructs and returns the User object.
    :param email_address: The email address of the user.
    :return: The constructed User object.
    """
    query = database.select(f"SELECT * FROM Users WHERE email='{email_address}';")  # Query database for the user
    user = None
    if query:
        user_info = query[0]  # Get the user information
        user = core.User(user_info[1], user_info[2], user_info[3], user_info[5], user_info[4])  # Construct user
    return user


def fetch_mp(mp_id: int) -> core.ParliamentMember or None:
    """
    Finds the member of parliament with the given ID, constructs and returns the ParliamentMember object.
    :param mp_id: The id of the MP.
    :return: The constructed ParliamentMember object.
    """
    parliament_member = None
    query = database.select(f"SELECT * FROM MP WHERE mpID='{mp_id}';")  # Query database for the member of parliament
    if query:
        mp_info = query[0]  # Extract the MP information
        parliament_member = core.ParliamentMember(mp_info[0], mp_info[3], mp_info[4], mp_info[5], mp_info[6],
                                                  mp_info[7], mp_info[8], mp_info[9])  # Construct MP object
    return parliament_member


def verify_user(email: str, session_token: str) -> bool:
    """
    Verify the user using their email and token. Checks if the email address is used, and verifies the token.
    :param email: The email address of the user.
    :param session_token: The session token of the user.
    :return: True if the user was verified, False otherwise.
    """
    if is_new_address(email):  # Check if the email corresponds to a User
        return False
    user = fetch_user(email)  # Get the user form the database using their email
    if user.verify_token(session_token):
        return True  # Login successful
    return False  # Tokens do not match


if __name__ == '__main__':
    app.run(debug=True, port=int("8080"), host="0.0.0.0")
