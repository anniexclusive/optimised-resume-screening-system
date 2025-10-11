/**
 * HTTP Client Service
 * Abstraction layer for HTTP requests using axios
 * Implements Dependency Inversion Principle
 */

const axios = require('axios');
const config = require('../config/api.config');

class HttpClient {
  constructor(baseURL = null, timeout = null) {
    this.client = axios.create({
      baseURL: baseURL || config.pythonApi.baseUrl,
      timeout: timeout || config.pythonApi.timeout,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        console.log(`[HttpClient] ${config.method.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('[HttpClient] Request error:', error.message);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        console.log(`[HttpClient] Response: ${response.status} ${response.statusText}`);
        return response;
      },
      (error) => {
        const errorMessage = error.response
          ? `${error.response.status} - ${error.response.statusText}`
          : error.message;
        console.error(`[HttpClient] Response error: ${errorMessage}`);
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
}

// Export singleton instance
const httpClient = new HttpClient();

module.exports = {
  HttpClient,
  httpClient
};
