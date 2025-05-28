import React, { useState, useEffect } from 'react';
import { useApi } from '../contexts/ApiContext';
import { format } from 'date-fns';
import { Link } from 'react-router-dom';

interface Event {
  id: string;
  event_type: string;
  repository: string;
  created_at: string;
  processed: boolean;
}

const Dashboard: React.FC = () => {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
  const { api } = useApi();

  useEffect(() => {
    fetchEvents();
    
    // Set up auto-refresh
    const interval = setInterval(() => {
      if (document.visibilityState === 'visible') {
        fetchEvents(true);
      }
    }, 30000); // 30 seconds
    
    return () => clearInterval(interval);
  }, []);

  const fetchEvents = async (silent = false) => {
    if (!silent) setLoading(true);
    setError(null);
    
    try {
      const response = await api.get('/api/v1/events?limit=10');
      setEvents(response.data);
      setLastUpdated(new Date());
    } catch (err) {
      console.error('Error fetching events:', err);
      if (!silent) setError('Failed to fetch events');
    } finally {
      if (!silent) setLoading(false);
    }
  };

  const handleRefresh = () => {
    fetchEvents();
  };

  return (
    <div>
      <div className="row">
        <div className="col-md-6">
          <div className="card">
            <div className="card-header">
              Active Triggers
            </div>
            <div className="card-body">
              <p className="card-text">You have <strong>{5}</strong> active triggers configured.</p>
              <Link to="/triggers" className="btn btn-primary">Manage Triggers</Link>
            </div>
          </div>
        </div>
        <div className="col-md-6">
          <div className="card">
            <div className="card-header">
              System Status
            </div>
            <div className="card-body">
              <p className="card-text"><span className="status-active">●</span> All systems operational</p>
              <p className="card-text">Last updated: {format(lastUpdated, 'yyyy-MM-dd HH:mm:ss')}</p>
            </div>
          </div>
        </div>
      </div>
      
      <div className="row mt-4">
        <div className="col-md-12">
          <div className="card">
            <div className="card-header d-flex justify-content-between">
              <span>Recent Events</span>
              <button 
                className="btn btn-sm btn-outline-secondary" 
                onClick={handleRefresh}
                disabled={loading}
              >
                {loading ? 'Loading...' : 'Refresh'}
              </button>
            </div>
            <div className="card-body">
              {error && <div className="alert alert-danger">{error}</div>}
              
              <div className="event-list">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Event Type</th>
                      <th>Repository</th>
                      <th>Timestamp</th>
                      <th>Processed</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {events.length > 0 ? (
                      events.map(event => (
                        <tr key={event.id}>
                          <td>{event.event_type}</td>
                          <td>{event.repository}</td>
                          <td>{format(new Date(event.created_at), 'yyyy-MM-dd HH:mm:ss')}</td>
                          <td>
                            <span className={event.processed ? 'status-active' : 'status-inactive'}>
                              {event.processed ? 'Yes' : 'No'}
                            </span>
                          </td>
                          <td>
                            <button 
                              className="btn btn-sm btn-outline-info"
                              onClick={() => alert(`View details for event ${event.id}`)}
                            >
                              View Details
                            </button>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={5} className="text-center">
                          {loading ? 'Loading events...' : 'No events found'}
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

