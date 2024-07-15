import unittest

from CNLWizard.cnl import CompiledRule


class TestCnl(unittest.TestCase):

    def test_CompiledRule(self):
        rule = CompiledRule('test', ['"terminal" non_terminal'])
        self.assertEqual(['non_terminal'], rule.get_non_terminal_symbols())
        rule = CompiledRule('test', ['non_terminal'])
        self.assertEqual(['non_terminal'], rule.get_non_terminal_symbols())
        rule = CompiledRule('test', ['TERMINAL non_terminal "terminal" non_terminal TERMINAL '
                                     '"terminal" "terminal" non_terminal'])
        self.assertEqual(['non_terminal', 'non_terminal', 'non_terminal'], rule.get_non_terminal_symbols())

    def test_rule_args(self):
        rule = CompiledRule('test', ['attr attr'])
        self.assertEqual(rule.get_rule_function_args(), ['attr', 'attr'])
        rule = CompiledRule('test', ['attr attr ATTR'])
        self.assertEqual(rule.get_rule_function_args(), ['attr', 'attr'])
        rule = CompiledRule('test', ['attr attr "attr" ATTR attr'])
        self.assertEqual(rule.get_rule_function_args(), ['attr', 'attr', 'attr'])
        rule = CompiledRule('test', ['"attr" ATTR attr attr "attr" ATTR attr'])
        self.assertEqual(rule.get_rule_function_args(), ['attr', 'attr', 'attr'])
        rule = CompiledRule('test', ['attr+'])
        self.assertEqual(rule.get_rule_function_args(), ['*attr'])
