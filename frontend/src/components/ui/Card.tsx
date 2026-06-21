import React from 'react';
import styles from './Card.module.css';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  glass?: boolean;
  hoverable?: boolean;
}

export const Card: React.FC<CardProps> = ({ 
  children, 
  glass = false, 
  hoverable = false,
  className = '', 
  ...props 
}) => {
  return (
    <div 
      className={`${styles.card} ${glass ? 'glass' : ''} ${hoverable ? styles.hoverable : ''} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};
