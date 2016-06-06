
                                            ![zenPassword Logo](/img/logo_96.png)

# Presentation
ZenPassword allows you to create an encrypted database where you can store your logins and passwords. This database is protected by a main password only known by you. It is used as the encryption key for the moment.

This application is developed for an educative purpose only, it doesn't use advanced algorithms such as AES to encrypt your data. For a consequence, I won't be responsible of loss of data or other damage.
Content of the databases are currently encrypted thanks to a simple algorithm based on Vigenere encryption.

# How to
## Create a database
To create a new database, click on "Create a database". Then set a name to your future file and a main password. Your main password must contains at least 8 characters to be secured. This password will be stored nowhere, so be careful not to forget it !
To continue, you will specify a path where the file will be stored.
Press "Ok" and the database should create herself without any problems.
ZenPassword files use the .zpdb extension.

The database is composed of two tables :
* Hash : it contains the hash value (signature) of your password (not your password).
* Boite : it contains all the encrypted entries

## Open a database
To open a database click "Open a database" and explore your disk to your .zpdb file. Then a password will be required to unlock it. Enter your password and press "Ok" to access the content.

## Close a database
To close properly your database, you must click "Close database". Using the operating system buttons can have unwanted effects on how your data are cleaned (not verified yet).
## Delete a database
To avoid loss of data into the application, you can't delete a database with it. Whereas, it's still possible to delete it within the operating system explorer, so be careful and backup !

## Managing your entries
Each entry contains several fields :
* A name (not editable yet)
* A login
* A password
* A comment (in case of need)

You can create, edit, and delete entries thanks to the top menubar. You can display content of each entry by clicking "Display entry".

When creating an entry, fields are encrypted thanks to your password and then stored into the database.

## Important informations
* The database structure is not encrypted yet. As a consequence, it is still accessible through database browser, but the content is unreadable.
