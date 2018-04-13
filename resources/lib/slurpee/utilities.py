import requests
import xbmc
import xbmcgui
import json

class TVDBSearch(object):
    
    def login(self):
        resp = requests.post(self.tvdbApi+'/login',json={'apikey':self.apiKey})
        if not resp.ok:
            xbmc.log('Failed to authenticate to TVDB: '+str(resp.status_code))
            resp.raise_for_status()
        respJ = json.loads(resp.content);
        self.jwtToken = respJ['token']
    
    def __init__(self, apiKey, language):
        self.lang = language
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
