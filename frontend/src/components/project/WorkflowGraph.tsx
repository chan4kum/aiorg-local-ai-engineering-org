import React from 'react';
import styles from './WorkflowGraph.module.css';

// A simple CSS-based visualization of a DAG
export const WorkflowGraph: React.FC = () => {
  const nodes = [
    { id: '1', label: 'Tech Spec', agent: 'Architect', status: 'completed', x: 50, y: 50 },
    { id: '2', label: 'DB Schema', agent: 'Backend DB', status: 'completed', x: 250, y: 50 },
    { id: '3', label: 'API Routes', agent: 'Backend API', status: 'in_progress', x: 450, y: 50 },
    { id: '4', label: 'UI Mockups', agent: 'UX Designer', status: 'completed', x: 250, y: 150 },
    { id: '5', label: 'React Components', agent: 'Frontend', status: 'pending', x: 450, y: 150 },
    { id: '6', label: 'Integration Test', agent: 'QA', status: 'pending', x: 650, y: 100 },
  ];

  const edges = [
    { from: '1', to: '2' },
    { from: '1', to: '4' },
    { from: '2', to: '3' },
    { from: '4', to: '5' },
    { from: '3', to: '6' },
    { from: '5', to: '6' },
  ];

  return (
    <div className={styles.graphContainer}>
      <svg className={styles.edges}>
        {edges.map((edge, i) => {
          const fromNode = nodes.find(n => n.id === edge.from);
          const toNode = nodes.find(n => n.id === edge.to);
          if (!fromNode || !toNode) return null;
          
          return (
            <line 
              key={i}
              x1={fromNode.x + 120} 
              y1={fromNode.y + 30} 
              x2={toNode.x} 
              y2={toNode.y + 30} 
              className={`${styles.edge} ${fromNode.status === 'completed' ? styles.edgeCompleted : ''}`}
            />
          );
        })}
      </svg>
      
      {nodes.map(node => (
        <div 
          key={node.id} 
          className={`${styles.node} ${styles[node.status]}`}
          style={{ left: node.x, top: node.y }}
        >
          <div className={styles.nodeHeader}>
            <span className={styles.agentTag}>{node.agent}</span>
            {node.status === 'in_progress' && <span className={styles.pulse} />}
          </div>
          <div className={styles.nodeLabel}>{node.label}</div>
        </div>
      ))}
    </div>
  );
};
