import React, { useState, useEffect } from 'react';
import './EventTriggers.css';

interface Trigger {
  id: string;
  name: string;
  project_id: string;
  conditions: {
    event_type: string;
  }[];
  actions: {
    action_type: string;
  }[];
  enabled: boolean;
}

const EVENT_TYPES: Record<string, string> = {
  'push': 'Push',
  'pull_request': 'Pull Request',
  'pull_request_review': 'PR Review',
  'pull_request_review_comment': 'PR Review Comment',
  'issues': 'Issues',
  'issue_comment': 'Issue Comment',
  'create': 'Create',
  'delete': 'Delete',
  'release': 'Release',
  'workflow_run': 'Workflow Run'
};

const ACTION_TYPES: Record<string, string> = {
  'codefile': 'Execute Code File',
  'github_action': 'GitHub Action',
  'github_workflow': 'GitHub Workflow',
  'pr_comment': 'PR Comment'
};

const EventTriggers: React.FC = () => {
  const [triggers, setTriggers] = useState<Trigger[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTriggers();
  }, []);

  const fetchTriggers = async () => {
    setLoading(true);
    
    try {
      const response = await fetch('/api/v1/triggers');
      if (!response.ok) throw new Error('Failed to fetch triggers');
      
      const data = await response.json();
      setTriggers(data);
      setError(null);
    } catch (err) {
      setError('Failed to load triggers. Please try again later.');
      console.error('Error fetching triggers:', err);
    } finally {
      setLoading(false);
    }
  };

  const toggleTrigger = async (triggerId: string, currentState: boolean) => {
    try {
      const response = await fetch(`/api/v1/triggers/${triggerId}/toggle`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ enabled: !currentState })
      });
      
      if (!response.ok) throw new Error('Failed to toggle trigger');
      
      // Update local state
      setTriggers(prevTriggers => 
        prevTriggers.map(trigger => 
          trigger.id === triggerId 
            ? { ...trigger, enabled: !trigger.enabled } 
            : trigger
        )
      );
    } catch (err) {
      console.error('Error toggling trigger:', err);
      alert('Failed to toggle trigger. Please try again.');
    }
  };

  return (
    <div className="event-triggers">
      <div className="triggers-header">
        <h2>Event Triggers</h2>
        <button className="btn btn-primary">Create Trigger</button>
      </div>
      
      <div className="card">
        <div className="card-header">
          Manage Triggers
        </div>
        <div className="card-body">
          {loading ? (
            <div className="text-center">Loading triggers...</div>
          ) : error ? (
            <div className="alert alert-danger">{error}</div>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Project</th>
                  <th>Event Type</th>
                  <th>Action</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {triggers.length > 0 ? (
                  triggers.map(trigger => {
                    const condition = trigger.conditions && trigger.conditions.length > 0 
                      ? trigger.conditions[0] 
                      : null;
                    const action = trigger.actions && trigger.actions.length > 0 
                      ? trigger.actions[0] 
                      : null;
                    
                    return (
                      <tr key={trigger.id}>
                        <td>{trigger.name}</td>
                        <td>{trigger.project_id}</td>
                        <td>
                          {condition 
                            ? EVENT_TYPES[condition.event_type] || condition.event_type 
                            : 'N/A'}
                        </td>
                        <td>
                          {action 
                            ? ACTION_TYPES[action.action_type] || action.action_type 
                            : 'No action'}
                          {trigger.actions && trigger.actions.length > 1 && (
                            <div className="trigger-connection">
                              <span className="connection-dot"></span> 
                              Triggers: {trigger.actions.length - 1} more action(s)
                            </div>
                          )}
                        </td>
                        <td>
                          <span className={trigger.enabled ? 'status-active' : 'status-inactive'}>
                            {trigger.enabled ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                        <td>
                          <button className="btn btn-sm btn-outline-primary mr-2">
                            Edit
                          </button>
                          <button 
                            className={`btn btn-sm btn-outline-${trigger.enabled ? 'danger' : 'success'}`}
                            onClick={() => toggleTrigger(trigger.id, trigger.enabled)}
                          >
                            {trigger.enabled ? 'Disable' : 'Enable'}
                          </button>
                        </td>
                      </tr>
                    );
                  })
                ) : (
                  <tr>
                    <td colSpan={6} className="text-center">No triggers found</td>
                  </tr>
                )}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
};

export default EventTriggers;

