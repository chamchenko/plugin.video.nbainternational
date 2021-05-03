# -*- coding: utf-8 -*-
# Copyright: (c) 2016, Chamchenko
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)
# This file is part of plugin.video.nbainternational


import xbmcplugin
import urlquick

from resources.lib.vars import *
from resources.lib.tools import *
from codequick import Route
from codequick import Listitem
from codequick import Resolver



@Resolver.register(autosort=False, content_type="videos")
def SEARCH_VIDEOS(plugin, search_query, start=0):
    plugin.add_sort_methods(xbmcplugin.SORT_METHOD_UNSORTED)
    headers = {'User-Agent': USER_AGENT}
    params = {
                'fl': 'sequence,name,description,image,slug,share,runtime,releaseDate,pp_ipn',
                'sort': 'releaseDate desc',
                'rows': 22,
                'start': start,
                'q': search_query
             }
    result = urlquick.get(
                            SEARCH_URL,
                            params=params,
                            headers=headers
                         ).xml()
    results = result.findall("result")[0].findall('doc')
    liz = None
    for video in results:
        liz = Listitem()
        liz.info['mediatype'] = 'videos'
        for sub_vid in video:
            if sub_vid.attrib['name'] == 'image':
                liz.art['thumb'] = THUMB_BASE % sub_vid.text
            elif sub_vid.attrib['name'] == 'runtime':
                liz.info['duration'] = int(sub_vid.text)
            elif sub_vid.attrib['name'] == 'name':
                liz.label = sub_vid.text
            elif sub_vid.attrib['name'] == 'description':
                liz.info['plot'] = sub_vid.text
            elif sub_vid.attrib['name'] == 'releaseDate':
                liz.info.date(sub_vid.text, "%Y-%m-%dT%H:%M:%SZ")
            elif sub_vid.attrib['name'] == 'pp_ipn':
                url = sub_vid.text
                liz.path = url
                liz.property[INPUTSTREAM_PROP] ='inputstream.adaptive'
                for protocol, protocol_info in PROTOCOLS.items():
                    if any(".%s" % extension in url for extension in protocol_info['extensions']):
                        liz.property['inputstream.adaptive.manifest_type'] = protocol
                        yield liz
                    else:
                        continue
    if not liz:
        yield False
        return
    else:
        yield Listitem.next_page(
                                    search_query=search_query,
                                    start=start+22
                                )
