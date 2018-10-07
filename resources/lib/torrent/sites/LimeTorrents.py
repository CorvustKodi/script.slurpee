import re
import socket
import requests
from BaseSearch import BaseSearch
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup

socket.setdefaulttimeout(15)

def getLink(url):
    f = None
    try:
        r = requests.get(url,headers={'Accept-encoding':'gzip'})
        f = r.text
        soup = BeautifulSoup(f)
        # Look for a Cloudfare redirect ? 
        formNode = soup.findAll('form', {'id' : 'challenge-form'})[0]
        if formNode is not None:
          urlpath = formNode['action']
          params = ''
          first = True
          for child in soup.findAll('input', {'type' : 'hidden'}):
            iname = child['name']
            ivalue = None
            try:
              ivalue = child['value']
            except:
              pass
            if ivalue is None:
              ivalue = "wtf"
            if not first:
              params = params + '&'
            params = params + iname + '=' + ivalue
            first = False
          newUrl = url + urlpath + '?' + params
          print 'redirect to: %s' % newUrl
          r = requests.get(newUrl,headers={'Accept-encoding':'gzip'})
          f = r.text
    except:
        pass
    return f

class Search(BaseSearch):
    def __init__(self):
        self.search_uris = ['https://limetorrents.cc/search/all/'
                           ]
    def search(self, terms, settings={}):
        torrents = []
        f = None

        for url in self.search_uris:
            final_url = url + terms.replace(' ','%20') + '/seeds/1/'
            print 'search URL: %s' % final_url
            f = getLink(final_url)
            if f is not None:
                break;
        if not f:
            raise Exception('Out of proxies')
        soup = BeautifulSoup(f)
        links = []
        for details in soup.findAll('div', {'class': 'tt-name'}):
            sub = details.findAll('a');
            for a in sub:
                if a['href'].find('.torrent?') == -1:
                    par = details.parent.parent
                    seedNode = par.find('td', {'class':'tdseed'})
                    leechNode = par.find('td', {'class':'tdleech'})
                    if seedNode is None or leechNode is None:
                        break;

                    name = a.text

                    seeds = int(seedNode.text.replace(',',''))
                    leechers = int(leechNode.text.replace(',',''))            
                    trusted = False
                    if par.find('img', {'title':'Verified torrent'}) is not None:
                        trusted = True


                    turl = a['href']
                    # Follow the new link
                    baseUrl = final_url.split('/')[0:3]
                    turl = '/'.join(baseUrl) + turl
                    f = getLink(turl)
                    if not f:
                        raise Exception('Invalid link')
                    newSoup = BeautifulSoup(f)
                    for mag in newSoup.findAll('a'):
                        if mag['href'].startswith('magnet:?'):
                            url = mag['href']

#                    print "name : %s, seeds: %d, trusted: %s" % (name,seeds,trusted)

                    if trusted or 'trusted_uploaders' not in settings.keys() or str(settings['trusted_uploaders']).lower() != 'true':
                        torrents.append({
                                 'url': url,
                                 'name': name,
                                 'seeds': seeds,
                                 'leechers': leechers,
                        })
        sorted_torrents = sorted(torrents,key = lambda k: k['seeds'], reverse=True)
        return sorted_torrents


if __name__ == '__main__':
    s = Search()
    results = s.search('deadliest catch')
    print results


