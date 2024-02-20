import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from sanity.agent.data import dev_data


class mail:
    # mail
    MESSG = ["finished", "failed"]
    PASSWD = os.getenv("MAIL_TOKEN")
    SENDER = os.getenv("MAIL_SENDER")
    recipients = []

    def send_mail(status="failed", message="None", filename=""):
        if (
            mail.PASSWD is None
            or mail.SENDER is None
            or len(mail.recipients) == 0
        ):
            print(
                "Can not send notification due to mail sender has not been set"
            )
            return

        msg = MIMEMultipart()
        msg["From"] = mail.SENDER
        msg["To"] = ", ".join(mail.recipients)
        msg["Subject"] = "{} Auto Sanity was {} !!".format(
            dev_data.project, mail.MESSG[status]
        )
        body = "This is auto sanity bot notification\n" + message
        msg.attach(MIMEText(body, "plain"))

        if filename != "":
            filename = filename
            attachment = open(filename, "rb")
            p = MIMEBase("application", "octet-stream")
            p.set_payload((attachment).read())
            encoders.encode_base64(p)
            p.add_header(
                "Content-Disposition", "attachment; filename= %s" % filename
            )
            msg.attach(p)

        s = smtplib.SMTP("smtp.gmail.com", 587)
        s.starttls()
        try:
            s.login(mail.SENDER, mail.PASSWD)
        except smtplib.SMTPAuthenticationError:
            print("Mail account login failed")
            return
        text = msg.as_string()
        s.sendmail(mail.SENDER, mail.recipients, text)
        s.quit()
