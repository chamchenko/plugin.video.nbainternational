# -*- coding: utf-8 -*-
# Copyright: (c) 2016, Chamchenko
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)
# This file is part of plugin.video.nbainternational


import json
import urlquick
import time
import urllib.parse

from resources.lib.vars import *
from codequick.storage import PersistentDict
from codequick import Script
from base64 import b64decode
from random import choice





login_headers = {
                    'User-Agent': USER_AGENT,
                    'Content-Type': 'application/json'
                }
auth_payload = {
                    'format': 'json',
                    'accesstoken': 'true',
                    'ciamlogin': 'true'
               }



def get_cookies():
    EMAIL = Script.setting.get_string('username')
    PASSWORD = Script.setting.get_string('password')
    if not EMAIL or not PASSWORD:
        Script.log('get_cookies: email or password empty', lvl=Script.DEBUG)
        Script.notify(
                        Script.localize(30208),
                        Script.localize(30201),
                        display_time=5000,
                        sound=True
                     )
        return None
    # set time to live to 90 days (NBA cookies expires in 90 days)
    logindata = PersistentDict(".accountinfo.profileinfo", ttl=7776000)
    try:
        CIAM_TOKEN = logindata['CIAM_TOKEN']
        refreshToken = logindata['refreshToken']
        Script.log('get_cookies: got cookies from cache', lvl=Script.DEBUG)
    except:
        CIAM_TOKEN = None
        refreshToken = None
        Script.log('get_cookies: unable to get cookies from cache', lvl=Script.DEBUG)


    if refreshToken and CIAM_TOKEN:
        login_payload = {'refreshToken': refreshToken}
        login_headers['CIAM_TOKEN'] = CIAM_TOKEN
        try:
            Script.log('get_cookies: Trying to renew cookies', lvl=Script.DEBUG)
            login_data = urlquick.post(
                                        TOKEN_URL,
                                        json=login_payload,
                                        headers=login_headers,
                                        max_age=0
                                     ).json()
            CIAM_TOKEN = login_data['data']['newTokens']['jwt']
            refreshToken = login_data['data']['newTokens']['refreshToken']
        except:
            Script.log('get_cookies: renew cookies failed will try to authtenticate', lvl=Script.DEBUG)
            CIAM_TOKEN = None
            refreshToken = None
    if not refreshToken or not CIAM_TOKEN:
        login_payload = {
                            "email": EMAIL,
                            "password": PASSWORD,
                            "rememberMe": True
                        }
        try:
            Script.log('get_cookies: Trying to authtenticate', lvl=Script.DEBUG)
            login_data = urlquick.post(
                                        LOGIN_URL,
                                        json=login_payload,
                                        headers=login_headers,
                                        max_age=0
                                      ).json()
            CIAM_TOKEN = login_data['data']['jwt']
            refreshToken = login_data['data']['refreshToken']
        except:
            Script.log('get_cookies: login failed', lvl=Script.DEBUG)
            Script.notify(
                            Script.localize(30209),
                            Script.localize(30202),
                            display_time=5000,
                            sound=True
                         )
            return None
    logindata['CIAM_TOKEN'] = CIAM_TOKEN
    logindata['refreshToken'] = refreshToken
    logindata.flush()
    Script.log('get_cookies: stored cookies to cache', lvl=Script.DEBUG)
    return CIAM_TOKEN, refreshToken



def get_token():
    headers = {'User-Agent': USER_AGENT}
    Script.log('get_token: Getting access token', lvl=Script.DEBUG)
    tokeninfo = PersistentDict(".accountinfo.token", ttl=7198)
    try:
        access_token = tokeninfo['access_token']
        expiry_time = None #tokeninfo['expiry_time']
        Script.log('get_token: Got access token from cache', lvl=Script.DEBUG)
    except:
        access_token = None
        expiry_time = None
        Script.log('get_token: Unable to get access token from cache', lvl=Script.DEBUG)
    if expiry_time:
        try:
            # b64 = access_token.split('.')[1]
            # token_json = b64decode(b64 + '=' * (-len(b64) % 4)).decode('utf-8')
            # exp = json.loads(token_json)['exp']
            exp = time.mktime(time.strptime(expiry_time[:26], '%Y-%m-%dT%H:%M:%S.%f'))
            now = time.time()
            # renew if under 5 minutes to expire
            if (exp > now) and (exp - now < 300):
                try:
                    Script.log('get_token: Trying to renew token', lvl=Script.DEBUG)
                    headers['CIAM_TOKEN'] = access_token
                    auth_data = urlquick.get(
                                                RENEW_TOKEN_URL,
                                                headers=headers,
                                                data=auth_payload,
                                                max_age=0
                                            ).json()
                except:
                    Script.log('get_token: Could not renew token will try to get new one', lvl=Script.DEBUG)
                    auth_data = None
                    access_token = None
            #if expired force renew
            if exp < now:
                Script.log('get_token: Cache token expired', lvl=Script.DEBUG)
                auth_data = None
                access_token = None
                expiry_time = None
            else:
                return access_token
        except Exception as exp:
            Script.log(exp, lvl=Script.ERROR)
            access_token = None

    if not access_token or not expiry_time:
        CIAM_TOKEN, refreshToken = get_cookies()
        if not CIAM_TOKEN:
            return False
        #headers['CIAM_TOKEN'] = CIAM_TOKEN
        Script.log('get_token: trying to get new token', lvl=Script.DEBUG)
        auth_data = urlquick.get(
                                    AUTH_URL,
                                    headers=headers,
                                    cookies={
                                        'nbaidentity': '{"jwt":"%s","refreshToken":"%s"}' % (CIAM_TOKEN, refreshToken)
                                    },
                                    max_age=0
                                ).json()
    
    login_status = auth_data['status']
    Script.log('get_cookies: Login status %s' % login_status, lvl=Script.DEBUG)
    if not 'success' in login_status:
        return False
        
    access_token = auth_data['data']['AccessToken']
    tokeninfo['access_token'] = access_token
    tokeninfo['expiry_time'] = auth_data['data']['ExpiryTime']
    tokeninfo.flush()
    Script.log('get_token: stored access token to cache', lvl=Script.DEBUG)
    login_headers.update({'authorization': 'Bearer %s' % CIAM_TOKEN})
    params = {'associations': 'false'}
    Script.log('get_token: getting subscrition infos', lvl=Script.DEBUG)
    subscrition_data = urlquick.get(
                                        SUBSCRIPTION_URL,
                                        headers=login_headers,
                                        max_age=86400
                                    ).json()
    if 'subscriptions' in subscrition_data['data']:
        Script.log('get_token: found subscrition infos', lvl=Script.DEBUG)
        """ 
        subscrition_type = subscrition_data['subs'][0]['productSubType']
        subscrition = subscrition_data['subs'][0]['name']
        country = subscrition_data['subs'][0]['country']
        expiration = subscrition_data['subs'][0]['accessThrough']
        Script.log('get_token: Found expriation date %s' % expiration, lvl=Script.DEBUG)
        packages = subscrition_data['subs'][0]['details']
        """
    else:
        Script.log('get_token: subscrition infos unavailable', lvl=Script.DEBUG)
        Script.notify(
                        Script.localize(30209),
                        Script.localize(30203),
                        display_time=5000,
                        sound=True
                     )
        return None
    return access_token



def get_free_token():
    headers = {'User-Agent': USER_AGENT}
    Script.log('get_free_token: Getting free access token', lvl=Script.DEBUG)
    tokeninfo = PersistentDict(".accountinfo.token", ttl=7198)
    try:
        access_token = tokeninfo['free_access_token']
        Script.log('get_free_token: Got free access token from cache', lvl=Script.DEBUG)
    except:
        access_token = None
        Script.log('get_free_token: Unable to get free access token from cache', lvl=Script.DEBUG)
    if not access_token:
        token_data = urlquick.get(
                                    FREE_TOKEN_URL,
                                    headers=headers,
                                    params={'format': 'json'},
                                    max_age=0
                                 ).json()
        access_token = token_data['data']['accessToken']
        tokeninfo['free_access_token'] = access_token
        tokeninfo.flush()
        Script.log('get_free_token: stored free access token to cache', lvl=Script.DEBUG)
    return access_token



def get_headers(free=False):
    if free:
        access_token = get_free_token()
    else:
        access_token = get_token()
    if access_token:
        headers = {
                    'User-Agent': USER_AGENT,
                    'Content-Type': 'application/json',
                    'Authorization': 'OAUTH2 access_token="%s"' % access_token
                  }
    else:
        headers = None
    return headers



def get_profile_info():
    profileinfo = PersistentDict(".accountinfo.profileinfo", ttl=7776000)
    try:
        FAVORITE_TEAMS = profileinfo['fav_team']
        FAVORITE_PLAYERS = profileinfo['fav_players']
        Script.log('get_profile_info: Got profile info from cache', lvl=Script.DEBUG)
    except:
        Script.log(
                    'get_profile_info: Favorite team or Favorite players unset',
                    lvl=Script.DEBUG
                  )
        FAVORITE_TEAMS = None
        FAVORITE_PLAYERS = None
    if not FAVORITE_TEAMS or not FAVORITE_PLAYERS:
        access_token = get_cookies()
        if not access_token:
            return {'FAVORITE_TEAMS': None, 'FAVORITE_PLAYERS': None}
        headers = {
                    'User-Agent': USER_AGENT,
                    'authorization': 'Bearer %s' % access_token
                  }
        Script.log('get_profile_info: Getting profile info', lvl=Script.DEBUG)
        profile_data = urlquick.get(
                                        PROFILE_URL,
                                        headers=headers,
                                        max_age=2592000
                                   ).json()
        #select the first team only
        FAVORITE_TEAMS = []
        for team in profile_data['data']['result']['favoriteTeams']:
            FAVORITE_TEAMS.append(team['teamTriCode'])
        FAVORITE_PLAYERS = []
        for player in profile_data['data']['result']['favoritePlayers']:
            FAVORITE_PLAYERS.append({'name': player['playerName'], 'player_id': player['playerId']})
        profileinfo['fav_team'] = FAVORITE_TEAMS
        profileinfo['fav_players'] = FAVORITE_PLAYERS
        profileinfo.flush()
        if not FAVORITE_PLAYERS and not DIS_MSGS:
            Script.notify(
                            Script.localize(30208),
                            Script.localize(30205),
                            display_time=5000,
                            sound=True
                         )
        if not FAVORITE_TEAMS and not DIS_MSGS:
            Script.notify(
                            Script.localize(30208),
                            Script.localize(30206),
                            display_time=5000,
                            sound=True
                         )
        Script.log('get_profile_info: stored profile info to cache', lvl=Script.DEBUG)
    return {'FAVORITE_TEAMS': FAVORITE_TEAMS, 'FAVORITE_PLAYERS': FAVORITE_PLAYERS}



def get_device_ids():
    profileinfo = PersistentDict(".accountinfo.profileinfo", ttl=7776000)
    try:
        return {'PCID': profileinfo['PCID'], 'DEVICEID': profileinfo['DEVICEID']}
        Script.log('get_device_ids: Got device ids from cache', lvl=Script.DEBUG)
    except:
        Script.log(
                    'get_profile_info: DEVICEID or PCID unset',
                    lvl=Script.DEBUG
                  )
        profileinfo['PCID'] = ''.join(choice('0123456789abcdef-') for n in range(36)).encode('utf-8')
        profileinfo['DEVICEID'] = 'web-%s' % profileinfo['PCID']
        profileinfo.flush()
        Script.log('get_device_ids: stored device ids to cache', lvl=Script.DEBUG)
        return {'PCID': profileinfo['PCID'], 'DEVICEID': profileinfo['DEVICEID']}

