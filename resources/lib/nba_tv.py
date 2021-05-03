# -*- coding: utf-8 -*-
# Copyright: (c) 2016, Chamchenko
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)
# This file is part of plugin.video.nbainternational


import json
import urlquick

from resources.lib.vars import *
from resources.lib.tools import urlencode
from resources.lib.tools import get_headers
from codequick import Route
from codequick import Listitem
from codequick import Resolver
from inputstreamhelper import Helper


@Resolver.register(content_type="files")
def NBA_TV(plugin):
    plugin.log('NBA_TV', lvl=plugin.DEBUG)
    headers = get_headers()
    payload_data = {
                        'type': 'channel',
                        'id': 1,
                        'drmtoken': True,
                        'deviceid': DEVICEID,
                        'pcid': PCID,
                        'format': 'json'
                   }
    plugin.log('Fetching url: %s' % PUBLISH_ENDPOINT, lvl=plugin.DEBUG)
    plugin.log('Fetching data: %s' % payload_data, lvl=plugin.DEBUG)
    Response = urlquick.post(
                                PUBLISH_ENDPOINT,
                                data=payload_data,
                                headers=headers
                           ).json()
    url = Response['path']
    drm = Response['drmToken']
    liz = Listitem()
    liz.path = url
    liz.label = 'NBA TV'
    liz.property[INPUTSTREAM_PROP] ='inputstream.adaptive'
    
    for protocol, protocol_info in PROTOCOLS.items():
        if any(".%s" % extension in url for extension in protocol_info['extensions']):
            is_helper = Helper(protocol, drm=DRM)
            if is_helper.check_inputstream():
                liz.property['inputstream.adaptive.manifest_type'] = protocol
                liz.property['inputstream.adaptive.license_type'] = DRM
                license_key = '%s|authorization=bearer %s|R{SSM}|' % (LICENSE_URL, drm)
                liz.property['inputstream.adaptive.license_key'] = license_key
    return liz
