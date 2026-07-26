"use client";
import { useEffect, useState } from 'react';

export default function FeedPage() {
  const [events, setEvents] = useState<any[]>([]);

  useEffect(() => {
    // Poll every 3 seconds for simplicity
    const fetchFeed = () => {
      fetch('http://localhost:8000/api/v1/feed')
        .then(r => r.json())
        .then(data => setEvents(data.events || []))
        .catch(console.error);
    };
    
    fetchFeed();
    const interval = setInterval(fetchFeed, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="dashboard-page feed-page">
      <header className="page-header">
        <h1>Live Event Feed</h1>
        <p>Real-time stream of incoming customer interactions</p>
      </header>

      <div className="feed-container">
        {events.map((event: any, idx: number) => (
          <div key={event._id || idx} className="feed-item">
            <div className="feed-time">
              {new Date(event.timestamp).toLocaleTimeString()}
            </div>
            <div className="feed-source badge">{event.source}</div>
            <div className="feed-details">
              <strong>{event.event_type}</strong>
              <div className="feed-meta">
                ID: {event.event_id}
              </div>
            </div>
          </div>
        ))}
        {events.length === 0 && <div className="empty-state">Waiting for events...</div>}
      </div>
    </div>
  );
}
