# -*- coding: utf-8 -*-
# This file is part of plugin.video.nbainternational


import json
import re
import urlquick

from resources.lib.vars import *
from resources.lib.games import resolve_stream
from codequick import Route
from codequick import Listitem
from codequick import Resolver

WATCH_FEED_URL = CORE_API + 'feeds/watch'
COLLECTION_PAGE_URL = 'https://www.nba.com/watch/list/collection/%s'
NEXT_DATA_RE = re.compile(r'__NEXT_DATA__" type="application/json">(.*?)</script>', re.S)



@Route.register(content_type="videos")
def CLASSICS_MENU(plugin):
    feed = urlquick.get(
                            WATCH_FEED_URL,
                            params={'isvip': 'false', 'platform': 'web', 'section': 'nbatv'},
                            headers={'Ocp-Apim-Subscription-Key': CORE_API_KEY, 'User-Agent': USER_AGENT},
                            max_age=3600
                       ).json()
    for module in feed.get('modules', []):
        if not module['moduleData'].get('header', '').upper().startswith('CLASSIC GAMES'):
            continue
        for card in module['cards']:
            data = card['cardData']
            if 'slug' not in data:
                continue
            liz = Listitem()
            liz.label = data['title']
            liz.art['thumb'] = (data.get('image') or {}).get('imageUrl', '')
            liz.set_callback(BROWSE_CLASSICS, slug=data['slug'])
            yield liz



@Route.register(autosort=False, content_type="episodes")
def BROWSE_CLASSICS(plugin, slug):
    html = urlquick.get(
                            COLLECTION_PAGE_URL % slug,
                            headers={'User-Agent': USER_AGENT},
                            max_age=3600
                       ).text
    match = NEXT_DATA_RE.search(html)
    if not match:
        return
    videos = json.loads(match.group(1))['props']['pageProps'].get('videos', [])
    for video in videos:
        mediaId = video.get('mediaKindAssetId')
        if not mediaId:
            continue
        liz = Listitem()
        liz.label = video['title']
        liz.art['thumb'] = video.get('featuredImage', '')
        liz.info['mediatype'] = 'episode'
        liz.info['plot'] = video.get('excerpt', '')
        liz.info['duration'] = video.get('videoDurationSeconds') or 0
        liz.set_callback(PLAY_CLASSIC, mediaId=mediaId, title=video['title'])
        yield liz



@Resolver.register
def PLAY_CLASSIC(plugin, mediaId, title):
    liz = resolve_stream(plugin, 'NBA_%s_Jitp_Reach_HD' % mediaId, '', rights_mode=1)
    if liz:
        liz.label = title
    yield liz
