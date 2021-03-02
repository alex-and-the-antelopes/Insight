from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,
    PushResponseError,
    PushServerError,
)
from requests.exceptions import ConnectionError, HTTPError


# Basic arguments. You should extend this function with the push features you
# want to use, or simply pass in a `PushMessage` object.
def send_push_message(client_token, message, extra=None):
    try:
        response = PushClient().publish(
            PushMessage(to=client_token,
                        body=message,
                        data=extra,
                        sound="default"
                        )
        )  # Note: extra is a dictionary
        response.validate_response()  # Check we got a valid response
    except PushServerError:  # Format/validation error
        print("PushServerError, likely caused due to format or validation error")
    except (ConnectionError, HTTPError):  # Encountered some Connection or HTTP error - retry a few times in
        print("Connection or HTTP error")  # Todo: could retry to solve this error (could also ignore the existance of this)
    except DeviceNotRegisteredError:
        print("Device not registered")  # Todo: Should remove device (could also ignore the existance of this)
    except PushResponseError:  # Encountered some other per-notification error.
        print("PushResponseError")


if __name__ == "__main__":
    send_push_message("ExponentPushToken[dTC1ViHeJ36_SqB7MPj6B7]", "Message header")
