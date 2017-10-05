# Mailing List Cleaner

Unsubscribe from mailing lists and clean inbox

### Set Up

Within the python file, you will need to edit the following to correspond to your email/password/folder:

```
FOLDER=''     # mail folder to look at
LOGIN=''      # email address
PASSWORD=''   # password
```
As well as your IMAP/SMTP host:

```
server = smtplib.SMTP('smtp.gmail.com', 587)	
mail = imaplib.IMAP4_SSL('imap.gmail.com')		
```

**Note:** Default is set up for *Gmail*


### Running Program

Within the terminal, go into the corresponding directory and use the following command:

```sh
$ python mlc.py
```

### Options
```
-list name		to get a list of all mailing lists names
-list address		to get a list of all mailing lists addresses
-unsub all [del]	to unsubscribe from all / add 'del' to delete emails as well
-unsub # [del]		list multiple with commas Ex. -unsub 4, 3, 20 / add 'del' to delete emails as well
-options		get list of options
-exit			to exit program and logout
```

### Development

Want to contribute? Great!

Current TODOs are:
  - testing
  - optimize mailing list retrievals 

### License

MIT License
