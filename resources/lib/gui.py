# -*- coding: utf-8 -*-
# Copyright (c) 2018 CorvustKodi

import sys
import os
import xbmc
import xbmcgui
import slurpee.utilities as util
import slurpee.dataTypes as dataTypes

ADDON = sys.modules[ "__main__" ].ADDON
ADDON_PATH = sys.modules[ "__main__" ].ADDON_PATH

KEY_MENU_ID = 92

EXIT_SCRIPT = (6, 10, 247, 275, 61467, 216, 257, 61448,)
CANCEL_DIALOG = EXIT_SCRIPT + (216, 257, 61448,)

class GrabberGUI(xbmcgui.WindowXMLDialog):
    def __init__(self, strXMLname, strFallbackPath, strDefaultName, bforeFallback=0):
        self.shows = None

    def updateList(self, slist):
        slist.reset()
        for show in self.shows.getShows():
            l = xbmcgui.ListItem(label=show.name + ' - Season ' + str(show.season), label2='Enabled: ' + str(show.enabled))
            slist.addItem(l)

    def onInit(self):
        file_path = ADDON.getSetting('file_path')
        self.shows = dataTypes.ShowList(file_path)

        slist = self.getControl(120)
        self.updateList(slist)
        slist.setEnabled(True)

    def onClick(self, controlID):
        slist = self.getControl(120)
        if (controlID == 111):
            # Add button
            new_show = dataTypes.TVShow('', '', '', 0, 0, 'false')
            self.shows.addShow(new_show)
            w = ShowInfoGUI("script-slurpee-details.xml", ADDON_PATH , "Default", isNew=True, shows=self.shows)
            w.setShow(len(self.shows.getShows()) - 1)
            w.doModal()
            del w
            self.shows.cleanUp()
            self.updateList(slist)
        if (controlID == 112):
            # Exit button
            self.close()
        if (controlID == 113):
            # Save button
            self.save()
        if (controlID == 120):
            # A show was chosen, show details
            index = slist.getSelectedPosition()
            item = slist.getListItem(index)
            show = self.shows.getShow(index)
            w = ShowInfoGUI("script-slurpee-details.xml", ADDON_PATH , "Default", isNew=False, shows=self.shows)
            w.setShow(index)
            w.doModal()
            del w
            self.updateList(slist)
    def onFocus(self, controlID):
        # Focus on the selection list, make sure we highlight a entry
        if controlID == 120:
            list = self.getControl(120)
            if list.getSelectedPosition() < 0 or list.getSelectedPosition() >= list.size():
                if list.size() > 0:
                    list.selectItem(0)

    def onAction(self, action):
        if (action.getButtonCode() in CANCEL_DIALOG) or (action.getId() == KEY_MENU_ID):
            self.close()
    def close(self):
        dialog = xbmcgui.Dialog()
        if dialog.yesno('Are you sure?', 'Are you sure you want to exit', '(unsaved changes will be lost)?'):
            super(GrabberGUI, self).close()
    def save(self):
        self.shows.toXML(ADDON.getSetting('file_path'))
        dialog = xbmcgui.Dialog()
        dialog.ok('Save Successful!', 'Show list has been saved.')

class ShowInfoGUI(xbmcgui.WindowXMLDialog):
    def __init__(self, strXMLname, strFallbackPath, strDefaultName, bforeFallback=0, isNew=False, shows=None):
        self.show = None
        self.show_index = -1
        self.props = {}
        self.isNew = isNew
        self.shows = shows
    def setShow(self, index):
        self.show_index = index
        self.show = self.shows.getShow(self.show_index)
    def onInit(self):
        if self.isNew:
            self.doWizard()
        slist = self.getControl(110)
        self.props['name'] = xbmcgui.ListItem(label="Name:", label2=self.show.name)
        slist.addItem(self.props['name'])
        self.props['season'] = xbmcgui.ListItem(label="Season:", label2=str(self.show.season))
        slist.addItem(self.props['season'])
        self.props['episode'] = xbmcgui.ListItem(label="Starting Episode:", label2=str(self.show.minepisode))
        slist.addItem(self.props['episode'])
        self.props['enabled'] = xbmcgui.ListItem(label="Enabled:", label2=str(self.show.enabled))
        slist.addItem(self.props['enabled'])
        self.props['filename'] = xbmcgui.ListItem(label="Filename:", label2=self.show.filename)
        slist.addItem(self.props['filename'])
        self.props['path'] = xbmcgui.ListItem(label="Path:", label2=self.show.path)
        slist.addItem(self.props['path'])
        slist.setEnabled(True)

    def close(self):
        super(ShowInfoGUI, self).close()
    def onAction(self, action):
        if (action.getButtonCode() in CANCEL_DIALOG) or (action.getId() == KEY_MENU_ID):
            self.close()
            pass
    def doWizard(self):
        # Get the name of the show
        keyboard = xbmc.Keyboard(self.show.name)
        keyboard.doModal()
        if not keyboard.isConfirmed():
            self.show.name=None
            self.close()
        show_name = keyboard.getText()
        searcher = util.TVDBSearch(ADDON.getSetting('tvdb_api_key'),ADDON.getLanguage(xbmc.ISO_639_1))
        showNames = searcher.search(show_name)
        showNames.append(xbmcgui.ListItem(show_name + ' | (Original Search)'))
        dialog = xbmcgui.Dialog()
        val = dialog.select('Search Results', showNames)
        if val < 0:
            self.show.name=None
            self.close()
            
        self.show.name = showNames[val].getLabel().split('|')[0].rstrip()
        # Auto generate the filename
        self.show.filename = (self.show.name).replace(' ', '.')
        # Auto generate the library path
        self.show.path = os.path.join(ADDON.getSetting('default_base_path'),self.show.name)

        # Select the season
        seasonList = []
        while len(seasonList) < 100:
            seasonList.append(str(len(seasonList) + 1))

        dialog = xbmcgui.Dialog()
        val = dialog.select('Season Number', seasonList, preselect=0)
        if val < 0:
            self.show.name=None
            self.close()
        self.show.season = seasonList[val]
        
        # Auto set minimum episode to 0
        self.show.minepisode = 0
        # Auto enable
        self.show.enabled = True
        
    def onClick(self, controlID):
        slist = self.getControl(110)
        if (controlID == 101):
            # Exit button
            self.close()
        elif (controlID == 102):
            # Delete button
            self.shows.removeShow(self.show_index)
            self.close()
        elif (controlID == 110):
            item = slist.getSelectedItem()
            if item.getLabel() == "Name:":
                # Name edit dialog
                keyboard = xbmc.Keyboard(self.show.name)
                keyboard.doModal()
                if(keyboard.isConfirmed()):
                    self.show.name = keyboard.getText()
                    self.show.filename = (self.show.name).replace(' ', '.')
                    self.show.path = os.path.join(ADDON.getSetting('default_base_path'),self.show.name)
                    self.updateItem()
            if item.getLabel() == "Season:":
                # Season edit dialog
                dialog = xbmcgui.Dialog()
                val = dialog.numeric(0, 'Enter Season Number', str(self.show.season))
                self.show.season = int(val)
                self.updateItem()
            if item.getLabel() == "Starting Episode:":
                # Episode edit dialog
                dialog = xbmcgui.Dialog()
                val = dialog.numeric(0, 'Enter First Episode', str(self.show.minepisode))
                self.show.minepisode = int(val)
                self.updateItem()
            if item.getLabel() == "Enabled:":
                # Enabled toggle
                self.show.enabled = not self.show.enabled
                self.updateItem()
            if item.getLabel() == "Filename:":
                # Filename edit dialog
                keyboard = xbmc.Keyboard(self.show.filename)
                keyboard.doModal()
                if(keyboard.isConfirmed()):
                    self.show.filename = keyboard.getText()
                    self.updateItem()
            if item.getLabel() == "Path:":
                # Path edit dialog
                keyboard = xbmc.Keyboard(self.show.path)
                keyboard.doModal()
                if(keyboard.isConfirmed()):
                    self.show.path = keyboard.getText()
                    self.updateItem()

    def onFocus(self, controlID):
        pass

    def updateItem(self):
        self.props['name'].setLabel2(self.show.name)
        self.props['season'].setLabel2(str(self.show.season))
        self.props['episode'].setLabel2(str(self.show.minepisode))
        self.props['enabled'].setLabel2(str(self.show.enabled))
        self.props['filename'].setLabel2(self.show.filename)
        self.props['path'].setLabel2(self.show.path)
