import React from 'react';
import { Card } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';
import styles from './page.module.css';

export default function AgentsPage() {
  const agents = [
    { id: '1', name: 'Architect_Primary', role: 'System Architect', status: 'working', task: 'E-commerce Spec', skillLevel: 'Senior' },
    { id: '2', name: 'Frontend_React', role: 'Frontend Engineer', status: 'idle', task: 'None', skillLevel: 'Mid' },
    { id: '3', name: 'Backend_Rust', role: 'Backend Engineer', status: 'working', task: 'Auth Microservice', skillLevel: 'Senior' },
    { id: '4', name: 'DB_Admin', role: 'Database Admin', status: 'idle', task: 'None', skillLevel: 'Senior' },
    { id: '5', name: 'QA_Automated', role: 'QA Engineer', status: 'working', task: 'API Tests', skillLevel: 'Mid' },
    { id: '6', name: 'DevOps_AWS', role: 'DevOps Engineer', status: 'offline', task: 'None', skillLevel: 'Senior' },
  ];

  return (
    <div className="flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold mb-2">Agent Workforce</h1>
        <p className="text-secondary">Monitor the status and performance of your AI engineering team.</p>
      </div>

      <div className={styles.statsRow}>
        <Card className={styles.statBox}>
          <span className="text-secondary text-sm">Total Agents</span>
          <span className="text-2xl font-bold">15</span>
        </Card>
        <Card className={styles.statBox}>
          <span className="text-secondary text-sm">Currently Working</span>
          <span className="text-2xl font-bold text-primary-color">8</span>
        </Card>
        <Card className={styles.statBox}>
          <span className="text-secondary text-sm">Tasks Completed Today</span>
          <span className="text-2xl font-bold text-success-color">142</span>
        </Card>
      </div>

      <Card className="p-0 overflow-hidden">
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Agent Name</th>
              <th>Role</th>
              <th>Status</th>
              <th>Current Task</th>
              <th>Skill Level</th>
            </tr>
          </thead>
          <tbody>
            {agents.map(agent => (
              <tr key={agent.id}>
                <td className="font-semibold">{agent.name}</td>
                <td className="text-secondary">{agent.role}</td>
                <td>
                  <Badge variant={
                    agent.status === 'working' ? 'primary' as any : 
                    agent.status === 'idle' ? 'success' : 'default'
                  }>
                    {agent.status}
                  </Badge>
                </td>
                <td>{agent.task}</td>
                <td>{agent.skillLevel}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
