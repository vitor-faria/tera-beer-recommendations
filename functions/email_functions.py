from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os import environ as env
import smtplib


def send_mail(to_email, markdown_list, image_list):
    # Define the source and target email address.
    str_from = env["EMAIL_FROM"]
    sender_pass = env["EMAIL_PASSWORD"]
    str_to = to_email

    # Create an instance of MIMEMultipart object, pass 'related' as the constructor parameter.
    message = MIMEMultipart('related')
    message['Subject'] = 'Sua recomendação TeraBeer'
    message['From'] = str_from
    message['To'] = str_to

    content = '<br> '.join(markdown_list)
    message_html = f"""
    <b>Esta é a sua recomendação</b>:<br>
    <div> {content} </div>
    """
    msg_text = MIMEText(message_html, 'html')
    message.attach(msg_text)

    for image_index, image_filename in enumerate(image_list):
        with open(image_filename, 'rb') as fp:
            msg_image = MIMEImage(fp.read())
            fp.close()
        msg_image.add_header('Content-ID', f'<image{image_index + 1}>')
        message.attach(msg_image)

    # Create an smtplib.SMTP object to send the email.
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.starttls()  # enable security
    smtp.login(str_from, sender_pass)
    smtp.sendmail(str_from, str_to, message.as_string())
    smtp.quit()
