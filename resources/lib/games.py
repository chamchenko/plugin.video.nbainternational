# -*- coding: utf-8 -*-
# Copyright: (c) 2016, Chamchenko
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)
# This file is part of plugin.video.nbainternational


import urlquick
import json
import time
import calendar
import xbmcgui
import os
import re

from resources.lib.vars import *
from resources.lib.tools import *
from resources.lib.auth import get_headers
from resources.lib.auth import get_profile_info
from resources.lib.auth import get_device_ids
from codequick import Route
from codequick import Listitem
from codequick import Resolver
from codequick.utils import bold
from inputstreamhelper import Helper





def process_games(game, teams_info):
        gameID = game['id']
        gameCode = game['seoName']
        game_time = game['st']
        game_time = time.strptime(game_time, '%Y-%m-%dT%H:%M:%S.%f')
        game_end_timestamp = None
        if 'playoff' in game:
            playoff_round = game['playoff']['round']
            host_team_record = int(game['playoff']['hr'].split('-')[0])
            away_team_record = int(game['playoff']['vr'].split('-')[0])
            game_number = host_team_record + away_team_record
        else:
            playoff_round = None
            game_number = None
        if 'et' in game:
            game_end = game['et']
            game_end = time.strptime(game_end, '%Y-%m-%dT%H:%M:%S.%f')
            game_end_timestamp = int(calendar.timegm(game_end) * 1000)
        else:
            if game_number:
                game_number = gameID[-1]
        game_timestamp = int(calendar.timegm(game_time) * 1000)
        host_team_code = game['h'] or 'TBD'
        away_team_code = game['v'] or 'TBD'
        game_state = game['gs']
        game_time_local = toLocalTimezone(time.mktime(game_time) * 1000)
        time_game = game_time_local.strftime("%I:%M %p")
        title = gen_title(
                            game_timestamp,
                            teams_info,
                            time_game,
                            host_team_code,
                            away_team_code,
                            game_end_timestamp,
                            playoff_round,
                            game_number
                         )
        liz = Listitem()
        liz.label = title
        date_game = game_time_local.strftime("%Y-%m-%d")
        liz.info.date(date_game, "%Y-%m-%d")
        if is_resources():
            thumb = get_thumb(host_team_code, away_team_code)
        elif CACHE_THUMB:
            thumb = download_thumb(GAME_THUMB_URL % gameID, host_team_code, away_team_code)
        else:
            thumb = GAME_THUMB_URL % gameID
        liz.art["thumb"] = thumb
        liz.art["poster"] = thumb
        feeds = []
        for feed in game['caData']:
            gt = 1
            cn = None
            rd = False
            if 'name' in feed:
                name = feed['name']
                if 'cat' in feed:
                    name = '%s: %s' %(feed['cat'], name)
            elif 'subcat' in feed:
                if feed['subcat'] == 'Teams' and feed['id'] == 'a':
                    name = 'Home Feed (%s)' % host_team_code
                elif feed['subcat'] == 'Teams' and feed['id'] == 'b':
                    name = 'Away Feed (%s)' % away_team_code
                    gt = 4
            if 'cat' in feed:
                if feed['cat'] == 'Condensed':
                    gt = 8
                else:
                    name = 'Full Game %s' %name
            else:
                name = 'Full Game %s' %name
            if feed['id'].isnumeric():
                cn = int(feed['id'])
            if 'audio' in feed:
                if feed['audio']:
                    rd = True
                    gt = 256
            feeds.append({ 'name': name, 'gt': gt, 'cn': cn, 'rd': rd})
        if 'video' in game:
            if 'c' in game['video']:
                name = 'Condensed Game'
                feeds.append({ 'name': name, 'gt': 8, 'cn': None, 'rd': False})
        liz.set_callback(
                            BROWSE_GAME,
                            gameID=gameID,
                            start_time=game_timestamp,
                            end_time=game_end_timestamp,
                            game_state=game_state,
                            feeds=feeds
                        )
        return liz
                

                
@Route.register(content_type="videos")
def BROWSE_GAMES_MENU(plugin):
    FAVORITE_TEAMS = get_profile_info()['FAVORITE_TEAMS']
    yield Listitem.from_dict(
                                BROWSE_MONTHS,
                                bold('Archive Games')
                            )
    if FAVORITE_TEAMS:
        yield Listitem.from_dict(
                                    BROWSE_TEAMS,
                                    bold('Favortite Team\'s Games'),
                                    params={'FAVORITE_TEAMS': FAVORITE_TEAMS}
                                )
    yield Listitem.from_dict(
                                BROWSE_TEAMS,
                                bold('Teams')
                            )



@Route.register(content_type='movies')
def BROWSE_TEAMS(plugin, FAVORITE_TEAMS=False):
    headers = {'User-Agent': USER_AGENT}
    teams_info = urlquick.get(
                                TEAMS_URL,
                                headers=headers,
                                max_age=7776000
                             ).json()['teams']
    for team in teams_info:
        if 'external' in teams_info[team]:
            if teams_info[team]['external']:
                continue
        if FAVORITE_TEAMS:
            if teams_info[team]['teamkey'] not in FAVORITE_TEAMS:
                continue
        team_name = '%s %s' % (
                                teams_info[team]['cityname'],
                                teams_info[team]['teamname']
                              )
        team_id = teams_info[team]['teamid']
        team_logo = TEAMS_LOGO_URL % team_id
        yield Listitem.from_dict(
                                    BROWSE_MONTHS,
                                    bold(team_name),
                                    art = {"thumb": team_logo},
                                    params = {'team': team}
                                )



@Route.register
def BROWSE_DAYS(plugin, month, year, cal=False, **kwargs):
    start_day = None
    headers = get_headers(True)
    if not headers:
        yield False
        return
    DATE = nowWEST()
    YEAR = DATE.year
    MONTH = DATE.month
    params = {
                'year': year,
                'month': month
             }
    if year == YEAR and month == MONTH and not cal:
        max_age = 0
        max_days = DATE.day - 1
    elif cal:
        max_days = None
        max_age = 0
        start_day = DATE.day
    else:
        max_age = 7776000
        max_days = None
    m = '0' + str(month) if month < 10 else month
    params = { 'month': '%s-%s' % (year, m)}
    gameDates = urlquick.get(
                                GAMEDATES_URL,
                                params=params,
                                headers=headers,
                                max_age=max_age
                            ).json()['gamedates']
    if not max_days and not start_day:
        gameDates = reversed(gameDates)
    elif start_day and int(m) == MONTH:
        n = len(gameDates) - start_day
        gameDates = gameDates[-n:]
    else:
        gameDates = gameDates[:max_days]
    for gameDate in gameDates:
        if gameDate['gamecount'] != '0':
            gamecount = gameDate['gamecount']
            is_empty = False
            day_time = gameDate['date']
            title = day_time + ' (%s games)' % gamecount
            day_time = time.strptime(day_time, '%Y-%m-%d')
            day_timestamp = calendar.timegm(day_time)
            day = datetime.datetime.fromtimestamp(day_timestamp)
            games = {'games': gameDate}
            yield Listitem.from_dict(
                                        BROWSE_GAMES,
                                        bold(title),
                                        params = {'DATE': day}
                                    )



@Route.register(content_type="videos")
def BROWSE_GAMES(plugin, DATE=None, games=None):
    if not DATE:
        DATE = nowWEST()
    headers = {'User-Agent': USER_AGENT}
    teams_info = urlquick.get(
                                TEAMS_URL,
                                headers=headers,
                                max_age=7776000
                             ).json()['teams']
    if not games:
        todays_game_url = DAILY_URL % (
                                         DATE.year,
                                         DATE.month,
                                         DATE.day
                                       )
        resp = urlquick.get(
                                todays_game_url,
                                headers=headers,
                                max_age=0
                            ).text.replace('var g_schedule=','')
        games = json.loads(resp)
    liz = None
    for game in games['games']:
        if 'game' in game:
            if not game['game']:
                continue
        liz = process_games(game, teams_info)
        yield liz

    if not liz:
        yield False
    if EN_CAL:
        yield Listitem.from_dict(
                                    BROWSE_MONTHS,
                                    bold('Upcoming'),
                                    params = {'cal': True}
                                )        
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
            start_month = 1
            day = DATE + datetime.timedelta(days=-1)
            yield Listitem.from_dict(
                                        BROWSE_GAMES,
                                        bold('Last Night'),
                                        params = {'DATE': day}
                                    )
            day = DATE + datetime.timedelta(days=-2)
            yield Listitem.from_dict(
                                        BROWSE_GAMES,
                                        bold('Two Nights Ago'),
                                        params = {'DATE': day}
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
    headers = get_headers(True)
    if not headers:
        yield False
        return

    for m in reversed(range(start_month,month+1)):
        params = { 'month': '%s-%s' % (year, m)}
        month_infos = urlquick.get(
                                    GAMEDATES_URL,
                                    params=params,
                                    headers=headers,
                                    max_age=7776000
                                  ).json()
        game_count = 0
        for d in month_infos['gamedates']:
            game_count += int(d['gamecount'])
        if game_count == 0:
            continue
        if m == month and this_year:
            title = 'This Month'
        elif m == month - 1 and this_year:
            title = 'Last Month'
        else:
            title = calendar.month_name[m]

        if not team:
            if not cal:
                title = '%s (%s games)' % (title, game_count)
            callB = BROWSE_DAYS
        else:
            callB = BROWSE_MONTH
        yield Listitem.from_dict(
                                    callB,
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
def BROWSE_MONTH(plugin, year, month, team, **kwargs):
    headers = {'User-Agent': USER_AGENT}
    teams_info = urlquick.get(
                                TEAMS_URL,
                                headers=headers,
                                max_age=7776000
                             ).json()['teams']
    try:
        params = {
                    'year': year,
                    'month': month,
                    'team': team
                 }
        games = urlquick.get(
                                MONTHLY_URL,
                                params=params,
                                headers=headers,
                                max_age=240
                            ).json()['games']
        if not any(games):
            raise Exception('')
    except:
        plugin.notify(
                        'Info',
                        'No available game in the selected Month',
                        display_time=3000,
                        sound=True
                     )
        yield False
        return
    for game in games:
        if game != []:
            game = game[0]
            liz = process_games(game,teams_info)
            yield liz




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
def BROWSE_GAME(plugin, gameID, start_time, end_time, game_state, feeds):
    for feed in feeds:
        feed['gameID'] = gameID
        feed['start_time'] = start_time
        feed['end_time'] = end_time
        feed['game_state'] = game_state
        yield Listitem.from_dict(
                                    PLAY_GAME,
                                    bold(feed['name']),
                                    params = feed
                                )



@Resolver.register
def PLAY_GAME(plugin, gameID, start_time, end_time, game_state, name, gt, cn, rd):
    plugin.log('PLAY_GAME start_time: %s' % start_time, lvl=plugin.DEBUG)
    plugin.log('PLAY_GAME end_time: %s' % end_time, lvl=plugin.DEBUG)
    headers = get_headers()
    if not headers:
        yield False
        return
    deviceinfos = get_device_ids()
    DEVICEID = deviceinfos['PCID']
    PCID = deviceinfos['PCID']
    payload_data = {
                        'type': 'game',
                        'extid': gameID,
                        'drmtoken': True,
                        'deviceid': DEVICEID,
                        'pcid': PCID,
                        'gt': gt,
                        'gs': game_state,
                        'format': 'json'
                   }
    if cn:
        payload_data['cam'] = cn
    if end_time:
        duration = end_time - start_time
        payload_data.update({'st': start_time})
        payload_data.update({'dur': duration})
        game_type = 'archive'
    else:
        game_type = 'live'
    plugin.log('PLAY_GAME: Fetching url  %s' % PUBLISH_ENDPOINT, lvl=plugin.DEBUG)
    plugin.log('PLAY_GAME: params %s' % payload_data, lvl=plugin.DEBUG)
    plugin.log('PLAY_GAME: game type %s' % game_type, lvl=plugin.DEBUG)
    Response = urlquick.post(
                                PUBLISH_ENDPOINT,
                                data=payload_data,
                                headers=headers,
                                max_age=0
                            ).json()
    url = Response['path']
    drm = Response['drmToken']
    try:
        stream_type = Response['streamType']
        if stream_type == 'dash':
            protocol = 'mpd'
        else:
            protocol = 'hls'
    except:
        protocol = 'hls'

    headers = {'User-Agent': USER_AGENT}
    start_point = None
    live_play_type = int(Script.setting.get_string('live_play_type'))
    ret = None
    if game_type == 'live':
        if live_play_type == 0:
            line1 = "Start from Beginning"
            line2 = "Go LIVE"
            ret = xbmcgui.Dialog().select("Game Options", [line1, line2])
            if ret == -1:
                yield None
                return
        if ret == 0 or live_play_type == 2:
            url = url.replace('br_long_master', 'master')
        content = urlquick.get(url, headers=headers).text
        sample = re.findall('(.*video.*\.m3u8?)', content)[0]
        match = re.search('(https?)://([^:]+)/([^?]+?)\?(.+)$', url)
        baseurl = os.path.dirname(match.group(1)+'://'+match.group(2)+'/'+match.group(3))
        ql_url = baseurl + '/' + sample
        content = urlquick.get(ql_url, headers=headers, max_age=0).text
        durations = re.findall('\#EXTINF\:([0-9]+\.[0-9]+)\,', content)
        duration = sum([float(i) for i in durations])
        if ret == 0 or live_play_type == 2:
            stream_start = re.findall('PROGRAM\-DATE\-TIME\:(.*)', content)[0]
            stream_start = time.strptime(stream_start, '%Y-%m-%dT%H:%M:%S.%fZ')
            stream_start_ts = calendar.timegm(stream_start) * 1000
            start_point = str(int((start_time - stream_start_ts) / 1000))
        elif ret == 1 or live_play_type == 1 :
            start_point = str(duration).split('.')[0]

    liz = Listitem()
    liz.path = url
    liz.label = name
    if rd:
        yield liz
        return
    liz.property[INPUTSTREAM_PROP] = 'inputstream.adaptive'
    is_helper = Helper(protocol, drm=DRM)
    if is_helper.check_inputstream():
        liz.property['inputstream.adaptive.manifest_type'] = protocol
        liz.property['inputstream.adaptive.license_type'] = DRM
        license_key = '%s|authorization=bearer %s|R{SSM}|' % (LICENSE_URL, drm)
        liz.property['inputstream.adaptive.license_key'] = license_key
        liz.property['inputstream.adaptive.manifest_update_parameter'] = 'full'
        liz.property['inputstream.adaptive.play_timeshift_buffer'] = 'true'

        if start_point:
            plugin.log('PLAY_GAME start_point: %s' % start_point, lvl=plugin.DEBUG)
            liz.property['ResumeTime'] = start_point
            liz.property['TotalTime'] = '14400'

        yield liz
    else:
        yield False
        return
