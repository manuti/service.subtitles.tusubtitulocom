# -*- coding: utf-8 -*-
import urllib
import xbmc

languages = {
    u"Español (España)": ("Spanish", "es", "es", 1),
    u"Español (Latinoamérica)": ("Latino", "es", "es", 2),
    u"English": ("English", "en", "en", 2),
}

def log(module, msg):
    xbmc.log((u"### [%s] - %s" % (module,msg,)).encode('utf-8'), level=xbmc.LOGNOTICE)

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
