import unittest
from cybagents import Agent
class AgentTests(unittest.TestCase):
    def test_caller_cannot_mutate_capabilities(self):
        capabilities=['memory.recall'];agent=Agent('reader',capabilities)
        capabilities.append('memory.remember')
        self.assertEqual(agent.capabilities,('memory.recall',))
    def test_no_shell_capabilities(self):
        with self.assertRaises(ValueError): Agent('runner', ('shell.execute',))
    def test_capability_denied_before_memory_access(self):
        agent=Agent('reader', ('memory.recall',))
        with self.assertRaises(ValueError): agent.run('memory.remember', {}, None, None)

class AdvisorTests(unittest.TestCase):
    def test_context_budget_and_connection_closed_before_model(self):
        from contextlib import contextmanager
        from cybagents import Advisor
        class Memory:
            opened=False
            @contextmanager
            def connect(self):
                self.opened=True
                try:yield None
                finally:self.opened=False
            def search(self,db,query):return [{'id':str(i),'source':'journal','content':'x'*8000} for i in range(20)]
        memory=Memory()
        class Model:
            def answer(inner,question,context):
                self.assertFalse(memory.opened)
                self.assertEqual(sum(len(row['content']) for row in context),12000)
                return {'answer':'fixture','model':'fixture'}
        result=Advisor(Agent('advisor',('memory.recall',)),memory,Model()).answer('question','query')
        self.assertEqual(len(result['used_context']),2)
    def test_read_permission_required(self):
        from contextlib import nullcontext
        from cybagents import Advisor
        from types import SimpleNamespace
        memory=SimpleNamespace(connect=lambda:nullcontext(None))
        with self.assertRaises(ValueError):Advisor(Agent('writer',('memory.remember',)),memory,None).answer('question','query')
