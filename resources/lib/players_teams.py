# -*- coding: utf-8 -*-
# Copyright: (c) 2016, Chamchenko
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)
# This file is part of plugin.video.nbainternational


import urlquick
import json

from resources.lib.vars import *
from resources.lib.tools import *
from resources.lib.auth import get_profile_info
from codequick import Route
from codequick import Listitem
from codequick import Resolver
from codequick.utils import bold





def process_player(player):
    team = '%s %s' % (player['TEAM_CITY'], player['TEAM_NAME'])
    player_id = player['PERSON_ID']
    name = '%s %s' % (player['PLAYER_FIRST_NAME'], player['PLAYER_LAST_NAME'])
    plot = """Name: %s
Team: %s
Jersey Number: %s
Position: %s
Height: %s
Weight: %s
College: %s
Country: %s
Season Number: %s
Points Per Game: %s
Rebounds Per Game: %s
Assists Per Game: %s
"""%(
        name,
        team,
        player['JERSEY_NUMBER'],
        player['POSITION'],
        player['HEIGHT'],
        player['WEIGHT'],
        player['COLLEGE'],
        player['COUNTRY'],
        int(player['TO_YEAR']) - int(player['FROM_YEAR'])+1,
        player['PTS'],
        player['REB'],
        player['AST']
    )
    liz = Listitem()
    liz.label = name
    liz.art['thumb'] = PLAYER_PHOTO_URL % player_id
    liz.art['fanart'] = PLAYER_PHOTO_URL % player_id
    liz.info['plot'] = plot
    liz.set_callback(
                        BROWSE_VIDEOS,
                        player_id=player_id
                    )
    return liz



@Route.register(content_type="movies")
def TEAMS_SUB_MENU(plugin):
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
        team_name = '%s %s' % (
                                teams_info[team]['cityname'],
                                teams_info[team]['teamname']
                              )
        team_id = teams_info[team]['teamid']
        team_logo = TEAMS_LOGO_URL % team_id
        yield Listitem.from_dict(
                                    BROWSE_VIDEOS,
                                    team_name,
                                    art = {"thumb": team_logo},
                                    params = {'team_id': team_id}
                                ) 



@Route.register(content_type="videos")
def PLAYERS_SUB_MENU(plugin):
    FAVORITE_PLAYERS = get_profile_info()['FAVORITE_PLAYERS']
    yield Listitem.from_dict(
                                BY_TEAM,
                                bold('By Team')
                            )
    if FAVORITE_PLAYERS:
        yield Listitem.from_dict(
                                    FAV_PLAYERS,
                                    bold('Favorites Players'),
                                    params={'FAVORITE_PLAYERS': FAVORITE_PLAYERS}
                                )
    yield Listitem.search(
                                SEARCH_PLAYER
                         )



@Route.register(content_type="videos")
def FAV_PLAYERS(plugin, FAVORITE_PLAYERS):
    for player in FAVORITE_PLAYERS:
        liz = Listitem()
        liz.label = player['name']
        liz.art['thumb'] = PLAYER_PHOTO_URL % player['player_id']
        liz.art['fanart'] = PLAYER_PHOTO_URL % player['player_id']
        liz.set_callback(
                            BROWSE_VIDEOS,
                            player_id=player['player_id']
                        )
        yield liz



@Route.register(content_type="videos")
def SEARCH_PLAYER(plugin, search_query):
    headers = {
                'User-Agent': USER_AGENT,
                'Referer': WATCH
              }
    DATE = nowWEST()
    year = DATE.year
    month = DATE.month
    if month < 10:
        year = year - 1
    syear = divmod(year+1, 1000)[1]
    season = '%s-%s' % (year, syear)
    params = {
                'Historical': 1,
                'LeagueID': '00',
                'Season': season,
                'SeasonType': 'Regular Season',
                'TeamID': 0
            }
    jresp = urlquick.get(
                            PLAYERS_URL,
                            params=params,
                            headers=headers,
                            max_age=86400
                        ).json()
    jhead = jresp['resultSets'][0]['headers']
    players = []
    for person in jresp['resultSets'][0]['rowSet']:
        players.append(dict (zip (jhead, person)))
    liz = None
    for player in players:
        if all(w in json.dumps(player).lower() for w in search_query.lower().split(' ')):
            liz = process_player(player)
            yield liz
    if not liz:
        plugin.notify(
                        Script.localize(30208),
                        Script.localize(30207),
                        display_time=5000,
                        sound=True
                     )
        yield False
        return



@Route.register(content_type="movies")
def BY_TEAM(plugin):
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
        team_name = '%s %s' % (
                                teams_info[team]['cityname'],
                                teams_info[team]['teamname']
                              )
        team_id = teams_info[team]['teamid']
        team_logo = TEAMS_LOGO_URL % team_id
        yield Listitem.from_dict(
                                    PLAYERS,
                                    bold(team_name),
                                    art = {"thumb": team_logo},
                                    params = {'team_id': team_id}
                                )



@Route.register(content_type="videos")
def PLAYERS(plugin, team_id):
    headers = {
                'User-Agent': USER_AGENT,
                'Referer': WATCH
              }

    params = {
                'Historical': 0,
                'LeagueID': '00',
                'Season': '2020-21',
                'SeasonType': 'Regular Season',
                'TeamID': team_id
            }
    plugin.log('PLAYERS fetching: %s' % PLAYERS_URL, lvl=plugin.DEBUG)
    plugin.log('PLAYERS headers: %s' % headers, lvl=plugin.DEBUG)            
    jresp = urlquick.get(
                            PLAYERS_URL,
                            params=params,
                            headers=headers,
                            max_age=86400
                        ).json()
    plugin.log('PLAYERS fetching: done', lvl=plugin.DEBUG)            
    jhead = jresp['resultSets'][0]['headers']
    players = []
    for person in jresp['resultSets'][0]['rowSet']:
        players.append(dict (zip (jhead, person)))
    for player in players:
        liz = process_player(player)
        yield liz



@Route.register(autosort=False, content_type="videos")
def BROWSE_VIDEOS(plugin, player_id=False, team_id=False, page=1):
    headers = {
                'User-Agent': USER_AGENT,
                'Referer': 'WATCH'
              }
    params = {
                'region': 'international',
                'count': 22,
                'page': page
             }

    if team_id:
        params['teams'] = team_id
        params['types'] = 'video'
        url = TEAM_VODEO_URL
    elif player_id:
        params['players'] = player_id
        url = PLAYER_URL

    videos = urlquick.get(
                            url,
                            params=params,
                            headers=headers,
                            max_age=3600
                         ).json()['results']
    has_more = videos['pageNext']
    liz = None
    for video in videos['items']:
        liz = Listitem()
        videoId = video['id']
        liz.label = video['title']
        liz.art['thumb'] =  video['featuredImage']
        liz.info.date(video['date'], "%Y-%m-%dT%H:%M:%SZ")
        liz.info['mediatype'] = 'episode'
        liz.info['duration'] = video['videoDurationSeconds']
        liz.info['plot'] = video['excerpt']
        url = video['endeavorVideo']
        liz.path = url
        for protocol, protocol_info in PROTOCOLS.items():
            if any(".%s" % extension in url for extension in protocol_info['extensions']):
                liz.property['inputstream.adaptive.manifest_type'] = protocol
        yield liz
    if not liz:
        plugin.notify(
                        Script.localize(30208),
                        Script.localize(30207),
                        display_time=5000,
                        sound=True
                     )
        yield False
        return
    elif has_more:
        yield Listitem.next_page(
                                    player_id=player_id,
                                    team_id=team_id,
                                    page=page+1
                                )
