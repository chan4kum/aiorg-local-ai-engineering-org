from typing import Dict, Any

class ArchitectureGuard:
    """
    Architecture Compliance Engine.
    Reviews the developer's output against the project_blueprint to flag violations before QA.
    """
    
    def check_compliance(self, project_blueprint: Dict[str, str], code_manifest: Dict[str, str]) -> float:
        """
        Calculates compliance score based on the expected blueprint vs what was actually built.
        """
        print("[ArchitectureGuard] Verifying architecture compliance...")
        
        violations = []
        score = 100.0
        
        # Stub logic
        expected_db = project_blueprint.get("database", "postgres").lower()
        actual_db = code_manifest.get("database_used", "postgres").lower()
        
        if expected_db != actual_db:
            violations.append(f"Database mismatch: Expected {expected_db}, found {actual_db}")
            score -= 20.0
            
        if violations:
            print(f"[ArchitectureGuard] WARNING: Found violations: {violations}")
            
        return max(0.0, score)

architecture_guard = ArchitectureGuard()
