import sys
from typing import List, Callable, Tuple

from colorama import Fore, Style

from wrapper.ui.console import ConsoleUserInteractor


def create_impedance_scenario_interactor(actions: List[Tuple]) -> ConsoleUserInteractor:
    user_interactor = ConsoleUserInteractor()
    start_new_command = 'n'
    repeat_command = 'r'
    omit_command = ''
    asking_message = (f'To start new computation - type "{start_new_command}" button\n'
                      f'To repeat info collecting stage - type "{repeat_command}" button\n'
                      f'or press "Enter" button to exit.')
    commands = {
        start_new_command: {
            'action': actions[0], 'help': 'Start from first stage. Old result will be rewritten.'
        },
        repeat_command: {
            'action': actions[1], 'help': 'Repeat info collecting with new input frequency range if necessary.'
        },
        omit_command: {
            'action': actions[2], 'help': 'Ends program.'
        },
    }
    user_interactor.add_question(name='choose-calculation',
                                 commands=commands,
                                 header=asking_message)
    return user_interactor


def create_main_console_interactor(actions: List[Tuple]) -> ConsoleUserInteractor:
    user_interactor = ConsoleUserInteractor()
    start_new_command = 'n'
    end_command = ''
    header_message = (f'To start new calculation - type "{start_new_command}" button\n'
                      f'Or push "Enter" button again to completely terminate the program.')
    commands = {
        start_new_command: {
            'action': actions[0], 'help': 'Starts new computation.'
        },
        end_command: {
            'action': actions[1], 'help': 'Ends program.'
        },
    }
    user_interactor.add_question(name='new-computation',
                                 commands=commands,
                                 header=header_message)

    return user_interactor
