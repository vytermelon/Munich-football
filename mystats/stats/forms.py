from django import forms
from .models import Match

class Players(forms.Form):
    team_form = forms.CharField(label='Enter Teams', max_length=2500,  widget=forms.Textarea(attrs={'rows': 20, 'cols': 30}),initial="team1\rplayer1\n.\n.\nplayerN\rteam2\rplayer1\n.\n.\nplayerN")
    team1 = forms.BooleanField(required=False,label='Team1:')
    draw = forms.BooleanField(required=False, label='Draw:')
    team2 = forms.BooleanField(required=False, label='Team2:')


def make_contact_form(t1_list, t2_list, team1,draw,team2,latest):
    fields = {}
    temp = []
    for i in list(Match.objects.exclude(match_id=latest).values('player').distinct()):
        temp.append(i.get("player"))
    for i in range(len(t1_list)):
        fields["Team1_%s" % (i+1)] = forms.CharField(initial=t1_list[i])

        if t1_list[i] not in temp:
            fields["Team1_%s" % (i + 1)].widget.attrs.update({'class': 'N'})
    for i in range(len(t2_list)):
        fields["Team2_%s" % (i + 1)] = forms.CharField(initial=t2_list[i])
        if t2_list[i] not in temp:
            fields["Team2_%s" % (i + 1)].widget.attrs.update({'class': 'N'})
    fields['Team1'] = forms.BooleanField(initial=team1, required=False)
    fields['Draw'] = forms.BooleanField(initial=draw, required=False)
    fields['Team2'] = forms.BooleanField(initial=team2, required=False)
    return type('PlayerForm', (forms.BaseForm,), { 'base_fields': fields})