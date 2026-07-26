"use client";
import { useEffect, useState } from 'react';
import Link from 'next/link';

export default function CustomerSearchPage() {
  const [journeys, setJourneys] = useState<any[]>([]);
  const [search, setSearch] = useState("");

  useEffect(() => {
    fetch('http://localhost:8000/api/v1/journeys')
      .then(r => r.json())
      .then(setJourneys)
      .catch(console.error);
  }, []);

  const filtered = journeys.filter(j => 
    j.customer_id.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="dashboard-page">
      <header className="page-header">
        <h1>Customer Search</h1>
        <p>Search by Customer ID to view journey timeline and analytics</p>
      </header>
      
      <div className="search-bar">
        <input 
          type="text" 
          placeholder="Search Customer ID..." 
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
      </div>

      <div className="results-table-wrapper">
        <table className="results-table">
          <thead>
            <tr>
              <th>Customer ID</th>
              <th>Status</th>
              <th>Health Score</th>
              <th>Events</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(j => (
              <tr key={j.customer_id}>
                <td>{j.customer_id}</td>
                <td><span className={`status-badge ${j.status.toLowerCase()}`}>{j.status}</span></td>
                <td>{j.health_score} / 100</td>
                <td>{j.total_events}</td>
                <td>
                  <Link href={`/dashboard/search/${j.customer_id}`} className="btn-view">
                    View Journey
                  </Link>
                </td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr>
                <td colSpan={5} className="empty-state">No customers found.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
