#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib, urllib2, cookielib
import string, os, re, time, datetime, sys

import xbmc, xbmcgui, xbmcplugin, xbmcaddon

BASE = [
'http://www.123srilanka.net/livetv/family.xml',
]
HAS_UPDATED_LIBRTMP=False

try:
    from xml.etree import ElementTree
except:
    try:
        from elementtree import ElementTree
    except:
        dlg = xbmcgui.Dialog()
        dlg.ok('ElementTree missing', 'Please install the elementree addon.',
                'http://www.ontouch.tv/xbmc')
        sys.exit(0)
    
def addFolder(source=None, lang='', totalItems=0):
    if not lang:
        title=BASE[source]
    else:
        title=lang
        
    u=sys.argv[0]+"?src="+str(source)+"&lang="+lang
    item=xbmcgui.ListItem(title, iconImage="DefaultFolder.png")
    item.setInfo( type="Video", infoLabels={ "Title": title })
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,isFolder=True,totalItems=totalItems)

def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
        params=sys.argv[2]
        cleanedparams=params.replace('?','')
        if (params[-1]=='/'):
            params=params[0:-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in pairsofparams:
            splitparams={}
            splitparams=i.split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=splitparams[1]
    return param

def listSources():
    if len(BASE) < 2:
        listLanguages()
        return

    for source in BASE:
        addFolder(BASE.index(source),totalItems=len(BASE))
    xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ) )

def listLanguages(src=0):
    xml=getURL(BASE[int(src)])
    tree = ElementTree.XML(xml)
    streams = tree.findall('stream')
    languages = []
    for stream in streams:
        language = stream.findtext('language').strip()
        if not language in languages and language.find('Link Down') == -1:
            languages.append(language)
            
    languages = list(set(languages))
    languages.sort()
    if len(languages) < 2:
        listVideos(src, languages[0])
        return

    for lang in languages:
        addFolder(src, lang, totalItems=len(languages))
    xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ) )


def listVideos(src=0,lang=''):
    xml=getURL(BASE[int(src)])
    tree = ElementTree.XML(xml)
    streams = tree.findall('stream')
    newS=[]
    for stream in streams:
        language = stream.findtext('language').strip()
        if language == lang and language.find('Link Down') == -1 :
            newS.append(stream)
    for stream in newS:
        title = stream.findtext('title')
        rtmplink = stream.findtext('link')+' playpath='+stream.findtext('playpath')+'  swfurl='+stream.findtext('swfUrl')+' pageurl='+stream.findtext('pageUrl')+' live=1 '+stream.findtext('advanced').replace('-v','').replace('live=1','')
        if HAS_UPDATED_LIBRTMP:
            rtmplink += stream.findtext('advanced').replace('-v','').replace('live=1','').replace('-x ',"swfsize=").replace('-w ','swfhash=')
        else:
            rtmplink += stream.findtext('advanced').replace('-v','').replace('live=1','')
        logo=stream.findtext('logourl', default="DefaultTVShows.png")
        item=xbmcgui.ListItem(title, iconImage=logo)
        item.setInfo( type="Video", infoLabels={'title':title})
        item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=rtmplink,listitem=item,isFolder=False,totalItems=len(newS))
    xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ) )

def getURL( url ):
    if url[:7] == "file://":
        print 'RTMPGUI --> common :: getURL :: file = '+url[7:]
        usock=open(url[7:],'r')
    else:
        print 'RTMPGUI --> common :: getURL :: url = '+url
        cj = cookielib.LWPCookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [('User-Agent', 'python-urllib/2.6 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2;)')]
        usock=opener.open(url)
    
    response=usock.read()
    usock.close()
    return response

#listVideos()
parms=get_params()

if "src" in parms and 'lang' in parms and parms['lang']:
    listVideos(parms['src'], parms['lang'])
elif 'src' in parms:
    listLanguages(parms['src'])
else:
    listSources()