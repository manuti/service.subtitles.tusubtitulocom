# -*- coding: utf-8 -*-

# based on argenteam.net subtitles, based on a mod of Subdivx.com subtitles, based on a mod of Undertext subtitles
# developed by quillo86 and infinito for subtitulos.es and XBMC.org
# little fixes and updates by tux_os

# updated to new gotham subtitles service by infinito

# updated to tusubtitulo.com by jsevilleja

import xbmc
import re
import urllib
from operator import itemgetter
from utils import languages

main_url = "http://www.tusubtitulo.com/serie/"
subtitle_pattern1 = "<div id=\"version\" class=\"ssdiv\">(.+?)Versi&oacute;n(.+?)<span class=\"right traduccion\">(.+?)</div>(.+?)</div>"
subtitle_pattern2 = "<li class='li-idioma'>(.+?)<strong>(.+?)</strong>(.+?)<li class='li-estado (.+?)</li>(.+?)<li class='descargar (.+?)</li>"


def log(module, msg):
    xbmc.log((u"### [%s] - %s" % (module,msg,)).encode('utf-8'), level=xbmc.LOGNOTICE)

def search_tvshow(tvshow, season, episode, languages, filename):
    #log(__name__,"TVSHOW = %s" % (tvshow))
    subs = None
    for level in range(4):
        searchstring, ttvshow, sseason, eepisode = getsearchstring(tvshow, season, episode, level)
        if searchstring is None:
            continue
        code = getcode(ttvshow)
        url = main_url + searchstring.lower() + '/' + code
        #log( __name__ ,"URL = %s" % (url))

        subs = getallsubsforurl(url, languages, None, ttvshow, sseason, eepisode, level)
        if len(subs) > 0:
           break

    return subs

def getcode(tvshow):
    #log(__name__, "CODE=%s" %(tvshow))
    reg_code = '<a href="/show/([0-9]+)">'+tvshow+'</a>'
    content = geturl("http://www.tusubtitulo.com/series.php")
    result = re.findall(reg_code, content, re.IGNORECASE | re.DOTALL | re.MULTILINE | re.UNICODE)
    return result[0] if len(result) > 0 else ''

def getsearchstring(tvshow, season, episode, level):
    # Clean tv show name
    if level == 1:
        if '(' in tvshow or ')' in tvshow:
            # Series name like "Shameless (US)" -> "Shameless US"
            tvshow = tvshow.replace('(', '').replace(')', '')
        else:
            return None, None, None, None

    elif level == 2:
        if '(' in tvshow or ')' in tvshow:
            # Series name like "Shameless (*)" -> "Shameless"
            tvshow = re.sub(r'\s\([^)]*\)', '', tvshow)
        else:
            return None, None, None, None

    elif level == 3:
        if "'" in tvshow:
            tvshow = tvshow.replace("'", '')
        else:
            return None, None, None, None

    # Zero pad episode
    #episode = str(episode).rjust(2, '0')

    # Build search string
    searchstring = tvshow + '/' + season + '/' + episode

    # Replace spaces with dashes
    searchstring = re.sub(r'\s', '-', searchstring)

    #log( __name__ ,"%s Search string = %s" % ('test', searchstring))
    return searchstring, tvshow, season, episode

def getallsubsforurl(url, langs, file_original_path, tvshow, season, episode, level):

    subtitles_list = []

    content = geturl(url)

    for matches in re.finditer(subtitle_pattern1, content, re.IGNORECASE | re.DOTALL | re.MULTILINE | re.UNICODE):
        filename = urllib.unquote_plus(matches.group(2))

        subs = matches.group(4)

        for matches in re.finditer(subtitle_pattern2, subs, re.IGNORECASE | re.DOTALL | re.MULTILINE | re.UNICODE):
            ##log( __name__ ,"Descargas: %s" % (matches.group(2)))

            lang = matches.group(2)
            lang = re.sub(r'\xc3\xb1', 'n', lang)
            lang = re.sub(r'\xc3\xa0', 'a', lang)
            lang = re.sub(r'\xc3\xa9', 'e', lang)

            if lang not in languages:
                lang = "Unknown"
            languageshort = languages[lang][1]
            languagelong = languages[lang][0]
            ffilename = filename + ".(%s)" % languages[lang][2]
            order = 1 + languages[lang][3]

            estado = matches.group(4)
            #log(__name__, estado)
            estado = ''.join(c for c in estado if ord(c) >= 32)

            id = matches.group(6)
            #log(__name__, id)
            href_pattern = 'href="([^"]+)"' 
            link = re.findall(href_pattern, id)

            if estado.strip() == "green'>Completado".strip() and languageshort in langs and len(link) >0:
                subtitles_list.append({'rating': "0", 'no_files': 1, 'filename': ffilename, 'sync': False, 'id' : id, 'language_flag': languageshort + '.gif', 'language_name': languagelong, 'hearing_imp': False, 'link': link[0], 'lang': languageshort, 'order': order, 'referer': url})
                #log(__name__, "LINK = %s" %(link))

    return subtitles_list


def geturl(url):
    class AppURLopener(urllib.FancyURLopener):
        version = "Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko"
        def __init__(self, *args):
            urllib.FancyURLopener.__init__(self, *args)
        def add_referrer(self, url=None):
            if url:
                urllib._urlopener.addheader('Referer', url)

    urllib._urlopener = AppURLopener()
    urllib._urlopener.add_referrer("http://www.tusubtitulo.com/")
    try:
        response = urllib._urlopener.open(url)
        content    = response.read()
    except:
        #log( __name__ ,"%s Failed to get url:%s" % ('test', url))
        content    = None
    return content

#if __name__ == "__main__":
#    subs = search_tvshow("quantico", "1", "2", "es,en,fr", None)
#    for sub in subs: print sub['server'], sub['link']
