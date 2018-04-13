# -*- coding: utf-8 -*-
# Copyright (c) 2018 CorvustKodi

import xbmc
import xbmcaddon

ADDON = xbmcaddon.Addon()
ADDON_PATH = ADDON.getAddontInfo('path').decode('utf-8')
BASE_RESOURCE_PATH = xbmc.translatePath( os.path.join( ADDON_PATH, 'resources', 'lib' ) )
sys.path.append (BASE_RESOURCE_PATH)

if __name__ == '__main__':
    import torrent.scrape as scraper
    monitor = xbmc.Monitor()
    # The interval in the settings is in minutes
    runInterval = ADDON.getSetting('service_interval')

    while not monitor.abortRequested() and ADDON.getSetting('enable_service'):
        if monitor.waitForAbort(60*runInterval):
            break
        scraper.scrape(scraper.settingsFromKodi(ADDON))

