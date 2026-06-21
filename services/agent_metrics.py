from typing import Dict, Any
from memory.postgres_memory import PostgresMemory
import datetime

class AgentMetricsService:
    def __init__(self, memory_store: PostgresMemory = None):
        self.memory_store = memory_store
        
    async def log_agent_performance(self, run_id: str, agent_name: str, task: str, duration_sec: float, token_count: int, failures: int, success: bool):
        """Logs the agent performance metrics into Postgres for long-term evaluation."""
        metric = {
            "agent_name": agent_name,
            "task": task,
            "duration": duration_sec,
            "token_count": token_count,
            "failures": failures,
            "success": success,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        
        print(f"[AgentMetrics] Logging performance for {agent_name}: {metric}")
        
        if self.memory_store:
            metadata = {"type": "agent_performance", "agent": agent_name}
            await self.memory_store.save_record(run_id, str(metric), metadata)

agent_metrics = AgentMetricsService()
