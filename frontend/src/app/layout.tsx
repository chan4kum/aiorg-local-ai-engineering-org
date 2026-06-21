import type { Metadata } from 'next';
import './globals.css';
import { Sidebar } from '../components/layout/Sidebar';
import { Header } from '../components/layout/Header';

export const metadata: Metadata = {
  title: 'OpenClaw - AI Engineering Platform',
  description: 'Enterprise grade AI engineering organization platform',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <div className="app-container">
          <Sidebar />
          <div className="main-content">
            <Header />
            <main className="scrollable-content animate-fade-in">
              {children}
            </main>
          </div>
        </div>
      </body>
    </html>
  );
}
