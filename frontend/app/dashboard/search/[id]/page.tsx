"use client";
import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';

export default function JourneyDetailPage() {
  const params = useParams();
  const customerId = params.id as string;
  const [journey, setJourney] = useState<any>(null);
  
  useEffect(() => {
    fetch(`http://localhost:8000/api/v1/journeys/${customerId}`)
      .then(r => r.json())
      .then(setJourney)
      .catch(console.error);
  }, [customerId]);

  if (!journey) return <div className="loading">Loading Journey details...</div>;

  const analytics = journey.analytics || {};
  const metrics = analytics.metrics || {};

  return (
    <div className="dashboard-page journey-detail">
      <div className="detail-header">
        <Link href="/dashboard/search" className="btn-back">← Back to Search</Link>
        <h1>Journey: {customerId}</h1>
      </div>

      <div className="analytics-summary">
        <div className="kpi-card">
          <h3>Health Score</h3>
          <div className="kpi-value">{analytics.customer_health_score}</div>
        </div>
        <div className="kpi-card">
          <h3>Status</h3>
          <div className="kpi-value status">{analytics.journey_status}</div>
        </div>
        <div className="kpi-card">
          <h3>Completion Time</h3>
          <div className="kpi-value">{metrics.journey_duration_minutes || 0} min</div>
        </div>
        <div className="kpi-card">
          <h3>Root Cause</h3>
          <div className="kpi-value root-cause">{analytics.root_cause || "None"}</div>
        </div>
      </div>

      <div className="analytics-text-summary">
        <h3>Journey Summary</h3>
        <p>{analytics.summary}</p>
      </div>

      <div className="timeline-section">
        <h2>Journey Timeline</h2>
        <div className="timeline-container">
          {journey.events.map((event: any, index: number) => (
            <div key={event.event_id} className="timeline-item">
              <div className="timeline-marker"></div>
              <div className="timeline-content">
                <div className="event-time">{new Date(event.timestamp).toLocaleTimeString()}</div>
                <div className="event-source badge">{event.source}</div>
                <div className="event-type">{event.event_type}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
