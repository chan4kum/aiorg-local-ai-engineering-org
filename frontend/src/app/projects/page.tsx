import React from 'react';
import Link from 'next/link';
import { Card } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import styles from './page.module.css';

export default function ProjectsList() {
  const projects = [
    { id: '1', name: 'E-commerce Redesign', description: 'Complete overhaul of the main shop frontend using Next.js', status: 'active', agents: 4, tasksCompleted: 45, totalTasks: 50 },
    { id: '2', name: 'Authentication Microservice', description: 'Rust-based JWT auth service with Redis caching', status: 'completed', agents: 2, tasksCompleted: 20, totalTasks: 20 },
    { id: '3', name: 'Data Pipeline V2', description: 'Python ETL scripts for migrating legacy database to Snowflake', status: 'active', agents: 3, tasksCompleted: 12, totalTasks: 100 },
  ];

  return (
    <div className="flex-col gap-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold mb-2">Projects</h1>
          <p className="text-secondary">Manage and monitor all your AI-driven software projects.</p>
        </div>
        <Link href="/projects/new">
          <Button>Create Project</Button>
        </Link>
      </div>

      <div className={styles.grid}>
        {projects.map(p => (
          <Link key={p.id} href={`/projects/${p.id}`} className={styles.cardLink}>
            <Card hoverable className={styles.projectCard}>
              <div className="flex justify-between items-start mb-4">
                <h3 className="font-bold text-xl">{p.name}</h3>
                <Badge variant={p.status === 'active' ? 'success' : 'default'}>{p.status}</Badge>
              </div>
              <p className="text-secondary mb-6 flex-1">{p.description}</p>
              
              <div className={styles.metrics}>
                <div className={styles.metric}>
                  <span className="text-muted text-sm">Agents</span>
                  <span className="font-semibold">{p.agents}</span>
                </div>
                <div className={styles.metric}>
                  <span className="text-muted text-sm">Progress</span>
                  <div className={styles.progressBar}>
                    <div 
                      className={styles.progressFill} 
                      style={{ width: `${(p.tasksCompleted / p.totalTasks) * 100}%` }}
                    />
                  </div>
                  <span className="font-semibold text-sm mt-1">
                    {p.tasksCompleted} / {p.totalTasks} tasks
                  </span>
                </div>
              </div>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
