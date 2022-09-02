from email.message import EmailMessage
import smtplib
import ssl

def send_mail(subject, body, to_email):
    try:
        mail = EmailMessage()
        mail['from'] = 'trackmyvaccine37@gmail.com'
        mail['subject'] = subject
        mail['to'] = to_email
        mail.set_content(body)
        
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT')
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        with smtplib.SMTP_SSL('smtp.gmail.com',465,context=ctx) as server:
            server.login('trackmyvaccine37@gmail.com','tgbmlofefkosjifl')
            server.send_message(mail)
        return True
    except Exception as e:
        print(e)
        return False