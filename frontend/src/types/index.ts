export interface Project {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'archived' | 'completed';
  createdAt: string;
  updatedAt: string;
}

export interface Workflow {
  id: string;
  projectId: string;
  name: string;
  status: 'running' | 'completed' | 'failed' | 'pending';
  startedAt?: string;
  completedAt?: string;
}

export interface Task {
  id: string;
  workflowId: string;
  name: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  dependsOn: string[]; // Task IDs
  assignedAgentId?: string;
}

export interface Artifact {
  id: string;
  projectId: string;
  name: string;
  type: 'code' | 'document' | 'image' | 'other';
  content: string; // the actual code/text or URL
  version: number;
  createdAt: string;
}

export interface Agent {
  id: string;
  name: string;
  role: string;
  status: 'idle' | 'working' | 'offline';
  capabilities: string[];
}

export interface AgentRun {
  id: string;
  agentId: string;
  taskId: string;
  status: 'running' | 'success' | 'failed';
  logs: string[];
  startTime: string;
  endTime?: string;
}

export interface Event {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  message: string;
  timestamp: string;
  source: string; // e.g. agent name, system
}
