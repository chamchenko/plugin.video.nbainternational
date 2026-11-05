# -*- coding: utf-8 -*-
# Copyright: (c) 2016, Chamchenko
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)
# This file is part of plugin.video.nbainternational

import xbmc

from codequick import run
from codequick import Route
from codequick import Resolver
from codequick import Listitem
from codequick.utils import bold
from resources.lib.tools import *
from resources.lib.vars import *
from resources.lib.nba_tv import NBA_TV
from resources.lib.games import BROWSE_GAMES_MENU
from resources.lib.classics import CLASSICS_MENU





@Route.register(content_type="videos")
def root(plugin):
    plugin.log('Creating Main Menu', lvl=plugin.WARNING)
    yield Listitem.from_dict(
                                NBA_TV,
                                bold('NBA TV')
                            )
    yield Listitem.from_dict(
                                BROWSE_GAMES_MENU,
                                bold('Games')
                            )
    yield Listitem.from_dict(
                                CLASSICS_MENU,
                                bold('Classic Games')
                            )
