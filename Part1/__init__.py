from otree.api import *
import random

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'Part1'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 9
    TIME_INI = 30
    TIME_RESET = 20
    TIME_ALERT = None  # if the time alert/popup is different from time_reset


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    Remaining = models.IntegerField(initial=999)
    Contribution = models.IntegerField(initial=0)
    Externality = models.IntegerField(initial=0)
    MaxTotal = models.IntegerField()
    Threshold = models.IntegerField()
    Status = models.StringField()


class Player(BasePlayer):
    Age = models.IntegerField(
        label='How old are you?',
        choices=range(10, 99, 1)
    )
    Nationality = models.StringField(
        label='What is your nationality?'
    )
    Male = models.IntegerField(
        label='What is your gender?',
        choices=[
            [0, 'Female'],
            [1, 'Male'],
            [-1, 'Diverse']
        ],
        widget=widgets.RadioSelectHorizontal
    )
    StudyField = models.StringField(
        label='What is your (main) field of study?'
    )
    StudyLevel = models.IntegerField(
        label='What is the level of your current study programme?',
        choices=[
            [0, 'Bachelor'],
            [1, 'Master'],
            [2, 'PhD'],
            [3, 'None of the above']
        ],
        widget=widgets.RadioSelect
    )
    StudyYear = models.IntegerField(
        label='Within your study programme, what is your current year of study?'
              ' (1st/2nd semester = year 1, 3rd/4th semester = year 2 etc.)',
        choices=[
            [1, '1'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
            [5, '5'],
            [6, '>5']
        ]
    )
    # Timer things:
    TimeLimit = models.IntegerField(initial=-1)
    TimeLeft = models.IntegerField(initial=-1)
    TimeSpent = models.IntegerField(initial=-1)
    TimeShift = models.IntegerField(initial=-1)
    Timeout = models.IntegerField(initial=0)

    # Choices:
    Contribution = models.IntegerField(min=0, initial=0)
    MyContris = models.StringField(initial="")
    Earnings = models.IntegerField(initial=0)
    SelectedEarnings = models.StringField()

    # Tutorial:
    ContributionT = models.IntegerField(min=0, initial=0)
    ProjectSuccessT = models.IntegerField(initial=0)

    # Misc
    ProjectSuccess = models.IntegerField(initial=0)
    Endowment = models.IntegerField(initial=0)
    TestBot = models.BooleanField(initial=False)


# FUNCTIONS
def iif(boolean, if_true, if_false):
    if boolean:
        return if_true
    else:
        return if_false


def str_time(time_limit):
    import math
    minutes = math.floor(time_limit / 60)
    seconds = time_limit - 60 * minutes
    if minutes > 0:
        s_time = str(minutes) + " minute" + iif(minutes > 1, "s", "")
        if seconds > 0:
            s_time += " and " + str(seconds) + " seconds"
    else:
        s_time = str(seconds) + " seconds"
    return s_time


# Function to create random list of targets and timer and a random number that selects the round for payment
def def_group_var(group: Group, vtreatment):
    s = group.session
    if vtreatment:
        Timerlist = [random.randint(60, 70) for _ in range(9)]
        s.vars['GroupTimerListV'] = [x * s.config['team_size'] for x in Timerlist]
    else:
        s.vars['TimerList'] = [random.randint(300, 310) for _ in range(9)]
    s.vars['random_numbers'] = random.randint(1, 9)


# Function to list players' earnings and contributions throughout the rounds
def set_payoff_list(player: Player):
    group = player.group
    s = player.session
    MaxTotal = group.MaxTotal
    Threshold = group.Threshold
    GroupContribution = group.Contribution

    if GroupContribution < Threshold:
        group.Status = "Fail"
        group.Externality = group.MaxTotal * 2
        Donation = 0
        player.Earnings = 0
    elif Threshold <= GroupContribution < MaxTotal:
        group.Status = "Incomplete"
        group.Externality = 2 * (group.MaxTotal - group.Contribution)
        Donation = 2 * (group.Contribution)
        player.Earnings = player.Endowment - player.Contribution + s.config['clear']
    else:
        group.Status = "Success"
        group.Externality = 0
        player.Earnings = player.Endowment - player.Contribution + s.config['clear']
        Donation = 2 * (group.Contribution)

    if player.round_number == 1:
        player.participant.vars['earnings_lists'] = [player.Earnings]
        player.participant.vars['unicef_list'] = [Donation]
    elif 1 < player.round_number <= 9:
        participant_vars = player.participant.vars.get('earnings_lists', [])
        participant_vars.append(player.Earnings)
        player.participant.vars['earnings_list'] = participant_vars

        p_vars = player.participant.vars.get('unicef_list', [])
        p_vars.append(Donation)
        player.participant.vars['unicef_list'] = p_vars


# PAGES
class Test(Page):
    pass


class P01Welcome(Page):
    # form_model = 'player'
    # form_fields = ['Age', 'Nationality', 'StudyField', 'StudyLevel', 'StudyYear', 'Male']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def js_vars(player: Player):
        import random
        # For now:
        player.participant.TestBot = False
        return dict(
            TestBot=player.participant.TestBot,
            TestAge=random.randint(20, 60),
            TestNat=random.choice(["German", "UK", "Dutch", "French", "US", "Danish", "Polish", "Turkish", "Swiss"]),
            TestField=random.choice(["Economics", "Mathematics", "Sociology", "Medicine", "Psychology", "Physics"]),
            TestLevel=random.randint(0, 3),
            TestYear=random.randint(1, 6),
            TestMale=random.randint(0, 1)
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        s = player.session
        totals = s.config['max_totals']
        random.shuffle(totals)
        s.vars['MaxTotals'] = totals[0:1] * 3 + totals[1:2] * 3 + totals[2:3] * 3

        def_group_var(player.group, player.session.config['vertical'])


class P02Instructions(Page):
    @staticmethod
    def vars_for_template(player):
        group = player.group
        s = player.session
        x_var = s.vars['MaxTotals'][0]
        return dict(
            ShowUpFee=s.config['participation_fee'],
            TimeLimit=str_time(s.config['time_limit']),
            TeamSize=s.config['team_size'],
            Others=s.config['team_size'] - 1,
            NumRounds=s.config['num_rounds'],
            PointValue=100 * s.config['real_world_currency_per_point'],
            Endowment=player.Endowment,
            x=x_var,
            xx=2 * x_var,
            OneThird=int(x_var / 3),
            Clear=s.config['clear']
        )

    @staticmethod
    def js_vars(player: Player):
        return dict(
            TeamSize=player.session.config['team_size'],
            Vertical=player.session.config['vertical'],
            TestBot=player.participant.TestBot
        )

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class P02aTutorial(Page):
    form_model = 'player'
    form_fields = ['ProjectSuccessT']

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        s = player.session
        group.MaxTotal = int(s.vars['MaxTotals'][player.round_number - 1])
        group.Threshold = int(group.MaxTotal / 3)
        player.Endowment = player.session.config['endowment']
        player.group.Contribution = 0
        return {
            "Round": group.subsession.round_number,
            "MaxTotal": group.MaxTotal,
            "MyEndowment": player.Endowment,
            "AccountBalance": player.Endowment - player.Contribution,
            "MyID": player.id_in_group,
            "Threshold": group.Threshold
        }

    @staticmethod
    def js_vars(player: Player):
        group = player.group
        return dict(
            MyID=player.id_in_group,
            MyEndowment=player.Endowment,
            Threshold=group.Threshold,
            MaxTotal=group.MaxTotal,
            Vertical=player.session.config['vertical']
        )

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class P02bPractice(Page):
    form_model = 'player'
    form_fields = ['TimeLeft', 'Timeout', 'ProjectSuccessT']

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        s = player.session
        group.MaxTotal = int(s.vars['MaxTotals'][player.round_number - 1])
        group.Threshold = int(group.MaxTotal / 3)
        player.Endowment = player.session.config['endowment']
        player.group.Contribution = 0
        return {
            "Round": group.subsession.round_number,
            "MaxTotal": group.MaxTotal,
            "MyEndowment": player.Endowment,
            "AccountBalance": player.Endowment - player.Contribution,
            "MyID": player.id_in_group,
            "Threshold": group.Threshold
        }

    @staticmethod
    def get_timeout_seconds(player):
        return 60

    @staticmethod
    def js_vars(player: Player):
        TimeLimit = 60
        TimeShift = TimeLimit - C.TIME_INI
        group = player.group
        return dict(
            MyID=player.id_in_group,
            MyEndowment=player.Endowment,
            Threshold=group.Threshold,
            MaxTotal=group.MaxTotal,
            TimeLimit=TimeLimit,
            TimeIni=C.TIME_INI,
            TimeReset=C.TIME_RESET,
            TimeAlert=C.TIME_ALERT,
            Vertical=player.session.config['vertical']
        )

    @staticmethod
    def live_method(player: Player, data):
        group = player.group
        players = group.get_players()
        TimeLimit = 60
        if data['MsgType'] == "Update":
            TimeShift = TimeLimit - C.TIME_INI
            return {player.id_in_group: dict(
                MyTotals=[p.ContributionT for p in players],
                TeamTotal=group.Contribution,
                TimeShift=TimeShift
            )}
        contri = data['Contri']
        cur_time = data['CurTime']
        if player.ContributionT < player.Endowment:
            contri = min(contri, player.Endowment - player.Contribution)
        else:
            contri = 0
        if player.ContributionT < group.MaxTotal:
            contri = min(contri, group.MaxTotal - group.Contribution)
        else:
            contri = 0
        if contri > 0:
            player.ContributionT += contri
            if cur_time < C.TIME_INI - C.TIME_RESET:
                TimeShift = TimeLimit - C.TIME_INI
            else:
                TimeShift = max(TimeLimit - cur_time - C.TIME_RESET - 1, 0)
            return {player.id_in_group: dict(
                Contri=contri,
                Contributor=player.id_in_group,
                MyTotals=[p.ContributionT for p in players],
                TimeShift=TimeShift
            )}

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def before_next_page(player, timeout_happened):
        if player.Timeout == 0:
            player.Timeout = iif(timeout_happened, 1, 0)
        player.TimeLeft = iif(player.Timeout, 0, max(0, player.TimeLeft))
        player.TimeSpent = player.TimeLimit - player.TimeLeft
        set_payoff_list(player)


# Informing subjects about changes in the max total / min threshold
class P03Change(Page):
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        group.MaxTotal = int(group.session.vars['MaxTotals'][player.round_number - 1])
        group.Threshold = int(group.MaxTotal / 3)
        return {
            "MaxTotal": group.MaxTotal,
            "Threshold": group.Threshold
        }

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 4 or player.round_number == 7


class TaskSync(WaitPage):
    wait_for_all_groups = True


class P04Contribution(Page):
    form_model = 'player'
    form_fields = ['TimeLeft', 'Timeout', 'ProjectSuccess']

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        s = player.session
        group.MaxTotal = int(s.vars['MaxTotals'][player.round_number - 1])
        group.Threshold = int(group.MaxTotal / 3)
        player.Endowment = player.session.config['endowment']
        player.group.Contribution = 0
        return {
            "Round": group.subsession.round_number,
            "MaxTotal": group.MaxTotal,
            "MyEndowment": player.Endowment,
            "AccountBalance": player.Endowment - player.Contribution,
            "MyID": player.id_in_group,
            "Threshold": group.Threshold
        }

    @staticmethod
    def get_timeout_seconds(player):
        return player.session.vars['TimerList'][player.round_number - 1]

    @staticmethod
    def js_vars(player: Player):
        player.TimeLimit = player.session.vars['TimerList'][player.round_number - 1]
        player.TimeShift = player.TimeLimit - C.TIME_INI
        group = player.group
        return dict(
            MyID=player.id_in_group,
            MyEndowment=player.Endowment,
            Threshold=group.Threshold,
            MaxTotal=group.MaxTotal,
            TimeLimit=player.TimeLimit,
            TimeIni=C.TIME_INI,
            TimeReset=C.TIME_RESET,
            TimeAlert=C.TIME_ALERT,
            Vertical=player.session.config['vertical']
        )

    @staticmethod
    def live_method(player: Player, data):
        group = player.group
        players = group.get_players()
        if data['MsgType'] == "Update":
            return {player.id_in_group: dict(
                MyTotals=[p.Contribution for p in players],
                TeamTotal=group.Contribution,
                TimeShift=player.TimeShift
            )}
        contri = data['Contri']
        cur_time = data['CurTime']
        if player.Contribution < player.Endowment:
            contri = min(contri, player.Endowment - player.Contribution)
        else:
            contri = 0
        if group.Contribution < group.MaxTotal:
            contri = min(contri, group.MaxTotal - group.Contribution)
        else:
            contri = 0
        if contri > 0:
            # Contri = (TimeStamp + Group contribution so far + My contribution so far + My new contribution)
            new_entry = iif(player.MyContris == "", "", ", ") + "(" + str(cur_time) + ", " \
                        + str(group.Contribution) + ", " + str(player.Contribution) + ", " + str(contri) + ")"
            player.MyContris += new_entry
            player.Contribution += contri
            group.Contribution += contri
            if cur_time < C.TIME_INI - C.TIME_RESET:
                player.TimeShift = player.TimeLimit - C.TIME_INI
            else:
                player.TimeShift = max(player.TimeLimit - cur_time - C.TIME_RESET - 1, 0)
            return {0: dict(
                Contri=contri,
                Contributor=player.id_in_group,
                MyTotals=[p.Contribution for p in players],
                TeamTotal=group.Contribution,
                TimeShift=player.TimeShift
            )}

    @staticmethod
    def is_displayed(player: Player):
        return player.session.config['vertical'] == False

    @staticmethod
    def before_next_page(player, timeout_happened):
        if player.Timeout == 0:
            player.Timeout = iif(timeout_happened, 1, 0)
        player.TimeLeft = iif(player.Timeout, 0, max(0, player.TimeLeft))
        player.TimeSpent = player.TimeLimit - player.TimeLeft
        set_payoff_list(player)


class P04ContributionV(Page):
    form_model = 'player'
    form_fields = ['TimeLeft', 'Timeout', 'ProjectSuccess']

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        s = player.session
        group.MaxTotal = int(s.vars['MaxTotals'][player.round_number - 1])
        group.Threshold = int(group.MaxTotal / 3)
        player.Endowment = player.session.config['endowment']
        player.group.Contribution = 0
        return {
            "Round": group.subsession.round_number,
            "MaxTotal": group.MaxTotal,
            "MyEndowment": player.Endowment,
            "AccountBalance": player.Endowment - player.Contribution,
            "MyID": player.id_in_group,
            "Threshold": group.Threshold
        }

    @staticmethod
    def get_timeout_seconds(player):
        return player.session.vars['GroupTimerListV'][player.round_number - 1]

    @staticmethod
    def js_vars(player: Player):
        multiplier = player.session.config['team_size'] - player.id_in_group
        player.TimeLimit = int(player.session.vars['GroupTimerListV'][player.round_number - 1] * multiplier / player.session.config['team_size'])
        player.TimeShift = player.session.vars['GroupTimerListV'][player.round_number - 1] - C.TIME_INI - 1
        group = player.group
        return dict(
            Teamsize=player.session.config['team_size'],
            MyID=player.id_in_group,
            MyEndowment=player.Endowment,
            Threshold=group.Threshold,
            MaxTotal=group.MaxTotal,
            TimeLimit=player.TimeLimit,
            GroupTimeLimit=player.session.vars['GroupTimerListV'][player.round_number - 1],
            TimeIni=C.TIME_INI,
            TimeReset=C.TIME_RESET,
            TimeAlert=C.TIME_ALERT,
            Vertical=player.session.config['vertical']
        )

    @staticmethod
    def live_method(player: Player, data):
        group = player.group
        players = group.get_players()
        if data['MsgType'] == "Update":
            return {player.id_in_group: dict(
                MyTotals=[p.Contribution for p in players],
                TeamTotal=group.Contribution,
                TimeShift=player.TimeShift
            )}
        cur_time = data['CurTime']
        if data['MsgType'] == "submit":
            ChangePlayer = True
            multiplier = data['CurPlayer']
            multiplier2 = data['CurPlayer'] -1
            Lim = player.session.vars['GroupTimerListV'][player.round_number - 1]/3
            adjust = (Lim * multiplier) - cur_time
            adjust2 = cur_time - (Lim * multiplier2)
            player.TimeShift = player.session.vars['GroupTimerListV'][player.round_number - 1] - C.TIME_INI - cur_time - 1
            return {0: dict(
                ChangePlayer=ChangePlayer,
                MyTotals=[p.Contribution for p in players],
                TeamTotal=group.Contribution,
                TimeShift=player.TimeShift,
                Adjustment=adjust,
                Adjustment2=adjust2
            )}
        contri = data['Contri']
        if player.Contribution < player.Endowment:
            contri = min(contri, player.Endowment - player.Contribution)
        else:
            contri = 0
        if group.Contribution < group.MaxTotal:
            contri = min(contri, group.MaxTotal - group.Contribution)
        else:
            contri = 0
        if contri > 0:
            # Contri = (TimeStamp + Group contribution so far + My contribution so far + My new contribution)
            new_entry = iif(player.MyContris == "", "", ", ") + "(" + str(cur_time) + ", " \
                        + str(group.Contribution) + ", " + str(player.Contribution) + ", " + str(contri) + ")"
            player.MyContris += new_entry
            player.Contribution += contri
            group.Contribution += contri
            if cur_time < C.TIME_INI - C.TIME_RESET:
                player.TimeShift = player.session.vars['GroupTimerListV'][player.round_number - 1] - C.TIME_INI
            else:
                player.TimeShift = max(player.session.vars['GroupTimerListV'][player.round_number - 1] - cur_time - C.TIME_RESET - 1,
                                       player.TimeLimit)
            return {0: dict(
                Contri=contri,
                Contributor=player.id_in_group,
                MyTotals=[p.Contribution for p in players],
                TeamTotal=group.Contribution,
                TimeShift=player.TimeShift
            )}

    @staticmethod
    def is_displayed(player: Player):
        return player.session.config['vertical'] == True

    @staticmethod
    def before_next_page(player, timeout_happened):
        if player.Timeout == 0:
            player.Timeout = iif(timeout_happened, 1, 0)
        player.TimeLeft = iif(player.Timeout, 0, max(0, player.TimeLeft))
        player.TimeSpent = player.TimeLimit - player.TimeLeft


class P05Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        s = player.session
        set_payoff_list(player)
        return {
            "Round": group.subsession.round_number,
            "MaxTotal": group.MaxTotal,
            "AccountBalance": player.Endowment - player.Contribution,
            "MyID": player.id_in_group,
            "Threshold": group.Threshold,
            "Timeout": player.Timeout,
            "Status": group.Status,
            "Earnings": player.Earnings,
            "GroupContribution": group.Contribution,
            "LeftFromMax": group.MaxTotal - group.Contribution,
            "Externality": group.Externality
        }

    @staticmethod
    def js_vars(player: Player):
        group = player.group
        return dict(
            MyID=player.id_in_group,
            MyEndowment=player.Endowment,
            Threshold=group.Threshold,
            MaxTotal=group.MaxTotal,
            Vertical=player.session.config['vertical'],
            Status=group.Status
        )


class P06Payment(Page):
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        s = player.session
        Selected = s.vars['random_numbers'] - 1
        Earned = cu(player.participant.vars['earnings_lists'][Selected] * 0.2) + player.session.config[
            'participation_fee']
        player.SelectedEarnings = str(Earned) + str(s.vars['random_numbers'])
        Donation = cu(player.participant.vars['unicef_list'][Selected] * 0.2)
        return {
            "SelectedRound": s.vars['random_numbers'],
            "Earned": Earned,
            "Donation": Donation
        }

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 9


page_sequence = [P01Welcome, TaskSync, P02Instructions, P02aTutorial, P02bPractice, P03Change, TaskSync, P04ContributionV, P04Contribution,
                 TaskSync, P05Results, P06Payment]
