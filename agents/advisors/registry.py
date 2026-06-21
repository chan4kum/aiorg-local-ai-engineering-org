from typing import Callable, Dict, Any

def security_advisor(context: Dict[str, Any]) -> str:
    print("[Advisor: Security] Reviewing for vulnerabilities...")
    return "Ensure JWT tokens have strict expiration. Use parameterized queries."

def devops_advisor(context: Dict[str, Any]) -> str:
    print("[Advisor: DevOps] Reviewing infrastructure and docker setup...")
    return "Use multistage builds in Dockerfile to minimize image size."

def data_advisor(context: Dict[str, Any]) -> str:
    print("[Advisor: Data] Reviewing data schemas...")
    return "Add indexes to frequently queried columns."

def observability_advisor(context: Dict[str, Any]) -> str:
    print("[Advisor: Observability] Reviewing telemetry setup...")
    return "Include request ID tracing in logger context."

def database_advisor(context: Dict[str, Any]) -> str:
    print("[Advisor: Database] Reviewing query efficiency...")
    return "Consider using asyncpg for better Postgres connection pooling."

def performance_advisor(context: Dict[str, Any]) -> str:
    print("[Advisor: Performance] Reviewing bottlenecks...")
    return "Cache the results of the heavy DB query using Redis if available."

class AdvisorRegistry:
    def __init__(self):
        self.advisors: Dict[str, Callable] = {
            "security": security_advisor,
            "devops": devops_advisor,
            "data": data_advisor,
            "observability": observability_advisor,
            "database": database_advisor,
            "performance": performance_advisor
        }
        
    def call_advisors(self, task_description: str, context: Dict[str, Any]) -> Dict[str, str]:
        """Dynamically select advisors based on context matching."""
        task_lower = task_description.lower()
        advice = {}
        
        if "auth" in task_lower or "security" in task_lower or "jwt" in task_lower:
            advice["security"] = self.advisors["security"](context)
            
        if "docker" in task_lower or "deploy" in task_lower or "ci/cd" in task_lower:
            advice["devops"] = self.advisors["devops"](context)
            
        if "schema" in task_lower or "data" in task_lower:
            advice["data"] = self.advisors["data"](context)
            
        if "postgres" in task_lower or "sql" in task_lower or "db" in task_lower:
            advice["database"] = self.advisors["database"](context)
            
        if "trace" in task_lower or "log" in task_lower or "metrics" in task_lower:
            advice["observability"] = self.advisors["observability"](context)
            
        if "slow" in task_lower or "optimize" in task_lower or "performance" in task_lower:
            advice["performance"] = self.advisors["performance"](context)
            
        return advice

registry = AdvisorRegistry()
