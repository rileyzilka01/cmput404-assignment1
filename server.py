#  coding: utf-8 
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):

    def handle(self):
        #self.request is the socket
        self.data = self.request.recv(1024)
        #print (f"Got a request of: {self.data}") #Prints the entire request with headers, if no file requested

        args = self.data.decode('utf8').split(" ") #Split up the request for headers
        if len(args) <= 1: #If there are no args after the method (rare case which causes errors)
            return
        method = args[0]
        url = args[1]
        #print(f"Request Method: {method}\nRequested File: {url}\n") #Debug string for developers

        if method != "GET": #If the method is not GET return 405 and break
            status_line = "HTTP/1.1 405 Method Not Allowed\r\n"
            response = status_line
            self.request.sendall(response.encode())
            return

        if url == '/deep': #for known directory inside www, redirect to 127.0.0.1:8080/deep/
            status_line = "HTTP/1.1 301 Moved Permanently\r\n"
            location_header = f"Location: {url}/\r\n"
            response = status_line + location_header
            self.request.sendall(response.encode())

        self.sendFile(url) #Send the requested file (Only GET requests are allowed)
       

    def sendFile(self, url):
        '''
        This method will take the url and send the requested file with the header
        One note is that the response
        '''
        url = url.split("?")[0] #Remove the paramters
        ftype, body, code = self.loadFile(url) #Get the body (html content)
        head = f"HTTP/1.1 {code} OK\r\nContent-Type: text/{ftype}\r\n\n" #Create the response header
        response = head + body #Join the head and body
        self.request.send(response.encode()) #Send response

    def loadFile(self, url):
        '''
        This method will attempt to open the file requested, 
        If the file exists it will return a 200 code and the file
        If it doesnt exist it will return a 404 code and the 404 HTML page
        '''
        if url[-1] == '/': #If the url ends with a / assume we are in a directory
            url += 'index.html'
            ftype = 'html'
        elif url.split('.')[-1] not in ['html', 'css']: #If file type is not html or css
            ftype = 'plain'
        else: #Else set the file type to the end of the file
            ftype = url.split('.')[-1]
        	
        if url in self.compileFiles(): #If the file is in the www directory
            with open('www'+url, 'r') as f:
                response = f.read()
                f.close()
            code = 200
        else: #Otherwise open the 404 file and return
            f = open('www/404.html', 'r')
            response = f.read()
            f.close()
            code = 404
            ftype = 'html'

        return ftype, response, code

    def compileFiles(self):
        path = './www'
        file_list = []
        #Get all files and nested files
        for root, dirs, files in os.walk(path):
            for file in files:
                file_list.append(root+'/'+file)

        #Adjust file names and remove www root
        for i in range(len(file_list)):
            file_list[i] = file_list[i][5:]
            file_list[i] = file_list[i].replace('\\', '/')
        return file_list

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
