import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const Dashboard = ({ unreadCount, showNotifications, toggleNotifications }) => {
  const [goals, setGoals] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [notifications, setNotifications] = useState([
    { id: 1, message: 'New goal created: Learn React', created_at: '2025-10-17T10:00:00Z', is_read: false },
    { id: 2, message: 'Task due today: SQL JOINs', created_at: '2025-10-17T12:00:00Z', is_read: true },
    { id: 3, message: 'Progress updated: 35%', created_at: '2025-10-17T14:00:00Z', is_read: false },
  ]);

  // **REAL GOALS FETCH FROM BACKEND**
  useEffect(() => {
    const fetchRealGoals = async () => {
      setLoading(true);
      try {
        const token = localStorage.getItem('token');
        const response = await fetch(`http://127.0.0.1:8000/goals/?user_id=${token}`);
        
        if (response.ok) {
          const realGoals = await response.json();
          setGoals(realGoals.map(goal => ({
            id: goal.id,
            title: goal.title,
            description: goal.description,
            progress_percentage: goal.progress * 100 || 0,
            duration_days: goal.duration_days,
            status: goal.completed ? 'completed' : 'active',
            category: 'AI Generated',
            weekly_schedule: goal.weekly_schedule,
            resources: goal.resources,
            milestones: goal.milestones
          })));
        }
      } catch (error) {
        console.error('Error fetching goals:', error);
        // Fallback to demo data if API fails
        setGoals([
          {
            id: 1,
            title: 'Learn React Fundamentals',
            description: 'Master React components, hooks, and state management',
            progress_percentage: 35,
            duration_days: 60,
            status: 'active',
            category: 'Programming',
          }
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchRealGoals();
  }, []);

  const markNotificationAsRead = (id) => {
    setNotifications(notifications.map(notif =>
      notif.id === id ? { ...notif, is_read: true } : notif
    ));
  };

  useEffect(() => {
    setTimeout(() => {
      setTasks([
        {
          id: 1,
          title: 'Learn React Conditional Rendering',
          dueDate: 'Today',
          completed: false,
          priority: 'high',
        },
        {
          id: 2,
          title: 'Practice SQL JOINs and Indexes',
          dueDate: 'Tomorrow',
          completed: false,
          priority: 'medium',
        },
      ]);
    }, 1000);
  }, []);

  const canCompleteTask = (taskId) => {
    const dependencies = {
      2: [1],
    }[taskId] || [];
    const incompleteDependencies = dependencies.filter(depId => {
      const depTask = tasks.find(t => t.id === depId);
      return depTask && !depTask.completed;
    });
    return incompleteDependencies.length === 0;
  };

  const handleTaskToggle = (taskId) => {
    const task = tasks.find(t => t.id === taskId);
    if (!task.completed && !canCompleteTask(taskId)) {
      const dependencies = { 2: [1] }[taskId] || [];
      const depNames = dependencies.map(depId => {
        const dep = tasks.find(t => t.id === depId);
        return dep ? dep.title : `Task ${depId}`;
      });
      alert(`❌ Complete these tasks first: ${depNames.join(', ')}`);
      return;
    }
    setTasks(tasks.map(task =>
      task.id === taskId ? { ...task, completed: !task.completed } : task
    ));
  };

  const handleAIQuestion = (question) => {
    console.log(`AI Question: ${question}`);
    alert(`AI Assistant: I'll help you with "${question}"`);
  };

  if (loading) return <div className="loading">Loading your AI learning dashboard...</div>;

  return (
    <div className="dashboard">
      <div className="page-header">
        <h1>🎯 Goal Pilot AI</h1>
        <p>Your personalized learning journey powered by AI</p>
      </div>

      {showNotifications && (
        <div className="notifications-section">
          <div className="notification-dropdown">
            <ul>
              {notifications.map((notif) => (
                <li
                  key={notif.id}
                  className={notif.is_read ? '' : 'unread'}
                  onClick={() => markNotificationAsRead(notif.id)}
                >
                  {notif.message} ({new Date(notif.created_at).toLocaleDateString()})
                </li>
              ))}
            </ul>
            <a href="/notifications" className="view-all">View All</a>
          </div>
        </div>
      )}

      <div className="dashboard-grid-enhanced">
        <div className="welcome-card glass-card">
          <div className="welcome-content">
            <h2>👋 Welcome back!</h2>
            <p>Ready to continue your learning journey?</p>
            <div className="streak-counter">
              <span className="streak-number">5</span>
              <span className="streak-label">day streak! 🔥</span>
            </div>
          </div>
        </div>

        <div className="progress-overview glass-card">
          <h3>📊 Program Overview</h3>
          <div className="progress-stats-enhanced">
            <div className="stat-card-enhanced">
              <div className="stat-icon">🎯</div>
              <div className="stat-info">
                <h4>Active Goals</h4>
                <p className="stat-number">{goals.length}</p>
              </div>
            </div>
            <div className="stat-card-enhanced">
              <div className="stat-icon">💻</div>
              <div className="stat-info">
                <h4>Weekly Progress</h4>
                <p className="stat-number">89%</p>
              </div>
            </div>
            <div className="stat-card-enhanced">
              <div className="stat-icon">⏱️</div>
              <div className="stat-info">
                <h4>Study Time</h4>
                <p className="stat-number">24h</p>
              </div>
            </div>
          </div>
        </div>

        <div className="ai-assistant-card glass-card">
          <h3>🤖 AI Assistant</h3>
          <p>Need help with your goals? Ask me anything!</p>
          <div className="ai-quick-questions">
            <button className="ai-question-btn" onClick={() => handleAIQuestion('learning resources')}>
              Find learning resources
            </button>
            <button className="ai-question-btn" onClick={() => handleAIQuestion('daily routines')}>
              Suggest study routines
            </button>
          </div>
        </div>

        <div className="goals-section glass-card">
          <div className="section-header">
            <h3>🎯 Your Learning Goals</h3>
            <Link to="/create-goal" className="btn-primary btn-sm">+ New Goal</Link>
          </div>
          <div className="goals-grid">
            {goals.map(goal => (
              <div key={goal.id} className="goal-card-enhanced">
                <div className="goal-header">
                  <h4>{goal.title}</h4>
                  <span className="goal-category">{goal.category}</span>
                </div>
                <p className="goal-description">{goal.description}</p>
                <div className="goal-progress-enhanced">
                  <div className="progress-info">
                    <span>Progress</span>
                    <span>{goal.progress_percentage}%</span>
                  </div>
                  <div className="progress-bar-enhanced">
                    <div
                      className="progress-fill-enhanced"
                      style={{ width: `${goal.progress_percentage}%` }}
                    ></div>
                  </div>
                </div>
                <div className="goal-footer">
                  <div className="goal-meta">
                    <span>📅 {goal.duration_days} days</span>
                    <span>🟢 {goal.status}</span>
                  </div>
                  <button className="btn-outline btn-sm">Continue Learning</button>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="tasks-section glass-card">
          <div className="section-header">
            <h3>📅 Upcoming Tasks</h3>
            <span className="tasks-count">{tasks.filter(t => !t.completed).length} pending</span>
          </div>
          <div className="tasks-list">
            {tasks.map(task => (
              <div key={task.id} className="task-item">
                <div className="task-checkbox">
                  <input
                    type="checkbox"
                    checked={task.completed}
                    onChange={() => handleTaskToggle(task.id)}
                  />
                </div>
                <div className="task-content">
                  <h4 className={task.completed ? 'completed' : ''}>{task.title}</h4>
                  <p>Due: {task.dueDate}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;