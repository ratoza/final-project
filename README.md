Prerequist for database:
1. Create an account on [Firebase](https://firebase.google.com)
2. Create a project
3. Go to `Settings` -> `Project Settings` -> `Service Accounts`
4. Press on `Generate new private key`
5. Rename the file to `ServerAccountKey.json` and move it to the root of the project
6. After that run the project and it will create for you a collection name `Todo` and document `todo_list` where inside this document there is an array called `data` that contains all the todo

For kivy:
`pip3 install kivy`

You need to have firebase_admin module to connect to the database:
Make sure to `pip3 install firebase_admin`

To run the project:
`python3 todo.py`