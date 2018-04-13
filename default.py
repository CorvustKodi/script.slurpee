# -*- coding: utf-8 -*-
# Copyright (c) 2018 CorvustKodi

import os
import sys
import xbmc
import xbmcaddon

ADDON = xbmcaddon.Addon()
ADDON_PATH = ADDON.getAddontInfo('path').decode('utf-8')
BASE_RESOURCE_PATH = xbmc.translatePath( os.path.join( ADDON_PATH, 'resources', 'lib' ) )
sys.path.append (BASE_RESOURCE_PATH)

if __name__ == '__main__':
    from gui import GrabberGUI
    w = GrabberGUI("script-slurpee-main.xml", ADDON_PATH , "Default")
    w.doModal()
    del w
