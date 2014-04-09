#!/usr/bin/python
# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------#
# Client / Server Architecture                                                 #
# ============================================================================ #
# Developer:    Chavaillaz Johan                                               #
# Filename:     Server.py                                                      #
# Version:      1.0                                                            #
#                                                                              #
# Licensed to the Apache Software Foundation (ASF) under one                   #
# or more contributor license agreements. See the NOTICE file                  #
# distributed with this work for additional information                        #
# regarding copyright ownership. The ASF licenses this file                    #
# to you under the Apache License, Version 2.0 (the                            #
# "License"); you may not use this file except in compliance                   #
# with the License. You may obtain a copy of the License at                    #
#                                                                              #
# http://www.apache.org/licenses/LICENSE-2.0                                   #
#                                                                              #
# Unless required by applicable law or agreed to in writing,                   #
# software distributed under the License is distributed on an                  #
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY                       #
# KIND, either express or implied. See the License for the                     #
# specific language governing permissions and limitations                      #
# under the License.                                                           #
#                                                                              #
#------------------------------------------------------------------------------#

#------------------------------------------------------------------------------#
#                                                                              #
#                               LIBRARIES IMPORT                               #
#                                                                              #
#------------------------------------------------------------------------------#

import socket
import sys
import threading
import argparse
import re
from collections import OrderedDict

#------------------------------------------------------------------------------#
#                                                                              #
#                             UTILITIES FUNCTIONS                              #
#                                                                              #
#------------------------------------------------------------------------------#

def prepareString(content):
	return bytes(content + "\n", 'UTF-8')

def getArguments(message):
	return message.split(" ")[1:]

#------------------------------------------------------------------------------#
#                                                                              #
#                              RESPONSE FUNCTIONS                              #
#                                                                              #
#------------------------------------------------------------------------------#

def helloRequest(thread):
	thread.send("MSG Hello from " + socket.gethostname())

def closeConnectionRequest(thread):
	thread.closeConnection = True
	thread.send("CLOSE CONFIRM")

def notFoundRequest(thread):
	thread.send("MSG Command not found")

#------------------------------------------------------------------------------#
#                                                                              #
#                                   CLASSES                                    #
#                                                                              #
#------------------------------------------------------------------------------#

class ThreadClient(threading.Thread):
	"""Manage each client connection to the server in a new thread"""
	
	functionArray = OrderedDict([
		(r"HELLO", helloRequest),
		(r"CLOSE", closeConnectionRequest),
		(r".*", notFoundRequest),
	])
	
	def __init__(self, connection):
		threading.Thread.__init__(self)
		self.connection = connection
		self.closeConnection = False
		
		self.data = {}
		self.data['message'] = ""
		
		print("%s connected" % self.getName())
	
	def send(self, message):
		print("%s -> %s" % (self.getName(), message))
		self.connection.send(prepareString(message))

	def run(self):
		try:
			while not self.closeConnection:
				
				character = self.connection.recv(1)
				
				if character == b'\n':
				
					print("%s <- %s" % (self.getName(), self.data['message']))
					
					for regex, function in ThreadClient.functionArray.items():
						if re.match(regex, self.data['message']):
							function(self)
							break
					
					self.data['message'] = ""
				else:
					self.data['message'] += character.decode('UTF-8')
				
		except ConnectionResetError:
			print("%s has reset connection" % self.getName())
		
		# Close connection
		self.connection.close()
		del connectionList[self.getName()]
		print("%s disconnected" % self.getName())

#------------------------------------------------------------------------------#
#                                                                              #
#                               "MAIN" FUNCTION                                #
#                                                                              #
#------------------------------------------------------------------------------#

# If this is the main module, run this
if __name__ == '__main__':
	argsCount = len(sys.argv)

	# Create argument parser to help user
	parser = argparse.ArgumentParser(
		description='Server instance for client-server communication.'
	)
	parser.add_argument(
		'port', 
		nargs='+',
		type=str,
		help='Port to use to receive connections (Default: 1991).'
	)

	# Show help if one of the arguments is missing
	if argsCount not in [1, 2]:
		parser.print_help()
		sys.exit()
	
	# Get configuration
	host = '127.0.0.1'
	port = int(sys.argv[1]) if argsCount == 3 else 1991
	
	# Server initialization
	serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		serverSocket.bind((host, port))
	except socket.error:
		print("Socket creation failed, maybe the port is already in use ?")
		sys.exit()
	
	# Listen new connection
	print("Server ready, waiting for requests ...")
	serverSocket.listen(1)

	# Connection list (clients)
	connectionList = {}
	
	try:
		while True:    
			connection, adresse = serverSocket.accept()
			
			# Start a new client
			thread = ThreadClient(connection)
			thread.start()
			
			# Store connection
			id = thread.getName()
			connectionList[id] = connection
			
			# Send a welcome message
			thread.send("MSG Welcome aboard !")
	
	except KeyboardInterrupt:
		print("Server shut down")
