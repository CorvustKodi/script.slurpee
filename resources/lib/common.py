import xml.dom.minidom
import requests
import BeautifulSoup
import xbmc
import xbmcgui
import json
import xbmcaddon

class TVShow(object):
    def __init__(self, path, name, filename, season, minepisode, enabled):
        self.name = str(name)
        self.path = str(path)
        self.filename = str(filename)
        self.season = int(season)
        self.minepisode = int(minepisode)
        if enabled.lower() == 'true':
            self.enabled = True
        else:
            self.enabled = False

class ShowList(object):
    def __init__(self, xmlpath):
        self.shows = []
        try:
            doc = xml.dom.minidom.parse(xmlpath)
        except Exception as details:
            print details
            doc = xml.dom.minidom.Document()
            # Don't fail on a parse error, just start with a blank file.
        
        showNodes = doc.getElementsByTagName('show')
        for node in showNodes:
            new_show = TVShow(node.attributes['path'].value, node.attributes['name'].value, \
                node.attributes['filename'].value, node.attributes['season'].value, \
                node.attributes['minepisode'].value, node.attributes['enabled'].value)
            self.shows.append(new_show)

    def addShow(self, newShow):
        self.shows.append(newShow)

    def removeShow(self, index):
        if index < len(self.shows):
            self.shows.pop(index)

    def getShows(self):
        return self.shows

    def getShow(self, index):
        if index < len(self.shows):
            return self.shows[index]
        return None

    def cleanUp(self):
        removeIdx = []
        i = 0
        while i < len(self.shows):
            if self.shows[i].name is None or self.shows[i].name == '':
                removeIdx.append(i)
            i=i+1    
        i = len(removeIdx)-1
        while i >= 0:
            self.removeShow(removeIdx[i])
            i = i-1

    def toXML(self, xmlpath):
        xmldoc = xml.dom.minidom.Document()
        xmldoc.encoding = u"UTF-8"
        xmldoc.version = u"1.0"
        root_node = xmldoc.createElement("root")
        xmldoc.appendChild(root_node)
        for show in self.shows:
            showNode = xmldoc.createElement("show")
            showNode.setAttribute(u"path", str(show.path))
            showNode.setAttribute(u"name", str(show.name))
            showNode.setAttribute(u"filename", str(show.filename))
            showNode.setAttribute(u"season", str(show.season))
            showNode.setAttribute(u"minepisode", str(show.minepisode))
            showNode.setAttribute(u"enabled", str(show.enabled))
            root_node.appendChild(showNode)
        f = open(xmlpath,'w')
        root_node.writexml(f," "," ","\n")
        f.close()
        xmldoc.unlink()
        
class TVDBSearch(object):
    
    def login(self):
        resp = requests.post(self.tvdbApi+'/login',json={'apikey':self.apiKey})
        if not resp.ok:
            xbmc.log('Failed to authenticate to TVDB: '+str(resp.status_code))
            resp.raise_for_status()
        respJ = json.loads(resp.content);
        self.jwtToken = respJ['token']
    
    def __init__(self, apiKey):
        settings = xbmcaddon.Addon(id='script.slurpee')
        self.lang = xbmc.getLanguage(xbmc.ISO_639_1)
        self.tvdbApi = 'https://api.thetvdb.com'
        self.apiKey = apiKey
        self.jwtToken = None
        self.login()
        
    def search(self, showTitle):
        
        search_url = self.tvdbApi + "/search/series?name=" + showTitle.replace(' ','+')
        if self.jwtToken is None:
            self.login()
        if self.jwtToken is None:
            xbmc.log('Could not authenticate!',xbmc.LOGERROR)
            return None
        
        headers = {'Authorization' : 'Bearer ' + self.jwtToken, \
                   'Accept-Language' : self.lang, \
                   'Accept' : 'application/json'}
        tvdb = requests.get(search_url,headers=headers)
        respJ = json.loads(tvdb.content)
        
        seriesNodes = respJ['data']

        ret = []
        for node in seriesNodes:
            sNames = []
            sNames.append(str(node['seriesName']).replace(')','').replace('(',''))
            aliases = node['aliases']
            
            year = node['firstAired'].split('-')[0]
            
            for a in aliases:
                sNames.append(str(a).replace(')','').replace('(',''))
            for n in sNames:
                li = xbmcgui.ListItem(n+' | (TheTVDB)')
                li.setUniqueIDs({'tvdb',str(node['id'])})
                li.setInfo('video',{'year':year,})
                ret.append(li)
        return ret