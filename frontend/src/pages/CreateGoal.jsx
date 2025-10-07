import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const CreateGoal = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  
  // REMOVED: setExistingGoals state setter (not used)
  const existingGoals = [
    'Learn React Fundamentals',
    'Master SQL Database', 
    'Python for Data Science'
  ];
  
  const validateResourceUrl = (url) => {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  };
 
  const [formData, setFormData] = useState({
    // Step 1: Goal Details
    title: "",
    description: "",

    // Step 2: Plan
    duration_days: "30",
    custom_days: "",
    start_date: "",
    end_date: "",
    difficulty: "beginner",
    study_schedule: "flexible",
    weekly_hours: "5",
    learning_style: "visual",

    // Step 3: Review
    resources: [],
    milestones: [],
  });
  const [loading, setLoading] = useState(false);
  const [aiPlan, setAiPlan] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await new Promise((resolve) => setTimeout(resolve, 2000));

      const finalData = {
        ...formData,
        duration_days:
          formData.duration_days === "custom"
            ? parseInt(formData.custom_days) || 30
            : parseInt(formData.duration_days),
      };

      console.log("Goal created:", finalData);
      navigate("/dashboard");
    } catch (error) {
      console.error("Error creating goal:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const generateAIPlan = async () => {
    setLoading(true);
    try {
      await new Promise((resolve) => setTimeout(resolve, 1500));
  
      const generatedPlan = {
        weekly_schedule: [
          {
            day: "Monday",
            topics: ["React Components", "JSX Syntax"],
            duration: "2h",
          },
          {
            day: "Wednesday",
            topics: ["State Management", "Hooks"],
            duration: "2h",
          },
          {
            day: "Saturday",
            topics: ["Project Practice", "Review"],
            duration: "3h",
          },
        ],
        resources: [
          {
            type: "Course",
            title: "React Official Tutorial",
            duration: "4 hours",
            url: "https://reactjs.org/tutorial/tutorial.html"
          },
          {
            type: "Video",
            title: "React Hooks Deep Dive", 
            duration: "2 hours",
            url: "invalid-url"
          },
          { 
            type: "Project", 
            title: "Build Todo App", 
            duration: "3 hours",
            url: "https://example.com/todo-app"
          },
        ],
        milestones: [
          { week: 1, goal: "Understand React Basics", completed: false },
          { week: 2, goal: "Build First Component", completed: false },
          { week: 3, goal: "Master State Management", completed: false },
          { week: 4, goal: "Complete Final Project", completed: false },
        ],
      };
  
      // URL VALIDATION
      generatedPlan.resources = generatedPlan.resources.map(resource => ({
        ...resource,
        valid: validateResourceUrl(resource.url)
      }));
  
      setAiPlan(generatedPlan);
      setFormData((prev) => ({
        ...prev,
        resources: generatedPlan.resources,
        milestones: generatedPlan.milestones,
      }));
    } catch (error) {
      console.error("Error generating AI plan:", error);
    } finally {
      setLoading(false);
    }
  };

  const nextStep = () => {
    if (currentStep === 1 && formData.title && formData.description) {
      setCurrentStep(2);
      generateAIPlan();
    } else if (currentStep === 2) {
      setCurrentStep(3);
    }
  };

  const prevStep = () => {
    setCurrentStep(currentStep - 1);
  };

  const StepIndicator = () => (
    <div className="form-steps">
      <span className={`step ${currentStep === 1 ? "active" : ""}`}>
        1. Goal
      </span>
      <span className={`step ${currentStep === 2 ? "active" : ""}`}>
        2. Plan
      </span>
      <span className={`step ${currentStep === 3 ? "active" : ""}`}>
        3. Review
      </span>
    </div>
  );

  // Step 1: Goal Details Page
  const renderStep1 = () => (
    <div className="step-page">
      <div className="step-header">
        <h2>🎯 Define Your Goal</h2>
        <p>Tell us what you want to learn and achieve</p>
      </div>

      <div className="form-group-enhanced">
        <label className="form-label-main">
          What do you want to learn? <span style={{color: 'red'}}>*</span>
          <span style={{fontSize: '0.8rem', color: '#666', marginLeft: '10px', fontWeight: 'normal'}}>
            ({formData.title.length}/100)
          </span>
        </label>
        <input
          type="text"
          placeholder="e.g., Master React.js, Learn Python for Data Science, Build a Mobile App..."
          value={formData.title}
          onChange={handleChange}
          name="title"
          required
          className="form-input-large"
          maxLength="100"
        />

        {formData.title.length > 80 && (
          <div className="warning-message">
            ⚠️ {100 - formData.title.length} characters remaining
          </div>
        )}
      </div>

      {existingGoals.some(goal => 
        goal.toLowerCase() === formData.title.toLowerCase().trim()
      ) && formData.title.length > 0 && (
        <div className="error-message">
          ❌ You already have a goal with this title. Please choose a different one.
        </div>
      )}

      <div className="form-group-enhanced">
        <label className="form-label-main">
          Describe your goal <span style={{color: 'red'}}>*</span>
          <span style={{fontSize: '0.8rem', color: '#666', marginLeft: '10px', fontWeight: 'normal'}}>
            ({formData.description.length}/500)
          </span>
        </label>
        <textarea
          placeholder="Tell us more about what you want to achieve, why it's important to you, and any specific areas you want to focus on..."
          rows="6"
          value={formData.description}
          onChange={handleChange}
          name="description"
          className="form-textarea"
          maxLength="500"
        />
        {formData.description.length > 450 && (
          <div className="warning-message">
            ⚠️ {500 - formData.description.length} characters remaining
          </div>
        )}
        <p className="input-hint">
          The more details you provide, the better we can personalize your learning path
        </p>
      </div>

      <div className="form-actions">
        <button
          type="button"
          className="btn-secondary"
          onClick={() => navigate("/dashboard")}
        >
          Cancel
        </button>
        <button
          type="button"
          className="btn-primary btn-large"
          onClick={nextStep}
          disabled={!formData.title || !formData.description}
        >
          Continue to Planning →
        </button>
      </div>
    </div>
  );

  // Step 2: Plan Page with Timeline & Schedule
  const renderStep2 = () => (
    <div className="step-page">
      <div className="step-header">
        <h2>📅 Create Your Plan</h2>
        <p>Set up your timeline and learning preferences</p>
      </div>

      {loading && !aiPlan ? (
        <div className="loading">
          🤖 AI is generating your personalized learning plan...
        </div>
      ) : (
        <>
          {/* Timeline & Difficulty Section */}
          <div className="form-section-enhanced glass-card">
            <div className="section-header-enhanced">
              <h3 className="section-title">Timeline & Difficulty</h3>
              <p>Set how long you want to learn and the challenge level</p>
            </div>

            <div className="timeline-schedule-grid">
              <div className="timeline-section">
                <h4>📅 Timeline</h4>
                <div className="timeline-options">
                  <select
                    name="duration_days"
                    value={formData.duration_days}
                    onChange={handleChange}
                    className="form-select"
                  >
                    <option value="7">1 Week</option>
                    <option value="14">2 Weeks</option>
                    <option value="30">1 Month</option>
                    <option value="60">2 Months</option>
                    <option value="90">3 Months</option>
                    <option value="custom">Custom duration...</option>
                  </select>
                  {formData.duration_days === "custom" && (
                    <div className="custom-input-wrapper">
                      <input
                        type="number"
                        name="custom_days"
                        value={formData.custom_days}
                        onChange={handleChange}
                        placeholder="Enter number of days"
                        min="1"
                        max="365"
                        className="custom-days-input"
                      />
                      <span className="custom-days-label">days</span>
                    </div>
                  )}
                </div>
              </div>

              <div className="difficulty-section">
                <h4>🎯 Difficulty Level</h4>
                <div className="difficulty-options">
                  <select
                    name="difficulty"
                    value={formData.difficulty}
                    onChange={handleChange}
                    className="form-select"
                  >
                    <option value="beginner">🚀 Beginner</option>
                    <option value="intermediate">⚡ Intermediate</option>
                    <option value="advanced">🔥 Advanced</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          {/* Schedule Section */}
          <div className="form-section-enhanced glass-card">
            <div className="section-header-enhanced">
              <h3 className="section-title">Schedule</h3>
              <p>Set your start and target dates</p>
            </div>

            <div className="schedule-dates-grid">
              <div className="date-section">
                <label className="form-label">Start Date</label>
                <div className="date-input-wrapper">
                  <input
                    type="date"
                    value={formData.start_date}
                    onChange={handleChange}
                    name="start_date"
                    className="date-input"
                  />
                </div>
              </div>
              {formData.start_date && formData.end_date && (
                <div className="date-validation">
                  {new Date(formData.end_date) <=
                    new Date(formData.start_date) && (
                    <div className="error-message">
                      ❌ End date must be after start date
                    </div>
                  )}
                  {formData.duration_days !== "custom" &&
                    formData.start_date &&
                    (() => {
                      const start = new Date(formData.start_date);
                      const end = new Date(formData.end_date);
                      const diffTime = Math.abs(end - start);
                      const diffDays = Math.ceil(
                        diffTime / (1000 * 60 * 60 * 24)
                      );
                      const selectedDays = parseInt(formData.duration_days);

                      if (diffDays !== selectedDays && !isNaN(diffDays)) {
                        return (
                          <div className="warning-message">
                            ⚠️ Date range ({diffDays} days) doesn't match
                            selected duration ({selectedDays} days)
                          </div>
                        );
                      }
                      return null;
                    })()}
                </div>
              )}
              <div className="date-section">
                <label className="form-label">Target Date</label>
                <div className="date-input-wrapper">
                  <input
                    type="date"
                    value={formData.end_date}
                    onChange={handleChange}
                    name="end_date"
                    className="date-input"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Learning Preferences Section */}
          <div className="form-section-enhanced glass-card">
            <div className="section-header-enhanced">
              <h3 className="section-title">Learning Preferences</h3>
              <p>Customize how you want to learn</p>
            </div>

            <div className="preferences-grid">
              <div className="preference-group">
                <label className="form-label">📚 Study Schedule</label>
                <select
                  name="study_schedule"
                  value={formData.study_schedule}
                  onChange={handleChange}
                  className="form-select"
                >
                  <option value="flexible">Flexible (Self-paced)</option>
                  <option value="regular">Regular (2-3 times/week)</option>
                  <option value="intensive">Intensive (Daily)</option>
                </select>
              </div>

              <div className="preference-group">
                <label className="form-label">⏰ Weekly Hours</label>
                <select
                  name="weekly_hours"
                  value={formData.weekly_hours}
                  onChange={handleChange}
                  className="form-select"
                >
                  <option value="2">2-3 hours</option>
                  <option value="5">5-7 hours</option>
                  <option value="10">10+ hours</option>
                </select>
              </div>

              <div className="preference-group full-width">
                <label className="form-label">🎨 Learning Style</label>
                <select
                  name="learning_style"
                  value={formData.learning_style}
                  onChange={handleChange}
                  className="form-select"
                >
                  <option value="visual">👀 Visual (Videos, Diagrams)</option>
                  <option value="reading">📖 Reading (Articles, Docs)</option>
                  <option value="hands-on">
                    🛠️ Hands-on (Projects, Exercises)
                  </option>
                  <option value="mixed">🌈 Mixed (All of the above)</option>
                </select>
              </div>
            </div>
          </div>

          <div className="form-actions">
            <button type="button" className="btn-secondary" onClick={prevStep}>
              ← Back to Goal
            </button>
            <button
              type="button"
              className="btn-primary btn-large"
              onClick={nextStep}
            >
              Review Plan →
            </button>
          </div>
        </>
      )}
    </div>
  );

  // Step 3: Review Page
  const renderStep3 = () => (
    <div className="step-page">
      <div className="step-header">
        <h2>📋 Review Your Plan</h2>
        <p>Check your AI-generated learning plan before creating</p>
      </div>
      <div className="review-content">
        {/* Goal Summary */}
        <div className="review-section glass-card">
          <h3 className="section-title">🎯 Goal Summary</h3>
          <div className="summary-grid">
            <div className="summary-item">
              <strong>Goal Title:</strong>
              <span>{formData.title}</span>
            </div>
            <div className="summary-item">
              <strong>Description:</strong>
              <span>{formData.description}</span>
            </div>
            <div className="summary-item">
              <strong>Duration:</strong>
              <span>
                {formData.duration_days === "custom"
                  ? formData.custom_days
                  : formData.duration_days}{" "}
                days
              </span>
            </div>
            <div className="summary-item">
              <strong>Difficulty:</strong>
              <span className={`difficulty-badge ${formData.difficulty}`}>
                {formData.difficulty}
              </span>
            </div>
          </div>
        </div>

        {/* Timeline & Schedule Review */}
        <div className="review-section glass-card">
          <h3 className="section-title">📅 Timeline & Schedule</h3>
          <div className="timeline-review-grid">
            <div className="timeline-review-item">
              <strong>Timeline:</strong>
              <span>
                {formData.duration_days === "custom"
                  ? formData.custom_days
                  : formData.duration_days}{" "}
                days
              </span>
            </div>
            <div className="timeline-review-item">
              <strong>Difficulty:</strong>
              <span>{formData.difficulty}</span>
            </div>
            <div className="timeline-review-item">
              <strong>Start Date:</strong>
              <span>{formData.start_date || "Not set"}</span>
            </div>
            <div className="timeline-review-item">
              <strong>Target Date:</strong>
              <span>{formData.end_date || "Not set"}</span>
            </div>
            <div className="timeline-review-item">
              <strong>Study Schedule:</strong>
              <span>{formData.study_schedule}</span>
            </div>
            <div className="timeline-review-item">
              <strong>Weekly Hours:</strong>
              <span>{formData.weekly_hours} hours</span>
            </div>
          </div>
        </div>

        {/* AI Generated Plan */}
        {aiPlan && (
          <div className="review-section glass-card">
            <h3 className="section-title">🤖 AI-Generated Learning Plan</h3>

            <div className="plan-section">
              <h4>📅 Weekly Schedule</h4>
              <div className="schedule-grid">
                {aiPlan.weekly_schedule.map((day, index) => (
                  <div key={index} className="schedule-item">
                    <div className="schedule-day">{day.day}</div>
                    <div className="schedule-topics">
                      {day.topics.join(", ")}
                    </div>
                    <div className="schedule-duration">{day.duration}</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="plan-section">
              <h4>📚 Learning Resources</h4>
              <div className="resources-grid">
                {aiPlan.resources.map((resource, index) => (
                  <div key={index} className="resource-item">
                    <span className="resource-type">{resource.type}</span>
                    <span className="resource-title">{resource.title}</span>
                    <span className="resource-duration">
                      {resource.duration}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="plan-section">
              <h4>🎯 Progress Milestones</h4>
              <div className="milestones-grid">
                {aiPlan.milestones.map((milestone, index) => (
                  <div key={index} className="milestone-item">
                    <div className="milestone-week">Week {milestone.week}</div>
                    <div className="milestone-goal">{milestone.goal}</div>
                    <div className="milestone-status">Pending</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        <div className="form-actions">
          <button type="button" className="btn-secondary" onClick={prevStep}>
            ← Back to Planning
          </button>
          <button
            type="submit"
            disabled={loading}
            className="btn-primary btn-large"
            onClick={handleSubmit}
          >
            {loading ? (
              <>
                <div className="loading-spinner-small"></div>
                Creating Your Goal...
              </>
            ) : (
              "🚀 Create Goal with AI"
            )}
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="create-goal-enhanced">
      <div className="page-header">
        <h1>🚀 Create New Goal</h1>
        <p>
          Tell AI what you want to achieve and we'll build your learning path
        </p>
      </div>

      <div className="form-container">
        <div className="form-card glass-card">
          <div className="form-header">
            <h3>
              {currentStep === 1 && "Step 1: Define Your Goal"}
              {currentStep === 2 && "Step 2: Create Your Plan"}
              {currentStep === 3 && "Step 3: Review & Create"}
            </h3>
            <StepIndicator />
          </div>

          <form onSubmit={handleSubmit} className="goal-form-enhanced">
            {currentStep === 1 && renderStep1()}
            {currentStep === 2 && renderStep2()}
            {currentStep === 3 && renderStep3()}
          </form>
        </div>

        {/* AI Preview Sidebar */}
        <div className="ai-preview-sidebar glass-card">
          <h4>🤖 AI Preview</h4>
          <p>Based on your goal, AI will:</p>
          <ul className="ai-features-list">
            <li>📚 Curate learning resources</li>
            <li>🗓️ Create study schedule</li>
            <li>✅ Break down into tasks</li>
            <li>📊 Track your progress</li>
            <li>💡 Provide personalized tips</li>
            <li>🔔 Set smart reminders</li>
            <li>📈 Adjust plan as you learn</li>
            <li>🎯 Focus on weak areas</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default CreateGoal;