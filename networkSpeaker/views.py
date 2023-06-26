from datetime import datetime
from flask import Flask, render_template, request, g, make_response, Response, Markup, redirect, url_for, session, send_file
from networkSpeaker import app
from flask_sqlalchemy import SQLAlchemy

from networkSpeaker.models import *
from networkSpeaker.remantek import *

import os
import socket
import dns.resolver

from vlc import MediaPlayer, State
import time
import datetime

import subprocess

import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import random
import threading

import logging
logging.basicConfig(filename = "logs/garosu.log", level=logging.INFO) # CRITICAL, ERROR, WARNING, INFO, DEBUG


"""
gVar.scheduler.start()

gVar.scheduled_jobs.append({'id': 'jobID_1', 'shed_name': 'playMusic_1', 'shed_mode': 'once', 'start_time': '2023-06-30 12:00:00'})
gVar.scheduled_jobs.append({'id': 'jobID_2', 'shed_name': 'playMusic_2', 'shed_mode': 'daily', 'start_time': '2023-06-30 12:00:00'})
gVar.scheduled_jobs.append({'id': 'jobID_3', 'shed_name': 'playMusic_3', 'shed_mode': 'weekly', 'start_time': '2023-06-30 12:00:00'})
gVar.scheduled_jobs.append({'id': 'jobID_4', 'shed_name': 'playMusic_3', 'shed_mode': 'monthly', 'start_time': '2023-06-30 12:00:00'})
"""
#=======================================================================
#===========      Define scheduler's job function...         ===========
#=======================================================================
def jobFunc_runAlarm(alarmlink, job_id, valmode):
    play_alarm(alarmlink)
    
    if valmode == 'once':
        gVar.scheduled_jobs = [item for item in gVar.scheduled_jobs if item['id'] != job_id]        		


# receive the tablename and .... because only string possible...
def jobFunc_playSonglist(valplaylist, job_id, valmode):
    print("garosu start song :: " + valplaylist)
    print("garosu start song :: " + valplaylist)
    
    valplaylist = valplaylist + '.m3u'
    play_playlist(valplaylist)
    
    if valmode == 'once':
        gVar.scheduled_jobs = [item for item in gVar.scheduled_jobs if item['id'] != job_id]        		

def jobFunc_stopSonglist(arg1, arg2):
    stop_vlcPlayer()    
    

#=======================================================================
#===========     this is route region, edited by garosu     ============
#=======================================================================

@app.route('/draw_sensor_test')
def draw_sensor_test():
    picture_path = gVar.pathPicture  
    return render_template('total_playlist.html' ,picture_path=picture_path)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/open')
def open():
    print("garosu why")	
    
    access_ip = request.remote_addr   
    #user_agent = request.user_agent.string
    #browser = request.user_agent.browser
    #platform = request.user_agent.platform 
    print("garosu access ip :: " + access_ip)
    #print("garosu access ip :: " + user_agent)
    #print("garosu access ip :: " + str(browser))
    #print("garosu access ip :: " + str(platform))
    
    alarm_folder = fr'c:\\remanteck\{access_ip}'
    print("garosu alarm folder :: " + alarm_folder)
    file_name = 'welcome.wav'
    
    file_path = os.path.join(alarm_folder, file_name)
    print(file_path)
    
    #files = os.listdir(alarm_folder)
    return send_file(file_path, as_attachment=True)

@app.route('/login', methods=['POST'])
def loginCheck():
    username = request.form['username']
    password = request.form['password']
    print("user :: " + username + " -   password :: " + password)
    
    logging.info(username)
    
    ##session['logged_in_root'] = True
    ##return redirect(url_for('overview'))
    user = User.query.filter_by(username=username).first()
    if user and user.password == password:
        session['logged_in'] = True
        if username == 'root':
            session['logged_in_root'] = True
        else:
            session['logged_in_root'] = False
            
        gVar.curUser = username
        print(gVar.curUser)
        
        return redirect(url_for('overview'))
    else:
        session['logged_in'] = False
        session['logged_in_root'] = False
        return redirect(url_for('login'))    


@app.route('/overview')
def overview():
    if not session.get('logged_in'):
        return redirect(url_for('login'))       
    
    product_name = Markup("<strong>RemantekSpeaker</strong>")
    print(">>>>>>>", type(product_name))
    return render_template('overview.html', title="Overview", productName=product_name, ip_address=gVar.ip_address)

@app.route('/schedules')
def schedules():
    songtables = getList_tablenames()
    alarminfos = get_Allalarmitems('alarmdb')
    return render_template('schedules.html', title="Schedules", lstSchedules=gVar.scheduled_jobs, songstablelist=songtables, alarminfos=alarminfos)


#================================== Routing about music ====================================
@app.route('/music')
def music():
    stream_entries = getItems_at_playlistTable(gVar.curPlaylistTableName)
    songtables = getList_tablenames() 
    print(songtables)
    return render_template('music.html', title="Music", songstablelist=songtables, dbSong=stream_entries)

@app.route('/playlist_tables/<table_name>')
def list_item(table_name):
    print("clicked : ", table_name )
    print("clicked : ", table_name )
    gVar.curPlaylistTableName = table_name
    gVar.curPlaylistFile = "./networkSpeaker/music/" + table_name + ".m3u"
    return redirect(url_for('music'))

@app.route('/makeplaylist-Exe', methods=['POST'])
def makeplaylist_Exe():
    #print("make play list")
    if 'Cancel' in request.form:
        print("clicked Cancel")
        return redirect(url_for('music'))

    newplaylistname = request.form['playlistname']    
    playlist_path = './networkSpeaker/music/' + newplaylistname + '.m3u'
    
    createFile_4_playlist(playlist_path)
    createTable_4_playlist(newplaylistname)
    
    gVar.curPlaylistFile = playlist_path
    gVar.curPlaylistTableName = newplaylistname

    return redirect(url_for('music'))

    
@app.route('/addsongPlaylist-Exe', methods=['POST'])
def addsongPlaylist_Exe():
    if 'Cancel' in request.form:
        print("clicked Cancel")
        return redirect(url_for('music'))

    song_name = request.form['songname']
    song_link = request.form['songlink']
    print(song_name)
    print(song_link)
    
    tmpLink = song_link.split('/')
    tmpLen = len(tmpLink)
    print(tmpLen)
    print(tmpLink[tmpLen-1])
    
    addItem_2_playlistFile(gVar.curPlaylistFile, song_name, tmpLink[tmpLen-1])
    addItem_2_playlistTable(gVar.curPlaylistTableName, song_name, song_link)

    return redirect(url_for('music'))

@app.route('/announcements')
def announcements():
    stream_entries = get_Allalarmitems('alarmdb')
    return render_template('announcements.html', title="Announcements", dbAlarm=stream_entries)

@app.route('/addAlarm-Exe', methods=['POST'])
def addAlarm_Exe():
    if 'Cancel' in request.form:
        print("clicked Cancel")
        return redirect(url_for('announcements'))

    alarm_name = request.form['alarmname']
    alarm_link = request.form['alarmlink']
    print(alarm_name)
    print(alarm_link)
    
    tmpLink = alarm_link.split('/')
    tmpLen = len(tmpLink)
    print(tmpLen)
    print(tmpLink[tmpLen-1])
    
    addAlarm_2_table(alarm_name, alarm_link)

    return redirect(url_for('announcements'))
#====================================================================================    

@app.route('/audio_clips')
def audio_clips():
    lstAudioclip = makeTotalAudioclipList_typeofDictionary()
    return render_template('audio_clips.html', title="Audio_clips", dbAudio=lstAudioclip)

@app.route('/output_gain')
def output_gain():
    convertVolume = gVar.iVolume
    return render_template('output_gain.html', title="Output_gain", curVolume=convertVolume)

"""
@app.route('/system_volume')
def system_volume():
    return render_template('system_volume.html', title="System_volume")
"""

@app.route('/dhcp_setting')
def dhcp_setting():
    return render_template('dhcp_setting.html', title="DHCP_setting")

@app.route('/change-dhcpip', methods=['POST'])
def change_dhcpip():
    set_dhcp_ip()    
    return redirect(url_for('dhcp_setting'))


@app.route('/static_setting')
def static_setting():
    dns_ips = get_dns_server()
    gateway = get_gateway()
    netmask = get_subnet_mask()
    
    return render_template('static_setting.html', title="Static_setting", valIP=gVar.ip_address, valDns=dns_ips, valGateway=gateway, valNetmask=netmask)

@app.route('/change-ip', methods=['POST'])
def change_ip():

    gateway = get_gateway()
    static_ip = request.form['ip-address']
    print("garosu new ip :: " + static_ip)
    set_static_ip(static_ip, gateway)
    
    return redirect(url_for('static_setting'))


@app.route('/add_user')
def add_user():
    return render_template('add_user.html', title="Add_User")

@app.route('/edit_user')
def edit_user():
    user_entries = get_AllUseritems('userdb')
    return render_template('edit_user.html', title="Edit_User", dbUser=user_entries)    

@app.route('/delete_user', methods=['POST'])
def delete_user():
    user_id = request.form['user_id']
    username = request.form['username']
    password = request.form['password']
    print(user_id + " : " + username + " -> " + password)
    if username == 'root':
        print("it is root, not delete!!!")
    else:
        print("it is root, not delete!!! :: " + user_id)
        deleteuser_2_table(user_id)
        #deleteuser_at_table(user_id)
        
    return redirect(url_for('edit_user'))    
    
@app.route('/gotoSchedulesPage', methods=['GET'])
def gotoSchedulesPage():
    return redirect(url_for('schedules'))    

@app.route('/gotoMusicPage', methods=['GET'])
def gotoMusicPage():
    return redirect(url_for('music'))    

@app.route('/gotoAnnouncementsPage', methods=['GET'])
def gotoAnnouncementsPage():
    return redirect(url_for('announcements'))    

# -------------------------------------------------------------
# it is clicked button event .....
# -------------------------------------------------------------
@app.route('/addSchedules', methods=['POST'])
def addSchedules():
    print("add schedules")
    
    if 'Close' in request.form:
        print("clicked close")
        return redirect(url_for('schedules'))

    valtype = request.form['valtype']
    valmode = request.form['valmode']
    valplaylist = request.form['valplaylist']
    valstarttime = request.form['valstarttime']
    valcalendar = request.form['valcalendar']
    
    now = datetime.datetime.now()
    
    if valcalendar == '':
        valcalendar = now.strftime('%Y-%m-%d') 
        tmpStarttime = now.strftime('%Y-%m-%d') + ' ' + valstarttime + ':00'
    else:
        tmpStarttime = valcalendar + ' ' + valstarttime + ':00'

    tmpDayofWeek = datetime.datetime.strptime(valcalendar, '%Y-%m-%d')
    tmpDayofWeek = tmpDayofWeek.strftime('%A')
    
    if tmpDayofWeek == 'Monday':
        day_of_week = 'mon'
    elif tmpDayofWeek == 'Tuesday':
        day_of_week = 'tue'		    		
    elif tmpDayofWeek == 'Wednesday':
        day_of_week = 'wed'		    		
    elif tmpDayofWeek == 'Thursday':
        day_of_week = 'thu'		    		
    elif tmpDayofWeek == 'Friday':
        day_of_week = 'fri'		    		
    elif tmpDayofWeek == 'Saturday':
        day_of_week = 'sat'		    		
    elif tmpDayofWeek == 'Sunday':
        day_of_week = 'sun'		    		
    
    valcalendar = valcalendar.split('-')
    valstarttime = valstarttime.split(':')
    tmpYear = valcalendar[0]
    tmpMonth = valcalendar[1]
    tmpDay = valcalendar[2]
    tmpHour = valstarttime[0]     
    tmpMinute = valstarttime[1]         

    numJobs = len(gVar.scheduled_jobs)
    job_id = 'jobID_' + str(numJobs+1)

    if valtype == 'music':    
        if valmode == 'once':
            tempJob = gVar.scheduler.add_job(jobFunc_playSonglist, trigger='date', id=job_id, run_date=tmpStarttime, args=(valplaylist, job_id, valmode))
        elif valmode == 'daily':
            print("it it daily")
            tempJob = gVar.scheduler.add_job(jobFunc_playSonglist, trigger='cron',  hour=int(tmpHour), minute=int(tmpMinute), id=job_id, args=(valplaylist, job_id, valmode))
        elif valmode == 'weekly':
            print("it it weekly")
            tempJob = gVar.scheduler.add_job(jobFunc_playSonglist, trigger='cron', day_of_week=day_of_week, hour=int(tmpHour), minute=int(tmpMinute), id=job_id, args=(valplaylist, job_id, valmode))
        elif valmode == 'monthly':
            print("it it monthly")
            tempJob = gVar.scheduler.add_job(jobFunc_playSonglist, trigger='cron', day=tmpDay, hour=int(tmpHour), minute=int(tmpMinute), id=job_id, args=(valplaylist, job_id, valmode))
        
    
    elif valtype == 'alarm':        
        #alarmLink = 'alarm/' + valplaylist
        alarmLink = valplaylist
                
        if valmode == 'once':
            tempJob = gVar.scheduler.add_job(jobFunc_runAlarm, trigger='date', id=job_id, run_date=tmpStarttime, args=(alarmLink, job_id, valmode))
        elif valmode == 'daily':
            print("it it daily")
            tempJob = gVar.scheduler.add_job(jobFunc_runAlarm, trigger='cron',  hour=int(tmpHour), minute=int(tmpMinute), id=job_id, args=(alarmLink, job_id, valmode))
        elif valmode == 'weekly':
            print("it it weekly")
            tempJob = gVar.scheduler.add_job(jobFunc_runAlarm, trigger='cron', day_of_week=day_of_week, hour=int(tmpHour), minute=int(tmpMinute), id=job_id, args=(alarmLink, job_id, valmode))
        elif valmode == 'monthly':
            print("it it monthly")
            tempJob = gVar.scheduler.add_job(jobFunc_runAlarm, trigger='cron', day=tmpDay, hour=int(tmpHour), minute=int(tmpMinute), id=job_id, args=(alarmLink, job_id, valmode))
                
    reservedDictionary = makeDictionary_reservedSchedule(job_id, valplaylist, valmode, tmpStarttime, '0')
    gVar.scheduled_jobs.append( reservedDictionary)

    return redirect(url_for('schedules'))



@app.route('/addUser-Exe', methods=['POST'])
def addUser_Exe():
    addedUsername = request.form['username']
    addedPassword = request.form['password']    
    print(addedUsername)
    print(addedPassword)
    
    adduser_2_table(addedUsername, addedPassword)
    return redirect(url_for('add_user'))
    

@app.route('/saveSystemVolume-Exe', methods=['POST'])
def saveSystemVolume_Exe():
    valVolume = request.form['saveVolume']

    print("it is music.... :: " + valVolume)
    print("it is music.... :: " + valVolume)
    
    #gVar.iVolume = int(valVolume) / 20
    gVar.iVolume = int(valVolume)
    gVar.playerAlarm.audio_set_volume(gVar.iVolume)
    gVar.playerSong.audio_set_volume(gVar.iVolume)

    return redirect(url_for('output_gain'))


@app.route('/play-Songlist', methods=['POST'])
def play_Songlist():
    print("garosu why ::" + gVar.curPlaylistFile)
    
    tmpLink = gVar.curPlaylistFile
    tmpLink = tmpLink.split('/')
    lenLink = len(tmpLink)
    tmpPlaylist = tmpLink[lenLink - 1]
    play_playlist(tmpPlaylist)
    
    return redirect(url_for('music'))


@app.route('/controlSong-form', methods=['POST'])
def controlSong_form():
    song_func = request.form['song_func']
    song_id = request.form['song_id']
    song_name = request.form['song_name']
    song_link = request.form['song_link']
    
    print("garosu function :: " + song_func)
    print("garosu current playlist table :: " + gVar.curPlaylistTableName)
    print("garosu current playlist file :: " + gVar.curPlaylistFile)

    if (song_func == "playsong"):	    
        play_song(song_link)
    elif (song_func == "stopsong"):
        stop_vlcPlayer()
    elif (song_func == "updatesong"):
        print("garosu update songitem")
    elif (song_func == "deletesong"):
        print("garosu delete songitem")
        print("garosu deleted id :: " + song_id)
        tmpLink = song_link.split('/')
        tmpLen = len(tmpLink)

        delItem_2_playlistFile(gVar.curPlaylistFile, tmpLink[tmpLen-1])
        delItem_2_playlistTable(gVar.curPlaylistTableName, song_id)

    return redirect(url_for('music'))


@app.route('/controlAlarm-form', methods=['POST'])
def controlAlarm_form():
    alarm_func = request.form['alarm_func']
    alarm_id = request.form['alarm_id']
    alarm_name = request.form['alarm_name']
    alarm_link = request.form['alarm_link']

    print(alarm_func)
    print(alarm_id)
    print(alarm_name)
    print(alarm_link)

    if (alarm_func == "playalarm"):	    
        play_alarm(alarm_link)
    elif (alarm_func == "stopalarm"):
        stop_vlcPlayer()
    elif (alarm_func == "updatealarm"):
        print("update alarm")
    elif (alarm_func == "deletealarm"):
        print("delete alarm")
        deleteAlarm_2_table(alarm_id)
    
    return redirect(url_for('announcements'))


@app.route('/controlAudioclip-form', methods=['POST'])
def controlAudioclip_form():
    audio_func = request.form['audio_func']
    audio_name = request.form['audio_name']
    audio_link = request.form['audio_link']
    
    if (audio_func == "playaudio"):
        print("garosu audio :: " + audio_link)	    
        play_audio(audio_link)
    elif (audio_func == "stopaudio"):
        stop_vlcPlayer()

    return redirect(url_for('audio_clips'))


@app.route('/alarm_backroom')
def alarm_backroom():
    now = datetime.datetime.now()
    rcvInfo = 'garosu log - ' + now.strftime('%Y-%m-%dT%H:%M:%S') + ' : received dont enter office alarm'
    logging.info(rcvInfo)
    return playalarm_fromCamera('alarm/backroom.wav')

@app.route('/alarm_counter')
def alarm_counter():
    now = datetime.datetime.now()
    rcvInfo = 'garosu log - ' + now.strftime('%Y-%m-%dT%H:%M:%S') + ' : received dont enter counter alarm'
    logging.info(rcvInfo)
    return playalarm_fromCamera('alarm/counter.wav')

@app.route('/alarm_exit')
def alarm_exit():
    now = datetime.datetime.now()
    rcvInfo = 'garosu log - ' + now.strftime('%Y-%m-%dT%H:%M:%S') + ' : received exit alarm'
    logging.info(rcvInfo)
    return playalarm_fromCamera('alarm/exit.wav')

@app.route('/alarm_microwave')
def alarm_microwave():
    now = datetime.datetime.now()
    rcvInfo = 'garosu log - ' + now.strftime('%Y-%m-%dT%H:%M:%S') + ' : received be careful to use microwave alarm'
    logging.info(rcvInfo)
    return playalarm_fromCamera('alarm/microwave.wav')

@app.route('/alarm_selfpos')
def alarm_selfpos():
    now = datetime.datetime.now()
    rcvInfo = 'garosu log - ' + now.strftime('%Y-%m-%dT%H:%M:%S') + ' : received take your card alarm'
    logging.info(rcvInfo)
    return playalarm_fromCamera('alarm/selfpos.wav')

@app.route('/alarm_table')
def alarm_table():
    now = datetime.datetime.now()
    rcvInfo = 'garosu log - ' + now.strftime('%Y-%m-%dT%H:%M:%S') + ' : received clean table after using alarm'
    logging.info(rcvInfo)
    return playalarm_fromCamera('alarm/table.wav')

@app.route('/alarm_welcome')
def alarm_welcome():
    #playalarm_fromCamera('alarm/welcome.wav')
    #response = Response(status=200)
    now = datetime.datetime.now()
    rcvInfo = 'garosu log - ' + now.strftime('%Y-%m-%dT%H:%M:%S') + ' : received welcome alarm'
    logging.info(rcvInfo)
    return playalarm_fromCamera('alarm/welcome.wav')


