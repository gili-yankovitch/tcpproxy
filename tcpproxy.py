#!/usr/bin/python3

from socket import *
import argparse
import select
import logging

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
logger = logging.getLogger("TCP Proxy")
logger.setLevel(logging.INFO)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)


def proxy(listenAddr, proxyAddr, chunkSize = 1024):
	listenIP, listenPort = listenAddr.split(':')
	proxyIP, proxyPort = proxyAddr.split(':')

	listenSocket = socket()
	listenSocket.bind((listenIP, int(listenPort)))
	listenSocket.listen()

	pollObj = select.poll()
	pollObj.register(listenSocket, select.POLLIN)

	# Initialize proxy map
	# This maps every socket to its proxy counterpart
	# socket object. So at any given moment, one can retrieve
	# the two objects together.
	proxyMap = {}

	while True:
		events = pollObj.poll()

		for desc, event in events:
			# New connection
			if desc == listenSocket.fileno():
				clientSocket, _ = listenSocket.accept()

				# Open a proxy connection
				proxySocket = socket()
				proxySocket.connect((proxyIP, int(proxyPort)))

				# List them in map
				proxyMap[clientSocket.fileno()] = proxySocket
				proxyMap[proxySocket.fileno()] = clientSocket

				pollObj.register(clientSocket, select.POLLIN | select.POLLHUP | select.POLLERR)
				pollObj.register(proxySocket, select.POLLIN | select.POLLHUP | select.POLLERR)

				logger.info(f"ACPT ({clientSocket.fileno()}, {proxySocket.fileno()})")
			elif (event & (select.POLLIN | select.POLLHUP | select.POLLERR | select.POLLNVAL)) != 0:
				outgoingSocket = proxyMap[desc]
				incomingSocket = proxyMap[outgoingSocket.fileno()]

				if event == select.POLLIN:
					data = incomingSocket.recv(chunkSize)

					if len(data) == 0:
						logger.info(f"TERM ({incomingSocket.fileno()}, {outgoingSocket.fileno()})")

						# Unregister from poll
						pollObj.unregister(incomingSocket)
						pollObj.unregister(outgoingSocket)

						# Close connections
						incomingSocket.close()
						outgoingSocket.close()

						continue

					logger.info(f"COMM ({incomingSocket.fileno()} -> {outgoingSocket.fileno()})")

					# Send data to the other end
					outgoingSocket.send(data)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="End-to-end TCP Proxy")
	parser.add_argument("listenAddr", type = str)
	parser.add_argument("proxyAddr", type = str)
	parser.add_argument("--chunkSize", default = 1024)
	args = parser.parse_args()

	proxy(args.listenAddr, args.proxyAddr, args.chunkSize)

