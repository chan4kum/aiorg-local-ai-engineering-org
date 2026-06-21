import hashlib
import difflib
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.database.models import Artifact, ArtifactVersion
from opentelemetry import trace
import structlog

tracer = trace.get_tracer(__name__)
logger = structlog.get_logger()

class ArtifactStore:
    def __init__(self, session_maker):
        self.session_maker = session_maker

    def _hash_content(self, content: str) -> str:
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    async def save_artifact(self, task_id: str, name: str, content: str) -> Dict[str, Any]:
        with tracer.start_as_current_span("artifact_store.save"):
            async with self.session_maker() as session:
                stmt = select(Artifact).where(Artifact.task_id == task_id, Artifact.name == name)
                result = await session.execute(stmt)
                artifact = result.scalar_one_or_none()

                if not artifact:
                    artifact = Artifact(task_id=task_id, name=name)
                    session.add(artifact)
                    await session.flush()
                    version_num = 1
                    diff = ""
                else:
                    stmt = select(ArtifactVersion).where(ArtifactVersion.artifact_id == artifact.id).order_by(ArtifactVersion.version.desc())
                    v_result = await session.execute(stmt)
                    latest_version = v_result.scalars().first()
                    version_num = latest_version.version + 1 if latest_version else 1
                    
                    # Compute diff
                    if latest_version and latest_version.diff is not None:
                        # In a real implementation we would reconstruct previous content from diffs or store full text
                        diff = "\n".join(difflib.unified_diff(["previous"], [content]))
                    else:
                        diff = content

                content_hash = self._hash_content(content)
                new_version = ArtifactVersion(
                    artifact_id=artifact.id,
                    version=version_num,
                    content_hash=content_hash,
                    diff=diff
                )
                session.add(new_version)
                await session.commit()
                logger.info("Saved artifact", artifact_id=str(artifact.id), version=version_num)
                return {"id": str(artifact.id), "version": version_num, "hash": content_hash}

    async def get_artifact_history(self, artifact_id: str) -> List[Dict[str, Any]]:
        with tracer.start_as_current_span("artifact_store.history"):
            async with self.session_maker() as session:
                stmt = select(ArtifactVersion).where(ArtifactVersion.artifact_id == artifact_id).order_by(ArtifactVersion.version)
                result = await session.execute(stmt)
                versions = result.scalars().all()
                return [{"version": v.version, "hash": v.content_hash, "created_at": v.created_at.isoformat()} for v in versions]
