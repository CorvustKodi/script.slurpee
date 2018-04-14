# -*- coding: utf-8 -*-
# Copyright (c) 2018 CorvustKodi

import xbmc
import xbmcaddon
import os

ADDON = xbmcaddon.Addon()
ADDON_PATH = ADDON.getAddonInfo('path').decode('utf-8')
BASE_RESOURCE_PATH = xbmc.translatePath( os.path.join( ADDON_PATH, 'resources', 'lib' ) )
sys.path.append (BASE_RESOURCE_PATH)

if __name__ == '__main__':
    import torrent.scrape as scraper
    monitor = xbmc.Monitor()
    # The interval in the settings is in minutes
    isFirst = True
    while not monitor.abortRequested():
        if not isFirst and monitor.waitForAbort(60*int(ADDON.getSetting('service_interval'))):
            break
        isFirst = False
        if 'true' == ADDON.getSetting('enable_service'):
            xbmc.log("running Slurpee scraping service",xbmc.LOGNOTICE)
            scraper.scrape(scraper.settingsFromKodi(ADDON))

