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

# Send data should be good
def rdt_send(data, host, port, sequenceNumber):
    data = data.encode()
    size = len(data)
    sequenceNumber 
    
    # Creates tuple
    packet_tuple = (sequenceNumber, size, data)
    packet_structure = struct.Struct(f'I I {MAX_STRING_SIZE}s')
    packed_data = packet_structure.pack(*packet_tuple)

    # Sets checksum as the total of the packed data
    checksum =  bytes(hashlib.md5(packed_data).hexdigest(), encoding="UTF-8")

    # Packs tuple
    packet_tuple = (sequenceNumber,size,data,checksum)
    UDP_packet_structure = struct.Struct(f'I I {MAX_STRING_SIZE}s 32s')
    UDP_packet = UDP_packet_structure.pack(*packet_tuple)

    # Sends tuple
    client_socket.sendto(UDP_packet, (host, port)) 


# Method checks if the data is corrupted or lost from server to client, and continues sending until an unlost acknowledgement is recieved
# should be good
def checkPacket(self, packet):
    # Gets info by breaking down packet
    sequence = packet[0]
    size = packet[1]
    data = packet[2]
    checksum = packet[3]

    # Computes the size of the value of the data sent 
    values = (sequence, size, data)
    packer = struct.Struct(f'I I {MAX_STRING_SIZE}s')
    packed_data = packer.pack(*values)
    computed_checksum =  bytes(hashlib.md5(packed_data).hexdigest(), encoding="UTF-8")
    
    if computed_checksum == checksum:
        return True 
    else:
        return False

# Method checks for acknowledgement on sever side, if acknowledgement is not sent, then resends message/data until acknowledgement is lossless
def getAcknowledgement(message):
    acknowledged = False
    global sequenceNumber
   
    # While an acknowledgement is not recieved
    while (acknowledged == False):
        try:
            # Waits for a response, then gets a message
            time.sleep(2)
            received_packet, addr = client_socket.recvfrom(1024)
            unpacker = struct.Struct(f'I I {MAX_STRING_SIZE}s 32s')
            recieved_UDP_packet = unpacker.unpack(received_packet)
            
            # If the recieved packet has loss, resend
            if (not checkPacket(recieved_UDP_packet)):
                
               # Sends Packet again with same sequence number
               rdt_send(message, host, port, sequenceNumber)
                        
            # Otherwise, if the packet isn't lost, breaks out of the loop
            elif (checkPacket(recieved_UDP_packet)):
                acknowledged = True
            
        except:
            print("Packet was lost, resending")

            # Creates packet adn sends
            rdt_send(message, host, port, sequenceNumber)       

# Signal handler for graceful exiting.  Let the server know when we're gone.

def signal_handler(sig, frame):
    print('Interrupt received, shutting down ...')
    message=f'DISCONNECT {user} CHAT/1.0\n'

    # Creates packet for disconnect message
    rdt_send(message, host, port)

    # Checks if acknowledgement has been recieved, and resends info if data does not match
    getAcknowledgement(message)

    # Exits  
    sys.exit(0)


# Simple function for setting up a prompt for the user.

def do_prompt(skip_line=False):
    if (skip_line):
        print("")
    print("> ", end='', flush=True)

# Read a single line (ending with \n) from a socket and return it.
# We will strip out the \r and the \n in the process.

def get_line_from_socket(sock):

    done = False
    line = ''
    while (not done):
        char = sock.recv(1).decode()
        if (char == '\r'):
            pass
        elif (char == '\n'):
            done = True
        else:
            line = line + char
    return line

# Function to handle incoming messages from server.  Also look for disconnect messages to shutdown and messages for sending and receiving files.

def handle_message_from_server(sock, mask):
    message=get_line_from_socket(sock)
    words=message.split(' ')
    print()

    # Handle server disconnection.

    if words[0] == 'DISCONNECT':
        print('Disconnected from server ... exiting!')
        sys.exit(0)

    # Handle file attachment request.

    elif words[0] == 'ATTACH':
        sock.setblocking(True)
        filename = words[1]
        if (os.path.exists(filename)):
            filesize = os.path.getsize(filename)

            # stores the length of the file
            header = f'Content-Length: {filesize}\n'
          
            # Creates packet storing info 
            global sequenceNumber
            sequenceNumber = (sequenceNumber + 1) % 2
            rdt_send(header, host, port, sequenceNumber)

            # Tries to get acknowledgment from server
            getAcknowledgement(header)

            # Sends and encodes lines of file in binary
            with open(filename, 'rb') as file_to_send:
                while True:
                    chunk = file_to_send.read(BUFFER_SIZE)
                    if chunk:

                        sequenceNumber = (sequenceNumber + 1) % 2
                        # Sends tuples in a UDP format
                        rdt_send(chunk, host, port, sequenceNumber)

                        # Gets acknowledgement
                        getAcknowledgement(message)
                                        
        else:
            header = f'Content-Length: -1\n'

            sequenceNumber = (sequenceNumber + 1) % 2

            # Sends packet
            rdt_send(header, host, port, sequenceNumber) 

            # Tries to get acknowledgment from server
            getAcknowledgement(header)

        sock.setblocking(False)
            
    # Handle file attachment request.

    elif words[0] == 'ATTACHMENT':
        filename = words[1]
        sock.setblocking(True)

        # Gets filename and length
        print(f'Incoming file: {filename}')
        origin=get_line_from_socket(sock)
        print(origin)
        contentlength=get_line_from_socket(sock)
        print(contentlength)

        # Prints error if attachment invalid
        length_words = contentlength.split(' ')
        if (len(length_words) != 2) or (length_words[0] != 'Content-Length:'):
            print('Error:  Invalid attachment header')
        else:
            bytes_read = 0
            bytes_to_read = int(length_words[1])
            with open(filename, 'wb') as file_to_write:
                while (bytes_read < bytes_to_read):

                    # Recieves chunk
                    chunk = sock.recv(BUFFER_SIZE)
                    bytes_read += len(chunk)
                    file_to_write.write(chunk)
        sock.setblocking(False)
        do_prompt()

    # Handle regular messages.

    else:
        print(message)
        do_prompt()

# Function to handle incoming messages from server.

def handle_keyboard_input(file, mask):
    line=sys.stdin.readline()
    message = f'@{user}: {line}'

    global sequenceNumber
    sequenceNumber = (sequenceNumber + 1) % 2

    # Sends packet
    client_socket.sendto(message, host, port, sequenceNumber) 

    # Tries to get acknowledgment from server
    getAcknowledgement(message)

    do_prompt()

# Our main function.

def main():

    global user
    global client_socket
    global host
    global port
    global sequenceNumber

    # Register our signal handler for shutting down.

    signal.signal(signal.SIGINT, signal_handler)

    # Check command line arguments to retrieve a URL.

    parser = argparse.ArgumentParser()
    parser.add_argument("user", help="user name for this user on the chat service")
    parser.add_argument("server", help="URL indicating server location in form of chat://host:port")
    parser.add_argument('-f', '--follow', nargs=1, default=[], help="comma separated list of users/topics to follow")
    args = parser.parse_args()

    # Check the URL passed in and make sure it's valid.  If so, keep track of
    # things for later.

    try:
        server_address = urlparse(args.server)
        if ((server_address.scheme != 'chat') or (server_address.port == None) or (server_address.hostname == None)):
            raise ValueError
        host = server_address.hostname
        port = server_address.port
    except ValueError:
        print('Error:  Invalid server.  Enter a URL of the form:  chat://host:port')
        sys.exit(1)
    user = args.user
    follow = args.follow

    #Now we try to make a connection to the server.

    print('Connecting to server ...')
    try:
        client_socket.connect((host, port))
    except ConnectionRefusedError:
        print('Error:  That host or port is not accepting connections.')
        sys.exit(1)

    # The connection was successful, so we can prep and send a registration message.
    
    print('Connection to server established. Sending intro message...\n')
    message = f'REGISTER {user} CHAT/1.0\n'

    # Sends packet
    sequenceNumber = (sequenceNumber + 1) % 2
    client_socket.sendto(message, host, port, sequenceNumber) 

    # Tries to get acknowledgment from server
    getAcknowledgement(message)

    # client_socket.send(message.encode())

    # If we have terms to follow, we send them now.  Otherwise, we send an empty line to indicate we're done with registration.

    if follow != []:
        message = f'Follow: {follow[0]}\n\n'
    else:
        message = '\n'

    # Sends packet
    client_socket.sendto(message, host, port, sequenceNumber) 

    # Tries to get acknowledgment from server
    getAcknowledgement(message)
    # client_socket.send(message.encode())
   
    # Receive the response from the server and start taking a look at it

    response_line = get_line_from_socket(client_socket)
    response_list = response_line.split(' ')
        
    # If an error is returned from the server, we dump everything sent and
    # exit right away.  
    
    if response_list[0] != '200':
        print('Error:  An error response was received from the server.  Details:\n')
        print(response_line)
        print('Exiting now ...')
        sys.exit(1)   
    else:
        print('Registration successful.  Ready for messaging!')

    # Set up our selector.

    client_socket.setblocking(False)
    sel.register(client_socket, selectors.EVENT_READ, handle_message_from_server)
    sel.register(sys.stdin, selectors.EVENT_READ, handle_keyboard_input)
    
    # Prompt the user before beginning.

    do_prompt()

    # Now do the selection.

    while(True):
        events = sel.select()
        for key, mask in events:
            callback = key.data
            callback(key.fileobj, mask)    



if __name__ == '__main__':
    main()
