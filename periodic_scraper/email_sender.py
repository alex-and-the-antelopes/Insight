import smtplib
import re
import sys

email_address = "parlpy.test@gmail.com"
email_password = "parlpy_pass123"


def send_message(recipient_address, message):
    """
    Sends the given message (email) to the given email address. Uses smtplib to connect to the server, log in and send
    the email. The details for the account being used are in the email_details file.
    :param message: The message (email) to be sent.
    :param recipient_address: The recipient's email address (destination).
    :return: None
    """
    if type(recipient_address) is not str or type(message) is not str:  # Check that the arguments are str
        return
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)  # Define the server (gmail server, with port number 587)
        server.ehlo()
        server.starttls()  # Connect to the server via tls
        server.login(email_address, email_password)  # Login to the account
        server.sendmail(email_address, recipient_address, message)  # Send the constructed email
        server.quit()  # Exit the server
    except smtplib.SMTPResponseException:
        print("Email failed to send.", file=sys.stderr)  # Print using error stream
    return


def create_message(subject="Insight message!", main_body=None):
    """
    Combines the given subject and main body to formulate an email message. Returns a str capable of being transmitted
    using smtplib and gmail.
    :param subject: The subject (title/header) of the email.
    :param main_body: The main body of the email.
    :return: The constructed email to be sent.
    """
    # Check for type errors:
    if type(subject) is not str:  # Check the email subject
        raise TypeError("Expected type <class 'str'> got type ", type(subject), " for subject")
    if type(main_body) is not str:  # Check the email body
        raise TypeError("Expected type <class 'str'> got type ", type(main_body), " for main_body")
    message = f'Subject: {subject}\n{main_body}'  # Bundle the contents in the appropriate format
    return message  # Return the constructed email


def check_email_address(email_address=None):
    """
    Checks if the given email address is a valid address. Uses a regular expression to check the address' validity.
    :param email_address: The email address to validate.
    :return: 0 if the address is valid, 1 if it is the wrong type (not str), 2 if it is not a valid address.
    """
    if type(email_address) is not str:  # Check that the given address is a str
        return 1  # Type error
    if not re.search('^[a-z0-9]+[._]?[a-z0-9]+[@]\w+[.]\w{2,}$', email_address):  # Use regex to evaluate address
        return 2  # Value error
    return 0  # Valid address (Correct type and value)


def send_email(recipient_email, email_subject, email_body):
    """
    Constructs and sends an email to the given email address. Includes error checking for type, value errors and
    invalid email addresses.
    :param recipient_email: The intended party's email address.
    :param email_subject: The subject for the email (title/header).
    :param email_body: The email's body.
    :return: None
    """
    # Check for type errors:
    if type(email_subject) is not str:  # Check the email subject
        raise TypeError("Expected type <class 'str'> got type ", type(email_subject), " for email_subject")
    if type(email_body) is not str:  # Check the email body
        raise TypeError("Expected type <class 'str'> got type ", type(email_body), " for email_body")
    if type(recipient_email) is not str:  # Check the recipient's email address
        raise TypeError("Expected type <class 'str'> got type ", type(recipient_email), " for recipient_email")
    # Check the validity of the email address
    email_code = check_email_address(recipient_email)
    if email_code == 1:  # Email is not a str
        raise TypeError("Expected type <class 'str'> got type ", type(recipient_email), " for recipient_email")
    if email_code == 2:  # Email is a str but is not a valid address
        raise ValueError(f"Expected a valid email address got: {recipient_email}")  # Raise value error for email

    message = create_message(email_subject, email_body)  # Construct the message (Format subject and body)
    send_message(recipient_email, message)  # Send the email to the intended recipient
    return


if __name__ == '__main__':
    # send_email("dummy@gmail.com", "okay", "23.23")
    # Test email checker: todo move to a test file
    test_addresses = ["dummy@gmail.com", "dummy@com", "dummy@gmail", "dummy.com", "dummy@gmail.com", 2, [], None, ""]
    for address in test_addresses:
        print(check_email_address(address), address)
    # Test email sender
    send_email("dummyemail@gmail.com", "EXAMPLE TITLE", "EXAMPLE TEXT FOR THE MAIN BODY HERE.")
