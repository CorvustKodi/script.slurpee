#!/usr/bin/python

import os
import xml.dom.minidom
import urllib
import search
import transmissionrpc
import time
import socket
import slurpee.parsing as parsing
import slurpee.dataTypes as dataTypes

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
        if kodiSettings.getSetting('search_enabled_tpb'):
            ret['SEARCHERS'].append('ThePirateBay')
    except:
        pass
    return ret    

def settingsFromFile(settings_file):
    ret = {'RPC_HOST':'127.0.0.1', 'RPC_PORT':2580, 'RPC_USER':'', \
           'RPC_PASS':'', 'TRUSTEDONLY':False, 'TORRENT_FILE_PATH':'', 'SEARCHERS':[]}
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
            if node.attributes['id'].value == 'search_trustedonly':
                if str(node.attributes['value'].value).lower() != 'true':
                    ret['TRUSTEDONLY'] = False
            if node.attributes['id'].value == 'search_enabled_tpb':
                ret['SEARCHERS'].append('ThePirateBay')
            if node.attributes['id'].value =='file_path':
                ret['TORRENT_FILE_PATH'] = node.attributes['value'].value
    except:
        pass
    return ret
    
def scraper(settings, allshows):
    socket.setdefaulttimeout(15)
    # Create the client conneciton to transmission
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
            try:
                dlTorrent = None
                # Figure out what the next episode we need is - only download 1 episode per sweep.
                dir_path = os.path.join(show.path,'Season %d' % show.season)
                if not os.path.exists(show.path):
                    os.makedirs(show.path)
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)

                lastEpisode = minepisode
                for f in os.listdir(dir_path): 
                    hasMatch = parsing.fuzzyMatch(show.filename,f)
                    if hasMatch != None:
                        season, episode = parsing.parseEpisode(f);
                        if episode > lastEpisode:
                            lastEpisode = episode
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
                print 'Looking for %s' % targetName

                engine = None
                for SEARCHER in settings['SEARCHERS']:
                    try:
                        print 'Calling engine %s' % SEARCHER
                        engine = getattr(search, SEARCHER)
                        results = engine().search(urllib.quote(targetName),{'trusted_uploaders':settings['TRUSTEDONLY']})
                    
                        if len(results) > 0:
                            dlTorrent = results[0];
                        else:
                            print 'No results returned.'
                            continue
                        found = False
                        if dlTorrent is not None :
                            for tfile in torrentFiles:
                                hasMatch = parsing.fuzzyMatch(targetName,tfile)
                                if hasMatch != None:
                                    print 'Found existing download: %s' % tfile
                                    found = True
                                    break
                            if not found:
                                print 'Adding torrent: %s' % dlTorrent['url']
                                tc.add_uri(dlTorrent['url'])
                                break
                    except Exception as details:
                        print 'An error occured: %s' % details
            except Exception as details:
                print 'An error occured: %s' % details
            time.sleep(10)

def scrape(settings):
    allshows = dataTypes.ShowList(settings['TORRENT_FILE_PATH'])
    scraper(settings,allshows)

if __name__ == '__main__':
    settings = settingsFromFile(sys.argv[1])
    scrape(settings)
    exit(0)
