"""The following provides a quick and dirty sentiment analysis of gmail snippets using AFINN.
Snippets are those little preview clips, in one's Promotion's tab. Interesting because
this represents how the advertisers gain one's attention past the subject line. To run the
code, one must register for google api and OAuth2. Guide here: 
http://wescpy.blogspot.com/2014_11_01_archive.html """

from __future__ import print_function
import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

"""Reading in AFINN, dictionary used to gauge pos and neg words"""
afinn = dict(map(lambda (k,v): (k,int(v)), 
                     [ line.split('\t') for line in open("AFINN-111.txt") ]))

"""Using standard google API code to initialize"""
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

"""Actually getting credential and initializing service"""   
maxR = 500
credentials = get_credentials()
http = credentials.authorize(httplib2.Http())
service = discovery.build('gmail', 'v1', http=http)
threads = service.users().threads().list(userId='me', labelIds=["INBOX", "CATEGORY_PROMOTIONS"],
maxResults=maxR).execute().get('threads', [])

snippets = []   
NumMSG = []
datelist = []

"""Pulling message snippet, id, and date from general inbox and appending to lists"""
for thread in threads:
    tdata = service.users().threads().get(userId='me', id=thread['id']).execute()
    nmsgs = len(tdata['messages'])
    msg = tdata['messages'][0]['snippet']
    #date = tdata['messages'][0]['internalDate']
    #id = tdata['messages'][0]['id']
    snippets.append(msg)
    #NumMSG.append(nmsgs)
    #datelist.append(date)
    
#mydictionary = dict(zip(snippets, NumMSG))

"""Getting total score for each snippet"""
totalsumz=[]
for item in snippets:
	totalsumz.append(sum(map(lambda word: afinn.get(word, 0), item.lower().split())))
	
"""Counting how many snippets are mostly positive versus mostly negative"""
senticountpos=0
senticountneg=0
neutrals=0
for item in totalsumz:
	if item > 0:
		senticountpos+=1
	elif item < 0:
		senticountneg+=1
	elif item == 0:
		neutrals+=1	

"""Printing out results"""
print("Average sentiment score of first "+str(maxR)+" promotion snippets is "
+str(sum(totalsumz)/len(totalsumz))+".")
print("There were "+str(senticountpos)+" mostly positive, "+str(senticountneg)
+" mostly negative, and "+str(neutrals)+" neutral snippets.")

	











