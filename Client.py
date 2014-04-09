#!/usr/bin/python
# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------#
# Client / Server Architecture                                                 #
# ============================================================================ #
# Developer:    Chavaillaz Johan                                               #
# Filename:     Client.py                                                      #
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

def messageResponse(thread):
	print(thread.message.replace("MSG ", ""))

def closeConnectionResponse(thread):
	thread.closeConnection = True
	print("The connection to the server has been closed.")

#------------------------------------------------------------------------------#
#                                                                              #
#                              RESPONSE FUNCTIONS                              #
#                                                                              #
#------------------------------------------------------------------------------#

def messageRequest(thread):
	thread.connection.send(prepareString(thread.message))

def closeRequest(thread):
	messageRequest(thread)
	thread.closeConnection = True

#------------------------------------------------------------------------------#
#                                                                              #
#                                   CLASSES                                    #
#                                                                              #
#------------------------------------------------------------------------------#

class Settings:
	"""Store settings of the client"""
	data = {}

class ThreadReception(threading.Thread):
	"""Manages the reception of messages"""
	
	functionArray = OrderedDict([
		(r"MSG .*", messageResponse),
		(r"CLOSE CONFIRM", closeConnectionResponse),
	])
	
	def __init__(self, connection, sendingThread):
		threading.Thread.__init__(self)
		self.connection = connection
		self.message = ""
		self.sendingThread = sendingThread
		self.closeConnection = False
       
	def run(self):
		while not self.closeConnection:
			try:
				character = self.connection.recv(1)
				
				if character == b'\n':
					
					for regex, function in ThreadReception.functionArray.items():
						if re.match(regex, self.message):
							function(self)
							break
					
					self.message = ""
				else:
					self.message += character.decode("UTF-8")
			
			except ConnectionResetError:
				print("connection dropped by the server.")
				break
			
			except KeyboardInterrupt:
				print("Client shut down (Keyboard interrupt)")
				break
		
		# Force closing sending thread
		self.sendingThread._stop()
		self.connection.close()

class ThreadSending(threading.Thread):
	"""Manages the sending of messages"""
	
	functionArray = OrderedDict([
		(r"CLOSE", closeRequest),
		(r".*", messageRequest),
	])
	
	def __init__(self, connection):
		threading.Thread.__init__(self)
		self.connection = connection
		self.closeConnection = False
		self.message = ""

	def run(self):
		while not self.closeConnection:
			try:
				self.message = input()
				
				for regex, function in ThreadSending.functionArray.items():
					if re.match(regex, self.message):
						function(self)
						break
			
			except KeyboardInterrupt:
				print("Client shut down")
				break

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
		description='Server instance for challenge response application.'
	)
	parser.add_argument(
		'server', 
		type=str,
		help='IP server with which to communicate.'
	)
	parser.add_argument(
		'port', 
		nargs='+',
		type=str,
		help='Port to use to communicate with the server (Default: 1991).'
	)

	# Show help if one of the arguments is missing
	if argsCount not in [2, 3]:
		parser.print_help()
		sys.exit()
	
	# Get configuration
	host = sys.argv[1]
	port = int(sys.argv[2]) if argsCount == 3 else 1991

	# Connection establishment
	connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		connection.connect((host, port))
	
	except socket.error:
		print("Can't connect to server host.")
		sys.exit(0)
	
	else:
		print("Connection established with the server.")
	
	# Launches two threads to independently manage
	# transmission and reception of messages
	threadSending = ThreadSending(connection)
	threadReception = ThreadReception(connection, threadSending)
	threadSending.start()
	threadReception.start()        