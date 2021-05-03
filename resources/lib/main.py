# -*- coding: utf-8 -*-
# Copyright: (c) 2016, Chamchenko
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)
# This file is part of plugin.video.nbainternational



from codequick import run
from codequick import Route
from codequick import Listitem

from codequick.utils import bold
from resources.lib.tools import *
from resources.lib.vars import *
from resources.lib.nba_tv import NBA_TV
from resources.lib.games import BROWSE_GAMES_MENU
from resources.lib.series import BROWSE_SERIES
from resources.lib.videos import BROWSE_VIDEOS
from resources.lib.videos import BROWSE_COLLECTIONS
from resources.lib.search import SEARCH_VIDEOS


@Route.register(content_type="videos")
def root(plugin):
    plugin.log('Creating Main Menu', lvl=plugin.WARNING)
    # get kids user id
    
    yield Listitem.from_dict(
                                NBA_TV,
                                bold('NBA TV')
                            )
    yield Listitem.from_dict(
                                BROWSE_GAMES_MENU,
                                bold('Games')
                            )
    yield Listitem.from_dict(
                                BROWSE_SERIES,
                                bold('Series')
                            )
    yield Listitem.from_dict(
                                BROWSE_COLLECTIONS,
                                bold('Video Collections')
                            )
    yield Listitem.from_dict(
                                BROWSE_VIDEOS,
                                bold('Clips'),
                                params = {'slug': 'nba-tv-clips'}
                            )
    yield Listitem.search(
                            SEARCH_VIDEOS
                         )
