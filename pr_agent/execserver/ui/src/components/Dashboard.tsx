import React, { useState, useEffect } from 'react'
import './Dashboard.css'

interface TabData {
  id: string
  label: string
  content: React.ReactNode
}

const Dashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview')
  const [unreadCount, setUnreadCount] = useState(0)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    // Load the active tab from localStorage if available
    const savedTab = localStorage.getItem('activeTab')
    if (savedTab) {
      setActiveTab(savedTab)
    }

    // Simulate unread notifications
    setUnreadCount(3)
  }, [])

  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId)
    localStorage.setItem('activeTab', tabId)
  }

  const handleRefresh = () => {
    setIsLoading(true)
    // Simulate data refresh
    setTimeout(() => {
      setIsLoading(false)
    }, 1000)
  }

  const handleMarkAllRead = () => {
    setUnreadCount(0)
  }

  const tabs: TabData[] = [
    {
      id: 'overview',
      label: 'Overview',
      content: (
        <div className="tab-content">
          <h2>Dashboard Overview</h2>
          <div className="stats-container">
            <div className="stat-card">
              <h3>Open PRs</h3>
              <p className="stat-value">12</p>
            </div>
            <div className="stat-card">
              <h3>Pending Reviews</h3>
              <p className="stat-value">5</p>
            </div>
            <div className="stat-card">
              <h3>Completed Today</h3>
              <p className="stat-value">7</p>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'prs',
      label: 'Pull Requests',
      content: (
        <div className="tab-content">
          <h2>Pull Requests</h2>
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>PR #</th>
                  <th>Title</th>
                  <th>Author</th>
                  <th>Status</th>
                  <th>Updated</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>#123</td>
                  <td>Implement user authentication</td>
                  <td>johndoe</td>
                  <td>Open</td>
                  <td>2 hours ago</td>
                </tr>
                <tr>
                  <td>#122</td>
                  <td>Fix navigation bug</td>
                  <td>janedoe</td>
                  <td>Merged</td>
                  <td>5 hours ago</td>
                </tr>
                <tr>
                  <td>#121</td>
                  <td>Update documentation</td>
                  <td>bobsmith</td>
                  <td>Closed</td>
                  <td>1 day ago</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )
    },
    {
      id: 'reviews',
      label: 'Reviews',
      content: (
        <div className="tab-content">
          <h2>Review Activity</h2>
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>PR #</th>
                  <th>Reviewer</th>
                  <th>Status</th>
                  <th>Comments</th>
                  <th>Submitted</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>#123</td>
                  <td>AI Assistant</td>
                  <td>Approved</td>
                  <td>2</td>
                  <td>1 hour ago</td>
                </tr>
                <tr>
                  <td>#122</td>
                  <td>AI Assistant</td>
                  <td>Changes Requested</td>
                  <td>5</td>
                  <td>3 hours ago</td>
                </tr>
                <tr>
                  <td>#120</td>
                  <td>AI Assistant</td>
                  <td>Approved</td>
                  <td>0</td>
                  <td>2 days ago</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )
    },
    {
      id: 'settings',
      label: 'Settings',
      content: (
        <div className="tab-content">
          <h2>Dashboard Settings</h2>
          <div className="settings-container">
            <div className="settings-group">
              <h3>Notification Settings</h3>
              <div className="setting-item">
                <label>
                  <input type="checkbox" defaultChecked /> Email notifications
                </label>
              </div>
              <div className="setting-item">
                <label>
                  <input type="checkbox" defaultChecked /> Browser notifications
                </label>
              </div>
            </div>
            <div className="settings-group">
              <h3>Display Settings</h3>
              <div className="setting-item">
                <label>
                  <input type="checkbox" defaultChecked /> Show closed PRs
                </label>
              </div>
              <div className="setting-item">
                <label>
                  <input type="checkbox" defaultChecked /> Auto-refresh (every 5 minutes)
                </label>
              </div>
            </div>
          </div>
        </div>
      )
    }
  ]

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div className="tabs">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              className={`tab ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => handleTabChange(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>
        <div className="dashboard-actions">
          <button className="refresh-button" onClick={handleRefresh} disabled={isLoading}>
            {isLoading ? 'Refreshing...' : 'Refresh'}
          </button>
          <div className="notification-badge" onClick={handleMarkAllRead}>
            <span className="icon">🔔</span>
            {unreadCount > 0 && <span className="badge">{unreadCount}</span>}
          </div>
        </div>
      </div>
      <div className="dashboard-content">
        {tabs.find(tab => tab.id === activeTab)?.content}
      </div>
    </div>
  )
}

export default Dashboard

