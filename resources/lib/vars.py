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
FAVORITE = Script.setting.get_string('fav_team')
CACHE_THUMB = Script.setting.get_boolean('cache_thumb')
DIS_MSGS = Script.setting.get_boolean('disable_msgs')
EN_CAL = Script.setting.get_boolean('enable_cal')

#Web related
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'

IDENTIFY = 'https://identity.nba.com/api/v1/'
PROFILE_URL = IDENTIFY + 'profile'
LOGIN_URL = IDENTIFY + 'auth'
TOKEN_URL = IDENTIFY + 'oauth/token'
AUTH_URL = IDENTIFY + 'sts'
SUBSCRIPTION_URL = IDENTIFY + 'profile?entitlements=true'

WATCH = 'https://watch.nba.com/'
GAME_DATA_ENDPOINT = WATCH + 'game/%s?format=json'
CONFIG_ENDPOINT = WATCH + 'service/config?format=json&cameras=true'
FREE_TOKEN_URL = WATCH + 'secure/accesstoken'

PLAY_OPTIONS_URL = 'https://ottapp-appgw-client.nba.com/S1/subscriber/v1/events/%s/play-options?IsexternalId=true'
PLAY_ROLL_URL = 'https://ottapp-appgw-amp.nba.com/v1/client/roll?ownerUid=azuki&mediaId=%s&sessionId=%s'
WIDEVINE_LICENSE_URL = 'https://ottapp-appgw-amp.nba.com/v1/client/get-widevine-license?ownerUid=azuki&mediaId=%s&sessionId=%s'

NBAAPI = 'https://nbaapi.neulion.com/api_nba/v1/'
RENEW_TOKEN_URL = NBAAPI + 'accesstoken'
PUBLISH_ENDPOINT = NBAAPI + 'publishpoint'
GAME_URL = NBAAPI + 'game'

TEAMS_URL = 'https://neulion-a.akamaihd.net/nlmobile/nba/config/2014/teams.json'
CONFIG_URL = 'https://neulionms-a.akamaihd.net/nbad/player/v1/nba/site_spa/config.json'
SEARCH_URL = 'https://neulionscnbav2-a.akamaihd.net/solr/nbad_program/usersearch'

TEAMS_LOGO_URL = 'https://cdn.nba.com/logos/nba/%s/global/L/512x512/logo.png'
GAME_THUMB_URL = 'https://davinci-qa.nba.com/images/lp/%s/details_pre_game_456x456.jpg'
THUMB_BASE = 'https://nbadsdmt.akamaized.net/media/nba/nba/thumbs/%s'


DAILY_URL = 'https://nlnbamdnyc-a.akamaihd.net/fs/nba/feeds_s2019/schedule_atv/%s/%s_%s.js'
WEEKLY_URL = 'https://nlnbamdnyc-a.akamaihd.net/fs/nba/feeds_s2019/schedule/%s/%s_%s.js?t=%s'
MONTHLY_URL = 'http://gmsapi.neulion.com/nbagameservice/games/month'
GAMEDATES_URL = 'https://nbaapi.neulion.com/api_nba/v1/schedule'

API_BASE_URL = 'https://content-api-prod.nba.com/public/1/'
NBA_TV_SERIES_URL = API_BASE_URL + 'endeavor/video-list/nba-tv-series'
NBA_TV_SERIE_URL = NBA_TV_SERIES_URL + '/%s'
VIDEO_CALLETIONS_URL = API_BASE_URL + 'endeavor/layout/watch/landing'
VIDEO_CALLETIONS_URL2 = API_BASE_URL + 'endeavor/layout/watch/nbatv'
VIDEO_CALLETIONS_URL3 = API_BASE_URL + 'endeavor/layout/watch/leaguepass'
VIDEO_CALLETION_URL = API_BASE_URL + 'endeavor/video-list/collection/%s'
PLAYER_URL = API_BASE_URL + 'content/video'
TEAM_VODEO_URL = API_BASE_URL + 'content'

REPLAY_CENTER_URL = 'https://official.nba.com/wp-json/api/v1/query_replay_feed'
REPLAY_CENTER_VID_URL = "https://videos.nba.com/nba/official-replay/media/%s_1280x720.mp4"

PLAYERS_URL = 'https://stats.nba.com/stats/playerindex'

PLAYER_PHOTO_URL = 'https://cdn.nba.com/headshots/nba/latest/1040x760/%s.png'
PLAYER_GENERIC_URL = 'https://cdn.nba.com/headshots/nba/latest/260x190/logoman.png'
CAM_LOGO = 'https://cdn.nba.com/logos/nba/Endeavor/cameras/logos/pc/%s'
MEDIA_PATH = 'resource://resource.images.nbainternational/%s'


PROTOCOLS = {
    'mpd': {'extensions': ['mpd'], 'mimetype': 'application/dash+xml'},
    'hls': {'extensions': ['m3u8', 'm3u'], 'mimetype': 'application/vnd.apple.mpegurl'},
}
DRM = 'com.widevine.alpha'
