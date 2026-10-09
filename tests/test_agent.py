import unittest
from cybagents import Agent
class AgentTests(unittest.TestCase):
    def test_no_shell_capabilities(self):
        with self.assertRaises(ValueError): Agent('runner', ('shell.execute',))
    def test_capability_denied_before_memory_access(self):
        agent=Agent('reader', ('memory.recall',))
        with self.assertRaises(ValueError): agent.run('memory.remember', {}, None, None)
