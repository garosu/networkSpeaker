from threading import Timer
import time
import os
import socket
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError

import subprocess
import netifaces
import vlc

from networkSpeaker.models import *
from flask import Response


class glovalVar():
    def __init__(self):
        self.curPlaylistTableName = 'baseplaylist'
        self.curPlaylistFile = './networkSpeaker/music/baseplaylist.m3u'
        self.curUser = ''
        self.ip_address = get_wifi_ip_address()
        self.scheduler = BackgroundScheduler()
        self.scheduled_jobs = []
        self.valTemperature = []
        self.valHumidity = []
        self.pathPicture = ''
        self.iVolume = 50    # max value = 5 (?) min value = 0  step = 0.1
        self.instanceVLC = ''
        self.playerSong = ''
        self.playerAlarm = ''
        self.statePlaysong = False
        self.tempsonglink = ''
        

# ================================================================================================
# about dictionary and list ---> user, alarm, playlist, scheduler ..... 
# ================================================================================================

def makeDictionary_reservedSchedule(job_id, valplaylist, mode, starttime, endtime):
    print("i will make job dictionary")
    dictionary_schedule = {'id': job_id, 'shed_name': valplaylist, 'shed_mode': mode, 'start_time': starttime, 'end_time': endtime}

    print(dictionary_schedule)
    
    return dictionary_schedule


def makeTotalAudioclipList_typeofDictionary():
    print("make list, it has type of dictionary")	

    listTotalAudioclip = []
    tmplist = os.listdir('./networkSpeaker/alarm')
    tmpPath = './networkSpeaker/alarm/'

    for item in tmplist:
        tmpItem = item.split('.')
        if tmpItem[1] != 'm3u':
            pathAudioclip = tmpPath + item
            dicAudioclip = {'audio_name':tmpItem[0], 'audio_link':pathAudioclip}
            print(dicAudioclip)	
            listTotalAudioclip.append(dicAudioclip)	

    tmplist = os.listdir('./networkSpeaker/music')
    tmpPath = './networkSpeaker/music/'
    
    for item in tmplist:
        tmpItem = item.split('.')
        if tmpItem[1] != 'm3u':
            pathAudioclip = tmpPath + item
            dicAudioclip = {'audio_name':tmpItem[0], 'audio_link':pathAudioclip}
            print(dicAudioclip)	
            listTotalAudioclip.append(dicAudioclip)	
            
    return listTotalAudioclip	
# ================================================================================================


# ================================================================================================
# ========================= about vlc player =====================================================
# ================================================================================================
def stop_vlcPlayer():
    #command = "kill $(pgrep vlc)"
    #os.system(command)
    print("garosu stop!!!")
    gVar.playerSong.stop()
    gVar.playerAlarm.stop()
    gVar.statePlaysong = False
	

def playalarm_fromCamera(play_alarmlink):
    print("i received alarm from camera!!!")	
    print(play_alarmlink)	
    
    gVar.playerSong.stop()
    gVar.playerAlarm.stop()
    gVar.statePlaysong = False

    tmplink = "./networkSpeaker/" + play_alarmlink
    media = gVar.instanceVLC.media_new(tmplink)
    gVar.playerAlarm.set_media(media)
    gVar.playerAlarm.play()
    
    while gVar.playerAlarm.get_state() != vlc.State.Ended:
        pass

    if gVar.statePlaysong == True:
        time.sleep(2)
        play_song(gVar.tempsonglink)		
 
    response = Response(status=200)
    return response
    

def play_alarm(play_alarmlink): # alarm/xxxx.wav
    #stop_vlcPlayer()
    #command = "cvlc  -I dummy --play-and-exit --gain=" + str(gVar.iVolume) + " ./networkSpeaker/" + play_alarmlink
    #command = "cvlc  networkSpeaker/" + play_alarmlink
    #os.system(command)
    
    gVar.playerSong.stop()
    gVar.playerAlarm.stop()
    
    if gVar.statePlaysong == True:
        gVar.playerSong.stop()    		

    tmplink = "./networkSpeaker/" + play_alarmlink
    print("garosu play alarm :: " + tmplink)
    media = gVar.instanceVLC.media_new(tmplink)
    gVar.playerAlarm.set_media(media)
    
    gVar.playerAlarm.play()
    
    while gVar.playerAlarm.get_state() != vlc.State.Ended:
        pass

    if gVar.statePlaysong == True:
        time.sleep(2)
        play_song(gVar.tempsonglink)
        		
    

def play_song(play_songlink): # music/xxx.mp3
    #stop_vlcPlayer()    
    #command = "cvlc networkSpeaker/" + play_songlink
    #os.system(command)
    
    print("garosu play song :: " + play_songlink)
    print("garosu play song :: " + play_songlink)

    tmplink = "./networkSpeaker/" + play_songlink
    media = gVar.instanceVLC.media_new(tmplink)
    gVar.playerSong.set_media(media)
    
    gVar.playerSong.play()
    gVar.statePlaysong = True
    gVar.tempsonglink = play_songlink
    
    while gVar.playerSong.get_state() != vlc.State.Ended:
        pass

    gVar.statePlaysong = False
    

def play_audio(play_audiolink):
    print("play audioclip :: " + play_audiolink)
    
    tmpname = play_audiolink.split('/')
    tmpname = tmpname[3]
    
    extention = play_audiolink.split('.')    
    extention = extention[2]
    
    if extention == 'wav':
        alarm_link = 'alarm/' + tmpname
        play_alarm(alarm_link)
    elif extention == 'mp3':
        song_link = 'music/' + tmpname
        play_song(song_link)
    else:
        print("it is non-official file")		        		
        print("it is non-official file")		        		
    
    #stop_vlcPlayer()    
    #command = "cvlc " + play_audiolink 
    #os.system(command)


def play_playlist(namePlaylist):
    print("this is playlist")
    print(namePlaylist)	

    abs_filename = './networkSpeaker/music/' + namePlaylist
    print(abs_filename)
    #print("garosu delete item 2 playlistFile :: " + abs_filename + " - " + song_link)   
    with open(abs_filename, 'r') as f:
        lines = f.readlines()

    for songlink in lines:
        print(songlink)
        songlink = songlink.strip("\n")
        songlink = 'music/' + songlink
        play_song(songlink)
    #for item in tmplist:
    #    tmpItem = item.split('.')
    #    if tmpItem[1] != 'm3u':
    #        pathAudioclip = tmpPath + item
    #        dicAudioclip = {'audio_name':tmpItem[0], 'audio_link':pathAudioclip}
    #        print(dicAudioclip)	
    #        listTotalAudioclip.append(dicAudioclip)	
    #stop_vlcPlayer()
    #command = "cvlc -I dummy --play-and-exit --gain=5.0 ./networkSpeaker/music/" + namePlaylist
    #os.system(command)
# ================================================================================================

        
# ================================================================================================
# ========================= about file 2 playlist ================================================
# ================================================================================================
def createFile_4_playlist(abs_filename):
    print("garosu create file 4 playlist :: " + abs_filename)
    subprocess.call(['touch', abs_filename])
    subprocess.call(['chmod', '0777', abs_filename])

	
def addItem_2_playlistFile(abs_filename, song_name, song_link):
    print("garosu add item 2 playlistFile :: " + abs_filename)
    with open(abs_filename, 'a+') as f:
        f.write(song_link + '\n')


def delItem_2_playlistFile(abs_filename, song_link):
    print("garosu delete item 2 playlistFile :: " + abs_filename + " - " + song_link)   
    with open(abs_filename, 'r') as f:
        lines = f.readlines()
        
    with open(abs_filename, 'w') as f:
        for line in lines:
            if line.strip("\n") != song_link:
                f.write(line)									        		 
# ================================================================================================

def get_dns_server():
    return '8.8.8.8'	

def get_subnet_mask():
    return '255.255.255.0'	

def get_gateway():
    gws = netifaces.gateways()
    #print(gws)	
    return gws['default'][netifaces.AF_INET][0]	

def get_wifi_ip_address():
    hostname = socket.gethostname()
    ip_address = None
    try:
        # Get the IP address of the machine's Wi-Fi interface
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
    except socket.error:
        # Unable to determine IP address
        pass
    return ip_address

def set_static_ip(new_ip_address, gateway):
    config_file = f"/etc/network/interfaces"
    interface = 'eth0'
    netmask = get_subnet_mask()
    print("garosu set new ip!!!")
    
    os.system(f"sudo cp {config_file} {config_file}.bak")
    with open(config_file, "w") as file:
        file.write(f"auto eth0\n")			
        file.write(f"iface eth0 inet static\n")			
        file.write(f"\taddress {new_ip_address}\n")			
        file.write(f"\tnetmask {netmask}\n")			
        file.write(f"\tgateway {gateway}\n")			

    os.system("sudo reboot")

def set_dhcp_ip():
    config_file = f"/etc/network/interfaces"
    interface = 'eth0'
    netmask = get_subnet_mask()
    print("garosu set new ip!!!")
    
    os.system(f"sudo cp {config_file} {config_file}.bak")
    with open(config_file, "w") as file:
        file.write(f"auto eth0\n")			
        file.write(f"iface eth0 inet dhcp\n")			
        file.write(f"#\taddress \n")			
        file.write(f"#\tnetmask \n")			
        file.write(f"#\tgateway \n")			

    os.system("sudo reboot")


os.system("sudo chmod 777 /home/rock/project/logs/garosu.log")
os.system("sudo chmod 777 /home/rock/project/networkSpeaker/static/graph.png")

gVar = glovalVar()

gVar.instanceVLC = vlc.Instance('--no-video --aout=alsa --alsa-audio-device=hw:1')

gVar.playerSong = gVar.instanceVLC.media_player_new()
gVar.playerAlarm = gVar.instanceVLC.media_player_new()

gVar.scheduler.start()
        
