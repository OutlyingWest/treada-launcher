import unittest
from io import StringIO
from unittest.mock import patch

from wrapper.ui.console import ConsoleUserInteractor


class ImpedancePlotBuilderTests(unittest.TestCase):

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
        self.assertEqual(self.interactor.questions['true-false'].commands, self.commands)

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

