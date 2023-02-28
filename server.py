import socket
import threading
import re
import numpy as np
import cv2
from PIL import Image
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = '!disconnect'
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ADDR = (SERVER,PORT)
server.bind(ADDR)

def send(msg,conn,addr):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length= str(msg_length).encode(FORMAT)
    send_length+= b' ' * (64-len(send_length))
    conn.send(send_length)
    conn.send(message)

def recieve_image(conn,addr):
    print(f"[NEW CONNECTION] {addr} connected")
    
    
    connected = True
   
    while connected:
        EndTable = True
        letter_binary = []
        while EndTable:
            msg_length = conn.recv(64).decode(FORMAT)
            if msg_length:
                msg_length= int(msg_length)
                msg = conn.recv(msg_length).decode(FORMAT)
                if msg == "Done":
                    EndTable = False
                else:
                    letter_binary.append([msg[0],msg[1:]])
                
        msg_length = conn.recv(64).decode(FORMAT)
        if msg_length:
            msg_length= int(msg_length)
            bitstring = conn.recv(msg_length).decode(FORMAT)
        print("Binary code generated:")
        for letter in letter_binary:
            print(letter[0], letter[1])
        code = ""
        uncompressed_string =""
        for digit in bitstring:
            code += digit
            pos=0                                        #iterating and decoding
            for letter in letter_binary:
                if code ==letter[1]:
                    uncompressed_string=uncompressed_string+letter_binary[pos] [0]
                    code=""
                pos+=1

        print("Your UNCOMPRESSED data is:")

        temp = re.findall(r'\d+', uncompressed_string)
        res = list(map(int, temp))
        res = np.array(res)
        res = res.astype(np.uint8)
        shape=(480,640,3)
        res = np.reshape(res, shape)
        
        data = Image.fromarray(res)
        data.save('uncompressed.png')
        print("Success")
def send_image(conn,addr):
    ss = input("Whteher want to send image (Y/N)")
    if ss=='Y' or ss=='y':
        ss=True
    else:
        ss=False
    while ss:
        print("Huffman Compression Program")
        print("=================================================================")


        image_name="input.img"
        

        cam = cv2.VideoCapture(0)

        cv2.namedWindow("test")


        while True:
            ret, frame = cam.read()
            if not ret:
                print("failed to grab frame")
                break
            cv2.imshow("test", frame)

            k = cv2.waitKey(1)
            if k%256 == 27:
                #  ESC pressed
                print("Escape hit, closing...")
                break
            elif k%256 == 32:
                # SPACE pressed
                img_name = "input.png"
                cv2.imwrite(img_name, frame)
                print("{} written!".format(img_name))
                break


        cam.release()

        cv2.destroyAllWindows()


        my_string = np.asarray(Image.open(img_name),np.uint8)
        shape = my_string.shape
        a = my_string
        print ("Enetered string is:",my_string)
        my_string = str(my_string.tolist())
    

        letters = []
        only_letters = []
        for letter in my_string:
            if letter not in letters:
                frequency = my_string.count(letter)             #frequency of each letter repetition
                letters.append(frequency)
                letters.append(letter)
                only_letters.append(letter)
        #print(letters)
        nodes = []
        while len(letters) > 0:
            nodes.append(letters[0:2])
            letters = letters[2:]                               # sorting according to frequency
        nodes.sort()
        huffman_tree = []
        huffman_tree.append(nodes)                             #Make each unique character as a leaf node

        def combine_nodes(nodes):
            pos = 0
            newnode = []
            if len(nodes) > 1:
                nodes.sort()
                nodes[pos].append("1")                       # assigning values 1 and 0
                nodes[pos+1].append("0")
                combined_node1 = (nodes[pos] [0] + nodes[pos+1] [0])
                combined_node2 = (nodes[pos] [1] + nodes[pos+1] [1])  # combining the nodes to generate pathways
                newnode.append(combined_node1)
                newnode.append(combined_node2)
                newnodes=[]
                newnodes.append(newnode)
                newnodes = newnodes + nodes[2:]
                nodes = newnodes
                huffman_tree.append(nodes)
                combine_nodes(nodes)
            return huffman_tree                                     # huffman tree generation

        newnodes = combine_nodes(nodes)

        huffman_tree.sort(reverse = True)
        print("Huffman tree with merged pathways:")

        checklist = []
        for level in huffman_tree:
            for node in level:
                if node not in checklist:
                    checklist.append(node)
                else:
                    level.remove(node)
        count = 0
        for level in huffman_tree:
            print("Level", count,":",level)             #print huffman tree
            count+=1
        print()

        letter_binary = []
        
        for letter in only_letters:
            code =""
            for node in checklist:
                if len (node)>2 and letter in node[1]:           #genrating binary code
                    code = code + node[2]
            lettercode =[letter,code]
            letter_binary.append(lettercode)
        print(letter_binary)
        print("Binary code generated:")
        for letter in letter_binary:
            send(letter[0]+letter[1],conn,addr)
        send("Done",conn,addr)    
            

        bitstring =""
        for character in my_string:
            for item in letter_binary:
                if character in item:
                    bitstring = bitstring + item[1]
        send(bitstring,conn,addr)
        ss = input("Whteher want to send image (Y/N)")
        if ss=='Y' or ss=='y':
            ss=True
        else:
            ss=False

def start():
    server.listen()
    print(f"[LISTENING] server is on {SERVER}")
    
    conn,addr = server.accept()
    thread = threading.Thread(target=recieve_image, args=(conn,addr))
    thread1 = threading.Thread(target=send_image, args=(conn,addr))
    thread.start()
    thread1.start()

print("[STARTING] server is starting...")
start()
