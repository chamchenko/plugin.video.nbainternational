# -*- coding: utf-8 -*-
# Copyright: (c) 2016, Chamchenko
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)
# This file is part of plugin.video.nbainternational


import json
import urlquick

from resources.lib.vars import *
from resources.lib.tools import urlencode
from resources.lib.games import resolve_stream
from codequick import Route
from codequick import Listitem
from codequick import Resolver
from inputstreamhelper import Helper





@Resolver.register
def NBA_TV(plugin):
    liz = resolve_stream(plugin, 'NBATVD', '1023', rights_mode=2)
    if liz:
        liz.label = 'NBA TV'
    yield liz
