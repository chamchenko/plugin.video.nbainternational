# -*- coding: utf-8 -*-
# Copyright: (c) 2016, Chamchenko
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)
# This file is part of plugin.video.nbainternational

import xbmc

from codequick.utils import urljoin_partial
from codequick import Script
from random import choice

XBMC_VERSION = int(xbmc.getInfoLabel("System.BuildVersion").split('-')[0].split('.')[0])
INPUTSTREAM_PROP = 'inputstream' if XBMC_VERSION >= 19 else 'inputstreamaddon'

#Add-on related
ADDON_ID = 'plugin.video.nbainternational'
ADDON_NAME =Script.get_info('name')
SETTINGS_LOC = Script.get_info('profile')
ADDON_PATH = Script.get_info('path')
ADDON_VERSION = Script.get_info('version')
ICON = Script.get_info('icon')
FANART = Script.get_info('fanart')
EMAIL = Script.setting.get_string('username')
PASSWORD = Script.setting.get_string('password')
CACHE_THUMB = Script.setting.get_boolean('cache_thumb')
DIS_MSGS = Script.setting.get_boolean('disable_msgs')
EN_CAL = Script.setting.get_boolean('enable_cal')

#Web related
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'

IDENTIFY = 'https://identity.nba.com/api/v1/'
LOGIN_URL = IDENTIFY + 'auth'
TOKEN_URL = IDENTIFY + 'oauth/token'
AUTH_URL = IDENTIFY + 'sts'
SUBSCRIPTION_URL = IDENTIFY + 'profile?entitlements=true'

WATCH = 'https://watch.nba.com/'
FREE_TOKEN_URL = WATCH + 'secure/accesstoken'

CORE_API = 'https://core-api.nba.com/cp/api/v1.9/'
CORE_API_KEY = '747fa6900c6c4e89a58b81b72f36eb96'
GAMECARD_URL = CORE_API + 'feeds/gamecardfeed'

PLAY_OPTIONS_URL = 'https://ottapp-appgw-client.nba.com/S1/subscriber/v2/events/%s/play-options?IsexternalId=true'
PLAY_ROLL_URL = 'https://ottapp-appgw-amp.nba.com/v1/client/roll?ownerUid=azuki&mediaId=%s&sessionId=%s'
PLAY_BEACON_URL = 'https://ottapp-appgw-amp.nba.com/v1/client/beacons?ownerUid=azuki&mediaId=%s&sessionId=%s'
WIDEVINE_LICENSE_URL = 'https://ottapp-appgw-amp.nba.com/v1/client/get-widevine-license?ownerUid=azuki&mediaId=%s&sessionId=%s'

RENEW_TOKEN_URL = 'https://nbaapi.neulion.com/api_nba/v1/accesstoken'

NBA_TEAMS = [
    ('ATL', 1610612737, 'Atlanta Hawks'), ('BOS', 1610612738, 'Boston Celtics'),
    ('BKN', 1610612751, 'Brooklyn Nets'), ('CHA', 1610612766, 'Charlotte Hornets'),
    ('CHI', 1610612741, 'Chicago Bulls'), ('CLE', 1610612739, 'Cleveland Cavaliers'),
    ('DAL', 1610612742, 'Dallas Mavericks'), ('DEN', 1610612743, 'Denver Nuggets'),
    ('DET', 1610612765, 'Detroit Pistons'), ('GSW', 1610612744, 'Golden State Warriors'),
    ('HOU', 1610612745, 'Houston Rockets'), ('IND', 1610612754, 'Indiana Pacers'),
    ('LAC', 1610612746, 'LA Clippers'), ('LAL', 1610612747, 'Los Angeles Lakers'),
    ('MEM', 1610612763, 'Memphis Grizzlies'), ('MIA', 1610612748, 'Miami Heat'),
    ('MIL', 1610612749, 'Milwaukee Bucks'), ('MIN', 1610612750, 'Minnesota Timberwolves'),
    ('NOP', 1610612740, 'New Orleans Pelicans'), ('NYK', 1610612752, 'New York Knicks'),
    ('OKC', 1610612760, 'Oklahoma City Thunder'), ('ORL', 1610612753, 'Orlando Magic'),
    ('PHI', 1610612755, 'Philadelphia 76ers'), ('PHX', 1610612756, 'Phoenix Suns'),
    ('POR', 1610612757, 'Portland Trail Blazers'), ('SAC', 1610612758, 'Sacramento Kings'),
    ('SAS', 1610612759, 'San Antonio Spurs'), ('TOR', 1610612761, 'Toronto Raptors'),
    ('UTA', 1610612762, 'Utah Jazz'), ('WAS', 1610612764, 'Washington Wizards'),
]
TEAMS_LOGO_URL = 'https://cdn.nba.com/logos/nba/%s/global/L/512x512/logo.png'

MEDIA_PATH = 'resource://resource.images.nbainternational/%s'

DRM = 'com.widevine.alpha'

KSS_URL = 'https://ottapp-appgw-client.nba.com/S1/kss/signkey'
