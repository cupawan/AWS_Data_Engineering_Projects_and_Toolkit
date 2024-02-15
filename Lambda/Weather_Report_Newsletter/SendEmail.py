import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import yaml
import re

class EmailWithPython:
    def __init__(self, config_path, text_file = False, is_html = False):
        self.config_path = config_path
        self.text_file = text_file
        self.is_html = is_html
        self.sender = self.load_config()[0]
        self.password = self.load_config()[1]
    def load_config(self):
        try:
            with open(self.config_path, 'r') as config_file:
                config = yaml.safe_load(config_file)
                return config['MY_EMAIL_ADDRESS'], config['MY_GMAIL_PASSWORD']
        except FileNotFoundError:
            print(f"Config file not found at {self.config_path}")
            return None
        except yaml.YAMLError as e:
            print(f"Error parsing YAML in {self.config_path}: {e}")
            return None    
    def get_message_from_txt(self,path):
        with open(path,'r') as f:
            data = f.readlines()
            return '\n'.join(data)
    def send_email(self, rec_email, subject, body):
        msg = MIMEMultipart()
        msg['From'] = self.sender
        msg['To'] = rec_email
        rec_name = rec_email.split("@")[0]
        match = re.search(r'([a-zA-Z]+)(\d+)', rec_name)
        rec_name = match.groups()[0] if match else rec_name
        today_date = datetime.now().strftime("%d-%m-%Y")
        msg['Subject'] = f"{today_date} {subject}"
        msg.attach(MIMEText(body, 'html'))        
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(self.sender, self.password)
        s.sendmail(self.sender, rec_email, msg.as_string())
        s.quit()
        return {'status': 'sent'}