"""
This script runs the FlaskWebProject1 application using a development server.
"""

from os import environ
from networkSpeaker import app
from networkSpeaker.views import *
from networkSpeaker.remantek import *

import threading
import socket

import subprocess, os


def getData_temperature():
    while True:    
        gVar.valTemperature.clear()
        gVar.valHumidity.clear()
        
        for idx in range(0, 10):
            valTemperature = random.randint(0,100)
            valHumidity = random.randint(20,100)	
            gVar.valTemperature.append({'index': idx, 'value': valTemperature})
            gVar.valHumidity.append({'index': idx, 'value': valHumidity})
    
        timestamps = [data['index'] for data in gVar.valTemperature]

        valTemperature = [data['value'] for data in gVar.valTemperature]
        valHumidity = [data['value'] for data in gVar.valHumidity]
    
        print("read new data!!!")

        fig, axes = plt.subplots(nrows=3, ncols=3)
        
        axes[0,2].plot(timestamps, valTemperature)
        axes[0,2].set_title('Temperature Sensor Data')
        axes[0,2].set_xlabel('Timestamp')
        axes[0,2].set_ylabel('Temperature')
        
        axes[1,1].plot(timestamps, valHumidity)
        axes[1,1].set_title('Humidity Sensor Data')
        axes[1,1].set_xlabel('Timestamp')
        axes[1,1].set_ylabel('Humidity')

        plt.savefig('networkSpeaker/static/graph.png')
        plt.cla()    
        #os.system(f"sudo cp graph.png ./networkSpeaker/static/")
    
        time.sleep(8)
        #gVar.pathPicture = './networkSpeaker/static/graph.png'
        #plt.show()
        #return 'garosu test'

 
def tcpip_server_tread():
    # Create a TCP/IP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_address = (gVar.ip_address, 12345)  
    #server_address = ('192.168.1.71', 12345)  
    server_socket.bind(server_address)

    # Listen for incoming connections
    server_socket.listen(1)

    print(f"Server is listening on {server_address[0]}:{server_address[1]}")
    
    while True:
        # Wait for a connection
        print("Waiting for a connection...")
        client_socket, client_address = server_socket.accept()
        print(f"Received connection from {client_address[0]}:{client_address[1]}")

        try:
            # Receive data from the client
            data = client_socket.recv(1024)
            if data:
                print(f"Received data from client: {data.decode()}")
                tmpData = data.decode()
                rcvData = tmpData.split(',')
                print(rcvData)
            
                if len(rcvData) > 0:
                    if rcvData[1] == 'play_welcome':
                        playalarm_fromCamera('alarm/welcome.wav')
                    elif rcvData[1] == 'play_dontcounter':
                        print("i receive dont enter counter")
                        #stop_vlcPlayer()
                        playalarm_fromCamera('alarm/dontEnterOffice.wav')
                    elif rcvData[1] == 'play_dontoffice':
                        print("i receive dont enter office")
                        #stop_vlcPlayer()
                        playalarm_fromCamera('alarm/dontEnterCounter.wav')
                    else:
                        print("it is non official!!")					    
            
        finally:
            # Clean up the connection
            client_socket.close()

                                
if __name__ == '__main__':
    #tcpip_thread = threading.Thread(target=tcpip_server_tread)
    #tcpip_thread.start()
    #HOST = environ.get('SERVER_HOST', 'localhost')
    #HOST = environ.get('SERVER_HOST', '192.168.1.71')
    HOST = environ.get('SERVER_HOST', gVar.ip_address)
    try:
        PORT = int(environ.get('SERVER_PORT', '5000'))
    except ValueError:
        PORT = 5555
    
    #garosuTimer = threading.Thread(target=getData_temperature)
    #garosuTimer.start()    
    #tcpip_thread = threading.Thread(target=tcpip_server_tread)
    #tcpip_thread.start()
    
    app.run(HOST, PORT, debug=True)
