import xml.dom.minidom

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
