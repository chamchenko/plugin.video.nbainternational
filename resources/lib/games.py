# -*- coding: utf-8 -*-
# Copyright: (c) 2016, Chamchenko
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)
# This file is part of plugin.video.nbainternational

import urlquick
import time
import calendar
import xbmcgui
import os
import re


from resources.lib.vars import *
from resources.lib.tools import *
from codequick import Route
from codequick import Listitem
from codequick import Resolver
from codequick.utils import bold
from inputstreamhelper import Helper



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


def process_games(game, teams_info):
        gameID = game['id']
        gameCode = game['seoName']
        game_time = game['st']
        game_time = time.strptime(game_time, '%Y-%m-%dT%H:%M:%S.%f')
        game_end_timestamp = None
        if 'et' in game:
            game_end = game['et']
            game_end = time.strptime(game_end, '%Y-%m-%dT%H:%M:%S.%f')
            game_end_timestamp = int(calendar.timegm(game_end) * 1000)
        if 'playoff' in game:
            playoff_round = game['playoff']['round']
            host_team_record = int(game['playoff']['hr'].split('-')[0])
            away_team_record = int(game['playoff']['vr'].split('-')[0])
            game_number = host_team_record + away_team_record
        else:
            playoff_round = None
            game_number = None
        game_timestamp = int(calendar.timegm(game_time) * 1000)
        host_team_code = game['h']
        away_team_code = game['v']
        game_state = game['gs']
        has_away_feed = False
        has_condensed_game = False
        if 'video' in game:
            if 'af' in game['video']:
                has_away_feed = True
            if 'c' in game['video']:
                has_condensed_game = True
        game_cameras = []
        if 'cameraAngles' in game:
            game_cameras = game['cameraAngles'].split(',')
        game_time_local = toLocalTimezone(game_timestamp)
        time_game = game_time_local.strftime("%H:%M")
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
        liz.art["poster"] = GAME_THUMB_URL % gameID
        liz.art["thumb"] = GAME_THUMB_URL % gameID
        liz.art["icon"] = GAME_THUMB_URL % gameID
        liz.set_callback(
                            BROWSE_GAME,
                            gameID=gameID,
                            gameCode=gameCode,
                            start_time=game_timestamp,
                            end_time=game_end_timestamp,
                            game_state=game_state,
                            game_cameras=game_cameras,
                            has_away_feed=has_away_feed,
                            has_condensed_game=has_condensed_game,
                            host_team=host_team_code,
                            away_team=away_team_code
                        )
        return liz

@Route.register
def BROWSE_GAMES_MENU(plugin):
    yield Listitem.from_dict(
                                BROWSE_GAMES,
                                bold('Live Games')
                            )
    yield Listitem.from_dict(
                                ARCHIVE_GAMES,
                                bold('Games Archive')
                            )
    yield Listitem.from_dict(
                                FAV_TM_GAMES,
                                bold('Favortite Team\'s Games')
                            )  
    yield Listitem.from_dict(
                                TEAMS,
                                bold('Teams')
                            )

@Route.register
def TEAMS(plugin):
    headers = {'User-Agent': USER_AGENT}
    teams_info = urlquick.get(
                                TEAMS_URL,
                                headers=headers,
                                max_age=-1
                             ).json()['teams']
    for team in teams_info:
        if 'external' in teams_info[team]:
            if teams_info[team]['external']:
                continue
        team_name = '%s %s' % (
                                teams_info[team]['cityname'],
                                teams_info[team]['teamname']
                              )
        team_id = teams_info[team]['teamid']
        team_logo = TEAMS_LOGO_URL % team_id
        yield Listitem.from_dict(
                                    FAV_TM_GAMES,
                                    bold(team_name),
                                    art = {"thumb": team_logo},
                                    params = {'team': team}
                                )  




@Route.register
def ARCHIVE_GAMES(plugin, year=None):
    if not year:
        this_year = True
        DATE = nowEST()
        year = DATE.year
        month = DATE.month
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
    else:
        this_year = False
        month = 12
    for m in reversed(range(1,month+1)):
        if m == month and this_year:
            title = 'This Month'
        elif m == month - 1 and this_year:
            title = 'Last Month'
        else:
            title = calendar.month_name[m]
        yield Listitem.from_dict(
                                    BROWSE_DAYS,
                                    bold(title),
                                    params = {
                                                'month': m,
                                                'year': year
                                             }
                                )
    yield Listitem.from_dict(
                                BROWSE_YEARS,
                                bold('Older'),
                                params = {'year': year}
                            )


@Route.register
def BROWSE_YEARS(plugin, year):
    for y in reversed(range(2013,year)):
        yield Listitem.from_dict(
                                    ARCHIVE_GAMES,
                                    bold(str(y)),
                                    params = {'year': y}
                                )


@Route.register
def BROWSE_DAYS(plugin, month, year):
    DATE = nowEST()
    YEAR = DATE.year
    MONTH = DATE.month
    headers = {'User-Agent': USER_AGENT}   
    params = {
                'year': year,
                'month': month
             }
    if year == YEAR and month == MONTH:
        max_age = 0
        max_days = DATE.day - 1
    else:
        max_age = -1
        max_days = None
    try:
        gameDates = urlquick.get(
                                MONTHLY_URL,
                                params=params,
                                headers=headers,
                                max_age=max_age
                            ).json()['games']
        if not any(gameDates):
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
    if not max_days:
        gameDates = reversed(gameDates)
    else:
        gameDates = gameDates[:max_days]
    for gameDate in gameDates:
        if gameDate != []:
            is_empty = False
            day_time = gameDate[0]['d']
            title = day_time.split('T')[0]
            day_time = time.strptime(day_time, '%Y-%m-%dT%H:%M:%S.%f')
            day_timestamp = calendar.timegm(day_time)
            day = datetime.datetime.fromtimestamp(day_timestamp)
            games = {'games': gameDate}
            yield Listitem.from_dict(
                                        BROWSE_GAMES,
                                        bold(title),
                                        params = {
                                                    'DATE': day,
                                                    'games': games
                                                 }
                                    )

@Route.register
def BROWSE_GAMES(plugin, DATE=None, games=None):
    if not DATE:
        DATE = nowEST()
    headers = {'User-Agent': USER_AGENT}
    teams_info = urlquick.get(
                                TEAMS_URL,
                                headers=headers,
                                max_age=-1
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
        return





@Route.register
def FAV_TM_GAMES(plugin, year=None, team=None):
    if not team:
        team = FAVORITE
    if not year:
        this_year = True
        DATE = nowEST()
        year = DATE.year
        month = DATE.month
    else:
        this_year = False
        month = 12
    for m in reversed(range(1,month+1)):
        if m == month and this_year:
            title = 'This Month'
        elif m == month - 1 and this_year:
            title = 'Last Month'
        else:
            title = calendar.month_name[m]
        yield Listitem.from_dict(
                                    BROWSE_MONTH,
                                    bold(title),
                                    params = {
                                                'month': m,
                                                'year': year,
                                                'team': team
                                             }
                                )
    yield Listitem.from_dict(
                                BROWSE_MONTHS,
                                bold('Older'),
                                params = {
                                            'year': year,
                                            'team': team
                                         }
                            )

@Route.register
def BROWSE_MONTH(plugin, year, month, team):
    headers = {'User-Agent': USER_AGENT}

    teams_info = urlquick.get(
                                TEAMS_URL,
                                headers=headers,
                                max_age=-1
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



@Route.register
def BROWSE_MONTHS(plugin, year, team):
    for y in reversed(range(2013,year)):
        yield Listitem.from_dict(
                                    FAV_TM_GAMES,
                                    bold(str(y)),
                                    params = {
                                                'year': y,
                                                'team': team
                                             }
                                )



@Route.register
def BROWSE_GAME(plugin, gameID, gameCode, start_time, game_state, host_team, away_team, game_cameras,
                    end_time=None, has_away_feed=False, has_condensed_game=False):
    game_url = GAME_DATA_ENDPOINT % gameCode
    headers = {'User-Agent': USER_AGENT}
    nba_config = urlquick.get(
                                CONFIG_ENDPOINT,
                                headers=headers,
                                max_age=-1
                             ).json()
    nba_cameras = {}
    for camera in nba_config['content']['cameras']:
        nba_cameras[camera['number']] = camera['name']
    cases = [True]
    if has_away_feed:
        cases.append(False)
    for ishomefeed in cases:
        title = "Full game, " + ("away feed" if not ishomefeed else "home feed")
        if host_team and away_team:
                if ishomefeed:
                    title += " (" + host_team + ")"
                else:
                    title += " (" + away_team + ")"
        liz = Listitem()
        liz.label = title
        liz.set_callback(
                            PLAY_GAME,
                            title=title,
                            gameID=gameID,
                            start_time=start_time,
                            end_time=end_time,
                            game_state=game_state,
                            ishomefeed=ishomefeed
                        )
    
        yield liz

    for camera_number in game_cameras:
        camera_number = int(camera_number)
        if camera_number == 0:
            continue
        
        title = "Camera %d: %s" % (camera_number, nba_cameras.get(camera_number, 'Unknown'))
        liz = Listitem()
        liz.label = title
        liz.set_callback(
                            PLAY_GAME,
                            title=title,
                            gameID=gameID,
                            start_time=start_time,
                            end_time=end_time,
                            game_state=game_state,
                            camera_number=camera_number
                        )
        yield liz
    if has_condensed_game:
        title = "Condensed Game"
        liz = Listitem()
        liz.label = title
        liz.set_callback(
                            PLAY_GAME,
                            title=title,
                            gameID=gameID,
                            game_state=game_state,
                            is_condensed_game=True
                        )
        yield liz



@Resolver.register
def PLAY_GAME(plugin, title, gameID, start_time, game_state, ishomefeed=True,
                    end_time=None, camera_number=None, is_condensed_game=False):
    plugin.log('PLAY_GAME start_time: %s' % start_time, lvl=plugin.DEBUG)
    plugin.log('PLAY_GAME end_time: %s' % end_time, lvl=plugin.DEBUG)
    gt = 1
    if not ishomefeed:
        gt = 4
    headers = get_headers()
    if not headers:
        yield False
        return
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
    if camera_number:
        payload_data.update({'cam': camera_number})
    if is_condensed_game:
        payload_data.update({'gt': 8})
        game_type = 'condensed'
    elif end_time:
        duration = end_time - start_time
        payload_data.update({'st': start_time})
        payload_data.update({'dur': duration})
        game_type = 'archive'
    else:
        game_type = 'live'

    Response = urlquick.post(
                                PUBLISH_ENDPOINT,
                                data=payload_data,
                                headers=headers
                            ).json()
    url = Response['path']
    drm = Response['drmToken']
    headers = {'User-Agent': USER_AGENT}
    start_point = None
    if game_type == 'live':
        line1 = "Start from Beginning"
        line2 = "Go LIVE"
        ret = xbmcgui.Dialog().select("Game Options", [line1, line2])
        if ret == -1:
            yield None
            return
        elif ret == 0:
            # br_long_master only contains segment of the last 2h of streaming
            # may not contains the entire game, works for go live 
            # master contains segments from the beginning of streaming,
            # way before game starts works for start from the beginning
            url = url.replace('br_long_master', 'master')
            content = urlquick.get(url, headers=headers).text
            sample = re.findall('(.*video.*\.m3u8?)', content)[0]
            match = re.search('(https?)://([^:]+)/([^?]+?)\?(.+)$', url)
            baseurl = os.path.dirname(match.group(1)+'://'+match.group(2)+'/'+match.group(3))
            ql_url = baseurl + '/' + sample
            content = urlquick.get(ql_url, headers=headers, max_age=0).text
            stream_start = re.findall('PROGRAM\-DATE\-TIME\:(.*)', content)[0]
            stream_start = time.strptime(stream_start, '%Y-%m-%dT%H:%M:%S.%fZ')
            stream_start_ts = calendar.timegm(stream_start) * 1000
            start_point = str(int((start_time - stream_start_ts) / 1000))
        elif ret == 1 :
            content = urlquick.get(url, headers=headers).text
            sample = re.findall('(.*video.*\.m3u8?)', content)[0]
            match = re.search('(https?)://([^:]+)/([^?]+?)\?(.+)$', url)
            baseurl = os.path.dirname(match.group(1)+'://'+match.group(2)+'/'+match.group(3))
            ql_url = baseurl + '/' + sample
            content = urlquick.get(ql_url, headers=headers, max_age=0).text
            durations = re.findall('\#EXTINF\:([0-9]+\.[0-9]+)\,', content)
            duration = sum([float(i) for i in durations])
            start_point = str(duration - 120).split('.')[0]
    liz = Listitem()
    liz.path = url
    liz.label = title
    liz.property[INPUTSTREAM_PROP] ='inputstream.adaptive'
    for protocol, protocol_info in PROTOCOLS.items():
        if any(".%s" % extension in url for extension in protocol_info['extensions']):
            is_helper = Helper(protocol, drm=DRM)
            if is_helper.check_inputstream():
                liz.property['inputstream.adaptive.manifest_type'] = protocol
                liz.property['inputstream.adaptive.license_type'] = DRM
                license_key = '%s|authorization=bearer %s|R{SSM}|' % (LICENSE_URL, drm)
                liz.property['inputstream.adaptive.license_key'] = license_key
                liz.property['inputstream.adaptive.manifest_update_parameter'] = 'full'
                if start_point:
                    plugin.log('PLAY_GAME start_point: %s' % start_point, lvl=plugin.DEBUG)
                    liz.property['ResumeTime'] = start_point
                    liz.property['TotalTime'] = '14400'
                yield liz
            else:
                yield False
                return
