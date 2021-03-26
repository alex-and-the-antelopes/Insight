import smtplib
import re
from util.gcp import secret_manager as secret
from profanityfilter import ProfanityFilter


def send_message(recipient_address: str, message: str) -> None:
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
        email_address = secret.get_version("email_address", version_name="latest")
        email_password = secret.get_version("email_pass", version_name="latest")
        server.login(email_address, email_password)  # Login to the account
        server.sendmail(email_address, recipient_address, message)  # Send the constructed email
        server.quit()  # Exit the server
    except smtplib.SMTPResponseException:
        raise OSError("Email failed to send.")  # Print using error stream
    return


def create_message(subject: str = "Insight message!", main_body: str = None) -> str:
    """
    Combines the given subject and main body to formulate an email message. Returns a str capable of being transmitted
    using smtplib and gmail. Uses a profanity filter to censor offensive content.
    :param subject: The subject (title/header) of the email.
    :param main_body: The main body of the email.
    :return: The constructed email to be sent.
    """
    # Check for type errors:
    if type(subject) is not str:  # Check the email subject
        raise TypeError(f"Expected type <class 'str'> got type {type(subject)} for subject")
    if type(main_body) is not str:  # Check the email body
        raise TypeError(f"Expected type <class 'str'> got type {type(main_body)} for main_body")
    message = f'Subject: {subject}\n{main_body}'  # Bundle the contents in the appropriate format
    profanity_filter = ProfanityFilter()  # Create ProfanityFilter object
    message = profanity_filter.censor(message)  # Censor offensive content from the message
    return message  # Return the constructed email


def send_email(recipient_email: str, email_subject: str, email_body: str) -> None:
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
        raise TypeError(f"Expected type <class 'str'> got type {type(email_subject)} for email_subject")
    if type(email_body) is not str:  # Check the email body
        raise TypeError(f"Expected type <class 'str'> got type {type(email_body)} for email_body")
    if type(recipient_email) is not str:  # Check the recipient's email address
        raise TypeError(f"Expected type <class 'str'> got type {type(recipient_email)} for recipient_email")
    if type(recipient_email) is not str:  # Email is not a str
        raise TypeError(f"Expected type <class 'str'> got type {type(recipient_email)} for recipient_email")
    if not is_valid_email(recipient_email):  # Email is a str but is not a valid address
        raise ValueError(f"Expected a valid email address got: {recipient_email}")  # Raise value error for email

    message = create_message(email_subject, email_body)  # Construct the message (Format subject and body)
    send_message(recipient_email, message)  # Send the email to the intended recipient
    return


def is_valid_email(email_address: str) -> bool:
    """
    Checks if the given email address is valid.
    Comments, IP literals, quotes and many other "quirks" of email addresses are NOT supported.
    :param email_address: The email address to validate.
    :return: True if the given email is valid, False otherwise.
    """
    # To check if email is valid, we break the email up into <local>@<domain>.<tld>
    # This is basically a state machine, where specific characters move us on to the next part

    local_legal_chars = r"[a-zA-Z0-9!#$%&'*+\-\/=?^_`{|}~]"  # Legal characters for local part
    domain_legal_chars = r"[a-zA-Z0-9]"  # Legal characters for domain and tld part

    state = "local"   # The "state" of our calculations i.e. the part of the email we're currently at

    for i, c in enumerate(email_address):
        if state == "local":
            if re.search(local_legal_chars, c):  # Ignore allowed chars
                pass
            elif c == '@':  # Move on to domain if we find an @
                state = "domain"
            elif c == '.':  # Check for consecutive .s
                if i == len(email_address) - 1 or email_address[i + 1] == '.':
                    return False
            else:  # Return False if any other character is encountered
                return False
        elif state == "domain" or state == "tld":
            if re.search(domain_legal_chars, c):  # Ignore allowed chars
                pass
            elif c == '.':  # Check for consecutive .s, a dot moves us on to the tld state
                if i == len(email_address) - 1 or email_address[i + 1] == '.':
                    return False
                state = "tld"
            elif c == "-":  # No hyphens at the beginning or end of <domain><tld>
                if email_address[i - 1] == '@' or i == len(email_address) - 1:
                    return False
            else:  # Return False if any other character is encountered
                return False

    if state != "tld":  # Did not reach "tld" state, so it is invalid (does not have necessary parts)
        return False

    return True  # The email is valid
