"use client";
import { useEffect, useState } from 'react';

export default function OverviewPage() {
  const [data, setData] = useState<any>(null);
  
  useEffect(() => {
    fetch('http://localhost:8000/api/v1/system/overview')
      .then(r => r.json())
      .then(setData)
      .catch(console.error);
  }, []);

  if (!data) return <div className="loading">Loading Overview...</div>;

  return (
    <div className="dashboard-page">
      <header className="page-header">
        <h1>Journey Intelligence Platform</h1>
        <p>High-level summary of platform activity</p>
      </header>
      
      <div className="kpi-grid">
        <div className="kpi-card">
          <h3>Total Customers</h3>
          <div className="kpi-value">{data.total_customers}</div>
        </div>
        <div className="kpi-card">
          <h3>Active Journeys</h3>
          <div className="kpi-value">{data.active_customers}</div>
        </div>
        <div className="kpi-card">
          <h3>Completed Journeys</h3>
          <div className="kpi-value">{data.completed_journeys}</div>
        </div>
        <div className="kpi-card">
          <h3>Events Processed</h3>
          <div className="kpi-value">{data.events_processed}</div>
        </div>
        <div className="kpi-card health-score">
          <h3>Avg Health Score</h3>
          <div className="kpi-value">{data.avg_health_score}</div>
        </div>
      </div>
    </div>
  );
}
