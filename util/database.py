import random
import string

from parlpy.utils.constituency import get_constituencies_from_post_code
from util.gcp import database_engine
from util import strip_text
import insight
import insight.parliament
from communications import notification


def fetch_user(email_address: str) -> insight.User or None:
    """
    Finds the user with the given email address, constructs and returns the User object.
    :param email_address: The email address of the user.
    :return: The constructed User object.
    """
    user_query = database_engine.select(f"SELECT * FROM Users WHERE email='{email_address}';")  # Get User from database
    user = None
    if user_query:
        user_info = user_query[0]  # Get the user information
        user = insight.User(user_info[1], user_info[2], user_info[4], user_info[3], user_info[5])  # Construct user
    return user


def fetch_mp(mp_id: int) -> insight.parliament.Member or None:
    """
    Finds the member of parliament with the given ID, constructs and returns the Member object.
    :param mp_id: The id of the MP.
    :return: The constructed Member object.
    """
    parliament_member = None
    mp_query = database_engine.select(f"SELECT * FROM MP WHERE mpID='{mp_id}';")  # Query database for MP
    if mp_query:
        mp_info = mp_query[0]  # Extract the MP information
        # Construct MP object:
        parliament_member = insight.parliament.Member(mp_info[0], mp_info[1], mp_info[2], mp_info[3], mp_info[4],
                                                      mp_info[5], mp_info[6], mp_info[7], mp_info[8], mp_info[9])
    return parliament_member


def fetch_bill(bill_id: str) -> insight.parliament.Bill or None:
    """
    Finds the bill with the given ID, constructs and returns the Bill object.
    :param bill_id: The id of the bill to fetch.
    :return: A Bill object with the bill's details if it exists, None otherwise.
    """
    bill_query = database_engine.select(f"SELECT billID, titleStripped, shortDesc, dateAdded, expiration, link, status,"
                                        f" description FROM  Bills WHERE billID='{bill_id}';")  # Get the bill by id
    bill = None
    if bill_query:  # If the query was successful (the bill exists), build the Bill object
        bill_data = bill_query[0]  # Get the bill's information
        bill = insight.parliament.Bill(bill_data[0], bill_data[1], bill_data[7],
                                       str(bill_data[3])[:10].replace(" ", ""),
                                       bill_data[4], bill_data[6], strip_text(bill_data[2]),
                                       bill_data[5])  # Construct the Bill

    return bill  # Return the Bill object


def fetch_recent_bills(limit: int = 50) -> list:
    """
    Fetches and returns a list containing the ids of the most recently updated bills.
    :param limit: The number of bills to fetch. Default number of bills is 50.
    :return: A list containing the ids of the most recently updated bills, or None.
    """
    if type(limit) is not int:
        raise TypeError(f"Expected type <class 'int'> but got {type(limit)}")  # Given unexpected limit type
    if limit <= 0:
        limit = 50  # If given an invalid value, default to 50
    bills_query = database_engine.select(f"SELECT billID FROM Bills ORDER BY billID DESC LIMIT {limit};")
    return bills_query  # Return the list of bill ids


def fetch_mp_bills(mp_id: str) -> list:
    """
    Fetch the id of the bills that the given MP has voted on.
    :param mp_id: The id of the MP.
    :return: A list of bills the MP has voted on, including their vote.
    """
    # Get all the bill ids the MP has voted on:
    bill_id_query = database_engine.select(f"SELECT DISTINCT Bills.billID FROM MPVotes RIGHT JOIN Bills ON "
                                           f"MPVotes.billID = Bills.billID WHERE MPVotes.mpID = {mp_id};")
    return bill_id_query  # Return the list of bill ids the MP has voted on


def fetch_user_id(email_address: str) -> str:
    """
    For a given email address, finds the user's id from the database.
    :param email_address: The email address of the User.
    :return: The id of the User with the given email address.
    """
    user_query = database_engine.select(f"SELECT userID FROM Users WHERE email='{email_address}';")  # Get the user
    if not user_query:
        raise KeyError(f"No user has email: {email_address}.")  # Query failed, no such User exists
    return user_query[0][0]  # Return the user's id


def fetch_user_interactions(bill_id: str) -> (int, int):
    """
    Fetches the users' votes (interaction) on the given bill.
    :param bill_id: The id of the bill.
    :return: A tuple containing the likes and dislikes (# of likes, # of dislikes).
    """
    likes_count, dislikes_count = 0, 0  # Hold the number of likes and dislikes for the bill
    # Get number of like:
    likes_query = database_engine.select(f"SELECT COUNT(*) FROM Votes WHERE billID = '{bill_id}' AND positive = 1;")
    if likes_query:
        likes_count = likes_query[0][0]
    # Get number of dislikes:
    dislikes_query = database_engine.select(f"SELECT COUNT(*) FROM Votes WHERE billID = '{bill_id}' and positive = 0;")
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
    user_vote_query = database_engine.select(f"SELECT positive FROM Votes WHERE userID='{user_id}' AND billID = "
                                             f"'{bill_id}';")  # Get the user's interaction with the bill
    if not user_vote_query:
        return 2  # If the query returns an empty list, return False
    return user_vote_query[0][0]  # If the query returns an empty list return True


def fetch_mp_votes(mp_id: str) -> list:
    """
    Constructs and returns a list of all of the MP's votes on bills from the database.
    :param mp_id: The id of the Member.
    :return: A list of all the MP's votes on bills.
    """
    # Get the bills the MP has voted on from the database
    bill_votes = database_engine.select(f"SELECT billID, positive, stage FROM MPVotes WHERE mpID='{mp_id}';")
    if not bill_votes:
        raise KeyError(f"No MP has mp_id: {mp_id}.")  # Query failed, no such MP exists
    return bill_votes


def fetch_mp_by_postcode(postcode: str) -> int:
    """
    Find and return the MP of the constituency, based on the given postcode.
    :param postcode: The postcode being searched.
    :return: The id of the MP for the constituency.
    """
    constituency = get_constituencies_from_post_code(postcode)  # Get the constituency from ParlPy
    if not constituency:
        raise KeyError(f"Found no constituencies for postcode '{postcode}'.")  # No constituency exists, raise an error
    return constituency[0]["currentRepresentation"]["member"]["value"]["id"]  # Return the MP for the constituency


def create_session_token() -> str:
    """
    Generate a unique token using a combination of random digits, lowercase and uppercase letters.
    :return: The unique, generated token.
    """
    token = ''.join(random.SystemRandom().choice(string.digits + string.ascii_lowercase + string.ascii_uppercase)
                    for _ in range(8))  # Use digits, lowercase and uppercase letters, length 8
    # Look if it's unique i.e. does not appear already in the db (if not repeat the process)
    if database_engine.select(f"SELECT * FROM Users WHERE sessionToken='{token}';"):  # Check if the token is in use
        return create_session_token()  # Repeat the process until a unique token is generated
    return token  # Return the unique token


def is_new_address(email_address: str) -> bool:
    """
    Checks the database to see if the given email address is already in use.
    :param email_address: The email address to look up.
    :return: True if the email address is not being used, false otherwise.
    """
    query = database_engine.select(f"SELECT * FROM Users WHERE email='{email_address}';")  # Get the user with the email
    if query:
        return False  # If the query returns a populated list, return False
    return True  # If the query returns an empty list return True


def add_user_to_database(user: insight.User) -> None:
    """
    Add the given User object to the database.
    :param user: User object.
    :return: None.
    """
    if not user or type(user) is not insight.User:  # If the given user is not a User object, return immediately
        return
    # The SQL statement to add the user into the Users table:
    statement = f"INSERT INTO Users (email,password,postcode,sessionToken,notificationToken) VALUES ('{user.email}','" \
                f"{user.password_hash}','{user.postcode}','{user.session_token}','{user.notification_token}');"
    database_engine.interact(statement)  # Carry out the SQL statement
    return


def update_user_postcode(user_email: str, postcode: str) -> bool:
    """
    Updates the user's postcode with the given postcode, returning a bool value to indicate success/failure.
    :param user_email: The user's email address.
    :param postcode: The new postcode.
    :return: True if the postcode was updated successfully.
    """
    try:
        # Update the user's postcode in the respective database entry
        database_engine.interact(f"UPDATE Users SET postcode='{postcode}' WHERE email='{user_email}';")
    except RuntimeWarning:
        return False  # Error occurred when trying to update the database
    return True  # Update successful


def remove_user_interaction(bill_id: str, user_id: str) -> bool:
    """
    Removes the user's interaction (like/dislike) from the Bill with the given bill id.
    :param bill_id: The id of the Bill.
    :param user_id: The id of the User.
    :return: True if the reaction was removed successfully, False otherwise.
    """
    remove_statement = f"DELETE FROM Votes WHERE billID = {bill_id} AND userID = {user_id};"  # Remove interaction
    try:
        database_engine.interact(remove_statement)  # Carry out the relevant SQL statement
    except RuntimeWarning:
        return False  # Error executing the SQL statement
    return True


def add_user_interaction(bill_id: str, user_id: str, vote: int) -> bool:
    """
    Add a user interaction (like/dislike) for the Bill with the given id. The interaction can be either 0 (dislike) or 1
    (like).
    :param bill_id: The id of the Bill.
    :param user_id: The id of the User.
    :param vote: The (user) vote to add. Must be 0 or 1. Values: 0 --> dislike, 1 --> like.
    :return: True if the reaction was removed successfully, False otherwise.
    """
    if vote != 0 and vote != 1:
        return False  # Should only be given 0 or 1 (0 --> dislike, 1 --> like)
    add_statement = f"INSERT INTO Votes (positive, billID, userID, voteTime) VALUES ('{vote}', '{bill_id}', " \
                    f"'{user_id}', CURRENT_TIMESTAMP());"
    try:
        database_engine.interact(add_statement)  # Carry out the relevant SQL statement
    except RuntimeWarning:
        return False  # Error executing the SQL statement
    return True


def update_user_interaction(bill_id: str, user_id: str, vote: int) -> bool:
    """
    Update the user's interaction (like/dislike) for the Bill with the given id. The new interaction can be either 0
    (dislike) or 1 (like).
    :param bill_id: The id of the Bill.
    :param user_id: The id of the User.
    :param vote: The updated User vote. Must be 0 or 1. Values: 0 --> dislike, 1 --> like.
    :return: True if the reaction was removed successfully, False otherwise.
    """
    if vote != 0 and vote != 1:
        return False  # Should only be given 0 or 1 (0 --> dislike, 1 --> like)
    update_statement = f"UPDATE Votes SET positive = {vote}, voteTime = CURRENT_TIMESTAMP() WHERE billID = {bill_id}" \
                       f" AND userID = {user_id};"
    try:
        database_engine.interact(update_statement)  # Carry out the relevant SQL statement
    except RuntimeWarning:
        return False  # Error executing the SQL statement
    return True


def verify_email_and_session_token(email_address: str, session_token: str) -> bool:
    """
    Verify the user using their email and token. Checks if the email address is used, and verifies the token.
    :param email_address: The email address of the user.
    :param session_token: The session token of the user.
    :return: True if the user was verified, False otherwise.
    """
    if is_new_address(email_address):  # Check if the email corresponds to a User
        return False
    user = fetch_user(email_address)  # Get the user form the database using their email
    if user and user.verify_token(session_token):
        return True  # Login successful
    return False  # Tokens do not match


def notify_users(title: str, body: str) -> None:
    """
    Fetches the notification token (ExponentPushToken) for all Users, builds and sends a notification with the given
    title and body.
    :param title: The title of the notification.
    :param body: The body of the notification.
    :return: None.
    """
    user_emails = database_engine.select("SELECT email FROM Users;")  # Get all the user email addresses
    if not user_emails:
        raise KeyError("No users found in the database.")  # Database query failed
    user_list = []
    for user_email in user_emails:  # Go through each user email and construct the User object
        user = fetch_user(user_email)  # Construct the User object
        if user:
            user_list.append(user)  # Add User to the list of users
    notification.send_notification_to_clients(user_list, title, body)  # Build and send the notification to all users
    return


def filter_votes(bill_votes: list) -> list:
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


def prepare_bills(bill_id_list: list, email_address: str) -> list:
    """
    Builds a list containing the bills from the given list of bill ids. Constructs the Bill objects using the bill_ids.
    Includes user interactions with the bills. Used to keep a uniform response format with the front-end.
    :param bill_id_list: A list containing the ids of the Bills to build.
    :param email_address: The email address of the User. Used to get the user's interaction with the bills.
    :return: A list containing the built Bills.
    """
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
    return bill_list
