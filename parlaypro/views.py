from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import connection, transaction
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import AaaUser

#NOTE: for the scope of this project since we need to execute custom SQL queries
#we will be using connection.cursor() from django.db module to access the db directly
#in this way we can execute custom SQL queries (with cursor.execute())

def logout_view(request): 
    if not request.user.is_authenticated: 
        return HttpResponseRedirect(reverse('index'))

    logout(request)
    return redirect('/index/')

def follow(request, user_id): 
    cursor = connection.cursor()

    # SQL Looks like
    # INSERT INTO `aaa_following` (`user_id`, `user_id_follows`) 
    # VALUES ((SELECT user_id 
    #          FROM aaa_user
    #          WHERE email = "{}"), {})


    cursor.execute('INSERT INTO `aaa_following` (`user_id`, `user_id_follows`) VALUES ((SELECT user_id FROM aaa_user WHERE email = "{}"), {})'.format(request.user.email, user_id))
    return HttpResponseRedirect(reverse('index'))

def unfollow(request, user_id):
    cursor = connection.cursor() 
    try: 
        # first have to find the user id of our user
        cursor.execute("SELECT user_id FROM aaa_user WHERE email=\"{}\"".format(request.user.email))
        mainUserID = cursor.fetchall()
        
        # then have to match our userid (fetched from above here)
        cursor.execute("DELETE FROM aaa_following WHERE user_id = {} AND user_id_follows = {}".format(mainUserID[0][0], user_id))
        connection.commit() 

    except Exception as e: 
        print("error occured")
        print(e)

    return HttpResponseRedirect(reverse('index'))

def login(request): 
    if request.user.is_authenticated: 
        return HttpResponseRedirect('/index')
    else:
        return render(request, 'login.html')

def getBalance(user_email): 
    cursor = connection.cursor()
    cursor.execute('SELECT balance FROM aaa_user WHERE email = "{}"'.format(user_email))
    user_balance = cursor.fetchall()[0][0]

    return user_balance

@login_required
def index(request):
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM aaa_user WHERE email = "{}"'.format(request.user.email))

    DBuser = cursor.fetchall()

    if ( len(DBuser) == 0 ): 
        cursor.execute('INSERT INTO aaa_user (user_name, email, balance) VALUES ("{}", "{}", "{}")'.format(request.user.username, request.user.email, 0))
    
    user_balance = getBalance(request.user.email)
    print("balance: {}".format(user_balance))

    # check if the user email exists in the database

    # if it does we extract the user's current money and display it

    # otherwise we create a user and set their currency to 0

    # either way at the end we extract the user's money and pass it to the render



    # getting list of all users, that are not friends with user, (going to display five or so)
    # with a "add friend button"
    # SQL looks like: 

    # SELECT * from aaa_user 
    # WHERE aaa_user.user_id NOT IN (SELECT user_id_follows 
    #                                FROM aaa_following
    #                                WHERE user_id = (SELECT user_id 
    #                                                 FROM aaa_user 
    #                                                 WHERE email = request.user.email))
    # ORDER BY RAND()
    # LIMIT 5

    cursor.execute('SELECT * FROM aaa_user WHERE aaa_user.user_id NOT IN (SELECT user_id_follows FROM aaa_following WHERE user_id = (SELECT user_id FROM aaa_user WHERE email = "{}")) ORDER BY RAND() LIMIT 5'.format(request.user.email))
    addableUsers = cursor.fetchall()

    addableUsersList = []

    for userInfo in addableUsers: 
        user = AaaUser()
        user.user_id = userInfo[0]
        user.user_name = userInfo[1]
        user.name = userInfo[2]
        user.email = userInfo[3]

        addableUsersList.append(user)

    # display list of current friends (five or so) 
    # with a "remove friend button"

    cursor.execute('SELECT * FROM aaa_user WHERE aaa_user.user_id IN (SELECT user_id_follows FROM aaa_following WHERE user_id = (SELECT user_id FROM aaa_user WHERE email = "{}")) ORDER BY RAND() LIMIT 5'.format(request.user.email))
    followedUsers = cursor.fetchall()

    followedUsersList = []

    for userInfo in followedUsers:
        user = AaaUser()
        user.user_id = userInfo[0]
        user.user_name = userInfo[1]
        user.name = userInfo[2]
        user.email = userInfo[3]

        followedUsersList.append(user)


    cursor = connection.cursor()
    return render(request, 'index.html', context={'balance':user_balance, 'addableUsers':addableUsersList, 'followedUsers':followedUsersList})

@login_required
def parlays(request): 
    return render(request, 'parlays.html')


@login_required
def create_parlay(request):
    #create a new active parlay
    return render(request, 'createparlay.html')


@login_required
def players(request):
    cursor = connection.cursor()
    cursor.execute('SELECT city, team_name FROM aaa_team')
    teamList = cursor.fetchall()
    teamList = [t[0] + " " + t[1] for t in teamList]

    if request.method == 'POST':
        playerName = request.POST.get('player')
        teamName = request.POST.get('team')

        if playerName == "" and teamName == "":
            #query is all players from all teams
            cursor.execute('SELECT * FROM aaa_player NATURAL JOIN aaa_team')
            playerResult = cursor.fetchall()
            return render(request, 'players.html', {'teamList': teamList, 'playerResult': playerResult})
        elif teamName == "":
            #query is a specific player
            cursor.execute('SELECT * FROM aaa_player NATURAL JOIN aaa_team WHERE name LIKE %s', ['%' + playerName + '%'])
            playerResult = cursor.fetchall()
            return render(request, 'players.html', {'teamList': teamList, 'playerResult': playerResult})
        elif playerName == "":
            #query is all players from one team

            #split into city and team name
            if ' ' in teamName:
                teamCity, teamNm = teamName.split(' ', 1)
                cursor.execute('SELECT * FROM aaa_player NATURAL JOIN aaa_team where city LIKE %s AND team_name LIKE %s', ['%' + teamCity + '%', '%' + teamNm + '%'])
            else:
                cursor.execute('SELECT * FROM aaa_player NATURAL JOIN aaa_team where city LIKE %s OR team_name LIKE %s', ['%' + teamName + '%', '%' + teamName + '%'])
            playerResult = cursor.fetchall()
            return render(request, 'players.html', {'teamList': teamList, 'playerResult': playerResult})
        else:
            #query is both player and team matching

            #split into city and team name
            if ' ' in teamName:
                teamCity, teamNm = teamName.split(' ', 1)
                cursor.execute('SELECT * FROM aaa_player NATURAL JOIN aaa_team where city LIKE %s AND team_name LIKE %s AND name LIKE %s', ['%' + teamCity + '%', '%' + teamNm + '%', '%' + playerName + '%'])
            else:
                cursor.execute('SELECT * FROM aaa_player NATURAL JOIN aaa_team where name LIKE %s AND (city LIKE %s OR team_name LIKE %s)', ['%' + playerName + '%', '%' + teamName + '%', '%' + teamName + '%'])
            playerResult = cursor.fetchall()
            return render(request, 'players.html', {'teamList': teamList, 'playerResult': playerResult})


    return render(request, 'players.html', {'teamList': teamList, 'playerResult': []})



def playerPage(request, player_id):
    #get the relevant player information
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM aaa_player NATURAL JOIN aaa_team WHERE player_id = %s', [player_id])
    playerInfo = cursor.fetchall()
    #get all the line info
    cursor.execute('SELECT * FROM aaa_line where player_id = %s', [player_id])
    lineInfo = cursor.fetchall()
    gameList = set(l[2] for l in lineInfo)
    gameInfo = []
    statInfo = []

    cursor.execute('SELECT * FROM aaa_line WHERE player_id = %s AND sportsbook = \"DRAFTKINGS\"', [player_id])
    addableLines = cursor.fetchall()
    

    for game in gameList:
        #get all of the game and stats info for the given player for that game
        cursor.execute('SELECT * FROM aaa_stats NATURAL JOIN aaa_game WHERE player_id = %s AND game_id = %s', [player_id, game])
        statInfo.append(cursor.fetchall())
    statCategories = set()
    statDict = {} #format for this dict is {stat_category : [stats_for_game, line_for_game]}
    #if the player has stats make the dictionary
    if statInfo:
        #get all of the different stat categories
        statCategories = set(s[2] for s in statInfo[0])
        for stat in statCategories: #init dict
            statDict[stat] = []
            #now add all of the game infos
            for statistic in statInfo[0]:
                # print(statistic)
                if statistic[2] == stat:
                    #get line info for this game and value
                    cursor.execute('SELECT * FROM aaa_line where player_id = %s AND game_id = %s AND attribute = %s', [player_id, statistic[0], statistic[2]])
                    line = cursor.fetchall()
                    statDict[stat].append([statistic, line])

        
    return render(request, 'playerPage.html', {'playerInfo': playerInfo, 'lineInfo':lineInfo, 'addableLines':addableLines, 'gameInfo':gameInfo, 'statCategories':statCategories, 'statInfo':statInfo, 'statDict': statDict})
