import os
import sys
import json
import yaml
from kubernetes import client, config
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP("Kubernetes MCP Server", description="Manages local Kubernetes cluster with strict security scopes.")

# Initialize Kubernetes Client
try:
    # Phase 1: Load from mounted ~/.kube/config
    config.load_kube_config()
except Exception:
    try:
        # Phase 2: In-cluster service account fallback
        config.load_incluster_config()
    except Exception as e:
        print(f"Warning: Could not load Kubernetes configuration: {e}", file=sys.stderr)

v1 = client.CoreV1Api()
apps_v1 = client.AppsV1Api()
networking_v1 = client.NetworkingV1Api()

@mcp.tool()
def k8s_list_pods(namespace: str = "default") -> str:
    """Lists pods in a namespace, returning status, restarts, and age."""
    try:
        pods = v1.list_namespaced_pod(namespace)
        results = []
        for pod in pods.items:
            restarts = 0
            if pod.status.container_statuses:
                restarts = sum([c.restart_count for c in pod.status.container_statuses])
            
            results.append({
                "name": pod.metadata.name,
                "namespace": pod.metadata.namespace,
                "status": pod.status.phase,
                "restarts": restarts,
                "age": str(pod.metadata.creation_timestamp)
            })
        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error listing pods: {str(e)}"

@mcp.tool()
def k8s_get_logs(pod_name: str, namespace: str = "default", tail: int = 100, since_minutes: int = 10) -> str:
    """Retrieves logs for a pod. Strictly limited to last `tail` lines and `since_minutes`."""
    tail_limit = min(tail, 500)
    since_seconds = since_minutes * 60
    
    try:
        logs = v1.read_namespaced_pod_log(
            name=pod_name,
            namespace=namespace,
            tail_lines=tail_limit,
            since_seconds=since_seconds
        )
        return logs if logs else "No recent logs found."
    except Exception as e:
        return f"Error retrieving logs: {str(e)}"

@mcp.tool()
def k8s_deploy_workload(yaml_manifest: str, namespace: str = "default") -> str:
    """Deploys a workload. Strictly restricted to Deployment, Service, ConfigMap, and Ingress."""
    allowed_kinds = {"Deployment", "Service", "ConfigMap", "Ingress"}
    
    try:
        docs = list(yaml.safe_load_all(yaml_manifest))
        results = []
        
        for doc in docs:
            if not doc:
                continue
                
            kind = doc.get("kind")
            name = doc.get("metadata", {}).get("name", "unknown")
            
            if kind not in allowed_kinds:
                return f"SECURITY_ERROR: Kind '{kind}' is blocked. Only {allowed_kinds} are allowed."
                
            # Create/Update logic (simplified to creation for this stub)
            # In a production environment, this would use patch/replace for updates
            try:
                if kind == "Deployment":
                    apps_v1.create_namespaced_deployment(namespace, doc)
                elif kind == "Service":
                    v1.create_namespaced_service(namespace, doc)
                elif kind == "ConfigMap":
                    v1.create_namespaced_config_map(namespace, doc)
                elif kind == "Ingress":
                    networking_v1.create_namespaced_ingress(namespace, doc)
                results.append(f"Successfully deployed {kind} '{name}'")
            except Exception as e:
                if "AlreadyExists" in str(e):
                    results.append(f"Notice: {kind} '{name}' already exists.")
                else:
                    results.append(f"Error deploying {kind} '{name}': {str(e)}")
                    
        return "\n".join(results)
    except yaml.YAMLError as e:
        return f"YAML Parsing Error: {str(e)}"
    except Exception as e:
        return f"Error deploying workload: {str(e)}"

@mcp.tool()
def k8s_get_deployments(namespace: str = "default") -> str:
    """Lists deployments and their rollout status (replicas, available, status)."""
    try:
        deps = apps_v1.list_namespaced_deployment(namespace)
        results = []
        for dep in deps.items:
            replicas = dep.spec.replicas or 0
            available = dep.status.available_replicas or 0
            
            status_msg = "Healthy" if replicas == available else "Degraded/Rolling"
            
            results.append({
                "deployment": dep.metadata.name,
                "replicas": replicas,
                "available": available,
                "status": status_msg
            })
        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error listing deployments: {str(e)}"

if __name__ == "__main__":
    # Support dual-transport (SSE for network, stdio for IDEs)
    use_sse = os.environ.get("MCP_TRANSPORT") == "sse" or "--sse" in sys.argv
    
    if use_sse:
        print("[Kubernetes MCP] Starting SSE transport on port 8080...", file=sys.stderr)
        mcp.run(transport="sse", port=8080)
    else:
        mcp.run(transport="stdio")
