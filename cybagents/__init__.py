"""Bounded local agents; capabilities never execute shell commands."""
from dataclasses import dataclass

CAPABILITIES = frozenset({'memory.remember', 'memory.recall'})
@dataclass(frozen=True)
class Agent:
    id: str
    capabilities: tuple[str, ...]
    def __post_init__(self):
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
