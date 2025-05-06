import React, { useState, useEffect } from 'react';
import { useApi } from '../contexts/ApiContext';

interface Trigger {
  id: string;
  name: string;
  project_id: string;
  enabled: boolean;
  conditions: TriggerCondition[];
  actions: TriggerAction[];
}

interface TriggerCondition {
  event_type: string;
  repository?: string;
  branch?: string;
}

interface TriggerAction {
  action_type: string;
  target: string;
  parameters?: Record<string, any>;
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
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { api } = useApi();

  useEffect(() => {
    fetchTriggers();
  }, []);

  const fetchTriggers = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.get('/api/v1/triggers');
      setTriggers(response.data);
    } catch (err) {
      console.error('Error fetching triggers:', err);
      setError('Failed to fetch triggers');
    } finally {
      setLoading(false);
    }
  };

  const toggleTrigger = async (triggerId: string, currentEnabled: boolean) => {
    try {
      await api.patch(`/api/v1/triggers/${triggerId}`, {
        enabled: !currentEnabled
      });
      
      // Update local state
      setTriggers(prevTriggers => 
        prevTriggers.map(trigger => 
          trigger.id === triggerId 
            ? { ...trigger, enabled: !currentEnabled } 
            : trigger
        )
      );
    } catch (err) {
      console.error('Error toggling trigger:', err);
      alert('Failed to toggle trigger status');
    }
  };

  const handleCreateTrigger = () => {
    alert('Create trigger functionality will be implemented here');
  };

  const handleEditTrigger = (triggerId: string) => {
    alert(`Edit trigger ${triggerId}`);
  };

  return (
    <div className="card">
      <div className="card-header d-flex justify-content-between align-items-center">
        <span>Event Triggers</span>
        <button 
          className="btn btn-primary" 
          onClick={handleCreateTrigger}
        >
          Create Trigger
        </button>
      </div>
      <div className="card-body">
        {error && <div className="alert alert-danger">{error}</div>}
        
        {loading ? (
          <p>Loading triggers...</p>
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
                  // Get the first condition and action for display
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
                          <div className="mt-2">
                            <span className="badge bg-info">
                              +{trigger.actions.length - 1} more action(s)
                            </span>
                          </div>
                        )}
                      </td>
                      <td>
                        <span className={trigger.enabled ? 'status-active' : 'status-inactive'}>
                          {trigger.enabled ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td>
                        <button 
                          className="btn btn-sm btn-outline-primary me-2" 
                          onClick={() => handleEditTrigger(trigger.id)}
                        >
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
                  <td colSpan={6} className="text-center">
                    No triggers found. Click "Create Trigger" to add one.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default EventTriggers;

