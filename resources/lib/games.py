# -*- coding: utf-8 -*-
# Copyright: (c) 2016, Chamchenko
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)
# This file is part of plugin.video.nbainternational


import urlquick
import json
import time
import calendar
import datetime
import uuid
import os
from urllib.parse import parse_qsl

from resources.lib.vars import *
from resources.lib.tools import *
from resources.lib.auth import get_device_ids
from resources.lib.auth import get_headers
from resources.lib.auth import get_token
from resources.lib import ed25519
from codequick import Route
from codequick import Script
from codequick.storage import PersistentDict
from codequick import Listitem
from codequick import Resolver
from codequick.utils import bold
from inputstreamhelper import Helper
from base64 import b64encode


AZUKI_IMC = 'IMC7.1.0_AN_D3.0.0_S0'
GAME_STATUS = {1: 'UPCOMING starts at', 2: 'LIVE started', 3: 'Archive from'}



def get_game_cards(date, max_age=0):
    headers = {
                'User-Agent': USER_AGENT,
                'Accept': 'application/json',
                'Ocp-Apim-Subscription-Key': CORE_API_KEY,
                'Origin': 'https://www.nba.com',
                'Referer': 'https://www.nba.com/'
              }
    params = {
                'gamedate': '%02d/%02d/%d' % (date.month, date.day, date.year),
                'platform': 'web'
             }
    try:
        feed = urlquick.get(
                                GAMECARD_URL,
                                params=params,
                                headers=headers,
                                max_age=max_age
                           ).json()
    except Exception as e:
        Script.log('get_game_cards: %s' % e, lvl=Script.ERROR)
        return []
    cards = []
    for module in feed.get('modules', []):
        for card in module.get('cards', []):
            data = card.get('cardData')
            if data and data.get('gameId'):
                cards.append(data)
    return cards



def process_games(game):
    home = game['homeTeam']
    away = game['awayTeam']
    status = game.get('gameStatus', 1)
    start = datetime.datetime.fromisoformat(game['gameTimeUtc'].replace('Z', '+00:00'))
    start_local = datetime.datetime.fromtimestamp(start.timestamp())
    away_name = '%s %s' % (away.get('teamCity', ''), away['teamName'])
    home_name = '%s %s' % (home.get('teamCity', ''), home['teamName'])
    if not Script.setting.get_boolean('hide_scores') and status != 1:
        away_name = '%s %s' % (away_name, away.get('score', 0))
        home_name = '%s %s' % (home_name, home.get('score', 0))
    title = '%s %s: %s vs %s' % (
                                    GAME_STATUS.get(status, GAME_STATUS[3]),
                                    start_local.strftime('%H:%M'),
                                    away_name,
                                    home_name
                                )
    if game.get('seasonType') == 'Playoffs' and game.get('gameDetailsHeader'):
        header = game['gameDetailsHeader'].get('nonSpoilerHeader')
        if header:
            title = '%s %s' % (header, title)
    liz = Listitem()
    liz.label = title.replace('  ', ' ')
    liz.info.date(start_local.strftime('%Y-%m-%d'), '%Y-%m-%d')
    images = game.get('images') or {}
    thumb = images.get('640x360') or images.get('1280x720')
    if thumb:
        liz.art['thumb'] = thumb
        liz.art['poster'] = thumb
    liz.set_callback(
                        BROWSE_GAME,
                        gameID=game['gameId'],
                        cache_max_age=0
                    )
    return liz



@Route.register(content_type="videos")
def BROWSE_GAMES_MENU(plugin):
    yield Listitem.from_dict(
                                BROWSE_GAMES,
                                bold('Live Games'),
                                params = {'DATE': nowWEST()}
                            )
    if EN_CAL:
        yield Listitem.from_dict(
                                    BROWSE_MONTHS,
                                    bold('Upcoming'),
                                    params = {'cal': True}
                                )
    yield Listitem.from_dict(
                                BROWSE_MONTHS,
                                bold('Games Archive')
                            )
    yield Listitem.from_dict(
                                BROWSE_TEAMS,
                                bold('Teams')
                            )



@Route.register(content_type='movies')
def BROWSE_TEAMS(plugin):
    for tricode, team_id, team_name in NBA_TEAMS:
        yield Listitem.from_dict(
                                    BROWSE_MONTHS,
                                    bold(team_name),
                                    art = {"thumb": TEAMS_LOGO_URL % team_id},
                                    params = {'team': tricode}
                                )



@Route.register(content_type="videos")
def BROWSE_DAYS(plugin, month, year, cal=False, **kwargs):
    DATE = nowWEST()
    first = datetime.date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    today = DATE.date()
    days = [first + datetime.timedelta(days=d) for d in range(last_day)]
    if cal:
        days = [d for d in days if d >= today]
    else:
        days = [d for d in days if d < today]
        days.reverse()
    for day in days:
        yield Listitem.from_dict(
                                    BROWSE_GAMES,
                                    bold(day.strftime('%Y-%m-%d')),
                                    params = {
                                                'DATE': datetime.datetime(day.year, day.month, day.day),
                                                'cache_max_age': 0 if cal else 60 * 60
                                             }
                                )



@Route.register(content_type="videos")
def BROWSE_GAMES(plugin, DATE=None, team=None, cache_max_age=0):
    if not DATE:
        DATE = nowWEST()
    cards = get_game_cards(DATE, cache_max_age)
    if team:
        cards = [c for c in cards if team in (c['homeTeam']['teamTricode'], c['awayTeam']['teamTricode'])]
    liz = None
    for card in cards:
        liz = process_games(card)
        yield liz

    if not liz:
        yield False
        return



@Route.register(content_type="videos")
def BROWSE_MONTHS(plugin, year=None, team=None, cal=False):
    start_month = 1
    if not year:
        this_year = True
        DATE = nowWEST()
        year = DATE.year
        month = DATE.month
        if not team and not cal:
            day = DATE + datetime.timedelta(days=-1)
            yield Listitem.from_dict(
                                        BROWSE_GAMES,
                                        bold('Last Night'),
                                        params = {'DATE': day, 'cache_max_age': 60 * 60}
                                    )
            day = DATE + datetime.timedelta(days=-2)
            yield Listitem.from_dict(
                                        BROWSE_GAMES,
                                        bold('Two Nights Ago'),
                                        params = {'DATE': day, 'cache_max_age': 60 * 60}
                                    )
        if cal:
            day = DATE + datetime.timedelta(days=+1)
            yield Listitem.from_dict(
                                        BROWSE_GAMES,
                                        bold('Tomorrow'),
                                        params = {'DATE': day}
                                    )
            day = DATE + datetime.timedelta(days=+2)
            yield Listitem.from_dict(
                                        BROWSE_GAMES,
                                        bold('In Two days'),
                                        params = {'DATE': day}
                                    )
            start_month = month
            month = 12
    else:
        this_year = False
        month = 12

    for m in reversed(range(start_month, month + 1)):
        if m == month and this_year:
            title = 'This Month'
        elif m == month - 1 and this_year:
            title = 'Last Month'
        else:
            title = calendar.month_name[m]
        yield Listitem.from_dict(
                                    BROWSE_MONTH if team else BROWSE_DAYS,
                                    bold(title),
                                    params = {
                                                'month': m,
                                                'year': year,
                                                'team': team,
                                                'cal': cal
                                             }
                                )
    if not cal:
        yield Listitem.from_dict(
                                    BROWSE_YEARS,
                                    bold('Older'),
                                    params = {
                                                'year': year,
                                                'team': team
                                             }
                                )



@Route.register(content_type="videos")
def BROWSE_MONTH(plugin, year, month, team, cal=False, **kwargs):
    today = nowWEST().date()
    last_day = calendar.monthrange(year, month)[1]
    days = [datetime.date(year, month, d) for d in range(1, last_day + 1)]
    days = [d for d in days if (d >= today if cal else d <= today)]
    if not cal:
        days.reverse()
    found = False
    for day in days:
        max_age = 0 if day >= today else 60 * 60 * 24
        cards = get_game_cards(datetime.datetime(day.year, day.month, day.day), max_age)
        for card in cards:
            if team in (card['homeTeam']['teamTricode'], card['awayTeam']['teamTricode']):
                found = True
                yield process_games(card)
    if not found:
        plugin.notify(
                        'Info',
                        'No available game in the selected Month',
                        display_time=3000,
                        sound=True
                     )
        yield False
        return



@Route.register(content_type="videos")
def BROWSE_YEARS(plugin, year, team=False):
    for y in reversed(range(2013,year)):
        yield Listitem.from_dict(
                                    BROWSE_MONTHS,
                                    bold(str(y)),
                                    params = {
                                                'year': y,
                                                'team': team
                                             }
                                )



@Route.register(content_type="videos")
def BROWSE_GAME(plugin, gameID, cache_max_age=0):
    headers = get_headers()
    if not headers:
        yield False
        return
    play_options = urlquick.get(
                                PLAY_OPTIONS_URL % gameID,
                                headers=headers,
                                max_age=cache_max_age
                            ).json()
    found = False
    for play_option in play_options.get('Schedules', []) + play_options.get('Vods', []):
        if not play_option.get('PlayActions'):
            continue
        names = play_option.get('DisplayName') or []
        name = names[0].get('Value') if names else None
        if not name:
            continue
        found = True
        yield Listitem.from_dict(
                                PLAY_GAME,
                                bold(name),
                                params = {
                                    'gameID': gameID,
                                    'videoProfileId': play_option['PlayActions'][0]['VideoProfile']['Id']
                                }
                            )
    if not found:
        plugin.notify(
                        'Info',
                        'No streams available for this game yet',
                        display_time=3000,
                        sound=True
                     )
        yield False
        return



def get_cdn_signature(access_token, qs):
    seed = os.urandom(32)
    kss = urlquick.post(
                            KSS_URL,
                            headers={
                                'User-Agent': USER_AGENT,
                                'Content-Type': 'application/json',
                                'Authorization': 'OAUTH2 access_token="%s"' % access_token
                            },
                            data=json.dumps({'PublicKey': b64encode(ed25519.public_key(seed)).decode('ascii')}),
                            max_age=0,
                            raise_for_status=False
                        )
    signed_key = kss.json().get('SignedKey')
    if not signed_key:
        return None
    signed_json = b64encode(json.dumps({'m': 'GET', 'qs': qs}, separators=(',', ':')).encode('utf-8')).decode('ascii')
    signature = b64encode(ed25519.sign(seed, signed_json.encode('ascii'))).decode('ascii')
    return b64encode(json.dumps({
        'signedKey': signed_key,
        'signedRequest': {'signedJson': signed_json, 'signature': signature}
    }, separators=(',', ':')).encode('utf-8')).decode('ascii')



def close_previous_session(headers):
    # Playback outlives this plugin call, so the previous session is closed on the next play
    # to avoid hitting the stream limit.
    store = PersistentDict(".lastsession", ttl=86400)
    try:
        last = store.get('session')
        if last:
            beacon_headers = {k: v for k, v in headers.items() if k != 'applicationtoken'}
            urlquick.post(
                            PLAY_BEACON_URL % (last['mediaId'], last['sessionId']),
                            headers=beacon_headers,
                            data=json.dumps({'beacon': {
                                'complete': True,
                                'inhome': 'no',
                                'inhome_changed': 'false',
                                'live': str(last['live']).lower(),
                                'inhome3pp': 'false'
                            }}),
                            max_age=0,
                            raise_for_status=False
                         )
            store['session'] = None
            store.flush()
    except Exception as e:
        Script.log('close_previous_session: %s' % e, lvl=Script.ERROR)
    return store



def resolve_stream(plugin, mediaId, application_token, rights_mode=1):
    access_token = get_token()
    if not access_token:
        return False
    device_uuid = get_device_ids()['PCID']
    if isinstance(device_uuid, bytes):
        device_uuid = device_uuid.decode('utf-8')
    device_profile = b64encode(json.dumps({
        'model': 'Desktop',
        'osVersion': '10.15.7',
        'vendorName': 'Apple',
        'osName': 'HTML5',
        'supportsHevcDecode': False,
        'wvLevel': 'L3',
        'deviceUUID': device_uuid
    }, separators=(',', ':')).encode('ascii')).decode('ascii')
    headers = {
        'content-type': 'text/plain;charset=UTF-8',
        'authorizationtoken': access_token,
        'azukiimc': AZUKI_IMC,
        'applicationtoken': application_token,
        'deviceprofile': device_profile
    }
    sessions = close_previous_session(headers)
    sessionId = uuid.uuid1()
    roll = urlquick.post(
                            PLAY_ROLL_URL % (mediaId, sessionId),
                            headers=headers,
                            data=json.dumps({'roll': {'inhome': 'no', 'rightsMode': rights_mode}}),
                            max_age=0,
                            raise_for_status=False
                        ).json()
    play_options = roll.get('response')
    if roll.get('result') != 'success' or not play_options:
        plugin.log('resolve_stream: roll failed: %s' % roll, lvl=plugin.ERROR)
        plugin.notify('Error', (roll.get('response') or {}).get('message') or 'Could not start the stream', display_time=5000, sound=True)
        return False

    sessions['session'] = {'mediaId': mediaId, 'sessionId': str(sessionId), 'live': bool(play_options.get('live'))}
    sessions.flush()

    manifest_path = play_options['manifest_uri'].split('?')[0]
    manifest_qs = dict(parse_qsl(play_options['manifest_uri'].partition('?')[2]))
    manifest_qs['sessionId'] = str(sessionId)
    url = '%s/%s?%s' % (
                            play_options['cdns']['cdn'][0]['base_uri'],
                            manifest_path,
                            urlencode(manifest_qs)
                        )
    signature = get_cdn_signature(access_token, manifest_qs)
    if not signature:
        plugin.log('resolve_stream: could not sign manifest request', lvl=plugin.ERROR)
        plugin.notify('Error', 'Could not sign stream request', display_time=5000, sound=True)
        return False
    protocol = 'mpd' if play_options['package_type'] in ('dash', 'mpd') else 'hls'
    license_url = WIDEVINE_LICENSE_URL % (mediaId, sessionId)

    liz = Listitem()
    liz.path = url
    liz.property[INPUTSTREAM_PROP] = 'inputstream.adaptive'

    is_helper = Helper(protocol, drm=DRM)
    if is_helper.check_inputstream():
        stream_headers = urlencode({
            'authorizationtoken': access_token,
            'x-mk-signature': signature,
            'User-Agent': USER_AGENT,
            'Origin': 'https://www.nba.com',
            'Referer': 'https://www.nba.com/'
        })
        liz.property['inputstream.adaptive.stream_headers'] = stream_headers
        liz.property['inputstream.adaptive.manifest_headers'] = stream_headers
        liz.property['inputstream.adaptive.license_type'] = DRM
        license_headers = urlencode({
            'AuthorizationToken': access_token,
            'AzukiIMC': AZUKI_IMC,
            'ApplicationToken': application_token,
            'DeviceProfile': device_profile,
            'Content-Type': 'text/plain'
        })
        license_key = '%s&is_dvr=false|%s|R{SSM}|' % (license_url, license_headers)
        liz.property['inputstream.adaptive.license_key'] = license_key
        liz.property['inputstream.adaptive.play_timeshift_buffer'] = 'true'
        return liz

    return False



@Resolver.register
def PLAY_GAME(plugin, gameID, videoProfileId):
    yield resolve_stream(plugin, videoProfileId, videoProfileId.split('_Jitp')[0])
