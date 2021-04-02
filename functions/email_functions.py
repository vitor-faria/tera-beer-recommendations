from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os import environ as env
import smtplib


def send_mail(to_email, to_name, markdown_list, image_list):
    # Define the source and target email address.
    str_from = env["EMAIL_FROM"]
    sender_pass = env["EMAIL_PASSWORD"]
    str_to = to_email

    # Create an instance of MIMEMultipart object, pass 'related' as the constructor parameter.
    message = MIMEMultipart('related')
    message['Subject'] = 'Sua recomendação TeraBeer'
    message['From'] = str_from
    message['To'] = str_to

    message_html = get_email_message(to_name, markdown_list)
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


def get_email_message(to_name, markdown_list):
    content = '<br> '.join(markdown_list)
    hello = f'Olá, <b>{to_name}</b>!' if to_name else 'Olá!'
    message_html = f"""
    <p>
        {hello}
    </p>
    <p>
        Abaixo está a sua lista de cervejas recomendadas pelo 
        <a target="_blank" href="https://terabeer-recomendacoes.herokuapp.com/">TeraBeer</a>! :D
    </p>
    <p>
        Para que possamos melhorar a sua experiência em nosso app, conta pra gente 
        <a target="_blank" href="https://forms.gle/sxpYt7GBYMnFKYA77">por aqui</a> o que achou das recomendações. 
        A sua opinião vai nos ajudar muito!
    </p>
    <p>
        A <b>Equipe TeraBeer</b> espera ter contribuído para sua jornada cervejeira e agradece pela colaboração.<br>
        Esperamos nos ver em breve, com novidades!
    </p>
    <p style="color:red;">
        <b>Beba com moderação.</b>
    </p>
    <h4 style="color:green;">
        <b>CHEERS!</b>
    </h4>
    <div> 
        {content} 
    </div>
    <p>
        <br> 
        <br>
        Não esqueça de responder a nossa <a target="_blank" href="https://forms.gle/sxpYt7GBYMnFKYA77">pesquisa</a>!
    </p>
    """

    return message_html
