// ============================================
// API Integration Module
// ============================================

// API Configuration
// Can be overridden by setting window.API_BASE_URL before script loads
const API_CONFIG = {
  baseURL: (typeof window !== 'undefined' && window.API_BASE_URL) || 'http://localhost:5000/api/v1',
  endpoints: {
    predict: '/predict'
  },
  timeout: 10000 // 10 seconds
};

/**
 * Make API request to prediction endpoint
 * @param {Object} formData - Form data object
 * @param {string} modelName - Selected model name (optional)
 * @returns {Promise<Object>} Prediction response
 */
async function predictDelay(formData, modelName = null) {
  // Construct full URL
  const baseURL = API_CONFIG.baseURL.endsWith('/api/v1') 
    ? API_CONFIG.baseURL 
    : `${API_CONFIG.baseURL}/api/v1`;
  let url = `${baseURL}${API_CONFIG.endpoints.predict}`;
  
  // Add model parameter if specified
  if (modelName) {
    url += `?model=${encodeURIComponent(modelName)}`;
  }
  
  const requestPayload = {
    route_id: formData.route_id,
    weather: formData.weather,
    passenger_count: formData.passenger_count,
    time_of_day: formData.time_of_day,
    is_weekend: formData.is_weekend
  };
  
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.timeout);
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestPayload),
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      // Handle FastAPI error response format
      let errorMessage = errorData.message || errorData.error || `HTTP error! status: ${response.status}`;
      const error = new Error(errorMessage);
      
      // Preserve error details if available (FastAPI returns 'detail' or 'details')
      if (errorData.details) {
        error.details = errorData.details;
      } else if (errorData.detail) {
        // FastAPI sometimes returns 'detail' as a string or object
        if (typeof errorData.detail === 'object' && errorData.detail.details) {
          error.details = errorData.detail.details;
        } else if (typeof errorData.detail === 'string') {
          error.message = errorData.detail;
        }
      }
      throw error;
    }
    
    const data = await response.json();
    return data;
    
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error('Request timeout. Please try again.');
    }
    
    if (error.message.includes('Failed to fetch')) {
      throw new Error('Unable to connect to server. Please check your connection.');
    }
    
    throw error;
  }
}

/**
 * Handle API errors and show user-friendly messages
 * @param {Error} error - Error object
 * @returns {Object} Error details for UI
 */
function handleApiError(error) {
  console.error('API Error:', error);
  
  // Parse error message
  let message = 'An unexpected error occurred. Please try again.';
  let details = {};
  
  if (error.message) {
    message = error.message;
  }
  
  // Check for validation errors in response
  if (error.details) {
    details = error.details;
  }
  
  return {
    message,
    details
  };
}

// Make functions available globally for use in app.js
if (typeof window !== 'undefined') {
  window.predictDelay = predictDelay;
  window.handleApiError = handleApiError;
  window.API_CONFIG = API_CONFIG;
}

// Export for use in other modules (Node.js)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { predictDelay, handleApiError, API_CONFIG };
}

