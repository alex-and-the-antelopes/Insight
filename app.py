from flask import Flask, jsonify, redirect, send_file, Response, request
from flask_cors import CORS
import bill_tracker_core as core
import db_interactions as database
import email_sender
import sqlalchemy
import logging
import os
import random
import string

app = Flask(__name__)
logger = logging.getLogger()
CORS(app)
# Get config from core
CONFIG = core.CONFIG


# initialises database pool as a global variable

# example call: database.interact("INSERT INTO bills_db VALUES (1,3,'large bill text')")

# Add more config constants
# CONFIG.update({
#     "key": "value"
# })


# region Bill actions.
# Todo: These could be placed in Bill class, or in core file?
# Returns n in upper case
def cap(n):
    return n.upper()


# Returns n with spaces between each character.
def space(n):
    return " ".join(n)


# Returns the bill with given id in JSON form
def find_bill(id):
    bill = core.Bill(
        "Sample bill",
        "This is a sample bill: a placeholder. Probably for debugging and testing purposes.",
        "1/1/2021",
        "2/1/2022",
        "active",
        short_desc="Sample Bill"
    )
    return bill.to_dict()


def get_top_bills(range):
    bill1 = core.Bill(
        "id_1",
        "Sample bill",
        "This is a sample bill: a placeholder. Probably for debugging and testing purposes.",
        "1/1/2021",
        "2/1/2022",
        "active",
        short_desc="Sample Bill"
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

    return [bill1.to_dict(), bill2.to_dict()]


# endregion

# Mapping of "actions" (from URL) to their respective functions
# !! Any function referenced in this dict can be run by anyone !!
safe_actions = {
    "capitalise": cap,
    "space": space,
    "get": find_bill,
}


# Sample private function
# We don't want private functions to be accessible from the internet, so this function should NOT be put in the actions
#   array.
def unsafe_function(n):
    # Do something that shouldn't be accessible publicly
    print("oh dear!")


# Perform action on given bill
@app.route('/b/<bill_id>/<action>')
def handle_request(bill_id, action):
    # not case-sensitive
    action = action.lower()

    # Run requested action if valiid
    if action in safe_actions:
        result = safe_actions[action](bill_id)
    else:
        result = f"unknown or forbidden action: {action}"

    # Construct output
    output = {
        "bill_id": bill_id,
        "action": action,
        "result": result
    }

    # Convert to json and return
    return jsonify(output)


@app.route('/top')
def top():
    result = get_top_bills(10)
    # Construct output
    output = {
        "result": result
    }

    # Convert to json and return
    return jsonify(output)


@app.route('/')
def landing_page():
    return redirect(CONFIG["default_url"])


# It will then redirect you to the logged_in or garbage page, depending on if you gave it the right password or not
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    # Get user from database using username, check if user is valid.
    # Return the session token
    return jsonify({"session_token": "session_placeholder"})


@app.route('/login_with_token', methods=['POST'])
def login_with_token():
    email = request.form['email']
    session_token = request.form['session_token']

    # Get user from database using username, check if user is valid.
    # Return the session token
    return jsonify({"session_token": "session_placeholder"})


@app.route('/register', methods=['POST'])
def register():
    # Get new User details from form:
    email = request.form['email']
    password = request.form['password']  # The given password is already hashed
    notification_token = request.form['notification_token']
    postcode = request.form['postcode']
    # Check for errors:
    if type(password) is not str:
        return jsonify({"error": "password_error"})
    if type(notification_token) is not str or "ExponentPushToken[" not in notification_token:
        return jsonify({"error": "notification_token_error"})
    if type(postcode) is not str or len(postcode) < 6 or len(postcode) > 8:  # Check that the postcode is valid
        return jsonify({"error": "postcode_error"})
    if email_sender.check_email_address(email) != 0:  # Check that the given email is a valid email address
        return jsonify({"error": "email_error"})
    # Todo check if email already exists in the database
    new_user = core.User(email, password, notification_token, postcode, create_session_token())  # Create new user
    add_user_to_database(new_user)
    # Return the session token
    return jsonify({"session_token": new_user.session_token})


# Deliver requested resource.
# todo: generalise so works with filetypes other than image
@app.route('/res/' + CONFIG["external_res_path"] + '/<name>')
def get_res(name):
    # print(request.mimetype)
    # todo: sort out mimetype. This might affect retrieving images in the future.
    return send_file(CONFIG["img_dir"] + name)

    # return send_file("CONFIG["img_dir"] + core.CONFIG["invalid_img"], mimetype='image/gif')


def create_session_token():
    """
    Generate a unique token using a combination of random digits, lowercase and uppercase letters.
    :return: The unique, generated token.
    """
    token = ''.join(random.SystemRandom().choice(string.digits + string.ascii_lowercase + string.ascii_uppercase)
                    for _ in range(8))  # Use digits, lowercase and uppercase letters, length 8
    # Look if it's unique i.e. does not appear already in the db (if not repeat the process) todo
    return token


def get_user(email_address):
    """
    Gets the
    :param email_address:
    :return:
    """
    return


def add_user_to_database(user):
    """
    Add the given User to the database.
    :param user: User object
    :return: None
    """
    # todo add user to database
    return


if __name__ == '__main__':
    app.run(debug=True, port=int("8080"), host="0.0.0.0")
