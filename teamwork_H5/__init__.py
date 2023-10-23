from otree.api import *
import random

doc = """
Simultaneous/Horizontal Game 5 Players
"""


class C(BaseConstants):
    NAME_IN_URL = 'teamwork_H5'
    PLAYERS_PER_GROUP = 5
    NUM_ROUNDS = 9
    endowment = 45
    clear = 14


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    #   treatment = models.CharField()
    remaining = models.IntegerField(initial=999)
    total_contribution = models.IntegerField(initial=0)
    target = models.IntegerField()
    min_target = models.IntegerField()
    # cur_editor = models.IntegerField(initial=1)
    timer = models.IntegerField()


class Player(BasePlayer):
    contribution = models.IntegerField(min=0, initial=0)
    earnings = models.IntegerField()


#Functions
def def_group_var(group: Group): #function to create the random list of target and timer and a random number that selects the round for payment
    group.session.vars['timer_list'] = [random.randint(300,310) for _ in range(9)]
    levels = [75, 125, 210]
    random.shuffle(levels)
    target_list = levels[0:1] * 3 + levels[1:2] * 3 + levels[2:3] * 3
    group.session.vars['target_list'] = target_list
    group.session.vars['rand'] = random.randint(1, 9)


def set_payoff_list(player: Player): #function that lists the player's earnings and contributions throughout the rounds
    if player.round_number == 1:
        player.participant.vars['earnings_lists'] = [player.earnings]
        group = player.group
        player.participant.vars['unicef_list'] = [group.total_contribution]
    elif 1 < player.round_number <= 9:
        participant_vars = player.participant.vars.get('earnings_lists',[])
        participant_vars.append(player.earnings)
        player.participant.vars['earnings_list'] = participant_vars

        group = player.group
        p_vars = player.participant.vars.get('unicef_list', [])
        p_vars.append(group.total_contribution)
        player.participant.vars['unicef_list'] = p_vars


# PAGES
#A buffer page to run the random function before using it, otherwise players in the same group would observe different values
class start(Page):
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        def_group_var(group)

    def is_displayed(player: Player):
        return player.round_number == 1


#Instruction page (to be removed if subjects are provided with printed instructions),(could consider provide a test on the understanding of it)
class Instruction(Page):
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        x_var = group.session.vars['target_list'][0]
        return {
            'n': C.PLAYERS_PER_GROUP,
            'nminus': C.PLAYERS_PER_GROUP - 1,
            'x': x_var,
            '2x': 2*x_var,
            "onethird": int(x_var/3)
        }

    def is_displayed(player: Player):
        return player.round_number == 1


#changes to be conveyed to subjects
class Change(Page):
    def vars_for_template(player: Player):
        group = player.group
        group.target = int(group.session.vars['target_list'][player.round_number - 1])
        group.min_target = int(group.target / 3)
        return {
            "target": group.target,
            "min": group.min_target
        }
    def is_displayed(player: Player):
        return player.round_number == 4 or player.round_number == 7


class Contribution(Page):
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        group.target = int(group.session.vars['target_list'][player.round_number - 1])
        group.min_target = int(group.target / 3)
        remaine = C.endowment - player.contribution
        group.timer = group.session.vars['timer_list'][player.round_number - 1]
        return {
            "target": group.target,
            "endowment": C.endowment,
            "remaine": remaine,
            "playerid": player.id_in_group,
            "timer": group.timer,
            "mintarget": group.min_target
        }

    def js_vars(player: Player):
        group = player.group
        return dict(
            MyRole = player.id_in_group,
            Grouptarget = group.target,
            Grouptimer = group.timer,
            Mintarget = group.min_target
        )

    def live_method(player, incre):
        group = player.group
        remaine = C.endowment - player.contribution
        if incre == 10 or incre == 1:
            group.remaining = group.target - group.total_contribution
            if incre == 1:
                maxi = min(C.endowment, group.target, group.remaining, remaine)
            else:
                maxi = min(C.endowment, group.target, group.remaining, remaine) - 9
            if maxi>0 :
                player.contribution = player.contribution + incre
                players = player.group.get_players()
                contributions = [p.contribution for p in players]
                group.total_contribution = sum(contributions)
                group.remaining = group.target - group.total_contribution
                remainE = C.endowment - player.contribution
                response = dict(senderid=player.id_in_group, groupremain=group.remaining, remainE=remainE, groupcontri = group.total_contribution, contributionslist=contributions)
                return {0: response}
            else:
                if min(C.endowment, group.target, group.remaining, remaine) == remaine:
                    extra = remaine
                if min(C.endowment, group.target, group.remaining, remaine) == group.remaining:
                    extra = group.remaining
                player.contribution = player.contribution + extra
                players = player.group.get_players()
                contributions = [p.contribution for p in players]
                group.total_contribution = sum(contributions)
                group.remaining = group.target - group.total_contribution
                remainE = C.endowment - player.contribution
                response = dict(senderid=player.id_in_group, groupremain=group.remaining, remainE=remainE, groupcontri=group.total_contribution, contributionslist=contributions)
                return {0: response}
        else:
            players = player.group.get_players()
            contributions = [p.contribution for p in players]
            group.total_contribution = sum(contributions)
            group.remaining = group.target - group.total_contribution
            response = dict(playerc=0, playert=group.remaining, remaine=C.endowment, change=1, groupcontri = group.total_contribution)
            return {0: response}


class Wait(WaitPage):
    pass


#result page if fail to reach the minimum threshold
class ResultsFail(Page):
    @staticmethod
    def vars_for_template(player: Player):
        player.earnings = 0
        group = player.group
        externality = group.remaining * 2
        if group.total_contribution == 0:
            externality = group.target * 2
        return {
            "earnings": player.earnings,
            "remaining": group.remaining,
            "externality": externality,
            "total_contribution": group.total_contribution
        }

    def is_displayed(player: Player):
        group = player.group
        return group.total_contribution < group.min_target

    def before_next_page(player: Player, timeout_happened):
        set_payoff_list(player)


#result page if maximum threshold is reached
class ResultsClear(Page):
    @staticmethod
    def vars_for_template(player: Player):
        player.earnings = C.endowment - player.contribution + C.clear
        return {
            "earnings": player.earnings,
            "endowleft": C.endowment - player.contribution
        }

    def is_displayed(player: Player):
        group = player.group
        return group.total_contribution >= group.min_target and group.remaining == 0

    def before_next_page(player: Player, timeout_happened):
        set_payoff_list(player)


#result page if minimum is reached but below the maximum
class ResultsIncomplete(Page):
    @staticmethod
    def vars_for_template(player: Player):
        player.earnings = C.endowment - player.contribution + C.clear
        group = player.group
        externality = group.remaining * 2
        return {
            "earnings": player.earnings,
            "remaining": group.remaining,
            "externality": externality,
            "total_contribution": group.total_contribution,
            "endowleft": C.endowment - player.contribution
        }

    def is_displayed(player: Player):
        group = player.group
        return group.total_contribution >= group.min_target and group.remaining > 0

    def before_next_page(player: Player, timeout_happened):
        set_payoff_list(player)


page_sequence = [start, Instruction, Change, Wait, Contribution, Wait, ResultsClear, ResultsIncomplete, ResultsFail]
