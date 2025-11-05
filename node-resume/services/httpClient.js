/**
 * HTTP Client Service
 * Abstraction layer for HTTP requests using axios
 * Implements Dependency Inversion Principle
 * Includes Circuit Breaker for resilience
 */

const axios = require('axios');
const config = require('../config/api.config');
const logger = require('../utils/logger');
const CircuitBreaker = require('../utils/circuitBreaker');

class HttpClient {
  constructor(baseURL = null, timeout = null) {
    this.client = axios.create({
      baseURL: baseURL || config.pythonApi.baseUrl,
      timeout: timeout || config.pythonApi.timeout,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    // SRE Best Practice: Circuit breaker for ML service (expensive operations)
    this.circuitBreaker = new CircuitBreaker({
      name: 'PythonAPI',
      failureThreshold: 5,
      successThreshold: 2,
      timeout: 60000 // 1 minute before retry
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        logger.debug(`[HttpClient] ${config.method.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        logger.error('[HttpClient] Request error:', { error: error.message });
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        logger.debug(`[HttpClient] Response: ${response.status} ${response.statusText}`);
        return response;
      },
      (error) => {
        const errorMessage = error.response
          ? `${error.response.status} - ${error.response.statusText}`
          : error.message;
        logger.error(`[HttpClient] Response error: ${errorMessage}`);
        return Promise.reject(this.handleError(error));
      }
    );
  }

  /**
   * Handle and normalize errors
   */
  handleError(error) {
    if (error.response) {
      // Server responded with error
      return {
        status: error.response.status,
        message: error.response.data?.message || error.response.statusText,
        data: error.response.data
      };
    } else if (error.request) {
      // Request made but no response
      return {
        status: 503,
        message: 'Service unavailable - no response from server',
        data: null
      };
    } else {
      // Error in request setup
      return {
        status: 500,
        message: error.message,
        data: null
      };
    }
  }

  /**
   * GET request
   */
  async get(url, config = {}) {
    try {
      const response = await this.client.get(url, config);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  /**
   * POST request
   */
  async post(url, data, config = {}) {
    try {
      const response = await this.client.post(url, data, config);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  /**
   * PUT request
   */
  async put(url, data, config = {}) {
    try {
      const response = await this.client.put(url, data, config);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  /**
   * DELETE request
   */
  async delete(url, config = {}) {
    try {
      const response = await this.client.delete(url, config);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  /**
   * POST with FormData (for file uploads)
   */
  async postFormData(url, formData) {
    try {
      const response = await this.client.post(url, formData, {
        headers: formData.getHeaders ? formData.getHeaders() : {}
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Retry logic with exponential backoff
   * SRE Best Practice: Implement retries for transient failures
   *
   * @param {Function} fn - Async function to retry
   * @param {Object} options - Retry configuration
   * @returns {Promise} - Result of successful execution
   */
  async retryWithBackoff(fn, options = {}) {
    const {
      maxRetries = config.pythonApi.retryConfig.maxRetries,
      retryDelay = config.pythonApi.retryConfig.retryDelay,
      retryableStatuses = config.pythonApi.retryConfig.retryableStatuses,
      exponentialBackoff = config.pythonApi.retryConfig.exponentialBackoff
    } = options;

    let lastError;

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        return await fn();
      } catch (error) {
        lastError = error;

        // Don't retry if not a retryable error
        const isRetryable = error.status && retryableStatuses.includes(error.status);
        const isLastAttempt = attempt === maxRetries;

        if (!isRetryable || isLastAttempt) {
          logger.warn(`[HttpClient] Not retrying: retryable=${isRetryable}, lastAttempt=${isLastAttempt}`);
          throw error;
        }

        // Calculate delay with exponential backoff and jitter
        const backoffMultiplier = exponentialBackoff ? Math.pow(2, attempt) : 1;
        const jitter = Math.random() * 0.3 * retryDelay; // 0-30% jitter to prevent thundering herd
        const delay = (retryDelay * backoffMultiplier) + jitter;

        logger.warn(
          `[HttpClient] Retry ${attempt + 1}/${maxRetries} after ${Math.round(delay)}ms. ` +
          `Error: ${error.status} - ${error.message}`
        );

        // Wait before retrying
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }

    throw lastError;
  }

  /**
   * POST with FormData and retry logic (for critical ML operations)
   */
  async postFormDataWithRetry(url, formData, retryOptions = {}) {
    return this.retryWithBackoff(
      () => this.postFormData(url, formData),
      retryOptions
    );
  }

  /**
   * POST with FormData, retry logic, AND circuit breaker (full SRE stack)
   * Use this for critical ML operations to Python API
   */
  async postFormDataResilient(url, formData, retryOptions = {}) {
    // Circuit breaker wraps the retry logic
    return this.circuitBreaker.execute(async () => {
      return this.retryWithBackoff(
        () => this.postFormData(url, formData),
        retryOptions
      );
    });
  }

  /**
   * Get circuit breaker state for health checks/monitoring
   */
  getCircuitBreakerState() {
    return this.circuitBreaker.getState();
  }
}

// Export singleton instance
const httpClient = new HttpClient();

module.exports = {
  HttpClient,
  httpClient
};
