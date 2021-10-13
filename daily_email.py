import re, json, smtplib
from datetime import date
import os

class ERROR_EMAIL(object):
    def __init__(self):
        gmail_account = json.load(open('conf_gmail.json', 'r'))

        self.FROM     = gmail_account["email"]
        self.TO       = [gmail_account["send_to"]]
        self.PW       = gmail_account["password"]
        
    def send(self,subject,content):
        server = smtplib.SMTP_SSL("smtp.gmail.com",465,context=None)
        server.login(self.FROM,self.PW)
        server.sendmail(self.FROM, self.TO, f"Subject: [Spotlight On The Credits] {subject}\n{content}")
        server.quit()

if __name__=="__main__":
    error_email = ERROR_EMAIL()
    
    todays_requests = []
    log_name = date.today().strftime("%Y-%m-%d")
    log_path = f"/home/spotcreds/logs/check_tweets/{log_name}.log"
    if os.path.isfile(log_path):
        f = open(log_path, "r")
        log=" "
        while log!="":
            log = f.readline()
            m = re.findall(r"playlist\sfor\s:\s(.*)\sat\shtt",log,re.DOTALL)
            if m!=[]:
                todays_requests.append(m[0])
    
        email_content = f"Salut BG,\nAujourd'hui on a eu {len(todays_requests)} demandes :\n"
        for artist in todays_requests :
            email_content= email_content+f"\t- {artist}\n"
        
        email_content+= "\nA demain,\nSpotlight On the Credits"
    else:
        email_content = f"No logs found for today at the following location : {log_path}"

    error_email.send(subject="Daily Report",content=email_content)