"""Bounded local agents; capabilities never execute shell commands."""
from dataclasses import dataclass

CAPABILITIES = frozenset({'memory.remember', 'memory.recall'})
@dataclass(frozen=True)
class Agent:
    id: str
    capabilities: tuple[str, ...]
    def __post_init__(self):
        object.__setattr__(self, 'capabilities', tuple(self.capabilities))
        if not self.id or len(self.id) > 64 or not self.capabilities or not set(self.capabilities) <= CAPABILITIES:
            raise ValueError('invalid agent or unsupported capability')
        if len(set(self.capabilities)) != len(self.capabilities):
            raise ValueError('duplicate capability')
    def run(self, capability, payload, memory, connection):
        if capability not in self.capabilities:
            raise ValueError('agent capability denied')
        if capability == 'memory.remember':
            return memory.remember(connection, payload['content'], payload['source'], self.id)
        return memory.search(connection, payload['query'])

class Advisor:
    """Retrieve bounded knowledge through an agent before calling a model adapter."""
    def __init__(self, agent, memory, model):
        self.agent, self.memory, self.model = agent, memory, model
    def answer(self, question, query):
        if not question.strip() or len(question) > 4000:
            raise ValueError('bounded nonempty question required')
        with self.memory.connect() as db:
            records = self.agent.run('memory.recall', {'query': query}, self.memory, db)
        # Release the SQLite connection before network I/O. Model output is not
        # automatically promoted into source-backed knowledge.
        context, remaining = [], 12000
        for record in records:
            if remaining <= 0 or len(context) >= 5:
                break
            text = record['content'][:remaining]
            context.append({'id': record['id'], 'source': record['source'], 'content': text})
            remaining -= len(text)
        result = self.model.answer(question, context)
        return {**result, 'agent_id': self.agent.id, 'used_context': context}
