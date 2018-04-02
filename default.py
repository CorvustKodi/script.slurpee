# -*- coding: utf-8 -*-
# Copyright (c) 2018 CorvustKodi

import os
import sys
import xbmc
import xbmcaddon

__scriptname__ = "Slurpee"
__author__ = "CorvustKodi <corvust.xbmc@gmail.com>"
__url__ = ""
__svn_url__ = ""
__credits__ = ""
__version__ = "0.1.0"

__settings__ = xbmcaddon.Addon(id='script.slurpee')
__language__ = __settings__.getLocalizedString

BASE_RESOURCE_PATH = xbmc.translatePath( os.path.join( __settings__.getAddonInfo('path'), 'resources', 'lib' ) )
sys.path.append (BASE_RESOURCE_PATH)

KEY_BUTTON_BACK = 275
KEY_KEYBOARD_ESC = 61467

if __name__ == '__main__':
    from gui import GrabberGUI
    w = GrabberGUI("script-slurpee-main.xml", __settings__.getAddonInfo('path') , "Default")
    w.doModal()
    del w
