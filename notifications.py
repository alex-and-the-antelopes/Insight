from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,
    PushResponseError,
    PushServerError,
)
from requests.exceptions import ConnectionError, HTTPError
from bill_tracker_core import User
import sys


def send_notification_to_clients(clients: list, title: str, body: str) -> None:
    """
    Send a notification with the given title and body to the client. Can raise TypeError.
    :param clients: The list of users to send the notification to. Should be a list of User objects.
    :param title: The title of the notification.
    :param body: The body of the notification.
    """
    if type(clients) is not list:  # Check that a list is passed
        raise TypeError("Expected type <class 'list'> got type ", type(clients))

    for client in clients:  # Loop through each client in the list
        send_notification(client, title, body)  # Send message to each client
    return


def send_notification(client: User, title: str, body: str) -> None:
    """
    Send a notification with the given title and body to the client. Can raise TypeError.
    :param client: The intended recipient of the notification to.
    :param title: The title of the notification.
    :param body: The body of the notification.
    """
    if type(client) is not User:  # Check that an instance of User is passed
        raise TypeError("Expected type <class 'User'> got type ", type(client))

    try:
        response = PushClient().publish(
            build_notification(client.notification_token, title, body)  # Build a valid expo notification
        )  # Send the notification
        response.validate_response()  # Check that we got a valid response from the expo server
    except PushServerError:  # Format or validation error
        print("PushServerError, likely caused due to format or validation error", file=sys.stderr)
    except (ConnectionError, HTTPError):  # Encountered some Connection or HTTP error - retry a few times in
        print("Connection or HTTP error", file=sys.stderr)
    except DeviceNotRegisteredError:  # Device token is outdated, or wrong
        print("Device not registered", file=sys.stderr)
    except PushResponseError:  # Did not deliver the notification
        print("PushResponseError", file=sys.stderr)
    return


def build_notification(destination: str, title: str, body: str) -> PushMessage:
    """
    Creates and returns a valid notification, ready to be broadcast. Can raise TypeError and ValueError.
    :param destination: expo client notification token.
    :param title: The notification's title.
    :param body: The main body of the notification.
    :return: The built notification to broadcast.
    """
    if type(destination) is not str or type(title) is not str or type(body) is not str:  # Check for type errors
        raise TypeError("Expected type <class 'str'>")

    if not PushClient.is_exponent_push_token(destination):  # Check if the token is valid
        raise ValueError("Not a value notification token")

    notification = PushMessage(to=destination,
                               title=title,
                               body=body,
                               sound="default")  # Build the push message (notification)

    return notification


if __name__ == "__main__":
    # Simple tests for notifications todo: remove or move to test file
    token = None
    try:
        with open("tokens.txt", "r") as file:
            token = file.readline().strip()  # Read the test token from token file
    except FileNotFoundError:
        print("No tokens.txt file found. Notifications tokens need to be in the tokens.txt file", file=sys.stderr)
    token = "ExponentPushToken[" + token + "]"  # Convert to valid format for push tokens
    user1 = User("joehd@emai.com", "pass1", token, "AB24EZ", "asaQSA2")
    # user2 = User("Joe", "pass2", token, "AB2 AB2", "SESSION TOKEN")
    # user3 = User("Alex", "pass3", token, "AB2 AB2", "SESSION TOKEN")
    # users = [user1, user2, user3]
    # send_notification(user1, "Test 4", "Example message body for user test")  # Send to single user
    # send_notification_to_clients(users, "Testing for many clients", "Example message body")  # Send to list of users
    send_notification(user1, "Insight Update!", "New bills have been updated. Take 5 minutes to go through them.")
