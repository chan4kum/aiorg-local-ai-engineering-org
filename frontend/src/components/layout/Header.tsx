import React from 'react';
import styles from './Header.module.css';

export const Header: React.FC = () => {
  return (
    <header className={`${styles.header} glass`}>
      <div className={styles.searchContainer}>
        <span className={styles.searchIcon}>🔍</span>
        <input 
          type="text" 
          placeholder="Search projects, workflows, or agents..." 
          className={styles.searchInput}
        />
      </div>

      <div className={styles.actions}>
        <button className={styles.iconBtn}>
          🔔
          <span className={styles.notificationDot} />
        </button>
        <div className={styles.avatar}>
          JD
        </div>
      </div>
    </header>
  );
};
