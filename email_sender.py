import smtplib
import email_details


def send_message(message=None, recipient_address=None):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(email_details.email_address, email_details.password)  # Login to the account
        server.sendmail(email_details.email_address, recipient_address, message)
        server.quit()
    except:
        print("Email failed to send.")


def create_email(subject="Insight message!", main_body=None):
    message = f'Subject: {subject}\n{main_body}'
    return message


def send_email():
    pass


if __name__ == '__main__':
    create_email(main_body="Dummy message")
    send_message(create_email(main_body="Dummy message"), "sgavriilidis1@gmail.com")
