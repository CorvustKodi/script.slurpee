#!/usr/bin/python

import re

def fuzzyMatch(targetName, f):
    terms = targetName.lower().replace('.',' ').split(' ')
    query_str = ''
    for term in terms:
        if term != '':
            if query_str != '':
                query_str = query_str+'[ .]+'
            query_str = query_str + re.escape(term)
    query_str = query_str + '.*'
    match = re.search(query_str,f.lower())
    if match:
        return f
    return None  

def parseEpisode(filename):
    # First try, look for the form sNNeMM
    season = 0
    episode = 0
    match = re.search('s([0-9]+)e([0-9]+)',filename.lower())
    if match:
        season = int(match.group(1))
        episode = int(match.group(2))
        # Next look for NN*MM
    else:
        match = re.search('([0-9]+)[a-z]([0-9]+)',filename.lower())
        if match:
            # Next look for NNMM
            season = int(match.group(1))
            episode = int(match.group(2))
        else:
            match = re.search("[ .]([0-9]{3,4})[ .]",filename.lower())
            if match:
                season = int(match.group(1))/100
                episode = int(match.group(1))%100                
    return season, episode

def getExtension(filename):
    toks = filename.split('.')
    ret = '.err'
    if len(toks) > 1:
        ret = toks[len(toks)-1]
    return ret
