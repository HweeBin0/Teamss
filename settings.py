from os import environ


def treatment_config(treatment_name):
    config = {
        'app_sequence': [
            'Part1',
        ],
        'num_rounds': 9,
        'time_limit': 60,
        'endowment': 45,
        'clear': 14
    }
    if treatment_name == "H3":
        config.update({
            'name': "H3",
            'display_name': "Horizontal. Group size: 3.",
            'vertical': False,
            'team_size': 3,
            'max_totals': [45, 75, 125],
            'num_demo_participants': 3
        })
    if treatment_name == "H5":
        config.update({
            'name': "H5",
            'display_name': "Horizontal. Group size: 5.",
            'vertical': False,
            'team_size': 5,
            'max_totals': [75, 125, 210],
            'num_demo_participants': 5
        })
    if treatment_name == "V3":
        config.update({
            'name': "V3",
            'display_name': "Vertical. Group size: 3.",
            'vertical': True,
            'team_size': 3,
            'max_totals': [45, 75, 125],
            'num_demo_participants': 3
        })
    if treatment_name == "V5":
        config.update({
            'name': "V5",
            'display_name': "Vertical. Group size: 5.",
            'vertical': True,
            'team_size': 5,
            'max_totals': [75, 125, 210],
            'num_demo_participants': 5
        })
    return config


SESSION_CONFIGS = [
    treatment_config("H3"),
    treatment_config("H5"),
    treatment_config("V3"),
    treatment_config("V5"),
]


# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1, participation_fee=5.00, doc=""
)

PARTICIPANT_FIELDS = [
    'TestBot',
    'earnings_lists',
    'unicef_list'
]

SESSION_FIELDS = [
    'TimerList',
    'GroupTimerListV',
    'MaxTotals',
    'random_numbers'
]

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'EUR'
USE_POINTS = False

ROOMS = [
    dict(
        name='econ101',
        display_name='Econ 101 class',
        participant_label_file='_rooms/econ101.txt',
    ),
    dict(name='live_demo', display_name='Room for live demo (no participant labels)'),
]

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """
Here are some oTree games.
"""


SECRET_KEY = '8878696600109'

INSTALLED_APPS = ['otree']
