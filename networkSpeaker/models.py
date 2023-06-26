from sqlalchemy import Column, Integer, Float, String, DateTime, TIMESTAMP, ForeignKey, PrimaryKeyConstraint, func, Table
from sqlalchemy.orm import relationship, backref
from networkSpeaker import app, db
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect

from networkSpeaker.remantek import *

import mysql.connector as mariaDB


class User(db.Model):
    __tablename__ = 'userdb'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    
"""
class Alarm(db.Model):
    __tablename__ = 'alarmdb'
    id = db.Column(db.Integer, primary_key=True)
    alarm_name = db.Column(db.String(60), unique=True, nullable=False)
    alarm_link = db.Column(db.String(60), nullable=False)

class SongPlaylist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    song_name = db.Column(db.String(60), unique=True, nullable=False)
    song_link = db.Column(db.String(60), nullable=False)
"""    
# ========== user DataBase ==============================================================================    
# adduser, deleteuser, edituser, get_AllUseritems.....
def adduser_2_table(username, password):
    try:
        connection = mariaDB.connect(
            host = '127.0.0.1',
            user = 'root',
            password = 'icandoit',
            database = 'garosudb'   
        )

        table_name = 'userdb'
        if connection.is_connected():
            db_info = connection.get_server_info()
            print('mysql Version : ', db_info)  

            cursor = connection.cursor(dictionary=True)

            insert_query = f"INSERT INTO {table_name} (username, password) VALUES ('{username}', '{password}');"
            cursor.execute(insert_query)
            connection.commit()
        
    finally:
        cursor.close()
        connection.close()
        print('MySQL Connection Close')

def deleteuser_2_table(user_id):
    try:
        connection = mariaDB.connect(
            host = '127.0.0.1',
            user = 'root',
            password = 'icandoit',
            database = 'garosudb'   
        )

        if connection.is_connected():
            db_info = connection.get_server_info()
            print('mysql Version : ', db_info)  

            cursor = connection.cursor(dictionary=True)

            table_name = 'userdb'
            delete_id = user_id
            delete_query = f"DELETE FROM {table_name} WHERE id={delete_id};"
            cursor.execute(delete_query)
            connection.commit()

    finally:
        cursor.close()
        connection.close()
        print('MySQL Connection Close')


def get_AllUseritems(table_name):
    try:
        connection = mariaDB.connect(
            host = '127.0.0.1',
            user = 'root',
            password = 'icandoit',
            database = 'garosudb'   
        )

        if connection.is_connected():
            db_info = connection.get_server_info()
            print('mysql Version : ', db_info)  

            cursor = connection.cursor(dictionary=True)

            select_query = f"select * from {table_name};"
            cursor.execute(select_query)
            myresult = cursor.fetchall()
            print(myresult)
        
            return myresult
        
    finally:
        cursor.close()
        connection.close()
        print('MySQL Connection Close')


#=========================================================================================
# it is alarm list
#=========================================================================================
# add alarm to alarmdb table....
def addAlarm_2_table(alarm_name, alarm_link):
    try:
        connection = mariaDB.connect(
            host = '127.0.0.1',
            user = 'root',
            password = 'icandoit',
            database = 'garosudb'   
        )

        table_name = 'alarmdb'
        if connection.is_connected():
            db_info = connection.get_server_info()
            print('mysql Version : ', db_info)  

            cursor = connection.cursor(dictionary=True)

            insert_query = f"INSERT INTO {table_name} (alarm_name, alarm_link) VALUES ('{alarm_name}', '{alarm_link}');"
            cursor.execute(insert_query)
            connection.commit()
        
    finally:
        cursor.close()
        connection.close()
        print('MySQL Connection Close')


def deleteAlarm_2_table(alarm_id):
    try:
        connection = mariaDB.connect(
            host = '127.0.0.1',
            user = 'root',
            password = 'icandoit',
            database = 'garosudb'   
        )

        if connection.is_connected():
            db_info = connection.get_server_info()
            print('mysql Version : ', db_info)  

            cursor = connection.cursor(dictionary=True)

            table_name = 'alarmdb'
            delete_id = alarm_id
            delete_query = f"DELETE FROM {table_name} WHERE id={delete_id};"
            cursor.execute(delete_query)
            connection.commit()

    finally:
        cursor.close()
        connection.close()
        print('MySQL Connection Close')


def get_Allalarmitems(tmptablename):
    try:
        connection = mariaDB.connect(
            host = '127.0.0.1',
            user = 'root',
            password = 'icandoit',
            database = 'garosudb'   
        )

        if connection.is_connected():
            db_info = connection.get_server_info()
            print('mysql Version : ', db_info)  

            cursor = connection.cursor(dictionary=True)

            table_name = 'alarmdb'

            select_query = f"select * from {table_name};"
            cursor.execute(select_query)
            myresult = cursor.fetchall()
            print(myresult)
        
            return myresult
        
    finally:
        cursor.close()
        connection.close()
        print('MySQL Connection Close')


#=========================================================================================
# it is scheduler database
#=========================================================================================
def createTable_4_Scheduler():
    try:
    
        # (1) MYSQL  
        connection = mariaDB.connect(
            host = '127.0.0.1',
            user = 'root',
            password = 'icandoit',
            database = 'garosudb'   
        )

        if connection.is_connected():
            db_info = connection.get_server_info()
            print('mysql Version : ', db_info)  

            cursor = connection.cursor()

            table_name = 'schedulerdb'
            create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} (id INT AUTO_INCREMENT PRIMARY KEY, shed_name VARCHAR(60), shed_mode VARCHAR(20), start_time DATETIME, end_time DATETIME);"
            cursor.execute(create_table_query)            

    #except Error as e:
    #    print('Database Error: ',e) 

    finally:
        cursor.close()
        connection.close()
        print('MySQL Connection Close')
        
    return "create table ok!!!"


def addSchedule_2_Table():
    try:
        connection = mariaDB.connect(
            host = '127.0.0.1',
            user = 'root',
            password = 'icandoit',
            database = 'garosudb'   
        )

        if connection.is_connected():
            db_info = connection.get_server_info()
            print('mysql Version : ', db_info)  

            cursor = connection.cursor()

            table_name = 'schedulerdb'
            name = 'mornningMusic'
            mode = 'Daily'
            start_time = '2023-06-01 10:00:00'
            end_time = '2023-06-01 11:00:00'
        
            insert_query = f"INSERT INTO {table_name} (shed_name, shed_mode, start_time, end_time) VALUES ('{name}', '{mode}', '{start_time}', '{end_time}');"
            cursor.execute(insert_query)
            connection.commit()
        
    finally:
        cursor.close()
        connection.close()
        print('MySQL Connection Close')



#=========================================================================================
# it is song play list
#=========================================================================================
def createTable_4_playlist(table_name):
    try:
    
        # (1) MYSQL  
        connection = mariaDB.connect(
            host = '127.0.0.1',
            user = 'root',
            password = 'icandoit',
            database = 'garosudb'   
        )

        if connection.is_connected():
            db_info = connection.get_server_info()
            print('mysql Version : ', db_info)  

            cursor = connection.cursor()

            #table_name = 'userdb'
            create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} (id INT AUTO_INCREMENT PRIMARY KEY, song_name VARCHAR(60), song_link VARCHAR(60));"
            cursor.execute(create_table_query)            

    #except Error as e:
    #    print('Database Error: ',e) 

    finally:
        cursor.close()
        connection.close()
        print('MySQL Connection Close')
        
    return "create table ok!!!"

    
def addItem_2_playlistTable(tblname, song_name, song_link):
    try:
        connection = mariaDB.connect(
            host = '127.0.0.1',
            user = 'root',
            password = 'icandoit',
            database = 'garosudb'   
        )

        if connection.is_connected():
            db_info = connection.get_server_info()
            print('mysql Version : ', db_info)  

            cursor = connection.cursor()

            table_name = tblname
        
            val_songname = song_name
            val_songlink = song_link
            insert_query = f"INSERT INTO {table_name} (song_name, song_link) VALUES ('{val_songname}', '{val_songlink}');"
            cursor.execute(insert_query)
            connection.commit()
        
    finally:
        cursor.close()
        connection.close()
        print('MySQL Connection Close')


def delItem_2_playlistTable(tblname, song_id):
    try:
        connection = mariaDB.connect(
            host = '127.0.0.1',
            user = 'root',
            password = 'icandoit',
            database = 'garosudb'   
        )

        if connection.is_connected():
            db_info = connection.get_server_info()
            print('mysql Version : ', db_info)  

            cursor = connection.cursor()

            table_name = tblname
        
            delete_id = song_id
            delete_query = f"DELETE FROM {table_name} WHERE id={delete_id};"
            cursor.execute(delete_query)
            connection.commit()
        
    finally:
        cursor.close()
        connection.close()
        print('MySQL Connection Close')


def getList_tablenames():
    try:
        connection = mariaDB.connect(
            host = '127.0.0.1',
            user = 'root',
            password = 'icandoit',
            database = 'garosudb'   
        )

        if connection.is_connected():
            db_info = connection.get_server_info()
            print('mysql Version : ', db_info)  

            cursor = connection.cursor()
            cursor.execute('show tables;')
        
            allTable = cursor.fetchall()
               
            delimiter = '('
            lstItems = []
            for temp in allTable:        
                result = delimiter.join(temp)	
                #print(result)
                if result != 'userdb' and result != 'alarmdb' and result != 'schedulerdb':
                    lstItems.append(result)	

            return lstItems
        
    finally:
        cursor.close()
        connection.close()
        print('MySQL Connection Close')

            
    
def getItems_at_playlistTable(tmptablename):
    try:
        connection = mariaDB.connect(
            host = '127.0.0.1',
            user = 'root',
            password = 'icandoit',
            database = 'garosudb'   
        )

        if connection.is_connected():
            db_info = connection.get_server_info()
            print('mysql Version : ', db_info)  

            cursor = connection.cursor(dictionary=True)

            table_name = tmptablename

            select_query = f"select * from {table_name};"
            cursor.execute(select_query)
            myresult = cursor.fetchall()
            #print(myresult)
        
            return myresult
        
    finally:
        cursor.close()
        connection.close()
        print('MySQL Connection Close')

    	
