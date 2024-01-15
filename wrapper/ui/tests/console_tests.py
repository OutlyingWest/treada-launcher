import unittest
from io import StringIO
from unittest.mock import patch

from wrapper.ui.console import ConsoleUserInteractor


class ConsoleUserInteractorTests(unittest.TestCase):

    def setUp(self) -> None:
        def true_action():
            print('true action called')

        def false_action():
            print('false action called')

        self.interactor = ConsoleUserInteractor()
        self.commands = {
            'true-action': {'action': true_action, 'help': 'performs action'},
            'false-action': {'action': false_action, 'help': 'performs action'},
        }

    # @unittest.skip
    def test_add_question(self):
        self.interactor.add_question('true-false', self.commands,
                                     header='Print true or false "action"',
                                     footer='Done',
                                     warning='Wrong command!')
        print(f'{self.interactor.questions=}')
        print(f'{self.interactor.questions["true-false"].commands=}')
        self.interactor.questions['true-false'].commands.pop('help')
        self.assertEqual(self.commands, self.interactor.questions['true-false'].commands)

    def test_ask_question(self):
        self.interactor.add_question('true-false', self.commands,
                                     header='Print true or false "action"',
                                     footer='Done',
                                     warning='Wrong command!')

        command = 'true-action'
        expected_output = 'true action called'

        with (patch('builtins.input', side_effect=[command]),
              patch('sys.stdout', new_callable=StringIO) as mock_stdout):

            self.interactor.ask_question('true-false')

            stdout_result = mock_stdout.getvalue().strip()

        print(f'{stdout_result=}')
        self.assertIn(expected_output, stdout_result)

    def test_wrong_command(self):
        self.interactor.add_question('true-false', self.commands,
                                     header='Print true or false "action"',
                                     footer='Done',
                                     warning='Wrong command!')

        wrong_command = 'wrong'
        right_command = 'true-action'
        expected_output = 'Wrong command!'

        with (patch('builtins.input', side_effect=[wrong_command, right_command]),
              patch('sys.stdout', new_callable=StringIO) as mock_stdout):
            self.interactor.ask_question('true-false')

            stdout_result = mock_stdout.getvalue().strip()

        print(f'{stdout_result=}')
        self.assertIn(expected_output, stdout_result)

    def test_help(self):
        self.interactor.add_question('true-false', self.commands,
                                     header='Print true or false "action"',
                                     footer='Done',
                                     warning='Wrong command!')

        command = 'help'
        expected_output = 'Shows the list of commands'

        with (patch('builtins.input', side_effect=[command]),
              patch('sys.stdout', new_callable=StringIO) as mock_stdout):

            self.interactor.ask_question('true-false')

            stdout_result = mock_stdout.getvalue().strip()

        print(f'{stdout_result=}')
        self.assertIn(expected_output, stdout_result)
