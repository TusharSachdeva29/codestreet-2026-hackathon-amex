import './dashboard.css';
import Link from 'next/link';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="dashboard-container">
      <nav className="dashboard-sidebar">
        <div className="sidebar-brand">
          <h2>AMEX Journey</h2>
        </div>
        <ul className="sidebar-nav">
          <li><Link href="/dashboard">Overview</Link></li>
          <li><Link href="/dashboard/search">Customer Search</Link></li>
          <li><Link href="/dashboard/graph">Identity Graph</Link></li>
          <li><Link href="/dashboard/feed">Live Event Feed</Link></li>
          <li><Link href="/dashboard/system">System Status</Link></li>
        </ul>
      </nav>
      <main className="dashboard-main">
        {children}
      </main>
    </div>
  );
}
