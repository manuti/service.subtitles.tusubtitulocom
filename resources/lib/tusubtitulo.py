# -*- coding: utf-8 -*-

import re
from utils import languages, geturl, log
from BeautifulSoup import BeautifulSoup

main_url = "https://www.tusubtitulo.com/serie/"

def search_tvshow(tvshow, season, episode, languages):
    #log(__name__,"TVSHOW = %s" % (tvshow))
    code = None
    level = 0
    while code is None and level < 4:
        _tvshow, code = parsetvshow(tvshow, level)
        if code is None:
            level += 1
    #log(__name__, tvshow)
    #log(__name__, season)
    #log(__name__, episode)
    #log(__name__, languages)
    searchstring = re.sub(r'\s', '-', _tvshow + '/' + season + '/' + episode)
    url = main_url + searchstring.lower() + '/' + code
    #log( __name__ ,"URL = %s" % (url))
    return getallsubsforurl(url, languages)

def getcode(tvshow):
    #log(__name__, "CODE=%s" %(tvshow))
    reg_code = '<a href="/show/([0-9]+)">'+tvshow+'</a>'
    content = geturl("https://www.tusubtitulo.com/series.php")
    result = re.findall(reg_code, content, re.IGNORECASE | re.DOTALL | re.MULTILINE | re.UNICODE)
    return result[0] if len(result) > 0 else None

def parsetvshow(tvshow, level):
    parser = {0: lambda: tvshow,
               1: lambda: tvshow.replace('(', '').replace(')', '') if '(' in tvshow else None,
               2: lambda: re.sub(r'\s+\([^)]*\)', '', tvshow) if '(' in tvshow else None,
               3: lambda: tvshow.replace("'", '') if '\'' in tvshow else None}
    _tvshow = parser.get(level, lambda: None)()
    code = None
    if _tvshow is not None:
        code = getcode(_tvshow)
    #log(__name__, code)
    return (_tvshow, code)

def getallsubsforurl(url, langs):
    result = []
    content = geturl(url)
    soup = BeautifulSoup(content)
    for versions in soup.findAll("div", {"class": "ssdiv", "id": re.compile('version[0-9]+')}):
        version = versions.find("p", {"class": "title-sub"})
        #log(__name__, version)
        if version is None:
            continue
        version = version.text.split(',')[0]
        #log(__name__, version)
        for subtitulo in versions.findAll("ul", {"class":"sslist"}):
            idioma = subtitulo.findNext("li", {"class": "li-idioma"}).findNext("b").text
            #log(__name__, idioma)
            enlace = subtitulo.findNext("li", {"class": "rng download green"})
            if enlace is None:
                continue
            enlace = enlace.findNext("a", {"class": None})["href"]
            #log(__name__, enlace)
            _idioma = languages.get(idioma, ("Unknown", "-", "???", 3))
            if _idioma[1] not in langs:
                continue
            filename = "{0}".format(version.encode('utf-8'))
            result.append({'filename': filename, 'flag': _idioma[2],
                           'link': "https://www.tusubtitulo.com/"+enlace, 
                           'lang': _idioma[0],'order': 1 + _idioma[3], 'referer': url})
    return result

if __name__ == "__main__":
    subs = search_tvshow("game of thrones", "6", "1", "es,en")
    for sub in subs: print sub['server'], sub['link']
