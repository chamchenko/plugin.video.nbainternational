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
def BROWSE_CLIPS(plugin):
    pass


@Route.register
def BROWSE_COLLECTIONS(plugin):
    headers = {'User-Agent': USER_AGENT}
    collections = urlquick.get(
                                VIDEO_CALLETIONS_URL,
                                headers=headers,
                                max_age=86400
                              ).json()['results']['carousels']
    collections += urlquick.get(
                                VIDEO_CALLETIONS_URL2,
                                headers=headers,
                                max_age=86400
                              ).json()['results']['carousels']
    collections += urlquick.get(
                                VIDEO_CALLETIONS_URL3,
                                headers=headers,
                                max_age=86400
                              ).json()['results']['carousels']
    for collection in collections:
        if collection['type'] == "video_carousel":
            title = collection['title']
            slug = collection['value']['slug']
            liz = Listitem()
            liz.info['mediatype'] = 'episode'
            liz.label = title
            liz.art['thumb'] = collection['value']['videos'][0]['image']
            liz.set_callback(
                                BROWSE_VIDEOS,
                                slug=slug
                            )
            yield liz
        else:
            if collection['title'] == "NBA TV SHOWS":
                continue
            for sub_collection in collection['value']['items']:
                title = sub_collection['name']
                slug = sub_collection['slug']
                liz = Listitem()
                liz.info['mediatype'] = 'episode'
                liz.label = title
                try:
                    liz.art['thumb'] = sub_collection['image']
                except:
                    liz.art['thumb'] = sub_collection['coverImage']['landscape']
                liz.set_callback(
                                    BROWSE_VIDEOS,
                                    slug=slug
                                )
                yield liz



@Route.register(autosort=False)
def BROWSE_VIDEOS(plugin, slug, page=1):
    headers = {'User-Agent': USER_AGENT}
    per_page = 22
    params = {
                "sort": "releaseDate desc",
                "page": page,
                "count": per_page
             }
    videos = urlquick.get(
                            VIDEO_CALLETION_URL % slug,
                            headers=headers,
                            params=params,
                            max_age=3600
                         ).json()
    has_more = videos['results']['pageNext']
    for video in videos['results']['videos']:
        videoId = video['program']['id']
        runtime = video['program']['runtimeHours'].split(':')
        seconds = int(runtime[-1])
        minutes = int(runtime[-2])
        duration = minutes * 60 + seconds
        liz = Listitem()
        liz.info['mediatype'] = 'episode'
        liz.label = video['title']
        liz.art['thumb'] = video['image']
        liz.info.date(video['releaseDate'], "%Y-%m-%dT%H:%M:%SZ")
        liz.info['mediatype'] = 'episode'
        liz.info['plot'] = video['description']
        liz.info['duration'] = duration
        liz.set_callback(
                            PLAY_VIDEO,
                            title=video['title'],
                            videoId=videoId
                        )
        yield liz
    if has_more:
        yield Listitem.next_page(
                                    slug=slug,
                                    page=page+1
                                )



@Resolver.register
def PLAY_VIDEO(plugin, videoId, title):
    headers = get_headers()
    if not headers:
        yield False
        return
    payload_data = {
                        'type': 'video',
                        'id': videoId,
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
    liz.path = url
    liz.label = title
    for protocol, protocol_info in PROTOCOLS.items():
        if any(".%s" % extension in url for extension in protocol_info['extensions']):
            is_helper = Helper(protocol, drm=DRM)
            if is_helper.check_inputstream():
                liz.property[INPUTSTREAM_PROP] ='inputstream.adaptive'
                liz.property['inputstream.adaptive.manifest_type'] = protocol
                liz.property['inputstream.adaptive.license_type'] = DRM
                license_key = '%s|authorization=bearer %s|R{SSM}|' % (LICENSE_URL, drm)
                liz.property['inputstream.adaptive.license_key'] = license_key
    yield liz
