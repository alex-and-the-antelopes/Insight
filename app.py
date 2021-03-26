from flask import Flask, jsonify, redirect, request
from flask_cors import CORS
import insight.parliament
from util.database import *
from util import is_valid_postcode
from communications import email
import logging
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
    return redirect("https://github.com/alex-and-the-antelopes/Insight")


@app.route('/register', methods=['POST'])
def register():
    """
    Register new User. Creates a new User object, updates the database and returns the session token.
    :return: Session token if successful, an Error otherwise.
    """
    # Get new User details from form:
    email_address = request.form['email']
    password = request.form['password']  # The given password is already hashed
    notification_token = request.form['notification_token']
    postcode = request.form['postcode']
    # Check for errors:
    if type(password) is not str or not password:
        return jsonify({"error": "password_error"})
    if type(notification_token) is not str or "ExponentPushToken[" not in notification_token:
        return jsonify({"error": "notification_token_error"})
    if not is_valid_postcode(postcode):  # Check that the postcode is valid
        return jsonify({"error": "postcode_error"})
    if not email.is_valid_email(email_address):  # Check that the given email is a valid email address
        return jsonify({"error": "email_error"})

    if not is_new_address(email_address):  # Check if the given email is already in use
        return jsonify({"error": "email_in_use_error"})

    # Add new user to the database:
    new_user = insight.User(email_address, password, notification_token, postcode,
                            create_session_token())  # Create new user
    add_user_to_database(new_user)  # Add new User to the database
    # Send email to user's email address
    email.send_email(new_user.email, "Insight: Registration", "Thanks for registering to use the Insight app!"
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
    email_address = request.form['email']
    password = request.form['password']
    if is_new_address(email_address):
        return jsonify({"error": "new_email_error"})  # Email does not correspond to a User
    # Get user from database using username, check if user is valid.
    user = fetch_user(email_address)  # Construct the user object
    if user and user.verify_password(password):
        # Send email to user address informing of new login
        email.send_email(user.email, "Insight: new login", "A new device signed in to your Insight account. We'"
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
    email_address = request.form['email']
    session_token = request.form['session_token']
    if verify_email_and_session_token(email_address,
                                                   session_token):  # Verify the user using email and session token
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
    email_address = request.form['email']
    session_token = request.form['session_token']
    bill_id = request.form['bill_id']  # The id of the bill to fetch

    if not verify_email_and_session_token(email_address, session_token):  # Verify the user
        return jsonify({"error": "invalid_credentials"})  # Verification unsuccessful

    bill = fetch_bill(str(bill_id))  # Fetch and construct the bill with the given id

    if not bill:
        return jsonify({"error": "query_failed"})  # Query failed, no such bill exists

    likes, dislikes = fetch_user_interactions(bill.id)  # Get the user interactions for the bill
    bill_dict = bill.prepare(
        {
            "likes": likes,
            "dislikes": dislikes,
            "user_vote": fetch_user_interaction(fetch_user_id(email_address), bill.id),
        }
    )  # Prepare bill to be sent to the front-end (add likes, dislikes and user_vote)

    return jsonify(bill_dict)  # Return the Bill as a dictionary


@app.route('/get_bills', methods=['POST'])
def get_bills():
    """
    Find and return the 50 bills that were most recently updated.
    Requires user verification.
    :return: The bills in a suitable format if successful, otherwise an error message.
    """
    # Get user info for verification
    email_address = request.form['email']
    session_token = request.form['session_token']

    if not verify_email_and_session_token(email_address, session_token):  # Verify the user
        return jsonify({"error": "invalid_credentials"})  # Verification unsuccessful

    bill_id_list = fetch_recent_bills()  # Get the 50 most recent bills

    if not bill_id_list:
        return jsonify({"error": "bill_id_query_failed"})  # Query failed, no bills in database

    bill_list = []
    for bill_id in bill_id_list:
        bill = fetch_bill(str(bill_id[0]))  # Fetch and construct the bill with the given id
        if bill:
            likes, dislikes = fetch_user_interactions(bill.id)  # Get the user interactions for the bill
            bill_dict = bill.prepare(
                {
                    "likes": likes,
                    "dislikes": dislikes,
                    "user_vote": fetch_user_interaction(fetch_user_id(email_address), bill.id),
                }
            )  # Prepare bill to be sent to the front-end (add likes, dislikes and user_vote)
            bill_list.append(bill_dict)  # Add the bill to the bill list

    if not bill_list:
        return jsonify({"error": "bill_query_failed"})  # Query failed, no bills found using the bill ids

    return jsonify(bill_list)  # Return the list of bills


@app.route('/get_mp_bills', methods=['POST'])
def get_mp_bills():
    """
    Find and return the bills voted on by the given MP.
    Requires user verification and the MP's id.
    :return: A list of bills voted by the given MP, if successful, or an error message if it failed.
    """
    # Get user info for verification
    email_address = request.form['email']
    session_token = request.form['session_token']
    mp_id = request.form['mp_id']  # Get ParliamentMember id

    if not verify_email_and_session_token(email_address, session_token):  # Verify the user
        return jsonify({"error": "invalid_credentials"})  # Verification unsuccessful

    bill_id_list = fetch_mp_bills(mp_id)  # Get the list of bills the MP has voted on (and their votes)
    if not bill_id_list:
        return jsonify({"error": "no_mp_votes"})  # Query failed

    bill_list = []
    for bill_id in bill_id_list:
        bill = fetch_bill(str(bill_id[0]))  # Fetch and construct the bill with the given id
        if bill:
            likes, dislikes = fetch_user_interactions(bill.id)  # Get the user interactions for the bill
            bill_dict = bill.prepare(
                {
                    "likes": likes,
                    "dislikes": dislikes,
                    "user_vote": fetch_user_interaction(fetch_user_id(email_address), bill.id),
                }
            )  # Prepare bill to be sent to the front-end (add likes, dislikes and user_vote)
            bill_list.append(bill_dict)  # Add the bill to the bill list

    if not bill_list:
        return jsonify({"error": "bill_query_failed"})  # Query failed, no bills found using the bill ids

    return jsonify(bill_list)  # Return the list of bills


@app.route('/message', methods=['POST'])
def send_message():
    """
    Sends an email to a member of parliament specified by the user.
    Requires user verification, MP id and the message itself.
    :return: A success message, if the email was sent successfully, otherwise an error message
    """
    # Get user info for verification
    email_address = request.form['email']
    session_token = request.form['session_token']
    # Get information to send email
    mp_id = request.form['mp_id']
    message = request.form['message']
    # Verify the user:
    if not verify_email_and_session_token(email_address, session_token):  # Verify the user
        return jsonify({"error": "invalid_credentials"})  # Verification unsuccessful

    mp = fetch_mp(mp_id)  # Construct and return the parliament member by following given id

    if mp:  # If the MP was successfully constructed
        try:
            email.send_email(mp.email, "Insight Update!", message)  # Send the email
            return jsonify({"success": "email_sent"})  # If sent without errors, return success message
        except ValueError:
            return jsonify({"error": "invalid_recipient_address"})  # Destination email is invalid
        except TypeError:
            return jsonify({"error": "invalid_arguments"})  # Given an invalid argument (empty or not of type str)
        except OSError:
            return jsonify({"error": "email_failed_to_send"})  # Error with sending email (connecting to smtp server)

    return jsonify({"error": "mp_database_error"})  # Could not build ParliamentMember


@app.route('/update_postcode', methods=['POST'])
def update_postcode():
    """
    Updates the user's postcode with the given postcode. Verifies the user before updating the postcode.
    :return: Success statement if the postcode was changed, an error statement otherwise.
    """
    # Get user info for verification
    email_address = request.form['email']
    session_token = request.form['session_token']
    postcode = request.form['postcode']  # Get the new postcode

    # Verify the user:
    if not verify_email_and_session_token(email_address, session_token):
        return jsonify({"error": "invalid_credentials"})  # Verification unsuccessful

    if not is_valid_postcode(postcode):  # Check that the postcode is valid
        return jsonify({"error": "invalid_postcode"})

    response = update_user_postcode(email_address, postcode)  # Update the user's postcode and get the result
    if not response:  # If the update returned False then it failed
        return jsonify({"error": "query_error"})  # Error when updating user's entry in the database

    return jsonify({"success": "postcode_updated"})  # Return success message


@app.route('/get_mp_votes', methods=['POST'])
def get_mp_votes():
    """
    Fetches all of the MP's votes on bills from the database and returns it in a suitable format.
    :return: A list of the MP's votes.
    """
    # Get user info for verification
    email_address = request.form['email']
    session_token = request.form['session_token']
    # Get information to send email
    mp_id = request.form['mp_id']

    # Verify the user:
    if not verify_email_and_session_token(email_address, session_token):
        return jsonify({"error": "invalid_credentials"})  # Verification unsuccessful

    if not fetch_mp(mp_id):  # Check if mp_id exists
        return jsonify({"error": "mp_id_error"})  # Return an error if the mp does not exist

    try:  # Get all the bills
        bill_votes = fetch_mp_votes(mp_id)  # Get the MP's votes on the bills
    except KeyError:
        return jsonify({"error": "bill_votes_error"})  # Return an error if the mp has not voted on any bills
    # Clean list of bills
    bill_votes = filter_votes(bill_votes)
    if not bill_votes:
        return jsonify({"error": "cleaned_bill_votes_error"})  # Return an error if the cleaned votes are empty
    # Put it in the final format:
    mp_votes = {}
    for bill in bill_votes:  # Iterate through the list of bills voted
        mp_votes[bill[0]] = bill[1]
    return jsonify(mp_votes)  # Return the list of {billID and positive}


@app.route('/local_mp', methods=['POST'])
def get_local_mp():
    """
    Get the user's local MP. Verifies the user's identity, uses the user's postcode to construct and return the user's
    local MP.
    :return: The user's local MP if successful, an error message otherwise.
    """
    # Get user info for verification
    email_address = request.form['email']
    session_token = request.form['session_token']
    # Verify the user:
    if not verify_email_and_session_token(email_address, session_token):
        return jsonify({"error": "invalid_credentials"})  # Verification unsuccessful

    user = fetch_user(email_address)  # Get the user's details
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
    email_address = request.form['email']
    session_token = request.form['session_token']
    bill_id = request.form['bill_id']
    positive = request.form['positive']
    # Verify the user:
    if not verify_email_and_session_token(email_address, session_token):
        return jsonify({"error": "invalid_credentials"})  # Verification unsuccessful

    user_id = fetch_user_id(email_address)  # Fetch and construct the User object from the database
    vote_state = fetch_user_interaction(user_id, bill_id)  # Gets the current reaction state of the bill for the user

    # Construct the appropriate SQL statement
    if int(positive) == 2:  # Remove interaction (remove like/dislike)
        statement = f"DELETE FROM Votes WHERE billID = {bill_id} AND userID = {user_id};"
    elif vote_state == 2:  # First time interaction with the bill
        statement = f"INSERT INTO Votes (positive, billID, userID, voteTime) VALUES ('{positive}', '{bill_id}', " \
                    f"'{user_id}', CURRENT_TIMESTAMP());"
    else:  # Change existing user interaction with the bill
        statement = f"UPDATE Votes SET positive = {positive}, voteTime = CURRENT_TIMESTAMP() WHERE billID = {bill_id}" \
                    f" AND userID = {user_id};"

    try:
        database_engine.interact(statement)  # Carry out the relevant SQL statement todo fix
    except RuntimeWarning:
        return jsonify({"error": "query_error"})  # Error when executing sql statement

    return jsonify({"success": "update_successful"})  # Return success message


def build_bills(bill_id_list: list, email_address: str) -> list:
    """
    Builds a list containing the bills from the given list of bill ids. Constructs the Bill objects using the bill_ids.
    Includes user interactions with the bills.
    :param bill_id_list: A list containing the ids of the Bills to build.
    :param email_address: The email address of the User. Used to get the user's interaction with the bills.
    :return: A list containing the built Bills.
    """
    bill_list = []
    for bill_id in bill_id_list:
        bill = fetch_bill(str(bill_id[0]))  # Fetch and construct the bill with the given id
        if bill:
            likes, dislikes = fetch_user_interactions(bill.id)  # Get the user interactions for the bill
            bill_dict = insight.parliament.Bill.prepare(
                bill,
                {
                    "likes": likes,
                    "dislikes": dislikes,
                    "user_vote": fetch_user_interaction(fetch_user_id(email_address), bill.id),
                }
            )  # Prepare bill to be sent to the front-end (add likes, dislikes and user_vote)
            bill_list.append(bill_dict)  # Add the bill to the bill list
    return bill_list


if __name__ == '__main__':
    app.run(debug=True, port=int("8080"), host="0.0.0.0")
