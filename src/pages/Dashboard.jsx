import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const Dashboard = () => {
  const [goals, setGoals] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // REMOVED: validateProgress function (not used)
  // REMOVED: taskDependencies state (not used)
  
  const canCompleteTask = (taskId) => {
    // Hardcoded dependencies since we removed taskDependencies state
    const dependencies = {
      2: [1], // Task 2 depends on Task 1
      3: [1, 2] // Task 3 depends on Task 1 and 2
    }[taskId] || [];
    
    const incompleteDependencies = dependencies.filter(depId => {
      const depTask = tasks.find(t => t.id === depId);
      return depTask && !depTask.completed;
    });
    
    return incompleteDependencies.length === 0;
  };

  // Mock data for demonstration
  useEffect(() => {
    setTimeout(() => {
      setGoals([
        {
          id: 1,
          title: 'Learn React Fundamentals',
          description: 'Master React components, hooks, and state management',
          progress_percentage: 35,
          duration_days: 60,
          status: 'active',
          category: 'Programming'
        },
        {
          id: 2,
          title: 'Master SQL Database',
          description: 'Learn advanced SQL queries and database design',
          progress_percentage: 15,
          duration_days: 45,
          status: 'active',
          category: 'Database'
        },
        {
          id: 3,
          title: 'Python for Data Science',
          description: 'Learn data analysis with Pandas and visualization',
          progress_percentage: 5,
          duration_days: 90,
          status: 'active',
          category: 'Data Science'
        }
      ]);

      setTasks([
        {
          id: 1,
          title: 'Learn React Conditional Rendering',
          dueDate: 'Today',
          completed: false,
          priority: 'high'
        },
        {
          id: 2,
          title: 'Practice SQL JOINs and Indexes',
          dueDate: 'Tomorrow',
          completed: false,
          priority: 'medium'
        },
        {
          id: 3,
          title: 'Complete Pandas Data Analysis Project',
          dueDate: 'In 2 days',
          completed: false,
          priority: 'medium'
        }
      ]);

      setLoading(false);
    }, 1000);
  }, []);

  const handleTaskToggle = (taskId) => {
    const task = tasks.find(t => t.id === taskId);
    
    // validation
    if (!task.completed && !canCompleteTask(taskId)) {
      const dependencies = {
        2: [1],
        3: [1, 2]
      }[taskId] || [];
      
      const depNames = dependencies.map(depId => {
        const dep = tasks.find(t => t.id === depId);
        return dep ? dep.title : `Task ${depId}`;
      });
      
      alert(`❌ Complete these tasks first: ${depNames.join(', ')}`);
      return;
    }
    
    setTasks(tasks.map(task => 
      task.id === taskId 
        ? { ...task, completed: !task.completed }
        : task
    ));
  };

  const handleAIQuestion = (question) => {
    // Add AI assistant functionality here
    console.log(`AI Question: ${question}`);
    // You can integrate with your AI API here
    alert(`AI Assistant: I'll help you with "${question}"`);
  };

  if (loading) return <div className="loading">Loading your AI learning dashboard...</div>;

  return (
    <div className="dashboard">
      <div className="page-header">
        <h1>🎯 Goal Pilot AI</h1>
        <p>Your personalized learning journey powered by AI</p>
      </div>

      <div className="dashboard-grid-enhanced">
        {/* Welcome Card */}
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

        {/* Progress Overview */}
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

        {/* AI Assistant Card */}
        <div className="ai-assistant-card glass-card">
          <h3>🤖 AI Assistant</h3>
          <p>Need help with your goals? Ask me anything!</p>
          <div className="ai-quick-questions">
            <button 
              className="ai-question-btn"
              onClick={() => handleAIQuestion('team collaboration features')}
            >
              Team collaboration features
            </button>
            <button 
              className="ai-question-btn"
              onClick={() => handleAIQuestion('learning resources')}
            >
              Find learning resources
            </button>
            <button 
              className="ai-question-btn"
              onClick={() => handleAIQuestion('share progress')}
            >
              Share progress with team
            </button>
            <button 
              className="ai-question-btn"
              onClick={() => handleAIQuestion('daily routines')}
            >
              Suggest study routines
            </button>
          </div>
        </div>

        {/* Goals Section */}
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
                      style={{width: `${goal.progress_percentage}%`}}
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

        {/* Tasks Section */}
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
          <div className="form-actions" style={{marginTop: '1rem', justifyContent: 'flex-start'}}>
            <button className="btn-outline btn-sm">View All Tasks</button>
          </div>
        </div>

        {/* Quick Actions Panel */}
        <div className="ai-assistant-card glass-card" style={{gridArea: 'assistant'}}>
          <h3>⚡ Quick Actions</h3>
          <div className="ai-quick-questions">
            <button className="ai-question-btn">
              <span>📚</span> Add Resource
            </button>
            <button className="ai-question-btn">
              <span>🔄</span> Update Progress
            </button>
            <button className="ai-question-btn">
              <span>📊</span> Generate Report
            </button>
            <button className="ai-question-btn">
              <span>👥</span> Invite Team
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;