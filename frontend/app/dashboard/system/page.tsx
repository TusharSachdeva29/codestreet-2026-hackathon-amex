"use client";
import { useEffect, useState } from 'react';

export default function SystemStatusPage() {
  const [status, setStatus] = useState<any>(null);

  useEffect(() => {
    fetch('http://localhost:8000/api/v1/system/status')
      .then(r => r.json())
      .then(setStatus)
      .catch(console.error);
  }, []);

  if (!status) return <div className="loading">Checking system status...</div>;

  return (
    <div className="dashboard-page">
      <header className="page-header">
        <h1>System Status</h1>
        <p>Operational visibility into the platform</p>
      </header>
      
      <div className="kpi-grid">
        <div className="kpi-card">
          <h3>Overall Status</h3>
          <div className="kpi-value status-healthy">{status.status}</div>
        </div>
        <div className="kpi-card">
          <h3>Kafka Cluster</h3>
          <div className="kpi-value status-online">{status.kafka}</div>
        </div>
        <div className="kpi-card">
          <h3>MongoDB (raw_events)</h3>
          <div className={`kpi-value ${status.database === 'Online' ? 'status-online' : 'status-offline'}`}>
            {status.database}
          </div>
        </div>
        <div className="kpi-card">
          <h3>System Uptime</h3>
          <div className="kpi-value">{status.uptime}</div>
        </div>
      </div>
    </div>
  );
}
