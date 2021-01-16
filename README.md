# UP_Firefly_API_Connector
API that connects Firefly III by James Cole to your UP bank accounts for auto updates.
Currently this project is just a webhook that runs on FLask & python.
In the future I will create a script that reduces the amount of work the user has to do to get their connector working. I will also improve the code a lot in the future.
There might be bugs here and there, but I have found it to work pretty well over the past month of testing.
See https://blog.dupreez.id.au/2021/01/automatically-update-firefly-iii-with-up-banking-transactions/ for detailed instructions on installing and using the connector API. 
Feel free to give any feedback or send through questions to gustavdprz@gmail.com


To-Dos:
->Update install guide to run the app on secure webserver like apache instead of dev flask server
->Implement security features to validate incoming data is from UP instead of bots
->Bug fix sometimes missing transactions if they happen in close succession
->Clean code for easier deployment
->Improve documentation to be more beginner friendly
