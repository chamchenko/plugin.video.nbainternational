# -*- coding: utf-8 -*-
# Copyright: (c) 2016, Chamchenko
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)
# This file is part of plugin.video.nbainternational

import xbmc
import json
import urlquick
import pytz
import datetime
import time


from resources.lib.vars import *
from codequick.utils import ensure_native_str
from codequick import Listitem
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




def toLocalTimezone(date):
    game_time = datetime.datetime.fromtimestamp(date/1000)
    local_timezone = tz.tzlocal()
    utc_timezone = pytz.timezone('UTC')
    return utc_timezone.localize(game_time).astimezone(local_timezone)


def nowEST():
    if hasattr(nowEST, "datetime"):
        return nowEST.datetime
    timezone = pytz.timezone('US/Eastern')
    utc_datetime = datetime.datetime.utcnow()
    est_datetime = utc_datetime + timezone.utcoffset(utc_datetime)
    nowEST.datetime = est_datetime
    return est_datetime


def authenticate():
    EMAIL = Script.setting.get_string('username')
    PASSWORD = Script.setting.get_string('password')
    FAVORITE = Script.setting.get_string('fav_team')
    if not EMAIL or not PASSWORD:
        Script.notify(
                        plugin.localize(30208),
                        plugin.localize(30201),
                        display_time=5000,
                        sound=True
                     )
        return None

    login_session = urlquick.Session()
    login_headers = {
                        'User-Agent': USER_AGENT,
                        'Content-Type': 'application/json',
                        'X-Client-Platform': 'web',
                        'Referer': 'https://watch.nba.com/',
                    }
    login_payload = {
                        "email": EMAIL,
                        "password": PASSWORD,
                        "rememberMe": True
                    }
    try:
        login_data = login_session.post(
                                            LOGIN_URL,
                                            json=login_payload,
                                            headers=login_headers,
                                            max_age=120
                                       ).json()
    except:
        Script.notify(
                        plugin.localize(30209),
                        plugin.localize(30202),
                        display_time=5000,
                        sound=True
                     )
        return None

    profile_data = login_session.get(PROFILE_URL, max_age=2592000).json()
    favorite_team = profile_data['data']['result']['favoriteTeams'][0]['teamTriCode']
    if favorite_team != FAVORITE:
        Script.setting.__setitem__('fav_team', favorite_team)

    auth_payload = {
                        'format': 'json',
                        'accesstoken': 'true',
                        'ciamlogin': 'true'
                   }
    auth_data = login_session.post(
                                    AUTH_URL,
                                    data=auth_payload,
                                    max_age=120
                                  ).json()
    login_status = auth_data['code']
    access_token = auth_data['data']['accessToken']
    login_headers.update({'authorization': 'Bearer %s' % access_token})
    params = {'associations': 'false'}
    subscrition_data = login_session.post(
                                            SUBSCRIPTION_URL,
                                            headers=login_headers,
                                            max_age=120
                                         ).json()
    if 'subs' in subscrition_data:
        subscrition = subscrition_data['subs'][0]['name']
        expiration_ = subscrition_data['subs'][0]['accessThrough']
        country = subscrition_data['subs'][0]['country']
        expiration_ = subscrition_data['subs'][0]['accessThrough']
        packages = subscrition_data['subs'][0]['details']
    elif login_status == "loginsuccess":
        Script.notify(
                        plugin.localize(30209),
                        plugin.localize(30203),
                        display_time=5000,
                        sound=True
                     )
        return None
    return access_token

def get_headers():
    access_token = authenticate()
    if access_token:
        headers = {
                    'User-Agent': USER_AGENT,
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'authorization': 'Bearer %s' % access_token
                  }
    else:
        headers = None
    return headers


