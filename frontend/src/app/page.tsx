import React from 'react';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import Link from 'next/link';
import styles from './page.module.css';

export default function Dashboard() {
  const stats = [
    { label: 'Active Projects', value: '12', trend: '+2 this week' },
    { label: 'Agents Online', value: '15', trend: 'All healthy' },
    { label: 'Workflows Running', value: '4', trend: '1 pending' },
    { label: 'Code Artifacts', value: '1,284', trend: '+156 this week' }
  ];

  const recentProjects = [
    { id: '1', name: 'E-commerce Redesign', status: 'active', updated: '2 hours ago' },
    { id: '2', name: 'Authentication Microservice', status: 'completed', updated: '1 day ago' },
    { id: '3', name: 'Data Pipeline V2', status: 'active', updated: '3 days ago' },
  ];

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div>
          <h1 className="text-2xl font-bold mb-2">Welcome back, Engineer</h1>
          <p className="text-secondary">Here is what's happening with your AI workforce.</p>
        </div>
        <Link href="/projects/new">
          <Button>New Project</Button>
        </Link>
      </header>

      <section className={styles.statsGrid}>
        {stats.map((stat, i) => (
          <Card key={i} hoverable className={styles.statCard}>
            <p className={styles.statLabel}>{stat.label}</p>
            <h3 className={styles.statValue}>{stat.value}</h3>
            <p className={styles.statTrend}>{stat.trend}</p>
          </Card>
        ))}
      </section>

      <div className={styles.twoCol}>
        <Card className={styles.recentSection}>
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold">Recent Projects</h2>
            <Link href="/projects" className="text-secondary hover:text-primary">View all</Link>
          </div>
          <div className="flex-col gap-4">
            {recentProjects.map(proj => (
              <div key={proj.id} className={styles.projectItem}>
                <div>
                  <h4 className="font-semibold">{proj.name}</h4>
                  <span className="text-secondary text-sm">Updated {proj.updated}</span>
                </div>
                <Badge variant={proj.status === 'active' ? 'success' : 'default'}>
                  {proj.status}
                </Badge>
              </div>
            ))}
          </div>
        </Card>

        <Card className={styles.activitySection}>
          <h2 className="text-xl font-bold mb-6">System Activity</h2>
          <div className={styles.timeline}>
            <div className={styles.timelineItem}>
              <div className={styles.timelineDot} style={{ background: 'var(--success-color)' }} />
              <div>
                <p className="font-semibold">BackendAgent deployed API</p>
                <p className="text-secondary text-sm">10 minutes ago</p>
              </div>
            </div>
            <div className={styles.timelineItem}>
              <div className={styles.timelineDot} style={{ background: 'var(--primary-color)' }} />
              <div>
                <p className="font-semibold">ArchitectAgent approved PR #12</p>
                <p className="text-secondary text-sm">1 hour ago</p>
              </div>
            </div>
            <div className={styles.timelineItem}>
              <div className={styles.timelineDot} style={{ background: 'var(--warning-color)' }} />
              <div>
                <p className="font-semibold">QA_Agent found 2 bugs in auth module</p>
                <p className="text-secondary text-sm">2 hours ago</p>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
