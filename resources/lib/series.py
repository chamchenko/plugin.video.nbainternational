# -*- coding: utf-8 -*-
# Copyright: (c) 2016, Chamchenko
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)
# This file is part of plugin.video.nbainternational

import urlquick

from resources.lib.vars import *
from resources.lib.tools import *
from codequick import Route
from codequick import Listitem
from codequick import Resolver



@Route.register
def BROWSE_SERIES(plugin):
    headers = {'User-Agent': USER_AGENT}
    series = urlquick.get(
                            NBA_TV_SERIES_URL,
                            headers=headers,
                            max_age=86400
                         ).json()['results']
    for serie in series:
        slug = serie['series']['slug']
        poster = serie['series']['coverImage']['portrait']
        liz = Listitem()
        liz.info['mediatype'] = 'tvshow'
        liz.label = serie['series']['name']
        liz.info['plot'] = serie['series']['description']
        liz.art['poster'] = poster
        liz.art['fanart'] = serie['series']['coverImage']['landscape']
        liz.set_callback(
                            BROWSE_SEASONS,
                            slug=slug,
                            poster=poster
                        )
        yield liz



@Route.register
def BROWSE_SEASONS(plugin, slug, poster, page=1):
    headers = {'User-Agent': USER_AGENT}
    per_page = 50
    params = {
                "sort": "releaseDate desc",
                "page": page,
                "count": per_page
             }
    seasons = urlquick.get(
                            NBA_TV_SERIE_URL % slug,
                            headers=headers,
                            params=params,
                            max_age=3600
                          ).json()['results']['seasons']
    seasonidx = 0
    for season in seasons:
        liz = Listitem()
        liz.info['mediatype'] = 'tvshow'
        liz.label = 'Season %s' % season['season']
        liz.art['poster'] = poster
        liz.set_callback(
                            BROWSE_EPISODES,
                            slug=slug,
                            seasonidx=seasonidx
                        )
        yield liz
        seasonidx = seasonidx +1



@Route.register
def BROWSE_EPISODES(plugin, slug, seasonidx, page=1):
    headers = {'User-Agent': USER_AGENT}
    per_page = 50
    params = {
                "sort": "releaseDate desc",
                "page": page,
                "count": per_page
             }
    episodes = urlquick.get(
                            NBA_TV_SERIE_URL % slug,
                            headers=headers,
                            params=params,
                            max_age=3600
                          ).json()['results']['seasons'][seasonidx]
    for episode in episodes['episodes']:
        runtime = episode['program']['runtimeHours'].split(':')
        seconds = int(runtime[-1])
        minutes = int(runtime[-2])
        duration = minutes * 60 + seconds
        episodeId = episode['program']['id']
        if len(runtime) == 3:
            hours = int(runtime[0])
            duration = duration + hours * 3600
        liz = Listitem()
        liz.label = episode['title']
        liz.art['thumb'] = episode['image']
        liz.info.date(episode['releaseDate'], "%Y-%m-%dT%H:%M:%SZ")
        liz.info['mediatype'] = 'episode'
        liz.info['plot'] = episode['description']
        liz.info['duration'] = duration
        liz.set_callback(
                            PLAY_EPISODE,
                            episodeId=episodeId,
                            title=episode['title']
                        )
        yield liz



@Resolver.register
def PLAY_EPISODE(plugin, episodeId, title):
    headers = get_headers()
    if not headers:
        yield False
        return
    payload_data = {
                        'type': 'video',
                        'id': episodeId,
                        'drmtoken': True,
                        'deviceid': DEVICEID,
                        'pcid': PCID,
                        'format': 'json'
                   }
    Response = urlquick.post(
                                PUBLISH_ENDPOINT,
                                data=payload_data,
                                headers=headers
                           ).json()
    url = Response['path']
    drm = Response['drmToken']
    liz = Listitem()
    liz.label = title
    liz.path = url
    for protocol, protocol_info in PROTOCOLS.items():
        if any(".%s" % extension in url for extension in protocol_info['extensions']):
            is_helper = Helper(protocol, drm=DRM)
            if is_helper.check_inputstream():
                liz.property[INPUTSTREAM_PROP] ='inputstream.adaptive'
                liz.property['inputstream.adaptive.manifest_type'] = protocol
                liz.property['inputstream.adaptive.license_type'] = DRM
                license_key = '%s|authorization=bearer %s|R{SSM}|' % (LICENSE_URL, drm)
                liz.property['inputstream.adaptive.license_key'] = license_key
            else:
                liz = False
    yield liz
    return
