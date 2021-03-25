from flask import Flask, jsonify, redirect, request
from flask_cors import CORS
import bill_tracker_core as core
import db_interactions as database
import parlpy.utils.constituency as pp_constituency
import email_sender
import logging
import string
import random
import notifications

app = Flask(__name__)
logger = logging.getLogger()
CORS(app)


# ////// End region ////// Endpoints //////


@app.route('/')
def landing_page():
    """
    The landing page for the API redirects visitors to the github repository. There they get access to the readme,
    the source code and the documentation for the project.
    :return: Redirects visitors to the github repository.
    """
    return redirect("https://github.com/alex-and-the-antelopes/BillTracker")


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
    if type(postcode) is not str or len(postcode) < 5 or len(postcode) > 8:  # Check that the postcode is valid
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
    if user and user.verify_password(password):
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


@app.route('/get_bill', methods=['POST'])
def get_bill():
    """
    Find and return the bill with the given bill id.
    Requires user verification and the Bill's id.
    :return: The bill, in a suitable format if successful, an error message otherwise.
    """
    # Get user info for verification
    email = request.form['email']
    session_token = request.form['session_token']
    bill_id = request.form['bill_id']  # The id of the bill to fetch

    if not verify_user(email, session_token):  # Verify the user
        return jsonify({"error": "invalid_credentials"})  # Verification unsuccessful

    bill = fetch_bill(str(bill_id))  # Fetch and construct the bill with the given id

    if not bill:
        return jsonify({"error": "query_failed"})  # Query failed, no such bill exists

    bill_dict = bill.to_dict()  # Convert the bill to a suitable format to be transmitted
    user_interactions = fetch_user_interactions(bill.id)  # Get the user interactions for the bill
    bill_dict['likes'] = user_interactions[0]  # Get number of likes
    bill_dict['dislikes'] = user_interactions[1]  # Get number of dislikes
    bill_dict['user_vote'] = fetch_user_interaction(fetch_user_id(email), bill.id)

    return jsonify(bill_dict)  # Return the Bill as a dictionary


@app.route('/get_bills', methods=['POST'])
def get_bills():
    """
    Find and return 10 random bills. TODO change it to get recently changed bills
    Requires user verification.
    :return: The bills in a suitable format, if successful, or an error message.
    """
    # Get user info for verification
    email = request.form['email']
    session_token = request.form['session_token']

    if not verify_user(email, session_token):  # Verify the user
        return jsonify({"error": "invalid_credentials"})  # Verification unsuccessful

    bill_list = []
    for i in range(9, 22):
        bill = fetch_bill(str(i))  # Fetch and construct the bill with the given id

        if bill:
            bill_dict = bill.to_dict()  # Convert the bill to a suitable format to be transmitted
            user_interactions = fetch_user_interactions(bill.id)  # Get the user interactions for the bill
            bill_dict['likes'] = user_interactions[0]  # Get number of likes
            bill_dict['dislikes'] = user_interactions[1]  # Get number of dislikes
            bill_dict['user_vote'] = fetch_user_interaction(fetch_user_id(email), bill.id)
            bill_list.append(bill_dict)  # Add the bill to the bill list

    if not bill_list:
        return jsonify({"error": "query_failed"})  # Query failed, no such bill exists

    return jsonify(bill_list)  # Return the list of bills


@app.route('/get_mp_bills', methods=['POST'])
def get_mp_bills():
    """
    Find and return the bills voted on by the given MP.
    Requires user verification and the MP's id.
    :return: A list of bills voted by the given MP, if successful, or an error message if it failed.
    """
    # Get user info for verification
    email = request.form['email']
    session_token = request.form['session_token']
    mp_id = request.form['mp_id']  # Get ParliamentMember id

    if not verify_user(email, session_token):  # Verify the user
        return jsonify({"error": "invalid_credentials"})  # Verification unsuccessful

    bill_query = database.select(f"SELECT DISTINCT Bills.billID, titleStripped, shortDesc, dateAdded, expiration, "
                                 f"Bills.link, status FROM MPVotes RIGHT JOIN Bills ON MPVotes.billID = "
                                 f"Bills.billID WHERE MPVotes.mpID = {mp_id};")  # Get all the bills the MP has voted on

    if not bill_query:
        return jsonify({"error": "query_failed"})  # Query failed

    bill_list = []  # Holds the list of bills to be transmitted
    for bill_data in bill_query:  # Put all bills in the query in the correct format
        bill = core.Bill(bill_data[0], bill_data[1], None, str(bill_data[3])[:10].replace(" ", ""),
                         bill_data[4], bill_data[6], parse_text(bill_data[2]), link=bill_data[5])  # Create MP object
        bill_dict = bill.to_dict()  # Get the dictionary representation of the bill
        user_interactions = fetch_user_interactions(bill.id)  # Get the user interactions for the bill
        bill_dict['likes'] = user_interactions[0]  # Get number of likes
        bill_dict['dislikes'] = user_interactions[1]  # Get number of dislikes
        bill_dict['user_vote'] = fetch_user_interaction(fetch_user_id(email), bill.id)
        bill_list.append(bill_dict)  # Append the bill to the list
    return jsonify(bill_list)  # Return the list of bills


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
        except Exception:
            return jsonify({"error": "email_failed_to_send"})  # Error with mail sending

    return jsonify({"error": "mp_database_error"})  # Could not build ParliamentMember


@app.route('/update_postcode', methods=['POST'])
def update_postcode():
    """
    Updates the user's postcode with the given postcode. Verifies the user before updating the postcode.
    :return: Success statement if the postcode was changed, an error statement otherwise.
    """
    # Get user info for verification
    email = request.form['email']
    session_token = request.form['session_token']
    postcode = request.form['postcode']  # Get the new postcode

    # Verify the user:
    if not verify_user(email, session_token):
        return jsonify({"error": "invalid_credentials"})  # Verification unsuccessful

    if type(postcode) is not str or len(postcode) < 5 or len(postcode) > 8:  # Check that the postcode is valid
        return jsonify({"error": "postcode_error"})
    try:
        database.interact(f"UPDATE Users SET postcode='{postcode}' WHERE email='{email}';")  # Update user's postcode
    except RuntimeWarning:
        return jsonify({"error": "query_error"})  # Error when executing sql statement

    return jsonify({"success": "postcode_updated"})  # Return success message


@app.route('/get_mp_votes', methods=['POST'])
def get_mp_votes():
    """
    Fetches all of the MP's votes on bills from the database and returns it in a suitable format.
    :return: A list of the MP's votes.
    """
    # Get user info for verification
    email = request.form['email']
    session_token = request.form['session_token']
    # Get information to send email
    mp_id = request.form['mp_id']

    # Verify the user:
    if not verify_user(email, session_token):
        return jsonify({"error": "invalid_credentials"})  # Verification unsuccessful

    if not fetch_mp(mp_id):  # Check if mp_id exists
        return jsonify({"error": "mp_id_error"})  # Return an error if the mp does not exist

    # Get all the bills
    bill_votes = fetch_mp_votes(mp_id)  # Get the MP's votes on the bills
    if not bill_votes:
        return jsonify({"error": "bill_votes_error"})  # Return an error if the mp has not voted on any bills
    # Clean list of bills
    bill_votes = clean_mp_votes(bill_votes)
    if not bill_votes:
        return jsonify({"error": "cleaned_bill_votes_error"})  # Return an error if the cleaned votes are empty
    # Put it in the final format:
    mp_votes = []
    for bill in bill_votes:  # Iterate through the list of bills voted
        bill_details = {"id": bill[0], "positive": bill[1]}
        mp_votes.append(bill_details)
    return jsonify(mp_votes)  # Return the list of {billID and positive}


@app.route('/local_mp', methods=['POST'])
def get_local_mp():
    """
    Get the user's local MP. Verifies the user's identity, uses the user's postcode to construct and return the user's
    local MP.
    :return: The user's local MP if successful, an error message otherwise.
    """
    # Get user info for verification
    email = request.form['email']
    session_token = request.form['session_token']
    # Verify the user:
    if not verify_user(email, session_token):
        return jsonify({"error": "invalid_credentials"})  # Verification unsuccessful

    user = fetch_user(email)  # Get the user's details
    if not user:
        return jsonify({"error": "user_error"})  # Verification unsuccessful

    # Get the id of the MP for the user's constituency
    try:
        mp_id = fetch_mp_by_postcode(user.postcode)  # Construct the MP for the user's constituency
    except KeyError:
        return jsonify({"error": "mp_error"})  # Key error caused by invalid postcode

    parliament_member = fetch_mp(mp_id)  # Construct the ParliamentMember (MP) object
    if parliament_member:
        return jsonify(parliament_member.to_dict())  # Return the user's local MP

    return jsonify({"error": "construct_mp_error"})  # Return error message


@app.route('/set_user_vote', methods=['POST'])
def set_user_vote():
    """
    Update the User's vote (like or dislike) to the given bill. Interacts with the database to update user interaction.
    Can handle removing votes (un-like or un-dislike) by updating the respective entry in the database.
    :return: A success message, if no errors occurred, otherwise an error message
    """
    # Get user info for verification
    email = request.form['email']
    session_token = request.form['session_token']
    bill_id = request.form['bill_id']
    positive = request.form['positive']
    # Verify the user:
    if not verify_user(email, session_token):
        return jsonify({"error": "invalid_credentials"})  # Verification unsuccessful

    user_id = fetch_user_id(email)  # Fetch and construct the User object from the database
    vote_state = fetch_user_interaction(user_id, bill_id)  # Gets the current reaction state of the bill for the user

    # Construct the appropriate SQL statement
    if positive is '2':  # Remove interaction (remove like/dislike)
        statement = f"DELETE FROM Votes WHERE billID = {bill_id} AND userID = {user_id};"
    elif vote_state == 2 and positive != 2:  # First time interaction with the bill
        statement = f"INSERT INTO Votes (positive, billID, userID, voteTime) VALUES ('{positive}', '{bill_id}', " \
                    f"'{user_id}', CURRENT_TIMESTAMP());"
    else:  # Change existing user interaction with the bill
        statement = f"UPDATE Votes SET positive = {positive}, voteTime = CURRENT_TIMESTAMP() WHERE billID = {bill_id}" \
                    f" AND userID = {user_id};"

    try:
        database.interact(statement)  # Carry out the relevant SQL statement
    except RuntimeWarning:
        return jsonify({"error": "query_error"})  # Error when executing sql statement

    return jsonify({"success": "update_successful"})  # Return success message


# ////// End region ////// Helper functions //////


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
    query = database.select(f"SELECT * FROM Users WHERE email='{email_address}';")  # Get the user with the given email
    if query:
        return False  # If the query returns a populated list, return False
    return True  # If the query returns an empty list return True


def add_user_to_database(user: core.User) -> None:
    """
    Add the given User object to the database.
    :param user: User object.
    :return: None.
    """
    if not user or type(user) is not core.User:  # If the given user is not a User object, return immediately
        return
    # The SQL statement to add the user into the Users table:
    statement = f"INSERT INTO Users (email,password,postcode,sessionToken,notificationToken) VALUES ('{user.email}','" \
                f"{user.password_hash}','{user.postcode}','{user.session_token}','{user.notification_token}');"
    database.interact(statement)  # Carry out the SQL statement
    return


def parse_text(text: str) -> str:
    """
    Finds and removes the escape characters in the given string. Checks for linux and windows escape characters.
    :param text: The string to be parsed.
    :return: The parsed string.
    """
    if "\r" in text:
        text = text.replace("\r", "")  # Remove linux next line char
    if "\n" in text:
        text = text.replace("\n", "")  # Remove mac & windows next line char
    return text


def notify_users(title: str, body: str) -> None:
    """
    Fetches the notification token (ExponentPushToken) for all Users, builds and sends a notification with the given
    title and body.
    :param title: The title of the notification.
    :param body: The body of the notification.
    :return: None.
    """
    user_emails = database.select("SELECT email FROM Users;")  # Get all the user email addresses
    if not user_emails:
        raise KeyError("No users found in the database.")  # Database query failed
    user_list = []
    for user_email in user_emails:  # Go through each user email and construct the User object
        user = fetch_user(user_email)  # Construct the User object
        if user:
            user_list.append(user)  # Add User to the list of users
    notifications.send_notification_to_clients(user_list, title, body)  # Build and send the notification to all users
    return


def fetch_user(email_address: str) -> core.User or None:
    """
    Finds the user with the given email address, constructs and returns the User object.
    :param email_address: The email address of the user.
    :return: The constructed User object.
    """
    user_query = database.select(f"SELECT * FROM Users WHERE email='{email_address}';")  # Query database for the user
    user = None
    if user_query:
        user_info = user_query[0]  # Get the user information
        user = core.User(user_info[1], user_info[2], user_info[4], user_info[3], user_info[5])  # Construct user
    return user


def fetch_mp(mp_id: int) -> core.ParliamentMember or None:
    """
    Finds the member of parliament with the given ID, constructs and returns the ParliamentMember object.
    :param mp_id: The id of the MP.
    :return: The constructed ParliamentMember object.
    """
    parliament_member = None
    mp_query = database.select(f"SELECT * FROM MP WHERE mpID='{mp_id}';")  # Query database for the member of parliament
    if mp_query:
        mp_info = mp_query[0]  # Extract the MP information
        # Construct MP object:
        parliament_member = core.ParliamentMember(mp_info[0], mp_info[1], mp_info[2], mp_info[3], mp_info[4],
                                                  mp_info[5], mp_info[6], mp_info[7], mp_info[8], mp_info[9])
    return parliament_member


def fetch_bill(bill_id: str) -> core.Bill or None:
    """
    Finds the bill with the given ID, constructs and returns the Bill object.
    :param bill_id: The id of the bill to fetch.
    :return: A Bill object with the bill's details if it exists, None otherwise.
    """
    bill_query = database.select(f"SELECT billID, titleStripped, shortDesc, dateAdded, expiration, link, status, "
                                 f"description FROM  Bills WHERE billID='{bill_id}';")  # Get the bill with the given id
    bill = None
    if bill_query:  # If the query was successful (the bill exists), build the Bill object
        bill_data = bill_query[0]  # Get the bill's information
        bill = core.Bill(bill_data[0], bill_data[1], bill_data[7], str(bill_data[3])[:10].replace(" ", ""),
                         bill_data[4], bill_data[6], parse_text(bill_data[2]), bill_data[5])  # Construct the Bill

    return bill  # Return the Bill object


def fetch_user_id(email_address: str) -> str:
    """
    For a given email address, finds the user's id from the database.
    :param email_address: The email address of the User.
    :return: The id of the User with the given email address.
    """
    user_query = database.select(f"SELECT userID FROM Users WHERE email='{email_address}';")  # Get the user
    if not user_query:
        raise KeyError(f"No user has email: {email_address}.")  # Query failed, no such User exists
    return user_query[0][0]  # Return the user's id


def fetch_user_interactions(bill_id: str) -> tuple:
    """
    Fetches the users' votes (interaction) on the given bill.
    :param bill_id: The id of the bill.
    :return: A tuple containing the likes and dislikes (# of likes, # of dislikes).
    """
    likes_count, dislikes_count = 0, 0  # Hold the number of likes and dislikes for the bill
    # Get number of like:
    likes_query = database.select(f"SELECT COUNT(*) FROM Votes WHERE billID = '{bill_id}' AND positive = 1;")
    if likes_query:
        likes_count = likes_query[0][0]
    # Get number of dislikes:
    dislikes_query = database.select(f"SELECT COUNT(*) FROM Votes WHERE billID = '{bill_id}' and positive = 0;")
    if dislikes_query:
        dislikes_count = dislikes_query[0][0]
    return likes_count, dislikes_count  # Return the number of likes/dislikes as a tuple


def fetch_user_interaction(user_id: str, bill_id: str) -> int:
    """
    Finds whether the user has reacted to the given bill.
    :param user_id: The id of the user.
    :param bill_id: The id of the bill.
    :return: An int value (0,1,2) indicating the user's interaction with the bill. 0 --> User has disliked the bill,
    1 --> User has liked the bill, 2 --> User has not interacted with the bill
    """
    # Get the user's interaction with the bill:
    user_vote_query = database.select(f"SELECT positive FROM Votes WHERE userID='{user_id}' AND billID = '{bill_id}';")

    if not user_vote_query:
        return 2  # If the query returns an empty list, return False
    return user_vote_query[0][0]  # If the query returns an empty list return True


def fetch_mp_votes(mp_id: str) -> list:
    """
    Constructs and returns a list of all of the MP's votes on bills from the database.
    :param mp_id: The id of the ParliamentMember.
    :return: A list of all the MP's votes on bills.
    """
    db_statement = f"SELECT billID, positive, stage FROM MPVotes WHERE mpID='{mp_id}';"
    bill_votes = database.select(db_statement)
    return bill_votes


def fetch_mp_by_postcode(postcode: str) -> int:
    """
    Find and return the MP of the constituency, based on the given postcode.
    :param postcode: The postcode being searched.
    :return: The id of the MP for the constituency.
    """
    constituency = pp_constituency.get_constituencies_from_post_code(postcode)  # Get the constituency from ParlPy
    if not constituency:
        raise KeyError(f"Found no constituencies for postcode '{postcode}'.")  # No constituency exists, raise an error
    return constituency[0]["currentRepresentation"]["member"]["value"]["id"]  # Return the MP for the constituency


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
    if user and user.verify_token(session_token):
        return True  # Login successful
    return False  # Tokens do not match


def clean_mp_votes(bill_votes: list) -> list:
    """
    Cleans the given list of bill votes to only include relevant bill votes. Filters out amendments and deprecated
    readings.
    :param bill_votes: The list of bill votes to clean/filter.
    :return: The filtered list of bill votes.
    """
    clean_votes = []
    prev_id = '-1'  # Used to filter out deprecated bills from the final list
    for bill in bill_votes:
        if "amendments" in bill[2]:  # Ignore amendments
            continue
        if prev_id == bill[0]:
            clean_votes.pop()  # If bill id appears twice, remove the deprecated version
        clean_votes.append(bill)  # Add the bill to the cleaned list
        prev_id = bill[0]  # Update the previous id for next iteration
    return clean_votes


if __name__ == '__main__':
    app.run(debug=True, port=int("8080"), host="0.0.0.0")
