from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,
    PushResponseError,
    PushServerError,
)
from requests.exceptions import ConnectionError, HTTPError
from bill_tracker_core import User


"""
    Send a notification with the given title and body to the client.
    :param clients: list of clients to send the notification to (List of Users)
    :param title: title of the notification (str)
    :param body: body of the notification (str)
    """


def send_notification_to_clients(clients, title, body):
    if type(clients) is not list:  # Check that a list is passed
        raise TypeError("Expected type <class 'list'> got type ", type(list))

    for client in clients:
        send_notification(client, title, body)


def send_notification(client, title, body):
    """
    Send a notification with the given title and body to the client.
    :param client: intended recipient of the notification to (User)
    :param title: title of the notification (str)
    :param body: body of the notification (str)
    """
    if type(client) is not User:  # Check that an instance of User is passed
        raise TypeError("Expected type <class 'User'> got type ", type(client))

    try:
        response = PushClient().publish(
            build_notification(client.notification_token, title, body)  # Build a valid expo notification
        )  # Send the notification
        response.validate_response()  # Check that we got a valid response from the expo server
    except PushServerError:  # Format or validation error
        print("PushServerError, likely caused due to format or validation error")
    except (ConnectionError, HTTPError):  # Encountered some Connection or HTTP error - retry a few times in
        print("Connection or HTTP error")
    except DeviceNotRegisteredError:  # Device token is outdated, or wrong
        print("Device not registered")  # Todo: Should remove device (or ignore), or request User for new token
    except PushResponseError:  # Did not deliver the notification
        print("PushResponseError")


def build_notification(destination, title, body):
    """
    Creates and returns a valid notification, ready to be broadcast
    :param destination: expo client notification token (str)
    :param title: notification title (str)
    :param body: main body of the notification (str)
    :return: built notification to broadcast (PushMessage)
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
    user1 = User("Joe", "pass", "ExponentPushToken[dTC1ViHeJ36_SqB7MPj6B7]")
    user2 = User("Joe", "pass", "ExponentPushToken[dTC1ViHeJ36_SqB7MPj6B7]")
    user3 = User("Joe", "pass", "ExponentPushToken[dTC1ViHeJ36_SqB7MPj6B7]")
    lister = [user1, user2, user3]
    # send_notification(user, "Test 2", "I DONT like watching the bee movie")
    send_notification_to_clients(lister, "Testing for many clients", "lol you must be loving this")
