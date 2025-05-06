import React, { useState, useEffect } from 'react';
import './Workflows.css';

interface Workflow {
  id: string;
  name: string;
  repository: string;
  status: string;
  last_run: string;
  run_count: number;
}

const Workflows: React.FC = () => {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchWorkflows();
  }, []);

  const fetchWorkflows = async () => {
    setLoading(true);
    
    try {
      const response = await fetch('/api/v1/workflows');
      if (!response.ok) throw new Error('Failed to fetch workflows');
      
      const data = await response.json();
      setWorkflows(data);
      setError(null);
    } catch (err) {
      setError('Failed to load workflows. Please try again later.');
      console.error('Error fetching workflows:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="workflows">
      <div className="workflows-header">
        <h2>GitHub Workflows</h2>
        <button className="btn btn-primary">Sync Workflows</button>
      </div>
      
      <div className="card">
        <div className="card-header">
          Workflow Status
        </div>
        <div className="card-body">
          {loading ? (
            <div className="text-center">Loading workflows...</div>
          ) : error ? (
            <div className="alert alert-danger">{error}</div>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Repository</th>
                  <th>Status</th>
                  <th>Last Run</th>
                  <th>Run Count</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {workflows.length > 0 ? (
                  workflows.map(workflow => (
                    <tr key={workflow.id}>
                      <td>{workflow.name}</td>
                      <td>{workflow.repository}</td>
                      <td>
                        <span className={`status-${workflow.status === 'active' ? 'active' : 'inactive'}`}>
                          {workflow.status === 'active' ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td>{workflow.last_run ? new Date(workflow.last_run).toLocaleString() : 'Never'}</td>
                      <td>{workflow.run_count}</td>
                      <td>
                        <button className="btn btn-sm btn-outline-info">
                          View Runs
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={6} className="text-center">No workflows found</td>
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

export default Workflows;

