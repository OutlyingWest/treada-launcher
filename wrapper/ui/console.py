from pprint import pprint
from typing import Callable, Dict, Union

from colorama import Fore, Style


class ConsoleUserQuestion:
    def __init__(self):
        self.descriptions = {'warning': 'Wrong command! Type "help" to see the commands list'}
        self.commands = {'help': {'action': (self.print_help, ), 'help': 'Shows the list of commands'}}

    def add_descriptions(self, header='', footer='', warning=''):
        self.descriptions.update({'header': header, 'footer': footer})
        if warning:
            self.descriptions['warning'] = warning

    def add_command(self, command: str, action: tuple, command_help=''):
        self.commands[command] = {'action': action, 'help': command_help}

    def add_commands(self, commands: Dict[str, dict]):
        for command_key, features in commands.items():
            if isinstance(features['action'][0], Callable) and isinstance(features['help'], str):
                self.commands[command_key] = {'action': features['action'], 'help': features['help']}

    def execute_command(self, user_command: str) -> bool:
        features = self.commands.get(user_command)
        if features:
            func = features['action'][0]
            args = features['action'][1:]
            func(*args)
            return True
        else:
            return False

    def print_header(self):
        print(self.descriptions['header'])

    def print_footer(self):
        print(self.descriptions['footer'])

    def print_warning(self):
        print(self.descriptions['warning'])

    def print_help(self):
        print('List of commands:')
        for command, features in self.commands.items():
            command_help = features['help']
            print(f'{f"{command}": >10}  {f"{command_help}": <10}')
        print()


class ConsoleUserInteractor:
    def __init__(self):
        self.questions: Dict[str, ConsoleUserQuestion] = {}

    def add_question(self, name: str, commands: Dict[str, dict], header='', footer='', warning=''):
        question = ConsoleUserQuestion()
        question.add_commands(commands)
        question.add_descriptions(header, footer, warning)
        self.questions[name] = question

    def ask_question(self, name: str):
        question = self.questions.get(name)
        if question:
            self.__question_loop(question)
        else:
            raise ValueError(f'Question with name: {name} does not exists.')

    @classmethod
    def __question_loop(cls, question: ConsoleUserQuestion):
        while True:
            question.print_header()
            user_command = input()
            is_executed = question.execute_command(user_command)
            if is_executed:
                question.print_footer()
                break
            else:
                question.print_warning()


def quit_user_warning_dialogue():
    print(f'To complete the scenario, push the {Fore.GREEN}Enter{Style.RESET_ALL} button. '
          f'{Fore.YELLOW}Be careful! All interactive plots will be destroyed.{Style.RESET_ALL}')
    input()
