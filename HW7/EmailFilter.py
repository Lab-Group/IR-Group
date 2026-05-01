import os
import email
from bs4 import BeautifulSoup
import re

ham_path = 'data/easy_ham/'
spam_path = 'data/spam/'
url = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', re.I)

def clean_string(input_string):
    cleaned_string = input_string.replace('-', ' ').replace('.', ' ').replace('?', ' ') \
        .replace('/', ' ').replace('!', ' ').replace('@', ' ').replace('#', ' ').replace(',', ' ') \
        .replace('%', ' ').replace(':', ' ').replace(';', ' ').replace('<', ' ').replace('>', ' ').replace('$', ' ') \
        .replace('*', ' ').replace('&', ' ').replace('_', ' ').replace('~', ' ').replace('[', ' ').replace(']', ' ') \
        .replace('(', ' ').replace(')', ' ').replace('\\', ' ').replace('{', ' ').replace('}', ' ').replace('^', ' ') \
        .replace('"', ' ').replace('\n', ' ').replace('=', ' ').replace('+', ' ')
    cleaned_string = ' '.join(cleaned_string.split())
    return cleaned_string

def process_folder(folder_path, label):
    for i, filename in enumerate(os.listdir(folder_path)):
        filepath = os.path.join(folder_path, filename)
        if not os.path.isfile(filepath):
            continue
        try:
            with open(filepath, 'r', encoding='ISO-8859-1') as f:
                msg = email.message_from_file(f)
            subject = msg.get('Subject', '') or ''
            payload = msg.get_payload()
            if isinstance(payload, list):
                body = ' '.join(p.get_payload(decode=True).decode('ISO-8859-1', errors='ignore')
                                for p in payload if hasattr(p, 'get_payload'))
            elif isinstance(payload, bytes):
                body = payload.decode('ISO-8859-1', errors='ignore')
            else:
                body = payload or ''
            emailText = subject + ' ' + body
            emailText = url.sub(' ', emailText)
            emailText = clean_string(emailText)
            emailID = "%s_%d" % (label, i)
            with open('Files/%s.txt' % emailID, 'w', encoding='utf-8') as eFile:
                content = "<EMAILID>%s</EMAILID>\n<TEXT>%s</TEXT>\n<LABEL>%s</LABEL>" % (emailID, emailText, label)
                eFile.write(content)
        except Exception as e:
            print("Skipped %s: %s" % (filename, e))

print("Processing ham emails...")
process_folder(ham_path, 'ham')
print("Processing spam emails...")
process_folder(spam_path, 'spam')
print("Done! Check the Files/ folder.")
