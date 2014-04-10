ClientServerPython
==================

Python implementation of a client-server architecture.

## Requirements

* Python 3.3

## Launch server

Launch the script with :
```
python ./Server.py port
```

Arguments : 
* **port** : Port to use to receive connections (default: 1991).

## Launch client

Launch the script with :
```
python ./Client.py ip port
```

Arguments : 
* **ip** : Server IP with which to communicate.
* **port** : Port to use to communicate with the server (default: 1991).

## Commands available by default

Command | Parameters | Action
--- | --- | ---
HELLO | - | Say hello to the server, and the server respond with his name.
CLOSE | - | Close connection to the server.

## Hooks command

### Server side

When the server receive a command from a client, you can hook this command and make a special action. To do that, you have to create a function (suffixed by ```Request``` by convention) to do the command action. For example : 
```python
def whatTimeRequest(thread):
	thread.send("TIME " + datetime.now().strftime('%d.%m.%Y %H:%M:%S'))
```

For this example, don't forget to import ```datetime```.

Now in ```ThreadClient``` class, add to the function dictionary (class static member) a line to register your function to hook the command. In our example :
```python
functionArray = OrderedDict([
		...
		(r"TIME", whatTimeRequest),
		...
	])
```

And it's done for the server part !

### Client side

For the client, we have two scenarios :

**The client send a message to the server**

To hook the message to send to the server, we need to implement a function (suffixed by ```Request``` by convention). In our example : 
```python
def timeRequest(thread):
	thread.connection.send(prepareString(thread.message))
```

And to register this hook function, we add an element to the function dictionary in ```ThreadSending``` class. The key is the regex used to know if it's the function to use for the current sending message. In our example :
```python
functionArray = OrderedDict([
		...
		(r"TIME .*", timeRequest, 
		...
	])
```

**The client receive a message from the server**

To hook the message sent from the server, we need to implement a function (suffixed by ```Response``` by convention). In our example : 

```python
def timeResponse(thread):
	print(thread.message.replace("TIME ", ""))
```

And to register this hook function, we add an element to the function dictionary in ```ThreadReception``` class. The key is the regex used to know if it's the function to use for the current receiving message. In our example :
```python
functionArray = OrderedDict([
		...
		(r"TIME", timeRequest),
		...
	])
```

## Feedback

Don't hesitate to fork this project, improve it and make a pull request.

## License

This project is under Apache 2.0 License.
