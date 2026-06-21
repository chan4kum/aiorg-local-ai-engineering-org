'use client';
"use client";

import React, { useState } from 'react';
import { Card } from '../../../components/ui/Card';
import { Badge } from '../../../components/ui/Badge';
import { Button } from '../../../components/ui/Button';
import { WorkflowGraph } from '../../../components/project/WorkflowGraph';
import { ArtifactViewer } from '../../../components/project/ArtifactViewer';
import styles from './page.module.css';

export default function ProjectDetail({ params }: { params: { id: string } }) {
  const [activeTab, setActiveTab] = useState<'workflow' | 'artifacts' | 'agents' | 'logs'>('workflow');

  const tabs = [
    { id: 'workflow', label: 'Workflow DAG' },
    { id: 'artifacts', label: 'Artifacts' },
    { id: 'agents', label: 'Assigned Agents' },
    { id: 'logs', label: 'System Logs' },
  ] as const;

  return (
    <div className="flex-col gap-6">
      <div className={styles.header}>
        <div>
          <div className="flex items-center gap-4 mb-2">
            <h1 className="text-2xl font-bold">E-commerce Redesign</h1>
            <Badge variant="success">Active</Badge>
          </div>
          <p className="text-secondary">Complete overhaul of the main shop frontend using Next.js</p>
        </div>
        <div className="flex gap-4">
          <Button variant="secondary">Pause Workflow</Button>
          <Button>Trigger Re-plan</Button>
        </div>
      </div>

      <div className={styles.tabs}>
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`${styles.tabBtn} ${activeTab === tab.id ? styles.activeTab : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className={styles.content}>
        {activeTab === 'workflow' && (
          <Card className={styles.tabCard}>
            <WorkflowGraph />
          </Card>
        )}
        {activeTab === 'artifacts' && (
          <ArtifactViewer />
        )}
        {activeTab === 'agents' && (
          <Card className={styles.tabCard}>
            <div className="text-secondary">Agent list coming soon...</div>
          </Card>
        )}
        {activeTab === 'logs' && (
          <Card className={`${styles.tabCard} ${styles.consoleCard}`}>
            <pre className={styles.console}>
              [10:45:01] INFO  System: Workflow initialized{'\n'}
              [10:45:03] INFO  Architect: Created technical design document{'\n'}
              [10:45:05] WARN  Frontend: Missing API specification for user profile{'\n'}
              [10:46:12] INFO  Backend: Generated swagger.json{'\n'}
              <span className="animate-pulse-glow" style={{ color: 'var(--primary-color)' }}>[10:46:15] RUN   Frontend: Implementing UI components...</span>
            </pre>
          </Card>
        )}
      </div>
    </div>
  );
}
