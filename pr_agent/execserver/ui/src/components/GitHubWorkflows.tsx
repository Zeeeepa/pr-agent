import React, { useState, useEffect } from 'react';
import { useApi } from '../contexts/ApiContext';
import { format } from 'date-fns';

interface Workflow {
  id: number;
  name: string;
  path: string;
  state: string;
  created_at: string;
  updated_at: string;
}

interface WorkflowRun {
  id: number;
  name: string;
  workflow_id: number;
  conclusion: string | null;
  status: string;
  created_at: string;
  updated_at: string;
  head_branch: string;
}

interface Repository {
  id: string;
  name: string;
  full_name: string;
}

const GitHubWorkflows: React.FC = () => {
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [selectedRepo, setSelectedRepo] = useState<string>('');
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [workflowRuns, setWorkflowRuns] = useState<WorkflowRun[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { api } = useApi();

  useEffect(() => {
    fetchRepositories();
  }, []);

  useEffect(() => {
    if (selectedRepo) {
      fetchWorkflows(selectedRepo);
      fetchWorkflowRuns(selectedRepo);
    }
  }, [selectedRepo]);

  const fetchRepositories = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.get('/api/v1/projects/github');
      setRepositories(response.data);
      
      // Select the first repository by default
      if (response.data.length > 0) {
        setSelectedRepo(response.data[0].full_name);
      }
    } catch (err) {
      console.error('Error fetching repositories:', err);
      setError('Failed to fetch repositories. Make sure your GitHub token is configured correctly.');
    } finally {
      setLoading(false);
    }
  };

  const fetchWorkflows = async (repository: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.get(`/api/v1/workflows?repository=${repository}`);
      setWorkflows(response.data);
    } catch (err) {
      console.error('Error fetching workflows:', err);
      setError('Failed to fetch workflows');
    } finally {
      setLoading(false);
    }
  };

  const fetchWorkflowRuns = async (repository: string) => {
    setLoading(true);
    
    try {
      const response = await api.get(`/api/v1/workflow_runs?repository=${repository}&limit=10`);
      setWorkflowRuns(response.data);
    } catch (err) {
      console.error('Error fetching workflow runs:', err);
      // Don't set error here to avoid overriding workflow fetch errors
    } finally {
      setLoading(false);
    }
  };

  const handleRepositoryChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedRepo(e.target.value);
  };

  const triggerWorkflow = async (workflowId: number) => {
    if (!selectedRepo) return;
    
    try {
      await api.post(`/api/v1/workflows/${workflowId}/dispatch`, {
        repository: selectedRepo,
        ref: 'main' // Default to main branch
      });
      
      alert('Workflow triggered successfully');
      
      // Refresh workflow runs after a short delay
      setTimeout(() => {
        fetchWorkflowRuns(selectedRepo);
      }, 2000);
    } catch (err) {
      console.error('Error triggering workflow:', err);
      alert('Failed to trigger workflow');
    }
  };

  const getStatusBadgeClass = (status: string, conclusion: string | null) => {
    if (status === 'completed') {
      if (conclusion === 'success') return 'bg-success';
      if (conclusion === 'failure') return 'bg-danger';
      if (conclusion === 'cancelled') return 'bg-secondary';
      return 'bg-warning';
    }
    
    if (status === 'in_progress') return 'bg-info';
    if (status === 'queued') return 'bg-secondary';
    
    return 'bg-secondary';
  };

  return (
    <div>
      <div className="card mb-4">
        <div className="card-header">GitHub Workflows</div>
        <div className="card-body">
          {error && <div className="alert alert-danger">{error}</div>}
          
          <div className="mb-3">
            <label htmlFor="repository-select" className="form-label">Select Repository:</label>
            <select 
              id="repository-select" 
              className="form-select" 
              value={selectedRepo} 
              onChange={handleRepositoryChange}
              disabled={loading || repositories.length === 0}
            >
              {repositories.length === 0 && (
                <option value="">No repositories available</option>
              )}
              {repositories.map(repo => (
                <option key={repo.id} value={repo.full_name}>
                  {repo.full_name}
                </option>
              ))}
            </select>
          </div>
          
          {loading ? (
            <p>Loading workflows...</p>
          ) : (
            <>
              <h5>Available Workflows</h5>
              {workflows.length > 0 ? (
                <table className="table">
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Path</th>
                      <th>State</th>
                      <th>Updated</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {workflows.map(workflow => (
                      <tr key={workflow.id}>
                        <td>{workflow.name}</td>
                        <td>{workflow.path}</td>
                        <td>
                          <span className={`badge ${workflow.state === 'active' ? 'bg-success' : 'bg-secondary'}`}>
                            {workflow.state}
                          </span>
                        </td>
                        <td>{format(new Date(workflow.updated_at), 'yyyy-MM-dd HH:mm')}</td>
                        <td>
                          <button 
                            className="btn btn-sm btn-primary"
                            onClick={() => triggerWorkflow(workflow.id)}
                            disabled={workflow.state !== 'active'}
                          >
                            Run Workflow
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <p>No workflows found for this repository.</p>
              )}
              
              <h5 className="mt-4">Recent Workflow Runs</h5>
              {workflowRuns.length > 0 ? (
                <table className="table">
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Branch</th>
                      <th>Status</th>
                      <th>Created</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {workflowRuns.map(run => (
                      <tr key={run.id}>
                        <td>{run.name}</td>
                        <td>{run.head_branch}</td>
                        <td>
                          <span className={`badge ${getStatusBadgeClass(run.status, run.conclusion)}`}>
                            {run.status === 'completed' 
                              ? (run.conclusion || 'unknown') 
                              : run.status}
                          </span>
                        </td>
                        <td>{format(new Date(run.created_at), 'yyyy-MM-dd HH:mm')}</td>
                        <td>
                          <button 
                            className="btn btn-sm btn-outline-info"
                            onClick={() => alert(`View logs for run ${run.id}`)}
                          >
                            View Logs
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <p>No recent workflow runs found.</p>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default GitHubWorkflows;

