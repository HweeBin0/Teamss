from otree.api import *
import random


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'post'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    age = models.IntegerField(
        min=16, max=99,
        label='What is your age?')
    gender = models.CharField(
        choices=[('Male', 'Male'), ('Female', 'Female')],
        widget=widgets.RadioSelect(),
        label='What is your gender?',
    )


# PAGES
class Payment(Page):
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        rand_num = group.session.vars['rand'] - 1
        earnings = cu(player.participant.vars['earnings_lists'][rand_num] * 0.2) + player.session.config['participation_fee']
        player.payoff = earnings
        donation = cu(player.participant.vars['unicef_list'][rand_num] * 2 * 0.2)

        return {'earnings': earnings,
                'donation': donation,
                'round': group.session.vars['random_numbers']}


class Survey(Page):
    form_model = "player"
    form_fields = ['age', 'gender']



page_sequence = [Survey, Payment]



