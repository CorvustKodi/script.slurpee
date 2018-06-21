#!/usr/bin/python

import sys
import os
import xml.dom.minidom
import datetime
import subprocess
import shutil
import traceback

import transmissionrpc
import time

import ../../slurpee.parsing as parsing
import ../../slurpee.dataTypes as dataTypes

SETTINGS_FILE_PATH="settings.xml"
COPY_SCRIPT="file_copy.sh"

def settingsFromFile(settings_file):
    ret = {'RPC_HOST':'127.0.0.1', 'RPC_PORT':2580, 'RPC_USER':'', \
           'RPC_PASS':'', 'TORRENT_FILE_PATH':'', 'MAIL_ENABLED':True, \
           'SENDMAIL_DEST':'foo@bar.com', \
           'DEFAULT_NEW_PATH':'/home/user/Content/New', \
           'TORRENT_DOWNLOAD_PATH':'/home/user/Downloads', \
           'FILE_OWNER':'user'
          }
    try:
        doc2 = xml.dom.minidom.parse(transmissionxbmc_file)
        settingsNodes = doc2.getElementsByTagName('setting')
        for node in settingsNodes:
            if node.attributes['id'].value == 'rpc_host':
                ret['RPC_HOST'] = node.attributes['value'].value
            if node.attributes['id'].value == 'rpc_port':
                ret['RPC_PORT'] = node.attributes['value'].value
            if node.attributes['id'].value == 'rpc_user':
                ret['RPC_USER'] = node.attributes['value'].value
            if node.attributes['id'].value == 'rpc_password':
                ret['RPC_PASS'] = node.attributes['value'].value
            if node.attributes['id'].value == 'mail_enabled':
                if str(node.attributes['value'].value).lower() != 'true':
                    ret['MAIL_ENABLED'] = False
            if node.attributes['id'].value == 'sendmail_dest':
                ret['SENDMAIL_DEST'] = node.attributes['value'].value
            if node.attributes['id'].value == 'default_new_path':
                ret['DEFAULT_NEW_PATH'] = node.attributes['value'].value
            if node.attributes['id'].value == 'torrent_download_path':
                ret['TORRENT_DOWNLOAD_PATH'] = node.attributes['value'].value
            if node.attributes['id'].value =='file_path':
                ret['TORRENT_FILE_PATH'] = node.attributes['value'].value
            if node.attributes['id'].value =='file_owner':
                ret['FILE_OWNER'] = node.attributes['value'].value
    except:
        pass
    return ret

def sendMail(to_address,subject_text,body_text):
    sendmail_location = "/usr/sbin/sendmail" # sendmail location
    p = os.popen("%s -t" % sendmail_location, "w")
    p.write("To: %s\n" % to_address)
    p.write("Subject: %s\n" % subject_text)
    p.write("\n") # blank line separating headers from body
    p.write("%s" % body_text)
    status = p.close()
    if status != 0:
        print "Sendmail exit status ", status

def mover(settings, allshows, tid = None):
    ''' The mover function is called by transmission when download is complete.
      It is responsible for extracting the proper video files from the set
      of files downloaded by the torrent, and placing them in the correct
      destination directory.
    '''
    try:
        if tid == None:
            torrent_id = os.environ.get('TR_TORRENT_ID')
        else:
            torrent_id = tid

        print 'Torrent ID: %s' % str(torrent_id)
        download_path = settings['TORRENT_DOWNLOAD_PATH']

        default_video_output_path = os.path.join(settings['DEFAULT_NEW_PATH'],"Video")
        default_audio_output_path = os.path.join(settings['DEFAULT_NEW_PATH'],"Audio")
        
        if not os.path.exists(default_video_output_path):
            os.makedirs(default_video_output_path)
            os.makedirs(default_audio_output_path)
        video_extensions = ['mp4', 'mov', 'mkv', 'avi', 'mpg']
        audio_extensions = ['mp3']

        tc = transmissionrpc.Client(settings['RPC_HOST'], port=settings['RPC_PORT'], user=settings['RPC_USER'], password=settings['RPC_PASS'])
        files_dict = tc.get_files()
        torrent_list = tc.get_torrents()
        if torrent_id != None:
            id_key = int(torrent_id)
            if id_key in files_dict.keys():
                video_files = []
                audio_files = []
                for file_key in files_dict[id_key].keys():
                    file_ext = (files_dict[id_key][file_key]['name']).rsplit('.',1)[1]
                    if file_ext in video_extensions and files_dict[id_key][file_key]['name'] not in video_files:
                        video_files.append(files_dict[id_key][file_key]['name'])
                    if file_ext in audio_extensions and files_dict[id_key][file_key]['name'] not in audio_files:
                        audio_files.append(files_dict[id_key][file_key]['name'])
                for tfile in audio_files:
                    try:
                        # No fancy processing for audio files, just copy to the NEW directory
                        subprocess.Popen(["sudo",COPY_SCRIPT,os.path.join(download_path,tfile),default_audio_output_path+"/"+tfile,settings['FILE_OWNER']]).wait()
                    except:
                        pass
                for tfile in video_files:
                    print ' --> %s' % tfile
                    matches = []
                    foundShow = False
                    for show in allshows.getShows():
                        if show.enabled:
                            print 'Checking %s' % show.name
                            foundShow = parsing.fuzzyMatch(show.filename,tfile)
                            matches.append(show)
                    if not foundShow:
                        print 'No match found for torrent id %d' % id_key      
                        try:
                            subprocess.Popen(["sudo",COPY_SCRIPT,os.path.join(download_path,tfile),default_video_output_path+"/",settings.['FILE_OWNER']]).wait()
                        except:
                            pass
                    else:
                        # All of the shows in 'matching' appear in the video filename. It stands to reason
                        # that the longest show name will be the best (kinda true right?)
                        bestmatch = matches[0]
                        for show in matches:
                            if len(show.filename) > len(bestmatch.filename):
                                bestmatch = show
                        season, episode = parsing.parseEpisode(tfile)
                        if int(season) < 10:
                            season = '0' + str(int(season))
                        if int(episode) < 10:
                            episode = '0' + str(int(episode))
                        dest_dir = os.path.join(bestmatch.path,'Season %d' % season)
                        if not os.path.exists(dest_dir):
                            os.makedirs(dest_dir)
                        if os.path.exists(dest_dir):
                            target_file = bestmatch.filename + ' s' + str(season) + 'e' + str(episode) + '.' + parsing.getExtension(tfile)
                            if not os.path.isfile(os.path.join(dest_dir,target_file)):
                                subprocess.Popen(["sudo",COPY_SCRIPT,os.path.join(download_path,tfile),dest_dir+"/",settings.['FILE_OWNER']]).wait()
                        if settings['MAIL_ENABLED']:
                            sendMail(settings['SENDMAIL_DEST'],'%s - new episode available' % bestmatch.name,'A new episode of %s is available for playback in \
                              %s/Season %d: %s' % (bestmatch.name, bestmatch.path, bestmatch.season,target_file))
            else:
                print 'no id match:'
                for key in files_dict.keys():
                    print '--> %d' % key
        now = time.time()
        oneWeek = 60*60*24*4
        for id in files_dict.keys():
            t = tc.get_torrent(id)
            doneDate = t.__getattr__('doneDate')
            if doneDate > 0 and doneDate < (now - oneWeek):
                print 'Found an old torrent (id = %d) - removing.' % int(id)
                tc.remove_torrent(id,True)
    except Exception:
        exc_details = traceback.format_exc()
        print '%s' % exc_details
        if settings['MAIL_ENABLED']:
            sendMail(settings['SENDMAIL_DEST'],'An error has occurred',exc_details)

if __name__ == '__main__':
    settings = settingsFromFile(SETTINGS_FILE_PATH)
    allshows = dataType.ShowList(settings['TORRENT_FILE_PATH'])
    if len(sys.argv) > 2:
        mover(settings,allshows,int(sys.argv[2]))
    else:
        mover(settings,allshows)
    exit(0)
