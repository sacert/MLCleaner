#!/usr/bin/python

import imaplib
import sys
import datetime
import email
import logging
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

FOLDER='inbox'							# mail folder
LOGIN=''							# email address
PASSWORD=''							# password

# support for logging unsubscribe efforts
LOG_FILENAME='mlc.log'
log_p = True
logging.basicConfig(filename=LOG_FILENAME,filemode='a')
if log_p:
        logging.getLogger().setLevel(logging.INFO)
else:
        logging.getLogger().setLevel(logging.WARNING)

email_list = [] # don't actually need this/ can actually just check if 'not sender_address in email_subs'
email_subs = [] # contain list of tuples with data for mailing lists

print 'Setting up servers...'
server = smtplib.SMTP('smtp.gmail.com', 587)		# need to alter if not using gmail
mail = imaplib.IMAP4_SSL('imap.gmail.com')		# need to alter if not using gmail

def log_in():
	# log in to send mail
	print 'Logging into SMTP...'
	server.ehlo()
	server.starttls()
	server.login(LOGIN, PASSWORD)

	# log in to see mail
	print 'Logging into IMAP...'
	mail.login(LOGIN, PASSWORD)
	mail.select(FOLDER)

def get_subs():
	print 'Retrieving subscriptions...'
	result, data = mail.search(None, '(HEADER List-Unsubscribe mailto)')
	ids = data[0]
	id_list = ids.split()
	fetch_ids = ','.join(data[0].split())
	typ, data = mail.fetch(fetch_ids,'(RFC822.HEADER)')
	for response_part in data:
		if isinstance(response_part, tuple):
			# get email
			msg = email.message_from_string(response_part[1])

			unsub = ' '
			sender_address = ' '
			sender_name = ' '
			# if there is a 'List-Unsubscribe' header, get email contents
			try:
				#print msg
				unsub_s = msg['List-Unsubscribe'].split()[0] #[1:-1]
				if 'mailto' not in unsub_s:
					unsub_s = msg['List-Unsubscribe'].split()[1]
				unsub = re.search('<(.*)>', unsub_s).group(1)
				sender_address = re.sub(r'[<>]','',msg['from'].split()[-1])
				sender_name = msg['from'].split('\"')[1]
				# Ignore any occurences of own email address and add to list
				if not re.search(r'' + re.escape(LOGIN),sender_address) and not sender_address in email_list and not sender_address == ' ':
					email_list.append(sender_address)	# not really needed but have to test it without using it - one day
					email_subs.append([sender_name, sender_address, unsub])
			except:
				pass
	print str(len(email_subs)) + " subscriptions found"

def print_options():
	print '======================================='
	print '-list name		to get a list of all mailing lists names'
	print '-list address		to get a list of all mailing lists addresses'
	print '-unsub all [del]	to unsubscribe from all / add \'del\' to delete emails'
	print '-unsub # [del]		list multiple with commas Ex. -unsub 4, 3, 20 / add \'del\' to delete emails'
	print '-options		get list of options'
	print '-exit			to exit program'

def delete_email(sub):
	result, data = mail.search(None, '(FROM \"' + sub[1] + '\")')
	for val in data[0].split():
   		mail.store(val, '+FLAGS', '\\Deleted')
	mail.expunge()

def sub_list(num):
	for index, sub in enumerate(email_subs):
		print str(index) + ". " + sub[num]

def send_mailto(sub):
	if "subject" not in sub[2]:
		to = re.search('mailto:(.*)', sub[2]).group(1)
		subject = ""
	else:
		to = re.search('mailto:(.*)\\?subject=', sub[2]).group(1)
		subject = re.search('subject=(.*)', sub[2]).group(1)
	msg = MIMEMultipart()
	msg['From'] = LOGIN
	msg['To'] = to
	msg['Subject'] = subject
	message = ''
	msg.attach(MIMEText(message))
        logging.info('%s\n%s\n%s\n%s',datetime.datetime.today(),LOGIN, to, msg.as_string())
	server.sendmail(LOGIN, to, msg.as_string())

# unsubscribe from a specific mailing list(s)
def unsub_num(nums,delete_p):

	# check if user entered a number
	try:
		for num in nums:
			num.isdigit()
	except:
	   print("Input Error! Ex: -unsub 3,4,8,10")
	for num in nums:
		print 'Removing: ' + email_subs[int(num)][0]
		send_mailto(email_subs[int(num)])
                if delete_p:
			delete_email(email_subs[int(num)])
	for num in nums:
		email_list.remove(email_subs[int(num)][1])
		email_subs.remove(email_subs[int(num)])


def unsub_all(delete):
	for sub in email_subs:
		print 'Removing: ' + sub[0]
		send_mailto(sub)
		if delete:
			delete_email(sub)
	for sub in email_subs:
		del email_list[:]
		del email_subs[:]

def main_loop():
	while True:
		user_input = raw_input('> ')
		if user_input == '-list name':
			sub_list(0)
		elif user_input == '-list address':
			sub_list(1)
		elif user_input == '-unsub all':
			unsub_all()
		elif user_input == '-unsub all del':
			unsub_all(True)
		elif '-unsub' in user_input:
			delete_p = re.search('\s*del\s*$',"-unsub 1,2,3,4 del")
                        ui = user_input.split("-unsub",1)[1].replace(" ", "").replace("del", "")
			nums = re.search('(.*)', ui).group(1).split(",")
			unsub_num(nums,delete_p)
		elif user_input == '-options':
			print_options()
		elif user_input == '-exit':
			server.quit()
			mail.logout()
			break
		else:
			print "Input Error"

if __name__ == '__main__':
	log_in()
	get_subs()
	print_options()
	main_loop()
