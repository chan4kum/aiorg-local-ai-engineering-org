'use client';
"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card } from '../../../components/ui/Card';
import { Button } from '../../../components/ui/Button';
import styles from './page.module.css';

export default function NewProject() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    // Simulate API call
    setTimeout(() => {
      router.push('/projects/1');
    }, 1500);
  };

  return (
    <div className={styles.container}>
      <div className="mb-8">
        <h1 className="text-2xl font-bold mb-2">Create New Project</h1>
        <p className="text-secondary">Define the requirements and let OpenClaw architect the solution.</p>
      </div>

      <Card className={styles.formCard}>
        <form onSubmit={handleSubmit} className="flex-col gap-6">
          <div className={styles.formGroup}>
            <label htmlFor="name">Project Name</label>
            <input 
              type="text" 
              id="name" 
              required
              placeholder="e.g. NextJS Marketing Site" 
              className={styles.input}
            />
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="description">Initial Requirements / Prompt</label>
            <textarea 
              id="description" 
              required
              rows={6}
              placeholder="Describe what you want the AI organization to build. Be as specific as possible regarding tech stack, features, and constraints."
              className={styles.textarea}
            />
          </div>

          <div className={styles.formGroup}>
            <label>Select Architect Agent</label>
            <select className={styles.select}>
              <option value="architect_v1">Senior Architect (Default)</option>
              <option value="architect_v2">Principal Engineer (Advanced)</option>
            </select>
          </div>

          <div className="flex justify-end gap-4 mt-4">
            <Button type="button" variant="ghost" onClick={() => router.back()}>Cancel</Button>
            <Button type="submit" isLoading={isSubmitting}>Initialize Organization</Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
