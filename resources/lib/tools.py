# -*- coding: utf-8 -*-
# Copyright: (c) 2016, Chamchenko
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)
# This file is part of plugin.video.nbainternational


import urlquick
import pytz
import datetime
import time
import xbmcvfs

from resources.lib.vars import *
from codequick.utils import ensure_native_str
from codequick import Script
from dateutil import tz
from inputstreamhelper import Helper

try:
    from urllib.parse import quote
    from urllib.parse import quote_plus
    from urllib.parse import unquote_plus
    from urllib.parse import urlencode
except ImportError:
    from urllib import quote
    from urllib import quote_plus
    from urllib import unquote_plus
    from urllib import urlencode

try:
    from xbmcvfs import translatePath
except ImportError:
    from xbmc import translatePath as translatepath
    def translatePath(path):
        return translatepath(path).decode('utf-8')





@Script.register
def clear_cache(plugin):
    # Clear urlquick cache
    urlquick.cache_cleanup(-1)
    Script.notify(
                    plugin.localize(30208),
                    plugin.localize(30204),
                    display_time=5000,
                    sound=True
                 )



def is_resources():
    return xbmc.getCondVisibility('System.HasAddon(resource.images.nbainternational)') == 1


def check_folder_path(path):
    end = ''
    if '/' in path and not path.endswith('/'):
        end = '/'
    if '\\' in path and not path.endswith('\\'):
        end = '\\'
    return path + end



def dir_exists(path):
    return xbmcvfs.exists(path)



def create_folder(path):
    if not dir_exists(path):
        xbmcvfs.mkdirs(path)



def download_thumb(url, ht, vt):
    create_folder('special://profile/addon_data/plugin.video.nbainternational/thumbnails/')
    thumb_file = 'special://profile/addon_data/plugin.video.nbainternational/thumbnails/%s-%s.png' % (ht, vt)
    rev_thumb = 'special://profile/addon_data/plugin.video.nbainternational/thumbnails/%s-%s.png' % (vt, ht)
    if not xbmcvfs.exists(thumb_file):
        try:
            content = urlquick.get(url).content
            file_handle = xbmcvfs.File(translatePath(thumb_file), 'wb')
            file_handle.write(bytearray(content))
            path = thumb_file
        except:
            thumb_file = rev_thumb
    return thumb_file



def get_thumb(ht, vt):
    thumb_file = 'resources/teams/%s/%s-%s.png' % (ht, ht, vt)
    if not xbmcvfs.exists(thumb_file):
        thumb_file = 'teams/%s/%s-%s.png' % (vt, vt, ht)
    return ensure_native_str(MEDIA_PATH % thumb_file)



def toLocalTimezone(date):
    game_time = datetime.datetime.fromtimestamp(date/1000)
    local_timezone = tz.tzlocal()
    utc_timezone = pytz.timezone('UTC')
    return utc_timezone.localize(game_time).astimezone(local_timezone)



def nowWEST():
    if hasattr(nowWEST, "datetime"):
        return nowWEST.datetime
    timezone = pytz.timezone('US/Pacific')
    utc_datetime = datetime.datetime.utcnow()
    est_datetime = utc_datetime + timezone.utcoffset(utc_datetime)
    nowWEST.datetime = est_datetime
    return est_datetime



def gen_title(game_timestamp, teams_info, time_game, host_team_code,
                away_team_code, game_end_timestamp, playoff_round, game_number):
    time_stamp_now = int(time.time() * 1000)
    if game_end_timestamp:
        if game_end_timestamp < time_stamp_now:
            status = 'Archive from'
    elif time_stamp_now < game_timestamp:
            status = 'UPCOMING starts at'
    else:
            status = 'LIVE started'

    if playoff_round and game_number:
        title = '%s (Game %s) ' %(playoff_round, game_number)
    else:
        title = ''
    host_team = '%s %s' % (
                            teams_info[host_team_code]['cityname'],
                            teams_info[host_team_code]['teamname']
                          )

    away_team = '%s %s' % (
                            teams_info[away_team_code]['cityname'],
                            teams_info[away_team_code]['teamname']
                          )

    title += '%s %s: %s vs %s ' % (
                                    status,
                                    time_game,
                                    away_team,
                                    host_team
                                 )
    return(title)
