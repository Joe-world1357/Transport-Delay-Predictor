// ============================================
// Transport Delay Predictor - Main Application
// ============================================

// DOM Elements
const form = document.getElementById('predictionForm');
const submitBtn = document.getElementById('submitBtn');
const resultsCard = document.getElementById('resultsCard');
const emptyState = document.getElementById('emptyState');
const loadedState = document.getElementById('loadedState');

// Form Input Elements
const routeIdInput = document.getElementById('routeId');
const weatherSelect = document.getElementById('weather');
const passengersInput = document.getElementById('passengers');
const timeOfDayRadios = document.querySelectorAll('input[name="timeOfDay"]');
const isWeekendToggle = document.getElementById('isWeekend');
const modelSelect = document.getElementById('modelSelect');
const datasetUpload = document.getElementById('datasetUpload');
const uploadBtn = document.getElementById('uploadBtn');
const uploadStatus = document.getElementById('uploadStatus');
const fileName = document.getElementById('fileName');
const comparisonTableBody = document.getElementById('comparisonTableBody');
const modelComparison = document.getElementById('modelComparison');
const viewComparisonBtn = document.getElementById('viewComparisonBtn');

// Result Display Elements
const delayValue = document.getElementById('delayValue');
const summaryRoute = document.getElementById('summaryRoute');
const summaryWeather = document.getElementById('summaryWeather');
const summaryPassengers = document.getElementById('summaryPassengers');
const summaryTime = document.getElementById('summaryTime');
const summaryDayType = document.getElementById('summaryDayType');
const modelName = document.getElementById('modelName');
const modelMAE = document.getElementById('modelMAE');

// ============================================
// Utility Functions
// ============================================

/**
 * Show error message for a form field
 */
function showFieldError(fieldId, message) {
  const errorElement = document.getElementById(`${fieldId}-error`);
  const inputElement = document.getElementById(fieldId);
  
  if (errorElement) {
    errorElement.textContent = message;
    errorElement.setAttribute('role', 'alert');
  }
  
  if (inputElement) {
    inputElement.classList.add('invalid');
    inputElement.classList.remove('valid');
  }
}

/**
 * Clear error message for a form field
 */
function clearFieldError(fieldId) {
  const errorElement = document.getElementById(`${fieldId}-error`);
  const inputElement = document.getElementById(fieldId);
  
  if (errorElement) {
    errorElement.textContent = '';
    errorElement.removeAttribute('role');
  }
  
  if (inputElement) {
    inputElement.classList.remove('invalid');
    inputElement.classList.add('valid');
  }
}

/**
 * Validate form field
 */
function validateField(fieldId, value) {
  switch (fieldId) {
    case 'routeId':
      const routeId = parseInt(value);
      if (isNaN(routeId) || routeId < 1 || routeId > 10) {
        showFieldError('routeId', 'Please enter a valid route ID (1-10)');
        return false;
      }
      clearFieldError('routeId');
      return true;
      
    case 'passengers':
      const passengers = parseInt(value);
      if (isNaN(passengers) || passengers < 0 || passengers > 500) {
        showFieldError('passengers', 'Passenger count must be between 0 and 500');
        return false;
      }
      clearFieldError('passengers');
      return true;
      
    case 'weather':
      if (!value) {
        showFieldError('weather', 'Please select a weather condition');
        return false;
      }
      clearFieldError('weather');
      return true;
      
    default:
      return true;
  }
}

/**
 * Get form data as object
 */
function getFormData() {
  const timeOfDayValue = Array.from(timeOfDayRadios).find(radio => radio.checked)?.value;
  
  return {
    route_id: parseInt(routeIdInput.value),
    weather: weatherSelect.value,
    passenger_count: parseInt(passengersInput.value),
    time_of_day: parseInt(timeOfDayValue),
    is_weekend: isWeekendToggle.checked ? 1 : 0
  };
}

/**
 * Validate entire form
 */
function validateForm() {
  let isValid = true;
  
  isValid = validateField('routeId', routeIdInput.value) && isValid;
  isValid = validateField('passengers', passengersInput.value) && isValid;
  isValid = validateField('weather', weatherSelect.value) && isValid;
  
  return isValid;
}

// ============================================
// Number Input Controls
// ============================================

const decrementBtn = document.querySelector('.btn-decrement');
const incrementBtn = document.querySelector('.btn-increment');

decrementBtn?.addEventListener('click', () => {
  const currentValue = parseInt(passengersInput.value) || 100;
  const newValue = Math.max(0, currentValue - 10);
  passengersInput.value = newValue;
  validateField('passengers', newValue);
});

incrementBtn?.addEventListener('click', () => {
  const currentValue = parseInt(passengersInput.value) || 100;
  const newValue = Math.min(500, currentValue + 10);
  passengersInput.value = newValue;
  validateField('passengers', newValue);
});

// ============================================
// Form Validation (Real-time)
// ============================================

routeIdInput?.addEventListener('blur', () => {
  validateField('routeId', routeIdInput.value);
});

// Debounced validation for better performance
const debouncedRouteValidation = debounce((value) => {
  if (routeIdInput.classList.contains('invalid')) {
    validateField('routeId', value);
  }
}, 300);

const debouncedPassengerValidation = debounce((value) => {
  if (passengersInput.classList.contains('invalid')) {
    validateField('passengers', value);
  }
}, 300);

routeIdInput?.addEventListener('input', (e) => {
  debouncedRouteValidation(e.target.value);
});

passengersInput?.addEventListener('blur', () => {
  validateField('passengers', passengersInput.value);
});

passengersInput?.addEventListener('input', (e) => {
  debouncedPassengerValidation(e.target.value);
});

weatherSelect?.addEventListener('change', () => {
  validateField('weather', weatherSelect.value);
});

// ============================================
// Form Submission
// ============================================

form?.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  // Validate form
  if (!validateForm()) {
    // Shake animation for errors
    form.classList.add('shake');
    setTimeout(() => form.classList.remove('shake'), 400);
    return;
  }
  
  // Set loading state
  setLoadingState(true);
  
  // Get form data
  const formData = getFormData();
  
  // Add selected model to request
  const selectedModel = modelSelect?.value || 'gradient_boosting';
  
  // Make API call
  try {
    const response = await predictDelay(formData, selectedModel);
    displayResults(formData, response);
    setLoadingState(false);
  } catch (error) {
    setLoadingState(false);
    const errorInfo = handleApiError(error);
    showErrorToast(errorInfo.message, errorInfo.details);
    
    // If there are field-specific errors, show them
    if (errorInfo.details && Object.keys(errorInfo.details).length > 0) {
      Object.keys(errorInfo.details).forEach(field => {
        const fieldMap = {
          'route_id': 'routeId',
          'passenger_count': 'passengers',
          'weather': 'weather'
        };
        const mappedField = fieldMap[field] || field;
        showFieldError(mappedField, errorInfo.details[field]);
      });
    }
  }
});

/**
 * Set loading state for submit button and form
 */
function setLoadingState(loading) {
  if (loading) {
    submitBtn.disabled = true;
    submitBtn.classList.add('loading');
    const submitText = submitBtn.querySelector('span');
    if (submitText) {
      submitText.textContent = 'Analyzing...';
    }
    // Add pulsing effect to form
    form?.classList.add('loading');
  } else {
    submitBtn.disabled = false;
    submitBtn.classList.remove('loading');
    const submitText = submitBtn.querySelector('span');
    if (submitText) {
      submitText.textContent = 'Predict Delay';
    }
    // Remove pulsing effect from form
    form?.classList.remove('loading');
  }
}

/**
 * Display prediction results
 */
function displayResults(formData, response) {
  // Hide empty state, show loaded state
  emptyState.style.display = 'none';
  loadedState.style.display = 'block';
  
  // Update delay value
  delayValue.textContent = `${response.predicted_delay.toFixed(1)} minutes`;
  
  // Update summary
  summaryRoute.textContent = `#${formData.route_id}`;
  
  const weatherEmoji = {
    'clear': '☀️',
    'cloudy': '☁️',
    'rainy': '🌧️',
    'snowy': '❄️'
  };
  summaryWeather.textContent = `${weatherEmoji[formData.weather] || ''} ${formData.weather.charAt(0).toUpperCase() + formData.weather.slice(1)}`;
  
  summaryPassengers.textContent = formData.passenger_count.toString();
  
  const timeLabels = {
    0: 'Morning (6-12)',
    1: 'Afternoon (12-18)',
    2: 'Evening (18-24)',
    3: 'Night (0-6)'
  };
  summaryTime.textContent = timeLabels[formData.time_of_day] || 'Unknown';
  
  summaryDayType.textContent = formData.is_weekend ? 'Weekend' : 'Weekday';
  
  // Update model info
  modelName.textContent = response.model_name || 'Random Forest Regressor';
  modelMAE.textContent = response.mae ? response.mae.toFixed(1) : '3.2';
  
  // Display feature importance if available
  if (response.feature_importance && Array.isArray(response.feature_importance)) {
    displayFeatureImportance(response.feature_importance);
  } else {
    // Hide feature importance section if not available
    const featureImportance = document.getElementById('featureImportance');
    if (featureImportance) {
      featureImportance.style.display = 'none';
    }
  }
  
  // Show results card with animation
  resultsCard.style.display = 'block';
  
  // Scroll to results on mobile
  if (window.innerWidth < 768) {
    setTimeout(() => {
      resultsCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
  }
}

/**
 * Display feature importance visualization
 * @param {Array} features - Array of {name: string, importance: number} objects
 */
function displayFeatureImportance(features) {
  const featureImportance = document.getElementById('featureImportance');
  const importanceChart = document.getElementById('importanceChart');
  
  if (!featureImportance || !importanceChart) return;
  
  // Sort features by importance (descending)
  const sortedFeatures = [...features].sort((a, b) => b.importance - a.importance);
  
  // Take top 3 features
  const topFeatures = sortedFeatures.slice(0, 3);
  
  // Calculate total for percentage
  const total = topFeatures.reduce((sum, f) => sum + f.importance, 0);
  
  // Clear previous content
  importanceChart.innerHTML = '';
  
  // Create bars for each feature
  topFeatures.forEach((feature, index) => {
    const percentage = total > 0 ? (feature.importance / total) * 100 : 0;
    
    const item = document.createElement('div');
    item.className = 'importance-item';
    item.style.opacity = '0';
    item.style.transform = 'translateX(-20px)';
    
    const label = document.createElement('span');
    label.className = 'importance-label';
    label.textContent = formatFeatureName(feature.name);
    
    const barContainer = document.createElement('div');
    barContainer.className = 'importance-bar-container';
    
    const bar = document.createElement('div');
    bar.className = 'importance-bar';
    bar.style.width = '0%'; // Start at 0 for animation
    
    const percentageText = document.createElement('span');
    percentageText.className = 'importance-percentage';
    percentageText.textContent = `${percentage.toFixed(0)}%`;
    
    bar.appendChild(percentageText);
    barContainer.appendChild(bar);
    
    item.appendChild(label);
    item.appendChild(barContainer);
    importanceChart.appendChild(item);
    
    // Animate bar fill
    setTimeout(() => {
      item.style.transition = 'all 0.4s ease-out';
      item.style.opacity = '1';
      item.style.transform = 'translateX(0)';
      
      setTimeout(() => {
        bar.style.width = `${percentage}%`;
      }, 100);
    }, index * 150 + 900); // Stagger animation
  });
  
  featureImportance.style.display = 'block';
}

/**
 * Format feature name for display
 */
function formatFeatureName(name) {
  const nameMap = {
    'weather': 'Weather',
    'time_of_day': 'Time of Day',
    'passenger_count': 'Passenger Count',
    'route_id': 'Route ID',
    'is_weekend': 'Weekend Status'
  };
  
  return nameMap[name] || name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

// ============================================
// Toast Notification System
// ============================================

const toastContainer = document.getElementById('toastContainer');

/**
 * Show toast notification
 * @param {string} message - Toast message
 * @param {string} type - Toast type: 'error', 'success', 'warning', 'info'
 * @param {number} duration - Auto-dismiss duration in ms (0 = no auto-dismiss)
 */
function showToast(message, type = 'error', duration = 5000) {
  if (!toastContainer) return;
  
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.setAttribute('role', 'alert');
  
  const icons = {
    error: '❌',
    success: '✓',
    warning: '⚠️',
    info: 'ℹ️'
  };
  
  toast.innerHTML = `
    <span class="toast-icon" aria-hidden="true">${icons[type] || 'ℹ️'}</span>
    <div class="toast-content">
      <div class="toast-message">${escapeHtml(message)}</div>
    </div>
    <button class="toast-close" aria-label="Close notification" onclick="this.parentElement.remove()">×</button>
  `;
  
  toastContainer.appendChild(toast);
  
  // Auto-dismiss after duration
  if (duration > 0) {
    setTimeout(() => {
      dismissToast(toast);
    }, duration);
  }
  
  return toast;
}

/**
 * Show error toast (convenience function)
 */
function showErrorToast(message, details = {}) {
  let fullMessage = message;
  
  // Add details if available
  if (details && Object.keys(details).length > 0) {
    const detailMessages = Object.values(details).join(', ');
    fullMessage = `${message}: ${detailMessages}`;
  }
  
  return showToast(fullMessage, 'error', 7000);
}

/**
 * Dismiss toast with animation
 */
function dismissToast(toast) {
  toast.classList.add('hiding');
  setTimeout(() => {
    if (toast.parentElement) {
      toast.remove();
    }
  }, 300);
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
  if (typeof text !== 'string') return '';
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

/**
 * Debounce function for performance optimization
 */
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// ============================================
// Initialize
// ============================================

// ============================================
// Keyboard Navigation Enhancements
// ============================================

// Handle Enter key on number inputs
document.addEventListener('keydown', (e) => {
  // Allow Enter to submit form from any input
  if (e.key === 'Enter' && e.target.tagName === 'INPUT' && e.target.type !== 'checkbox') {
    // Don't prevent default if it's a number input with increment/decrement buttons
    if (e.target.type === 'number' && (e.target.id === 'passengers' || e.target.id === 'routeId')) {
      return; // Let default behavior handle it
    }
  }
  
  // Escape key to clear errors
  if (e.key === 'Escape') {
    // Clear any visible toasts
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach(toast => dismissToast(toast));
  }
});

// Enhanced keyboard navigation for radio buttons
timeOfDayRadios.forEach((radio, index) => {
  radio.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
      e.preventDefault();
      const nextIndex = (index + 1) % timeOfDayRadios.length;
      timeOfDayRadios[nextIndex].focus();
      timeOfDayRadios[nextIndex].checked = true;
    } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
      e.preventDefault();
      const prevIndex = (index - 1 + timeOfDayRadios.length) % timeOfDayRadios.length;
      timeOfDayRadios[prevIndex].focus();
      timeOfDayRadios[prevIndex].checked = true;
    }
  });
});

// ============================================
// Initialize
// ============================================

// ============================================
// Dataset Upload Functionality
// ============================================

datasetUpload?.addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (file) {
    fileName.textContent = file.name;
    uploadBtn.disabled = false;
  } else {
    fileName.textContent = 'No file selected';
    uploadBtn.disabled = true;
  }
});

uploadBtn?.addEventListener('click', async () => {
  const file = datasetUpload.files[0];
  if (!file) {
    showErrorToast('Please select a CSV file first');
    return;
  }
  
  uploadBtn.disabled = true;
  uploadStatus.textContent = 'Uploading and training models...';
  uploadStatus.className = 'upload-status loading';
  
  try {
    const formData = new FormData();
    formData.append('file', file);  // Changed from 'dataset' to 'file' to match backend
    
    // Get base URL from API config
    const baseURL = typeof API_CONFIG !== 'undefined' && API_CONFIG.baseURL 
      ? API_CONFIG.baseURL 
      : 'http://localhost:5000';
    
    const apiURL = baseURL.endsWith('/api/v1') 
      ? `${baseURL}/upload-dataset`
      : `${baseURL}/api/v1/upload-dataset`;
    
    const response = await fetch(apiURL, {
      method: 'POST',
      body: formData
      // Don't set Content-Type header - browser will set it with boundary
    });
    
    if (!response.ok) {
      let errorMessage = 'Upload failed';
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || errorMessage;
        // If detail is a list (validation errors), format it
        if (Array.isArray(errorMessage)) {
          errorMessage = errorMessage.map(e => e.msg || e).join(', ');
        }
      } catch (e) {
        errorMessage = `Server error: ${response.status} ${response.statusText}`;
      }
      throw new Error(errorMessage);
    }
    
    const result = await response.json();
    uploadStatus.textContent = '✅ Dataset uploaded and models trained successfully!';
    uploadStatus.className = 'upload-status success';
    
    // Update model comparison
    if (result.comparison) {
      displayModelComparison(result.comparison);
    }
    
    // Update model select options
    updateModelSelect(result.models || []);
    
    showToast('Models trained successfully! You can now select different algorithms.', 'success');
    
    // Show data exploration section
    showDataExploration();
    
    // Auto-load visualizations
    setTimeout(() => {
      loadVisualizationsBtn?.click();
    }, 1000);
    
  } catch (error) {
    uploadStatus.textContent = `❌ Error: ${error.message}`;
    uploadStatus.className = 'upload-status error';
    showErrorToast(error.message);
  } finally {
    uploadBtn.disabled = false;
  }
});

// ============================================
// Model Comparison Display
// ============================================

async function loadModelComparison() {
  try {
    const response = await fetch(`${API_CONFIG.baseURL}/api/v1/model-comparison`);
    if (response.ok) {
      const data = await response.json();
      displayModelComparison(data.comparison);
    }
  } catch (error) {
    console.warn('Could not load model comparison:', error);
  }
}

function displayModelComparison(comparison) {
  if (!comparisonTableBody || !comparison) return;
  
  comparisonTableBody.innerHTML = '';
  
  // Find best model (lowest MAE)
  const bestModel = comparison.reduce((best, model) => {
    return (!best || parseFloat(model.MAE) < parseFloat(best.MAE)) ? model : best;
  }, null);
  
  comparison.forEach(model => {
    const row = document.createElement('tr');
    const isBest = bestModel && model.Model === bestModel.Model;
    
    if (isBest) {
      row.classList.add('best-model');
    }
    
    row.innerHTML = `
      <td>${model.Model}</td>
      <td>${parseFloat(model.MAE).toFixed(2)}</td>
      <td>${parseFloat(model.RMSE).toFixed(2)}</td>
      <td>${parseFloat(model['R²']).toFixed(3)}</td>
      <td>${isBest ? '⭐ Best' : 'Available'}</td>
    `;
    
    comparisonTableBody.appendChild(row);
  });
  
  modelComparison.style.display = 'block';
}

function updateModelSelect(models) {
  if (!modelSelect || !models.length) return;
  
  modelSelect.innerHTML = '';
  
  models.forEach(model => {
    const option = document.createElement('option');
    option.value = model.name;
    option.textContent = `${model.display_name}${model.is_best ? ' (Best)' : ''}`;
    if (model.is_best) {
      option.selected = true;
    }
    modelSelect.appendChild(option);
  });
}

viewComparisonBtn?.addEventListener('click', () => {
  loadModelComparison();
});

// ============================================
// Data Exploration & EDA
// ============================================

const dataExplorationCard = document.getElementById('dataExplorationCard');
const loadDataPreviewBtn = document.getElementById('loadDataPreviewBtn');
const dataTableContainer = document.getElementById('dataTableContainer');
const dataTableHead = document.getElementById('dataTableHead');
const dataTableBody = document.getElementById('dataTableBody');
const statsGrid = document.getElementById('statsGrid');
const loadVisualizationsBtn = document.getElementById('loadVisualizationsBtn');

// Load dataset preview
loadDataPreviewBtn?.addEventListener('click', async () => {
  try {
    loadDataPreviewBtn.disabled = true;
    loadDataPreviewBtn.textContent = 'Loading...';
    
    // Get base URL (API_CONFIG.baseURL already includes /api/v1)
    const baseUrl = (typeof API_CONFIG !== 'undefined' && API_CONFIG.baseURL) 
      ? API_CONFIG.baseURL.replace(/\/api\/v1$/, '') 
      : 'http://localhost:5000';
    const response = await fetch(`${baseUrl}/api/v1/dataset-preview`);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('Preview response error:', response.status, errorText);
      throw new Error(`Failed to load dataset preview: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    
    // Display statistics
    if (data.stats && statsGrid) {
      displayDatasetStats(data.stats);
    }
    
    // Display preview table
    if (data.preview && data.preview.length > 0) {
      displayDataPreview(data.preview);
      dataTableContainer.style.display = 'block';
    }
    
    loadDataPreviewBtn.textContent = 'Load Dataset Preview';
    loadDataPreviewBtn.disabled = false;
    dataExplorationCard.style.display = 'block';
    
  } catch (error) {
    console.error('Error loading data preview:', error);
    loadDataPreviewBtn.textContent = 'Load Dataset Preview';
    loadDataPreviewBtn.disabled = false;
    showErrorToast(`Failed to load dataset preview: ${error.message}`);
  }
});

// Load EDA visualizations
loadVisualizationsBtn?.addEventListener('click', async () => {
  try {
    loadVisualizationsBtn.disabled = true;
    loadVisualizationsBtn.textContent = 'Loading visualizations...';
    
    // Get base URL (API_CONFIG.baseURL already includes /api/v1)
    const baseUrl = (typeof API_CONFIG !== 'undefined' && API_CONFIG.baseURL) 
      ? API_CONFIG.baseURL.replace(/\/api\/v1$/, '') 
      : 'http://localhost:5000';
    const response = await fetch(`${baseUrl}/api/v1/eda-visualizations`);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('Visualizations response error:', response.status, errorText);
      throw new Error(`Failed to load visualizations: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    
    // Display visualizations
    if (data.visualizations) {
      displayEDAVisualizations(data.visualizations);
    }
    
    loadVisualizationsBtn.textContent = 'Load All Visualizations';
    loadVisualizationsBtn.disabled = false;
    
  } catch (error) {
    console.error('Error loading visualizations:', error);
    loadVisualizationsBtn.textContent = 'Load All Visualizations';
    loadVisualizationsBtn.disabled = false;
    showErrorToast(`Failed to load visualizations: ${error.message}`);
  }
});

function displayDatasetStats(stats) {
  if (!statsGrid) return;
  
  statsGrid.innerHTML = '';
  
  const statItems = [
    { label: 'Total Records', value: stats.total_records || 'N/A' },
    { label: 'Features', value: stats.total_features || 'N/A' },
    { label: 'Mean Delay', value: stats.mean_delay ? `${stats.mean_delay.toFixed(1)} min` : 'N/A' },
    { label: 'Max Delay', value: stats.max_delay ? `${stats.max_delay.toFixed(1)} min` : 'N/A' },
    { label: 'Min Delay', value: stats.min_delay ? `${stats.min_delay.toFixed(1)} min` : 'N/A' },
    { label: 'Std Deviation', value: stats.std_delay ? `${stats.std_delay.toFixed(1)}` : 'N/A' }
  ];
  
  statItems.forEach(stat => {
    const card = document.createElement('div');
    card.className = 'stat-card';
    card.innerHTML = `
      <span class="stat-value">${stat.value}</span>
      <span class="stat-label">${stat.label}</span>
    `;
    statsGrid.appendChild(card);
  });
}

function displayDataPreview(preview) {
  if (!preview || preview.length === 0) {
    console.warn('No preview data to display');
    return;
  }
  
  // Clear existing content
  if (!dataTableHead || !dataTableBody) {
    console.error('Table elements not found');
    return;
  }
  
  dataTableHead.innerHTML = '';
  dataTableBody.innerHTML = '';
  
  // Get column names from first row
  const columns = Object.keys(preview[0]);
  
  // Create header
  const headerRow = document.createElement('tr');
  columns.forEach(col => {
    const th = document.createElement('th');
    th.textContent = formatFeatureName(col);
    headerRow.appendChild(th);
  });
  dataTableHead.appendChild(headerRow);
  
  // Create rows
  preview.forEach(row => {
    const tr = document.createElement('tr');
    columns.forEach(col => {
      const td = document.createElement('td');
      let value = row[col];
      
      // Format values
      if (value === null || value === undefined) {
        value = 'N/A';
      } else if (typeof value === 'number') {
        value = value.toFixed(2);
      } else {
        value = String(value);
      }
      
      td.textContent = value;
      tr.appendChild(td);
    });
    dataTableBody.appendChild(tr);
  });
}

function displayEDAVisualizations(visualizations) {
  if (!visualizations) {
    console.warn('No visualizations data provided');
    return;
  }
  
  // Get base URL for images
  const baseUrl = (typeof API_CONFIG !== 'undefined' && API_CONFIG.baseURL) 
    ? API_CONFIG.baseURL.replace(/\/api\/v1$/, '') 
    : 'http://localhost:5000';
  
  // Delay Distribution
  if (visualizations.delay_distribution) {
    const img = document.getElementById('delayDistImg');
    const placeholder = document.getElementById('delayDistViz');
    if (img && placeholder) {
      // Ensure full URL if relative path
      const imgSrc = visualizations.delay_distribution.startsWith('http') 
        ? visualizations.delay_distribution 
        : `${baseUrl}${visualizations.delay_distribution}`;
      img.src = imgSrc;
      img.style.display = 'block';
      const pTag = placeholder.querySelector('p');
      if (pTag) pTag.style.display = 'none';
    }
  }
  
  // Weather Impact
  if (visualizations.weather_impact) {
    const img = document.getElementById('weatherImpactImg');
    const placeholder = document.getElementById('weatherImpactViz');
    if (img && placeholder) {
      const imgSrc = visualizations.weather_impact.startsWith('http') 
        ? visualizations.weather_impact 
        : `${baseUrl}${visualizations.weather_impact}`;
      img.src = imgSrc;
      img.style.display = 'block';
      const pTag = placeholder.querySelector('p');
      if (pTag) pTag.style.display = 'none';
    }
  }
  
  // Time of Day Impact
  if (visualizations.time_of_day_impact) {
    const img = document.getElementById('timeOfDayImg');
    const placeholder = document.getElementById('timeOfDayViz');
    if (img && placeholder) {
      const imgSrc = visualizations.time_of_day_impact.startsWith('http') 
        ? visualizations.time_of_day_impact 
        : `${baseUrl}${visualizations.time_of_day_impact}`;
      img.src = imgSrc;
      img.style.display = 'block';
      const pTag = placeholder.querySelector('p');
      if (pTag) pTag.style.display = 'none';
    }
  }
  
  // Feature Importance
  if (visualizations.feature_importance) {
    const img = document.getElementById('featureImportanceImg');
    const placeholder = document.getElementById('featureImportanceViz');
    if (img && placeholder) {
      const imgSrc = visualizations.feature_importance.startsWith('http') 
        ? visualizations.feature_importance 
        : `${baseUrl}${visualizations.feature_importance}`;
      img.src = imgSrc;
      img.style.display = 'block';
      const pTag = placeholder.querySelector('p');
      if (pTag) pTag.style.display = 'none';
    }
  }
}

// Auto-load data exploration after successful upload
function showDataExploration() {
  if (dataExplorationCard) {
    dataExplorationCard.style.display = 'block';
    // Scroll to exploration section
    setTimeout(() => {
      dataExplorationCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
  }
}

// ============================================
// Initialize
// ============================================

document.addEventListener('DOMContentLoaded', () => {
  console.log('Transport Delay Predictor initialized');
  
  // Ensure results card is visible (empty state)
  resultsCard.style.display = 'block';
  
  // Load model comparison on startup
  loadModelComparison();
  
  // Check if API module loaded correctly
  if (typeof predictDelay === 'undefined') {
    console.warn('API module not loaded. Using mock mode.');
    // Fallback: define mock function if API not available
    window.predictDelay = async (formData) => {
      // Simulate network delay
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Mock response with feature importance for demo
      return {
        predicted_delay: 18.5,
        model_name: "Random Forest Regressor",
        mae: 3.2,
        feature_importance: [
          { name: 'weather', importance: 0.45 },
          { name: 'time_of_day', importance: 0.30 },
          { name: 'passenger_count', importance: 0.25 }
        ]
      };
    };
    
    window.handleApiError = (error) => {
      return {
        message: error.message || 'An error occurred',
        details: {}
      };
    };
  }
  
  // Allow API base URL to be configured via script tag or global variable
  // Usage: <script>window.API_BASE_URL = 'http://your-api-url:5000';</script>
  if (typeof window !== 'undefined' && window.API_BASE_URL && window.API_CONFIG) {
    window.API_CONFIG.baseURL = window.API_BASE_URL;
    console.log('API base URL set to:', window.API_CONFIG.baseURL);
  }
  
  // Set initial focus on first input for better keyboard navigation
  routeIdInput?.focus();
});

