# What is this?

This is a bot that is used for communication between (mainly) Tatarsan orphanage alumni and orphans to get help from volunteers. The bot communicates in Russian and English.

There are 4 types of help that can be provided:
- Tutor help
- Psychologist help
- Lawyer help
- Other type of request

There is an admin who receives the messages and can find people to fulfil the request.
On the admin's side there is a group of volunteers and a manual of rules for providing help to orphanage graduates. The manual was created with the help of Innopolis University professors and other volunteers.

# How does the bot work?

There are 2 main tasks that the bot performs and a few additional ones. Each function is done asynchronously, at any step of the process the person can cancel and start from the beginning.

Registration process
* The registration process consists of filling in fields such as: name, age, region, orphanage name, status of the person (alumni/not).
* A person can try to register as many times as they want, but the person will only be added to the database once. Subsequent attempts will only rewrite the fields except User ID.

Requesting help
* Once a person is registered, they can request help.
* The request procedure consists of selecting the type of help from list provided above, writing the problem and lastly verifying and saving the message.

## Additional Functions

Reporting errors
* If there is an error while working with a bot, a person can send a message reporting the problem they encountered. The message will be forwarded to the admin. 

Changing the language of communication
* There are two languages available: English and Russian
