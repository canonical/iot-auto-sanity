"""This module help to send notification"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from sanity.agent.data import DevData


# pylint: disable=R0903
class Mail:
    """mail object to handle mail task"""

    # mail
    MESSG = ["finished", "failed"]
    PASSWD = os.getenv("MAIL_TOKEN")
    SENDER = os.getenv("MAIL_SENDER")
    recipients = []

    @staticmethod
    def send_mail(status="failed", message="None", filename=""):
        """send mail to assignee"""
        if (
            Mail.PASSWD is None
            or Mail.SENDER is None
            or len(Mail.recipients) == 0
        ):
            print(
                "Can not send notification due to mail sender has not been set"
            )
            return

        msg = MIMEMultipart()
        msg["From"] = Mail.SENDER
        msg["To"] = ", ".join(Mail.recipients)
        msg["Subject"] = (
            f"{DevData.project} Auto Sanity was {Mail.MESSG[status]} !!"
        )
        body = "This is auto sanity bot notification\n" + message
        msg.attach(MIMEText(body, "plain"))

        if filename != "":
            with open(filename, "rb") as attachment:
                p = MIMEBase("application", "octet-stream")
                p.set_payload((attachment).read())
                encoders.encode_base64(p)
                p.add_header(
                    "Content-Disposition", f"attachment; filename= {filename}"
                )
                msg.attach(p)

        s = smtplib.SMTP("smtp.gmail.com", 587)
        s.starttls()
        try:
            s.login(Mail.SENDER, Mail.PASSWD)
        except smtplib.SMTPAuthenticationError:
            print("Mail account login failed")
            return
        text = msg.as_string()
        s.sendmail(Mail.SENDER, Mail.recipients, text)
        s.quit()
