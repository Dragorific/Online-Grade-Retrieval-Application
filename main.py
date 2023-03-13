# Online Grade Retrieval Server and Client
# Using sockets and encryption
# By Sama, Yasmeen and Umar

import socket
import argparse
from cryptography.fernet import Fernet
import csv
import datetime

class Student:
    # Creating Student object/class to hold all the info
    def __init__(self, name, student_number, key, lab1, lab2, lab3, lab4, midterm, exam1, exam2, exam3, exam4):
        self.name = name
        self.student_num = student_number
        self.key = key
        self.lab1 = lab1
        self.lab2 = lab2
        self.lab3 = lab3
        self.lab4 = lab4
        self.midterm = midterm
        self.exam1 = exam1
        self.exam2 = exam2
        self.exam3 = exam3
        self.exam4 = exam4

    # All Accessor Methods
    def getName(self):
        return str(self.name)
    
    def getKey(self):
        return str(self.key)

    def getLab1(self):
        return self.lab1
    
    def getLab2(self):
        return self.lab2
    
    def getLab3(self):
        return self.lab3
    
    def getLab4(self):
        return self.lab4
    
    def getMidterm(self):
        return self.midterm
    
    def getExam(self):
        return (int(self.exam1) + int(self.exam2) + int(self.exam3) + int(self.exam4))/4
    
    def getGrades(self):
        return ("\nLab 1: " + str(self.lab1) + "\nLab 2: "+ str(self.lab2) + "\nLab 3: "+ str(self.lab3) + 
                "\nLab 4: "+ str(self.lab4) + "\nMidterm: "+ str(self.midterm) + "\nExam 1: "+ str(self.exam1) + 
                "\nExam 2: "+ str(self.exam2) + "\nExam 3: "+ str(self.exam3) + "\nExam 4: "+ str(self.exam4))

# Server class that runs a server constantly listening for client connections and commands  
class Server:
    PORT = 8080
    server_dict = {}

    def __init__(self, host, port):
        # Read through the csv file and each row creates a new student object
        with open('course_grades_2023.csv', 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                # Print out each line as per requirements
                print(row)
                Server.server_dict[row[1]] = Student(row[0], row[1], row[2], row[3], 
                                                     row[4], row[5], row[6], row[7], 
                                                     row[8], row[9], row[10], row[11])
        
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
                
        # Loop to keep finding new client connections
        while True:
            # Extract current system time
            formatted_time = Client.time()
            
            print(f"{formatted_time}: Listening for connections on port: {port}")
            # Try to see if the socket can listen, if it can't, it has been closed
            try:
                self.server_socket.listen()
            except:
                print(f"{formatted_time}: Server socket {self} is closed from invalid student ID.")
                break
            
            conn, addr = self.server_socket.accept()
            formatted_time = Client.time()
            print(f"{formatted_time}: Connected by {addr}")
            
            # Continuously accept data until the returned data is zero or empty
            while True:
                data = conn.recv(1024)
                if data:
                    # Extract current system time
                    formatted_time = Client.time()

                    data_decoded = data.decode('utf-8')
                    # If the response is the student number, then respond back greeting the user, and continue the loop because
                    # no other command is provided (skip all the if/elif)
                    if(len(data_decoded) < 8 and (data_decoded in Server.server_dict.keys())):
                        # Get the user information and create greeting message, encode into bytes
                        currStudent = Server.server_dict.get(data_decoded)
                        print(f"{formatted_time}: User found, successfully connected with " + currStudent.getName() + "'s profile")
                        response = currStudent.getKey()
                        response = response.encode('utf-8')

                        # Send encryption key to client
                        conn.sendall(response)
                        continue

                    elif(len(data_decoded) < 8 and (data_decoded not in Server.server_dict.keys())):
                        # If the user is not found, print a message to the server log and close the socket server, as per requirements
                        print(f"{formatted_time}: Incorrect Student ID, server shutting down")
                        self.server_socket.close()
                        break
                            
                    try:
                        id, command = data_decoded.split(",")
                        currStudent = Server.server_dict.get(id)
                        encryption_key = currStudent.getKey()
                    except:
                        print(f"{formatted_time}: Incorrect Student ID, server shutting down")
                        self.server_socket.close()
                        break
                    
                    # When it is not just the student number
                    # Encrypt the message based on student cryptography key value
                    encryption_key_bytes = encryption_key.encode('utf-8')
                    fernet = Fernet(encryption_key_bytes)

                    # Echo user command as per requirements
                    print(f"{formatted_time}: User inputted <{command}>")
                    grade = 0

                    if command == "GL1A":
                        for key in Server.server_dict.keys():
                            currStudent = Server.server_dict.get(key)
                            grade += int(currStudent.getLab1())

                        grade = grade / len(Server.server_dict.keys())
                    elif command == "GL2A":
                        for key in Server.server_dict.keys():
                            currStudent = Server.server_dict.get(key)
                            grade += int(currStudent.getLab2())

                        grade = grade / len(Server.server_dict.keys())
                    elif command == "GL3A":
                        for key in Server.server_dict.keys():
                            currStudent = Server.server_dict.get(key)
                            grade += int(currStudent.getLab3())

                        grade = grade / len(Server.server_dict.keys())
                    elif command == "GL4A":
                        for key in Server.server_dict.keys():
                            currStudent = Server.server_dict.get(key)
                            grade += int(currStudent.getLab4())

                        grade = grade / len(Server.server_dict.keys())
                    elif command == "GMA":
                        for key in Server.server_dict.keys():
                            currStudent = Server.server_dict.get(key)
                            grade += int(currStudent.getMidterm())

                        grade = grade / len(Server.server_dict.keys())
                    elif command == "GEA":
                        for key in Server.server_dict.keys():
                            currStudent = Server.server_dict.get(key)
                            grade += int(currStudent.getExam())

                        grade = grade / len(Server.server_dict.keys())
                    elif command == "GG":
                        grade = str(grade)[1:] + currStudent.getGrades()

                    # Encode the grade value into bytes and encrypt with user key
                    grade = str(grade)
                    grade = grade.encode('utf-8')
                    encrypted_message_bytes = fernet.encrypt(grade)
                    
                    # Send the encrypted bytes over TCP
                    conn.sendall(encrypted_message_bytes)
                else:
                    print(f'{formatted_time}: Connection closed from client at: {addr}')
                    break

# Client class that runs a client in the terminal to communicate with the server
class Client:
    # Dictionary holds all the command -> output pairings
    commandDict = {
        "GMA" : "Midterm Average",
        "GEA" : "Exam Average",
        "GL1A" : "Lab 1 Average",
        "GL2A" : "Lab 2 Average",
        "GL3A" : "Lab 3 Average",
        "GL4A" : "Lab 4 Average",
        "GG" : "Grades"
    }

    def __init__(self, host, port):
        formatted_time = Client.time()

        print(f"{formatted_time}: We have created a Client object: {self}")  
        self.student_number = input(f"{formatted_time}: Enter your Student ID: ")
        
        formatted_time = Client.time()

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))
        self.client_socket.sendall(self.student_number.encode('utf-8'))
        
        response = self.client_socket.recv(1024)
                
        # Encrypt the message based on student cryptography key value
        if response:
            encryption_key_bytes = response
            fernet = Fernet(encryption_key_bytes)
        
            # prompt the student for a command
            formatted_time = Client.time()
            command = input(f'{formatted_time}: Enter a command: ')
            
            # echo the command
            if command in Client.commandDict.keys():
                print(f'{formatted_time}: Command entered:', command)
                print(f"{formatted_time}: Fetching {Client.commandDict[command]}: ", end="")
                
                message = self.student_number + "," + command
                self.client_socket.sendall(message.encode('utf-8'))
                
                output = self.client_socket.recv(1024)
                decoded_output = fernet.decrypt(output)
                print(decoded_output.decode('utf-8'))
            else:
                print(f'{formatted_time}: Invalid Command')

            self.client_socket.close()
        else:
            print(f"{formatted_time}: Invalid Student ID inputted, server has been closed.")


    def time():
        return (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")

        
if __name__ == '__main__':
    
    roles = {'client': Client,'server': Server}
    parser = argparse.ArgumentParser()
    defaultHost = socket.gethostname()
    parser.add_argument('-r', '--role', choices=roles, help='Server or Client Role', required=True, type=str)
    parser.add_argument('--host', default=defaultHost, help="Server Host", type=str)
    parser.add_argument('--port', default=8080, help="Server Port", type=int)

    args = parser.parse_args()

    roles[args.role](args.host, args.port)