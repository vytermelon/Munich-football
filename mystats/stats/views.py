import re
from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import Match,Stats
from .forms import Players,make_contact_form
import itertools

def index(request):
    if request.method == 'POST':
        form = Players(request.POST)
        if form.is_valid():
            teams = form['team_form'].value()
            team1 = form['team1'].value()
            draw = form['draw'].value()
            team2 = form['team2'].value()
            update_db(teams, team1, draw, team2)
            if 'submit' in request.POST:
                return HttpResponseRedirect('/review')
            elif 'stat' in request.POST:
                latest = Match.objects.order_by("-match_id")[:1]
                latest = latest[0].match_id
                players = Match.objects.filter(match_id=latest)
                team1 = players.filter(team_id=1)
                team2 = players.filter(team_id=2)
                team1_list = [i.player for i in team1]
                team2_list = [i.player for i in team2]
                Match.objects.filter(match_id=latest).delete()
                one_man = recommendation(team1_list, 0)
                two_man = recommendation(team1_list, 1)
                three_man = recommendation(team1_list, 2)
                one_man2 = recommendation(team2_list, 0)
                two_man2 = recommendation(team2_list, 1)
                three_man2 = recommendation(team2_list, 2)
                form = Players(request.POST)
                return render(request, 'stats/index.html', {
                    'form': form,
                    'one1': one_man,
                    'two1': two_man,
                    'three1': three_man,
                    'one2': one_man2,
                    'two2': two_man2,
                    'three2': three_man2,

                })


    else:
        form = Players()
    return render(request, 'stats/index.html', {
                            'form': form,
                            }
                  )
def stats(request):
    temp = []
    one_man={}
    two_man = {}
    three_man = {}
    for i in list(Match.objects.values('player').distinct()):
        temp.append(i.get("player"))

    for i in temp:
        num = len(Match.objects.raw("SELECT * FROM stats_match WHERE player = '%s' AND win = True;" % i))
        num_draw = len(Match.objects.raw("SELECT * FROM stats_match WHERE player = '%s' AND draw = True;" % i))
        denom = len(Match.objects.raw("SELECT * FROM stats_match WHERE player = '%s';" % i))
        rate = (num*3 + num_draw*1)/(denom*3)
        one_man["%s (%s/%s)" % (i,(num*3 + num_draw*1),denom*3)] = rate

    data_list = [(key, value) for key, value in one_man.items()]

    # Sort the list of tuples based on the values
    sorted_list = sorted(data_list, key=lambda x: x[1], reverse=True)

    # Concatenate key and value pairs
    one_man_l = ["%s : %s" % (key,round(value*100,2)) for key, value in sorted_list]

    #list of 2 man win rate
    two_man_list = rec(temp, 0)
    for i in two_man_list :
        try:
            num = len(Match.objects.raw("SELECT * FROM stats_match AS t1 JOIN stats_match AS t2 ON t1.match_id = t2.match_id WHERE t1.player = '%s' AND t2.player = '%s' AND t1.team_id = t2.team_id AND t1.win=True;" % (i[0],i[1])))
            denom =len(Match.objects.raw("SELECT * FROM stats_match AS t1 JOIN stats_match AS t2 ON t1.match_id = t2.match_id WHERE t1.player = '%s' AND t2.player = '%s' AND t1.team_id = t2.team_id;" % (i[0],i[1])))
            rate = num / denom
            two_man["%s,%s (%s/%s)" % (i[0],i[1], num, denom)] = rate
        except BaseException:
            print("%s and %s have never played together" % (i[0],i[1]))
    data_list = [(key, value) for key, value in two_man.items()]

    # Sort the list of tuples based on the values
    sorted_list = sorted(data_list, key=lambda x: x[1], reverse=True)

    # Concatenate key and value pairs
    two_man_l = ["%s : %s" % (key,round(value*100,2)) for key, value in sorted_list]
    # of 3 man win rate
    three_man_list = list(itertools.combinations(temp, 3))
    for i in three_man_list:
        try:
            num = len(Match.objects.raw(
                "SELECT * FROM stats_match AS t1 JOIN stats_match AS t2 ON t1.match_id = t2.match_id JOIN stats_match AS t3 ON t1.match_id = t3.match_id WHERE t1.player = '%s' AND t2.player = '%s'  AND t3.player = '%s' AND t1.team_id = t2.team_id  AND t1.team_id = t3.team_id AND t1.win=True;" % (
                i[0], i[1],i[2])))
            denom = len(Match.objects.raw(
                "SELECT * FROM stats_match AS t1 JOIN stats_match AS t2 ON t1.match_id = t2.match_id JOIN stats_match AS t3 ON t1.match_id = t3.match_id WHERE t1.player = '%s' AND t2.player = '%s'  AND t3.player = '%s' AND t1.team_id = t2.team_id  AND t1.team_id = t3.team_id;" % (
                i[0], i[1],i[2])))
            rate = num / denom
            three_man["%s,%s,%s (%s/%s)" % (i[0], i[1],i[2], num, denom)] = rate
        except BaseException:
            print("%s and %s and %s have never played together" % (i[0], i[1],i[2]))
    data_list = [(key, value) for key, value in three_man.items()]

    # Sort the list of tuples based on the values
    sorted_list = sorted(data_list, key=lambda x: x[1], reverse=True)

    # Concatenate key and value pairs
    three_man_l = ["%s : %s" % (key, round(value*100,2)) for key, value in sorted_list]
    #update db
    Stats.objects.all().delete()
    for n,i in enumerate([one_man,two_man,three_man]):
        for k,v in i.items():
            new_obj = Stats.objects.create(stat_id=n, player_s=k,
                                   fraction=v)

    return render(request, 'stats/stats.html', {
        'one_man': one_man_l,
        'two_man':two_man_l,
        'three_man': three_man_l
    }
                  )

def stat_user(request):
    one_man = Stats.objects.filter(stat_id=0).order_by("-fraction")
    one_man_l = ["%s : %s" % (i.player_s,i.fraction) for i in one_man]
    two_man = Stats.objects.filter(stat_id=1).order_by("-fraction")
    two_man_l = ["%s : %s" % (i.player_s, i.fraction) for i in two_man]
    three_man = Stats.objects.filter(stat_id=2).order_by("-fraction")
    three_man_l = ["%s : %s" % (i.player_s, i.fraction) for i in three_man]
    print(one_man_l)
    num = Match.objects.raw("SELECT ID, player, count(*)*3 as matches, round((sum(iif(win=1,1,0))*3+sum(iif(draw=1,1,0)))*100.0/(3),2) as win_rate FROM stats_match group by player order by matches desc LIMIT 20;")
    for i in num:
        print(i.player,i.matches)
    return render(request, 'stats/stat_user.html', {
        'one_man': one_man_l[:5],
        'two_man':two_man_l,
        'three_man': three_man_l
    }
                  )


def rec(a, i):
    if i >= len(a) - 1:
        return
    temp = []
    for j in range(i + 1, len(a)):
        temp.append([a[i], a[j]])

    val = rec(a, i + 1)
    if val:
        temp.extend(val)
    return temp
def review(request):
    latest = Match.objects.order_by("-match_id")[:1]
    latest = latest[0].match_id

    #update db accordingly
    if request.method == 'POST':
        Match.objects.filter(match_id=latest).delete()
        team1_result = True if request.POST.get('Team1') == 'on' else False
        team2_result = True if request.POST.get('Team2') == 'on' else False
        draw_result = True if request.POST.get('Draw') == 'on' else False
        print(team1_result,team2_result,draw_result)
        for k,v in request.POST.items():
            if "Team1_" in k:
                new_obj = Match.objects.create(match_id=latest, player=v,
                                               win=team1_result,draw=draw_result,loss=team2_result,team_id=1)
            if "Team2_" in k:
                new_obj = Match.objects.create(match_id=latest, player=v,
                                               win=team2_result,draw=draw_result,loss=team1_result,team_id=2)
        return HttpResponseRedirect('/')
    else:

        players = Match.objects.filter(match_id=latest)
        team1 = players.filter(team_id=1)
        team2 = players.filter(team_id=2)
        team1_list = [i.player for i in team1]
        team2_list = [i.player for i in team2]
        result1 = team1.values('win').distinct()[0].get('win')
        result = team1.values('draw').distinct()[0].get('draw')
        result2 = team1.values('loss').distinct()[0].get('loss')
        #print(result1,result,result2)
        form = make_contact_form(team1_list, team2_list,result1,result,result2,latest)
        return render(request, 'stats/review.html', {
                            'latest': latest,
                            'form': form,
                            'recom': stats
                            }
                  )

def recommendation(team, num):
    print(team)
    max = 0
    player = "N/A"
    team_avg = 0
    if num == 0:
        for j in team:
            query = Stats.objects.filter(player_s__contains=j).filter(stat_id=num)
            for i in query:
                print(i.player_s)
                print("---")
                team_avg =team_avg +i.fraction
                if i.fraction >= max:
                    max = i.fraction
                    player = i.player_s
    if num ==1:
        team = list(itertools.combinations(team, 2))
        for j in team:
            query = Stats.objects.filter(player_s__contains=j[0]).filter(player_s__contains=j[1]).filter(stat_id=num)
            for i in query:
                print(i.fraction,i.player_s)
                if i.fraction >= max:
                    max = i.fraction
                    player = i.player_s
    if num == 2:
        team = list(itertools.combinations(team, 3))
        for j in team:
            query = Stats.objects.filter(player_s__contains=j[0]).filter(player_s__contains=j[1]).filter(player_s__contains=j[2]).filter(stat_id=num)
            for i in query:
                print(i.fraction, i.player_s)
                if i.fraction >= max:
                    max = i.fraction
                    player = i.player_s
    return [max*100,player,round(team_avg/len(team)*100,2)]

def update_db(teams, team1, draw, team2):
    #get latest match_id
    match_id = Match.objects.order_by("-match_id")[:1]
    print(match_id)
    id=0
    for i in match_id:
        id = int(i.match_id)
    #make teams into list
    pattern = r'\b(?![0-9]+\b)[a-zA-Z0-9]+\b'
    alphanumeric_words = re.findall(pattern, teams)
    print(alphanumeric_words)
    team_id = 0
    if team1 or team2:
        team1 = not team1
        team2 = not team2
        draw = False
    else:
        draw = True
    for i in alphanumeric_words:
        if "team" not in i.lower():
            new_obj = Match.objects.create(match_id=id+1, player=i.lower(),team_id=team_id,
                                   win=team1,draw=draw, loss=team2)
        else:
            team_id = team_id + 1
            if team1 or team2:
                team1 = not team1
                team2 = not team2
                draw = False
            else:
                draw = True