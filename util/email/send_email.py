import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .template import Template
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR=Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# environment variables
user_smtp = os.environ.get("USER_SMTP")
pass_smtp = os.environ.get("PASSWORD_SMTP")
host_src_smtp = os.environ.get("FROM_HOST_SMTP")
emails = ["krzysztof.gul@orange.com"] 


class Sender():
    subject = ""
    context = {}
    to_emails = []
    test_send = False
    from_email  = host_src_smtp
    template_file = None
    template_file_html = None


    def __init__(self, subject="", template_file= None, template_file_html = None, context = None, to_emails = emails, test_send=False):
        if template_file == None and template_file_html == None:
            raise Exception("You must set a template")
        assert isinstance(to_emails, list)
        self.to_emails = to_emails
        self.subject = subject
        self.template_file_html = template_file_html
        self.template_file = template_file
        self.context = context
        self.test_send = test_send

    def format_msg(self):
        msg = MIMEMultipart('alternative')
        msg['From'] = self.from_email
        msg['To'] = ", ".join(self.to_emails)

        msg['Subject'] = self.subject
        if self.template_file_html != None:
            tmpl_str = Template(template_file=self.template_file_html, context=self.context)
            txt_part = MIMEText(tmpl_str.render(), 'html')
        else:
            tmpl_str = Template(template_file=self.template_file, context=self.context)
            txt_part = MIMEText(tmpl_str.render(), 'plain')
        msg.attach(txt_part)
        msg_str = msg.as_string()
        return msg_str


    def send(self):
        msg = self.format_msg()
        did_send = False
        if not self.test_send:
            with smtplib.SMTP(host='smtp.corpnet.pl', port=587) as server:
                server.ehlo()
                server.starttls()
                server.login(user_smtp, pass_smtp)
                #try:
                server.sendmail(self.from_email, self.to_emails, msg)
                did_send = True
                #except:
                 #   did_send = False
        return did_send

