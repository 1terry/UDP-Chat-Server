import socket
import os
import signal
import sys
import sys
import argparse
from urllib.parse import urlparse
import selectors
import socket
import struct
import hashlib
import time

from sample_client import UDP_IP, UDP_PORT

# Define a constant for our buffer size

BUFFER_SIZE = 1024

# Selector for helping us select incoming data from the server and messages typed in by the user.

sel = selectors.DefaultSelector()

# Socket for sending messages.

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = "localHost"
port = 0
sampleData = "hi"

# User name for tagging sent messages.

user = ''

# Sequence number and size
sequenceNumber = 0
size = 0
data = ""
# UDP Packet and port

# Should this be buffer size?
MAX_STRING_SIZE = 256

# Client address and port
socketInfo = client_socket.getpeername()

print(socketInfo[1])