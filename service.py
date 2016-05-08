# -*- coding: utf-8 -*- 

import os
import sys
import xbmc
import urllib
import xbmcvfs
import xbmcaddon
import xbmcgui
import xbmcplugin
import re
import shutil
import unicodedata
import urlparse

__addon__ = xbmcaddon.Addon()
__author__     = __addon__.getAddonInfo('author')
__scriptid__   = __addon__.getAddonInfo('id')
__scriptname__ = __addon__.getAddonInfo('name')
__version__    = __addon__.getAddonInfo('version')
__language__   = __addon__.getLocalizedString

__cwd__        = xbmc.translatePath( __addon__.getAddonInfo('path') ).decode("utf-8")
__profile__    = xbmc.translatePath( __addon__.getAddonInfo('profile') ).decode("utf-8")
__resource__   = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib' ) ).decode("utf-8")
__temp__       = xbmc.translatePath( os.path.join( __profile__, 'temp') ).decode("utf-8")

sys.path.append (__resource__)

from tusubtitulo import search_tvshow, log

""" Called when searching for subtitles from XBMC """
def Search(item):
    log(__name__, item)
    subs = search_tvshow(item['tvshow'], item['season'], item['episode'], item['2let_language'])
    for sub in subs:
        append_subtitle(sub)

def append_subtitle(item):
    listitem = xbmcgui.ListItem(label=item['lang'],  label2=item['filename'], thumbnailImage=item['flag'])
    url = "plugin://%s/?action=download&link=%s&filename=%s&referer=%s" % (__scriptid__, item['link'], item['filename'].decode('utf-8'), item['referer'])
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem, isFolder=False)

def Download(link, filename, referer):
    subtitle_list = []
    if not link:
       return subtitle_list

    log(__name__, "Downloadlink %s" % link)

    class MyOpener(urllib.FancyURLopener):
        version = "Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko"

    my_urlopener = MyOpener()
    my_urlopener.addheader('Referer', referer)
    postparams = None

    log(__name__, "Fetching subtitles using url '%s' with referer header '%s' and post parameters '%s'" % (link, link, postparams))
    response = my_urlopener.open(link, postparams)
    local_tmp_file = os.path.join(__temp__, "sub.srt")

    if xbmcvfs.exists(__temp__):
        shutil.rmtree(__temp__)
    xbmcvfs.mkdirs(__temp__)
    try:
        log(__name__, "Saving subtitles to '%s'" % local_tmp_file)
        local_file_handle = open(local_tmp_file, "wb")
        local_file_handle.write(response.read())
        local_file_handle.close()

        subtitle_list.append(local_tmp_file)
        log(__name__, "=== returning subtitle file %s" % file)

    except:
        log(__name__, "Failed to save subtitle to %s" % local_tmp_file)

    return subtitle_list

def normalizeString(str):
  return unicodedata.normalize('NFKD', unicode(unicode(str, 'utf-8'))).encode('ascii','ignore')
 
def get_params():
  param = {}
  if len(sys.argv[2]) > 1:
      param = dict(urlparse.parse_qsl(sys.argv[2][1:]))
  return param


params = get_params()

if params['action'] == 'search':
  item = {}
  item['temp']               = False
  item['rar']                = False
  item['year']               = xbmc.getInfoLabel("VideoPlayer.Year")                           # Year
  item['season']             = str(xbmc.getInfoLabel("VideoPlayer.Season"))                    # Season
  item['episode']            = str(xbmc.getInfoLabel("VideoPlayer.Episode"))                   # Episode
  item['tvshow']             = normalizeString(xbmc.getInfoLabel("VideoPlayer.TVshowtitle"))   # Show
  item['title']              = normalizeString(xbmc.getInfoLabel("VideoPlayer.OriginalTitle")) # try to get original title
  item['file_original_path'] = urllib.unquote(xbmc.Player().getPlayingFile().decode('utf-8'))  # Full path of a playing file
  item['3let_language']      = []
  item['2let_language']      = []

  for lang in urllib.unquote(params['languages']).decode('utf-8').split(","):
    item['3let_language'].append(xbmc.convertLanguage(lang,xbmc.ISO_639_2))
    item['2let_language'].append(xbmc.convertLanguage(lang,xbmc.ISO_639_1))

  if item['title'] == "":
    item['title']  = normalizeString(xbmc.getInfoLabel("VideoPlayer.Title"))      # no original title, get just Title

  if item['episode'].lower().find("s") > -1:                                      # Check if season is "Special"
    item['season'] = "0"                                                          #
    item['episode'] = item['episode'][-1:]

  if ( item['file_original_path'].find("http") > -1 ):
    item['temp'] = True

  elif ( item['file_original_path'].find("rar://") > -1 ):
    item['rar']  = True
    item['file_original_path'] = os.path.dirname(item['file_original_path'][6:])

  elif ( item['file_original_path'].find("stack://") > -1 ):
    stackPath = item['file_original_path'].split(" , ")
    item['file_original_path'] = stackPath[0][8:]

  # required if tvshow is not indexed/recognized in library
  if item['tvshow'] == "":
    log(__name__, "item %s" % item)
    # replace dots with spaces in title
    titulo = re.sub(r'\.', ' ', item['title'])
    log(__name__, "title no dots: %s" % titulo)
    mo = re.search(r'(.*)[sS](\d+)[eE](\d+)', titulo) #S01E02 like
    if not mo:
      mo = re.search(r'(.*)(\d\d)[xX](\d+)', titulo) # old 10x02 style
    if not mo:
      mo = re.search(r'(.*)(\d)[xX](\d+)', titulo) # old 1x02 style
    if not mo:
      mo = re.search(r'(.*) (\d+)(\d\d)', titulo) # 102 style 
    # split title in tvshow, season and episode
    if mo:
      item['tvshow'] = mo.group(1)
      if item['tvshow'].endswith(' - '):
          item['tvshow'] = item['tvshow'][:-3]
      item['season'] = mo.group(2)
      item['episode'] = mo.group(3)
      log(__name__, "item %s" % item)
    else:
      log(__name__, "could not parse tvshow name and episode number")
  
  Search(item)  

elif params['action'] == 'download':
  log(__name__, params)
  ## we pickup all our arguments sent from def Search()
  subs = Download(params["link"],params["filename"],params['referer'])
  ## we can return more than one subtitle for multi CD versions, for now we are still working out how to handle that in XBMC core
  for sub in subs:
    listitem = xbmcgui.ListItem(label=sub)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=sub,listitem=listitem,isFolder=False)
 

xbmcplugin.endOfDirectory(int(sys.argv[1])) ## send end of directory to XBMC
