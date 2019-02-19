#!/usr/bin/python

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import os
import xml.dom.minidom
import datetime
import subprocess
import shutil
import traceback

from torrent import transmissionrpc
import time

import slurpee.parsing as parsing
import slurpee.dataTypes as dataTypes

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
        doc2 = xml.dom.minidom.parse(settings_file)
        settingsNodes = doc2.getElementsByTagName('setting')
        for node in settingsNodes:
            if node.attributes['id'].value == 'rpc_host':
                ret['RPC_HOST'] = node.attributes['value'].value
            if node.attributes['id'].value == 'rpc_port':
                ret['RPC_PORT'] = node.attributes['value'].value
            if node.attributes['id'].value == 'rpc_user':
                ret['RPC_USER'] = node.attributes['value'].value
            if node.attributes['id'].value == 'rpc_pass':
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



def processFiles(files, settings, allshows, timestamp=None):
    ''' The mover function is called by transmission when download is complete.
      It is responsible for extracting the proper video files from the set
      of files downloaded by the torrent, and placing them in the correct
      destination directory.
    '''
    runtime = time.time()
    try:
        video_files = []
        audio_files = []
        for file_name in files:
            if timestamp and timestamp > os.path.getmtime(os.path.join(download_path,str(file_name))):
                # If a timestamp is provided, ignore files that are older than it
		continue
            toks = file_name.rsplit('.',1)
            if len(toks)==2:
                file_ext = (file_name).rsplit('.',1)[1]
                if file_ext in video_extensions and file_name not in video_files:
                    video_files.append(file_name)
                if file_ext in audio_extensions and file_name not in audio_files:
                    audio_files.append(file_name)
        for tfile in audio_files:
            try:
                # No fancy processing for audio files, just copy to the NEW directory
                subprocess.Popen(["sudo",COPY_SCRIPT,os.path.join(download_path,str(tfile)),default_audio_output_path+"/"+tfile,settings['FILE_OWNER']]).wait()
            except:
                pass
        for tfile in video_files:
#                    print ' --> %s' % tfile
            matches = []
            foundShow = False
            for show in allshows.getShows():
                if show.enabled:
                    print 'Checking %s' % show.name
                    if parsing.fuzzyMatch(show.filename,str(tfile)) != None:
                        matches.append(show)
                        foundShow = True
            if not foundShow:
                print 'No match found for vidoe file %s' % tfile
                try:
                    print 'Copying to default video directory: %s' % 'sudo ' + COPY_SCRIPT + ' ' + os.path.join(download_path,tfile) + ' ' + default_video_output_path + '/ ' + settings['FILE_OWNER']
                    subprocess.Popen(["sudo",COPY_SCRIPT,os.path.join(download_path,str(tfile)),default_video_output_path+"/",settings['FILE_OWNER']]).wait()
                    if settings['MAIL_ENABLED']:
                        sendMail(settings['SENDMAIL_DEST'],'New video downloaded','%s - new file in videos' % str(tfile))
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
                print "best match is %s" % bestmatch.name
                dest_dir = os.path.join(bestmatch.path,'Season %d' % int(season))
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)
                if os.path.exists(dest_dir):
                    target_file = bestmatch.filename + ' s' + str(season) + 'e' + str(episode) + '.' + parsing.getExtension(str(tfile))
                    if not os.path.isfile(os.path.join(dest_dir,target_file)):
                        print "sudo" + " " + COPY_SCRIPT + " " + os.path.join(download_path,str(tfile)) + " " + dest_dir+"/" + " " + settings['FILE_OWNER']
                        subprocess.Popen(["sudo",COPY_SCRIPT,os.path.join(download_path,str(tfile)),os.path.join(dest_dir,target_file),settings['FILE_OWNER']]).wait()
                        if settings['MAIL_ENABLED']:
                            sendMail(settings['SENDMAIL_DEST'],'%s - new episode available' % bestmatch.name,'A new episode of %s is available for playback in \
                              %s/Season %d: %s' % (bestmatch.name, bestmatch.path, int(season),target_file))
    except Exception:
        exc_details = traceback.format_exc()
        print '%s' % exc_details
        if settings['MAIL_ENABLED']:
            sendMail(settings['SENDMAIL_DEST'],'An error has occurred',exc_details)
    return runtime

def scanner(settings, allshows, timefile):
    if not os.path.exists(timefile):
        print 'First run, creating timestamp file'
        timestamp = time.time()
    else:
        with open(timefile,'rt') as f:
            timestamp = int(f.read())    
        timestamp = processFiles(settings, allshows, timestamp)
    with open(timefile,'wt') as f:
        f.write('%d' % timestamp)

def cleanup(settings):
    try:
        tc = transmissionrpc.Client(settings['RPC_HOST'], port=settings['RPC_PORT'], user=settings['RPC_USER'], password=settings['RPC_PASS'])
        torrent_list = tc.get_torrents()
        now = time.time()
        oneWeek = 60*60*24*4
        for t in torrent_list:
            doneDate = t.__getattr__('doneDate')
            if doneDate > 0 and doneDate < (now - oneWeek):
                id = int(t.__getattr__('id'))
                print 'Found an old torrent (id = %d) - removing.' % id
                tc.remove_torrent(id,True)
    except Exception:
        exc_details = traceback.format_exc()
        print '%s' % exc_details
        if settings['MAIL_ENABLED']:
            sendMail(settings['SENDMAIL_DEST'],'An error has occurred',exc_details)

if __name__ == '__main__':
    print sys.argv
    srcPath = os.path.dirname(sys.argv[0])
    COPY_SCRIPT = os.path.join(srcPath,COPY_SCRIPT)
    settings = settingsFromFile(sys.argv[1])
    allshows = dataTypes.ShowList(settings['TORRENT_FILE_PATH'])
    timefile = sys.argv[2]
    scanner(settings,allshows,timefile)
    cleanup(settings)
    exit(0)
