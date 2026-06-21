import React from 'react';
import styles from './Spinner.module.css';

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  color?: string;
}

export const Spinner: React.FC<SpinnerProps> = ({ size = 'md', color = 'var(--primary-color)' }) => {
  return (
    <div 
      className={`${styles.spinner} ${styles[size]}`} 
      style={{ borderTopColor: color }}
    />
  );
};
