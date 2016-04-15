import re,xbmcplugin,xbmcgui,requests
import xbmc
import xbmcaddon
import os
import urlparse
from urllib import quote, unquote_plus, unquote, urlencode,quote_plus,urlretrieve
from resources import pafy

pluginhandle=int(sys.argv[1])
addon=xbmcaddon.Addon(id='plugin.video.doku.cc')
home=addon.getAddonInfo('path').decode('utf-8')
icon=xbmc.translatePath(os.path.join(home, 'icon.png'))
fanart=xbmc.translatePath(os.path.join(home, 'fanart.jpg'))
imageDir=os.path.join(home, 'thumbnails') + '/'
view_mode_id=int('503')
xbox=xbmc.getCondVisibility("System.Platform.xbox")
downloadpath=addon.getSetting('download_path')
xbmcplugin.setContent(pluginhandle, 'Episodes')
baseurl='http://doku.cc//api.php?'

def categories():
	genres = get_genres()
	for genre in genres:
		url = genre['url']
		name = genre['genre']
		icon = genre['thumb']
		addDir(name,url,'index',icon)
	addDir('Suche','','Search',imageDir+'6.png')
	addDir('Kategorien','','getcat',imageDir+'7.png')
	addDir('A-Z','','Alphabet',imageDir+'8.png')
	if downloadpath is '':
		pass
	else:
		addDir('meine Downloads','','listing',imageDir+'9.png')
			    
def get_genres():
	genres = ({'url': '%sget=new-dokus&page=1' % baseurl, 'genre': 'Die neusten Dokus', 'thumb': imageDir+'1.png'}, {'url': '%sget=reuploads&page=1' % baseurl, 'genre': 'Die neusten reUploads', 'thumb': imageDir+'2.png'}, {'url': '%stop-dokus=trend&page=1' % baseurl, 'genre': 'Aufsteiger der Woche', 'thumb': imageDir+'3.png'},  {'url': '%stop-dokus=last-month&page=1' % baseurl, 'genre': 'Top Dokus des Monats', 'thumb': imageDir+'4.png'}, {'url': '%stop-dokus=last-year&page=1' % baseurl, 'genre': 'Top Dokus des Jahres', 'thumb': imageDir+'5.png'})
	return genres
	
def getcat():
	url='%sgetCats' % baseurl
	data=getjson(url)
	for item in data:
		name=item['name']
		url=item['url']
		addDir(name,url,'index',icon)
			    
def index(url):
	data=getjson(url)
	for item in data['dokus']:
		url=item['youtubeId']
		desc=item['description']
		name=item['title']
		thumb=item['cover']
		duration=item['length']
		date=cleandate(item['date'])
		desc='%s       %s %s  bei  %s   Votes\n%s' % (date, item['voting']['voteCountInPerc'],'%', item['voting']['voteCountAll'],item['description'])
		addLink(name,url,'play',thumb,desc,duration)
	try:
		url=(data['query']['nextpage'])
		addDir('Next',url,'index',imageDir+'10.png')
	except:
		pass
	try:
		url=(data['query']['prevpage'])
		addDir('Prev',url,'index',imageDir+'11.png')
	except:
		pass
	
        
def play(url):
	video_url=((pafy.new(url)).getbest()).url
	listitem=xbmcgui.ListItem(path=video_url)
	xbmcplugin.setResolvedUrl(pluginhandle, succeeded=True, listitem=listitem)
	
def Search():
	search_entered=search()
	url='%ssearch=%s&page=1' % (baseurl,search_entered)
	index(url)
								
def search():
        search_entered=''
        keyboard=xbmc.Keyboard(search_entered, 'Suche auf Doku.cc')
        keyboard.doModal()
        if keyboard.isConfirmed():
            search_entered=keyboard.getText()
            if search_entered == None:
                return False          
        return search_entered 
              
def Alphabet():
		for i in range(ord('A'), ord('Z')+1):
			name=chr(i)
			url='%sletter=%s&page=1' % (baseurl,name)
			addDir(name,url,'index',icon)
			
def Download(url):
	if downloadpath is '':
		d=xbmcgui.Dialog()
		d.ok('Download Error','Du hast keinen Download Folder gesetzt','','')
		addon.openSettings(sys.argv[ 0 ])
		return
	xbmc.executebuiltin('XBMC.Notification(Doku.cc,Starte Download)')	
	name=(pafy.new(url)).title
	best=(pafy.new(url)).getbest()
	filepath=downloadpath+name+'.'+best.extension
	filepath=(filepath).replace('.temp','')
	best.download(filepath).replace('.temp','')
	xbmc.executebuiltin("XBMC.Notification(Download beendet!,2000)")
		
def listing():
	dirs=os.listdir(downloadpath)
	for url in dirs:
		url=downloadpath+url
		name=(url).replace(downloadpath,'')
		addLink(name,url,'play1',icon,'','')
		
def play1(url):
	videolink=str(url)
	listitem=xbmcgui.ListItem(path=videolink)
	xbmcplugin.setResolvedUrl(pluginhandle, succeeded=True, listitem=listitem)

def cleandate(date):
	date=date.split(' ', 1)[0]
	date='%s.%s.%s' % (date.split('-')[2],date.split('-')[1],date.split('-')[0])
	return date
		
def getjson(url):
	r=requests.get(url)
	data=r.json()
	r.connection.close()
	return data        
        
def addLink(name,url,mode,iconimage,desc,duration):
    u=sys.argv[0]+"?url="+quote_plus(url)+"&mode="+str(mode)
    ok=True
    item=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    item.setInfo( type="Video", infoLabels={ 'Genre': 'Doku', "Title": name , "Plot": desc , "Duration" : duration } )
    item.setProperty('IsPlayable', 'true')
    menu = []
    menu.append(('Download Video', 'XBMC.RunPlugin(%s?mode=59&name=%s&url=%s)' % (sys.argv[0], name, url)))
    item.addContextMenuItems(items=menu, replaceItems=False)
    item.setProperty('fanart_image', fanart)
    xbmc.executebuiltin('Container.SetViewMode(%d)' % view_mode_id)
    xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item)

def addDir(name,url,mode,iconimage):
    u=sys.argv[0]+"?url="+quote_plus(url)+"&mode="+str(mode)+"&name="+quote_plus(name)
    ok=True
    item=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    item.setInfo( type="Video", infoLabels={ "Title": name } )
    item.setProperty('fanart_image', fanart)
    xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=True)	

def parameters_string_to_dict(parameters):
    ''' Convert parameters encoded in a URL to a dict. '''
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict

params=parameters_string_to_dict(sys.argv[2])
mode=params.get('mode')
url=params.get('url')
if type(url)==type(str()):
  url=unquote_plus(url)

if mode == 'index':
	index(url)
elif mode =='play':
	play(url)
elif mode =='Search':	
	Search()
elif mode =='Alphabet':
    Alphabet()
elif mode =='getcat':
    getcat()
elif mode =='listing':
	listing()
elif mode =='play1':
	play1(url)
elif mode =='59':
    Download(url)
else:
   categories()

xbmcplugin.endOfDirectory(pluginhandle)