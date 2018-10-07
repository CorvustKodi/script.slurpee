#!/usr/bin/python

import os
import sys
import xml.dom.minidom
import urllib
import transmissionrpc
import time
import socket
import slurpee.parsing as parsing
import slurpee.dataTypes as dataTypes
import xbmc
from torrent.sites import *

def settingsFromKodi(kodiSettings):
    import xbmcaddon

    ret = {'RPC_HOST':'127.0.0.1', 'RPC_PORT':2580, 'RPC_USER':'', \
           'RPC_PASS':'', 'TRUSTEDONLY':False, 'TORRENT_FILE_PATH':'', 'SEARCHERS':[]}
    try:
        ret['RPC_HOST'] = kodiSettings.getSetting('rpc_host')
        ret['RPC_PORT'] = kodiSettings.getSetting('rpc_port')
        ret['RPC_USER'] = kodiSettings.getSetting('rpc_user')
        ret['RPC_PASS'] = kodiSettings.getSetting('rpc_pass')
        ret['TRUSTEDONLY'] = kodiSettings.getSetting('search_trustedonly')
        ret['TORRENT_FILE_PATH'] = kodiSettings.getSetting('file_path')
        if kodiSettings.getString('search_enable_limetorrents'):
            ret['SEARCHERS'].append('LimeTorrents')
        if kodiSettings.getSetting('search_enable_tpb'):
            ret['SEARCHERS'].append('ThePirateBay')
    except:
        pass
    return ret    

def settingsFromFile(settings_file):
    ret = {'RPC_HOST':'127.0.0.1', 'RPC_PORT':2580, 'RPC_USER':'', \
           'RPC_PASS':'', 'TRUSTEDONLY':False, 'TORRENT_FILE_PATH':'', 'SEARCHERS':[]}
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
            if node.attributes['id'].value == 'search_trustedonly':
                if str(node.attributes['value'].value).lower() != 'true':
                    ret['TRUSTEDONLY'] = False
            if node.attributes['id'].value == 'search_enable_limetorrents':
                if str(node.attributes['value'].value).lower() == 'true':
                    ret['SEARCHERS'].append('LimeTorrents')
            if node.attributes['id'].value == 'search_enable_tpb':
                if str(node.attributes['value'].value).lower() == 'true':
                    ret['SEARCHERS'].append('ThePirateBay')
            if node.attributes['id'].value =='file_path':
                ret['TORRENT_FILE_PATH'] = node.attributes['value'].value
    except:
        pass
    return ret
    
def scraper(settings, allshows):
    socket.setdefaulttimeout(15)
    # Create the client connection to transmission
    tc = transmissionrpc.Client(settings['RPC_HOST'], port=settings['RPC_PORT'], user=settings['RPC_USER'], password=settings['RPC_PASS'])
    activeTorrents = tc.list().values()
    torrentFiles = []
    for torrent in activeTorrents:
        files_dict = tc.get_files(torrent.id)
        for id_key in files_dict.keys():
            for file_key in files_dict[id_key].keys():
                torrentFiles.append(files_dict[id_key][file_key]['name'].lower())
    for show in allshows.getShows():
        if show.enabled:
            xbmc.log('Checking %s' % show.name,xbmc.LOGDEBUG)
            try:
                dlTorrent = None
                # Figure out what the next episode we need is - only download 1 episode per sweep.
                dir_path = os.path.join(show.path,'Season %d' % show.season)
                if not os.path.exists(show.path):
                    os.makedirs(show.path)
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)
                xbmc.log('Directory path: %s' % dir_path,xbmc.LOGDEBUG)
                lastEpisode = show.minepisode
                for f in os.listdir(dir_path): 
                    hasMatch = parsing.fuzzyMatch(show.filename,f)
                    if hasMatch != None:
                        season, episode = parsing.parseEpisode(f);
                        xbmc.log('%s = season %d, episode %d' % (f, season,episode),xbmc.LOGDEBUG)
                        if episode > lastEpisode:
                            lastEpisode = episode
                    else:
                        xbmc.log("No fuzzy match between '%s' and '%s'" % (show.filename, f),xbmc.LOGDEBUG)
                nextEpisode = lastEpisode + 1
  
                if show.season < 10:
                    season_str = '0' + str(show.season)
                else:
                    season_str = str(show.season)
                if nextEpisode < 10:
                    episode_str = '0' + str(nextEpisode)
                else:
                    episode_str = str(nextEpisode)

                targetName = show.filename + '.s'+season_str+'e'+episode_str
                xbmc.log('Looking for %s' % targetName,xbmc.LOGDEBUG)

                engine = None
                for SEARCHER in settings['SEARCHERS']:
                    try:
          
                        xbmc.log('Calling engine %s' % SEARCHER,xbmc.LOGDEBUG)
                        engine = globals()[SEARCHER].Search()
                        results = engine.search(urllib.quote(targetName),{'trusted_uploaders':settings['TRUSTEDONLY']})
                        sanitizedTarget = parsing.sanitizeString(targetName)
                        if len(results) == 0 and sanitizedTarget != targetName:
                            results = engine.search(urllib.quote(sanitizedTarget),{'trusted_uploaders':settings['TRUSTEDONLY']})
                        if len(results) > 0:
                            dlTorrent = results[0];
                        else:
                            xbmc.log('No results returned.',xbmc.LOGDEBUG)
                            continue
                        found = False
                        if dlTorrent is not None :
                            for tfile in torrentFiles:
                                hasMatch = parsing.fuzzyMatch(targetName,repr(tfile))
                                if hasMatch != None:
                                    xbmc.log('Found existing download: %s' % tfile,xbmc.LOGDEBUG)
                                    found = True
                                    break
                            if not found:
                                xbmc.log('Adding torrent: %s' % dlTorrent['url'],xbmc.LOGDEBUG)
                                tc.add_uri(dlTorrent['url'])
                                break
                    except Exception as details:
                        xbmc.log('An error occured: %s' % details,xbmc.LOGERROR)
            except Exception as details:
                xbmc.log('An error occured: %s' % details,xbmc.LOGERROR)
            time.sleep(10)

def scrape(settings):
    allshows = dataTypes.ShowList(settings['TORRENT_FILE_PATH'])
    scraper(settings,allshows)

if __name__ == '__main__':
    settings = settingsFromFile(sys.argv[1])
    scrape(settings)
    exit(0)
