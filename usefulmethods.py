# Starts a timer and awaits response to check if it is valid
# Returns true if there is a packet recieved within the time and it is full
# Otherwise, returns false and will be called again

# def getTimeout(t):
#     while t:
#         # Waits one sec
#         mins, secs = divmod(t, 60)
#         timer = '{:02d}:{:02d}'.format(mins, secs)
#         print(timer, end="\r")
#         time.sleep(1)

#         try:
#             # Tries recieving and upacking packet
#             received_packet, addr = client_socket.recvfrom(1024)
#             unpacker = struct.Struct(f'I I {MAX_STRING_SIZE}s 32s')
#             recieved_UDP_packet = unpacker.unpack(received_packet)

#             # If the packet is complete, we continue, otherwise keep sending packets
#             if (checkPacket(recieved_UDP_packet)):
#                 return True

#             elif (not checkPacket(recieved_UDP_packet)):
#                 return False

#             else:
#                 return False
        
#         except:
#             return False

#         t -= 1

#     return False