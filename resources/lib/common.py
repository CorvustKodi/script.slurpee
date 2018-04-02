import xml.dom.minidom
import requests
import BeautifulSoup
import xbmc
import xbmcgui

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
    def __init__(self, apiKey):
        self.apiKey = apiKey
        
    def search(self, showTitle):
        tvdb_url = 'http://thetvdb.com/api/GetSeries.php?seriesname='
        
        search_url = tvdb_url + showTitle.replace(' ','+')
        tvdb = requests.get(search_url)
        soup = BeautifulSoup.BeautifulStoneSoup(tvdb.text)
        xbmc.log(soup.prettify(),xbmc.LOGWARNING)
        seriesNodes = soup.findAll('series')
        ret = []
        for node in seriesNodes:
            xbmc.log(str(node),xbmc.LOGWARNING)
            sNames = []
            sNames.append(str(node.seriesname.string).rstrip().lstrip())
            if node.aliasnames is not None:
                tags = str(node.aliasnames.string).split('|')
                for tag in tags:
                    sNames.append(tag.rstrip().lstrip())
            for n in sNames:
                li = xbmcgui.ListItem(n+' | (TheTVDB)')
                li.setUniqueIDs({'tvdb',str(node.id.string)})
                ret.append(li)
        return ret