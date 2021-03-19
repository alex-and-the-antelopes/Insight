import smtplib
import re
import email_details


def send_message(message=None, recipient_address=None):
    # Message = the built email message and recipient_address = email address of recipient.
    # Todo add error checking
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(email_details.email_address, email_details.password)  # Login to the account
        server.sendmail(email_details.email_address, recipient_address, message)
        server.quit()
    except:
        print("Email failed to send.")  # Todo use error stream using sys


def create_message(subject="Insight message!", main_body=None):
    # Create the email message. subject = Title and main_body = main text
    # Todo add error checking
    message = f'Subject: {subject}\n{main_body}'
    return message


def check_email_address(email_address=None):
    """
    Checks if the given email address is a valid address. Uses a regular expression to check the address' validity.
    :param email_address: The email address to validate.
    :return: 0 if the address is valid, 1 if it is the wrong type (not str), 2 if it is not a valid address.
    """
    if type(email_address) is not str:  # Check that the given address is a str
        return 1  # Type error
    if not re.search('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,}$', email_address):  # Use regex to evaluate address
        return 2  # Value error
    return 0  # Valid address (Correct type and value)


def send_email(recipient_email, email_subject, email_body):
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
    send_message(message, recipient_email)  # Send the email to the intended recipient
    return


if __name__ == '__main__':
    send_email("dummyemail@gmail.com", "Title of message", "dummy text here here here one.")

