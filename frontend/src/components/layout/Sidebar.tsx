"use client";

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import styles from './Sidebar.module.css';

export const Sidebar: React.FC = () => {
  const pathname = usePathname();

  const navItems = [
    { label: 'Dashboard', path: '/', icon: '📊' },
    { label: 'Projects', path: '/projects', icon: '📁' },
    { label: 'Agents', path: '/agents', icon: '🤖' },
    { label: 'Settings', path: '/settings', icon: '⚙️' },
  ];

  return (
    <aside className={`${styles.sidebar} glass`}>
      <div className={styles.logo}>
        <div className={styles.logoIcon}>
          <span className={styles.claw}>⚡</span>
        </div>
        <span className={styles.brandName}>OpenClaw</span>
      </div>

      <nav className={styles.nav}>
        {navItems.map((item) => {
          const isActive = pathname === item.path || (item.path !== '/' && pathname.startsWith(item.path));
          return (
            <Link 
              key={item.path} 
              href={item.path}
              className={`${styles.navItem} ${isActive ? styles.active : ''}`}
            >
              <span className={styles.icon}>{item.icon}</span>
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className={styles.footer}>
        <div className={styles.status}>
          <span className={styles.statusDot}></span>
          System Online
        </div>
      </div>
    </aside>
  );
};
