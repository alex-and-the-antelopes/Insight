import smtplib
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


def send_email():
    pass


if __name__ == '__main__':
    send_email("dummyemail@gmail.com", "Title of message", "dummy text here here here one.")

