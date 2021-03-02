from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,
    PushResponseError,
    PushServerError,
)
from bill_tracker_core import User
from requests.exceptions import ConnectionError, HTTPError


def send_notification_to_all(clients, title, message):
    """

    :param clients: list of clients to send the message to
    :param title:
    :param message:
    :return:
    """

    pass


def send_notification(client, title, message):
    """

    :param client: the user to send the notification to (User object)
    :param title:
    :param message:
    :return:
    """
    if type(client) is not User:  # Check that an instance of User is passed
        raise TypeError("Expected type <class 'User'> got type ", type(client))

    try:
        response = PushClient().publish(
            PushMessage(to=client.notification_token,
                        title=title,
                        body=message,
                        sound="default")
        )
        response.validate_response()  # Check we got a valid response
    except PushServerError:  # Format or validation error
        print("PushServerError, likely caused due to format or validation error")
    except (ConnectionError, HTTPError):  # Encountered some Connection or HTTP error - retry a few times in
        print("Connection or HTTP error")
    except DeviceNotRegisteredError:  # Device token is outdated, or wrong
        print("Device not registered")  # Todo: Should remove device (or ignore), or request User for new token
    except PushResponseError:  # Did not deliver the notification
        print("PushResponseError")


if __name__ == "__main__":
    user = User("Joe", "pass", "ExponentPushToken[dTC1ViHeJ36_SqB7MPj6B7]")
    send_notification(user, "Test 1", "I like watching the bee movie")
