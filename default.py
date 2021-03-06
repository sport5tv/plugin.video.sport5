# -*- coding: utf-8 -*-
""" KODI addon for Sport5.cz    """

import urllib, urllib2, re, xbmcplugin, xbmcgui, os


def get_web_page(url):
    """    Sport5 web pages downloader    """
    req = urllib2.Request(url)
    req.add_header('User-Agent',
                   'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    web_page = response.read()
    web_page = web_page.decode('utf-8')
    response.close()
    return web_page


def get_shows():
    """    Create list of all shows    """
    link = get_web_page('http://sport5.cz/archiv/')

    match = re.compile('background-image:url\((?P<thumbnail>[^"]+)\).+?href=\"(?P<programme_url>[^"]+)\" title=\"(?P<title>[^"]+)\"',
                       re.MULTILINE | re.DOTALL).findall(link)

    for thumbnail, programme_url, title in match:
        add_dir(title.encode('utf-8'), programme_url, 1, thumbnail)

    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def get_episodes_of_show(programme_url):
    """    Create list of episodes    """
    link = get_web_page(programme_url)

    match = re.compile('background-image: url\((?P<thumbnail>[^"]+)\).+?href=\"(?P<episode_url>[^"]+)\" title=\"(?P<title>[^"]+)\".+?date">(?P<date>[^"]+ )<',
                       re.MULTILINE | re.DOTALL).findall(link)

    for thumbnail, episode_url, title, date in match:
        add_link(date.encode('utf-8') + title.encode('utf-8'), episode_url, 2, thumbnail)

    paging = re.compile(ur'"(?P<next_page_url>[^"]+)" title="Přejít na další stránku', re.UNICODE).findall(link)

    for next_page_url in paging:
        plugin_id = 'plugin.video.sport5'
        media_url = 'special://home/addons/{0}/resources/media/'.format(plugin_id)
        next_icon_path = media_url + "next.png"
        add_dir("[B]Další[/B]", next_page_url, 1, next_icon_path)

    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def get_video_link(episode_url):
    """ Download episode web page and parse stream url (one mp4 url)    """
    link = get_web_page(episode_url)

    match = re.compile('<video style.+?src="(?P<stream_url>[^"]+)"').findall(link)
    return match[0]


def get_params():
    """ Loads plugin parameters    """
    param = {'url': None,'mode': None,'name': None}
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if (params[len(params) - 1] == '/'):
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]
    return param


def add_link(name, url, mode, iconimage):
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    liz.setProperty('IsPlayable', 'true')
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def add_dir(name, url, mode, iconimage):
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

# MAIN EVENT PROCESSING STARTS HERE
url = None
name = None
mode = None

params = get_params()

if params["url"]:
    url = urllib.unquote_plus(params["url"])
if params["name"]:
    name = urllib.unquote_plus(params["name"])
if params["mode"]:
    mode = int(params["mode"])

# print "Sport5LOG: Mode: {0}, URL: {1}, Name: {2}".format(str(mode), str(url), str(name))

if mode is None:  # List all shows
    get_shows()

elif mode == 1:  # List episodes of selected show
    get_episodes_of_show(url)

elif mode == 2:  # Get stream url of episode and start player
    stream_url = str(get_video_link(url))
    list_item = xbmcgui.ListItem(path=stream_url)
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, list_item)