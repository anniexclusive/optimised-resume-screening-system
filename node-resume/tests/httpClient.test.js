/**
 * Unit tests for HttpClient service
 * Tests HTTP request abstraction and error handling
 */

// Mock axios before importing HttpClient
jest.mock('axios', () => {
  const mockAxiosInstance = {
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
    interceptors: {
      request: {
        use: jest.fn()
      },
      response: {
        use: jest.fn()
      }
    }
  };

  return {
    create: jest.fn(() => mockAxiosInstance)
  };
});

const { HttpClient } = require('../services/httpClient');
const axios = require('axios');

describe('HttpClient', () => {
  let httpClient;
  let mockAxiosInstance;

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();

    // Create mock axios instance
    mockAxiosInstance = {
      get: jest.fn(),
      post: jest.fn(),
      put: jest.fn(),
      delete: jest.fn(),
      interceptors: {
        request: {
          use: jest.fn((successHandler, errorHandler) => {
            // Return a mock deregistration function
            return () => {};
          })
        },
        response: {
          use: jest.fn((successHandler, errorHandler) => {
            // Return a mock deregistration function
            return () => {};
          })
        }
      }
    };

    // Mock axios.create to return our mock instance
    axios.create.mockReturnValue(mockAxiosInstance);

    // Create new HttpClient instance
    httpClient = new HttpClient('http://localhost:5000', 3000);
  });

  describe('Constructor', () => {
    it('should create axios instance with default config', () => {
      expect(axios.create).toHaveBeenCalledWith({
        baseURL: 'http://localhost:5000',
        timeout: 3000,
        headers: {
          'Content-Type': 'application/json'
        }
      });
    });

    it('should set up request and response interceptors', () => {
      expect(mockAxiosInstance.interceptors.request.use).toHaveBeenCalled();
      expect(mockAxiosInstance.interceptors.response.use).toHaveBeenCalled();
    });
  });

  describe('GET requests', () => {
    it('should make successful GET request', async () => {
      const mockData = { id: 1, name: 'Test' };
      mockAxiosInstance.get.mockResolvedValue({ data: mockData });

      const result = await httpClient.get('/api/test');

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/test', {});
      expect(result).toEqual(mockData);
    });

    it('should pass config options to GET request', async () => {
      const mockData = { results: [] };
      const config = { params: { page: 1 } };
      mockAxiosInstance.get.mockResolvedValue({ data: mockData });

      await httpClient.get('/api/items', config);

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/items', config);
    });

    it('should throw error on failed GET request', async () => {
      const error = new Error('Network error');
      mockAxiosInstance.get.mockRejectedValue(error);

      await expect(httpClient.get('/api/test')).rejects.toThrow('Network error');
    });
  });

  describe('POST requests', () => {
    it('should make successful POST request', async () => {
      const postData = { name: 'New Item' };
      const mockResponse = { id: 1, ...postData };
      mockAxiosInstance.post.mockResolvedValue({ data: mockResponse });

      const result = await httpClient.post('/api/items', postData);

      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/api/items', postData, {});
      expect(result).toEqual(mockResponse);
    });

    it('should pass config options to POST request', async () => {
      const postData = { name: 'Test' };
      const config = { headers: { 'X-Custom': 'value' } };
      mockAxiosInstance.post.mockResolvedValue({ data: {} });

      await httpClient.post('/api/items', postData, config);

      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/api/items', postData, config);
    });

    it('should throw error on failed POST request', async () => {
      const error = new Error('Validation error');
      mockAxiosInstance.post.mockRejectedValue(error);

      await expect(httpClient.post('/api/items', {})).rejects.toThrow('Validation error');
    });
  });

  describe('PUT requests', () => {
    it('should make successful PUT request', async () => {
      const putData = { name: 'Updated Item' };
      const mockResponse = { id: 1, ...putData };
      mockAxiosInstance.put.mockResolvedValue({ data: mockResponse });

      const result = await httpClient.put('/api/items/1', putData);

      expect(mockAxiosInstance.put).toHaveBeenCalledWith('/api/items/1', putData, {});
      expect(result).toEqual(mockResponse);
    });

    it('should throw error on failed PUT request', async () => {
      const error = new Error('Not found');
      mockAxiosInstance.put.mockRejectedValue(error);

      await expect(httpClient.put('/api/items/1', {})).rejects.toThrow('Not found');
    });
  });

  describe('DELETE requests', () => {
    it('should make successful DELETE request', async () => {
      const mockResponse = { success: true };
      mockAxiosInstance.delete.mockResolvedValue({ data: mockResponse });

      const result = await httpClient.delete('/api/items/1');

      expect(mockAxiosInstance.delete).toHaveBeenCalledWith('/api/items/1', {});
      expect(result).toEqual(mockResponse);
    });

    it('should throw error on failed DELETE request', async () => {
      const error = new Error('Forbidden');
      mockAxiosInstance.delete.mockRejectedValue(error);

      await expect(httpClient.delete('/api/items/1')).rejects.toThrow('Forbidden');
    });
  });

  describe('POST with FormData', () => {
    it('should make successful FormData POST request', async () => {
      const mockFormData = {
        getHeaders: jest.fn().mockReturnValue({ 'content-type': 'multipart/form-data' })
      };
      const mockResponse = { success: true };
      mockAxiosInstance.post.mockResolvedValue({ data: mockResponse });

      const result = await httpClient.postFormData('/api/upload', mockFormData);

      expect(mockAxiosInstance.post).toHaveBeenCalledWith(
        '/api/upload',
        mockFormData,
        { headers: { 'content-type': 'multipart/form-data' } }
      );
      expect(result).toEqual(mockResponse);
    });

    it('should handle FormData without getHeaders method', async () => {
      const mockFormData = {}; // No getHeaders method
      const mockResponse = { success: true };
      mockAxiosInstance.post.mockResolvedValue({ data: mockResponse });

      const result = await httpClient.postFormData('/api/upload', mockFormData);

      expect(mockAxiosInstance.post).toHaveBeenCalledWith(
        '/api/upload',
        mockFormData,
        { headers: {} }
      );
      expect(result).toEqual(mockResponse);
    });
  });

  describe('Error handling', () => {
    it('should handle server response errors', () => {
      const error = {
        response: {
          status: 400,
          statusText: 'Bad Request',
          data: { message: 'Invalid input' }
        }
      };

      const handled = httpClient.handleError(error);

      expect(handled).toEqual({
        status: 400,
        message: 'Invalid input',
        data: { message: 'Invalid input' }
      });
    });

    it('should handle server response errors without message', () => {
      const error = {
        response: {
          status: 500,
          statusText: 'Internal Server Error',
          data: {}
        }
      };

      const handled = httpClient.handleError(error);

      expect(handled).toEqual({
        status: 500,
        message: 'Internal Server Error',
        data: {}
      });
    });

    it('should handle request timeout errors', () => {
      const error = {
        request: {},
        message: 'timeout of 3000ms exceeded'
      };

      const handled = httpClient.handleError(error);

      expect(handled).toEqual({
        status: 503,
        message: 'Service unavailable - no response from server',
        data: null
      });
    });

    it('should handle request setup errors', () => {
      const error = {
        message: 'Invalid URL'
      };

      const handled = httpClient.handleError(error);

      expect(handled).toEqual({
        status: 500,
        message: 'Invalid URL',
        data: null
      });
    });
  });

  describe('retryWithBackoff - SRE Resilience Tests', () => {
    beforeEach(() => {
      jest.clearAllMocks();
    });

    it('should succeed on first attempt', async () => {
      const mockFn = jest.fn().mockResolvedValue('success');

      const result = await httpClient.retryWithBackoff(mockFn);

      expect(result).toBe('success');
      expect(mockFn).toHaveBeenCalledTimes(1);
    });

    it('should retry on retryable status codes', async () => {
      const mockFn = jest.fn()
        .mockRejectedValueOnce({ status: 503, message: 'Service unavailable' })
        .mockResolvedValue('success');

      const result = await httpClient.retryWithBackoff(mockFn, { maxRetries: 1, retryDelay: 10 });

      expect(result).toBe('success');
      expect(mockFn).toHaveBeenCalledTimes(2);
    });

    it('should not retry on non-retryable status codes', async () => {
      const mockFn = jest.fn().mockRejectedValue({ status: 400, message: 'Bad request' });

      await expect(
        httpClient.retryWithBackoff(mockFn, { maxRetries: 3 })
      ).rejects.toMatchObject({ status: 400 });

      expect(mockFn).toHaveBeenCalledTimes(1);
    });

    it('should stop after max retries', async () => {
      const mockFn = jest.fn().mockRejectedValue({ status: 503, message: 'Service unavailable' });

      await expect(
        httpClient.retryWithBackoff(mockFn, { maxRetries: 2, retryDelay: 10 })
      ).rejects.toMatchObject({ status: 503 });

      expect(mockFn).toHaveBeenCalledTimes(3); // Initial + 2 retries
    });
  });

  describe('postFormDataResilient - Full SRE Stack', () => {
    it('should call circuit breaker with retry logic', async () => {
      const mockFormData = { getHeaders: () => ({}) };
      mockAxiosInstance.post.mockResolvedValue({ data: 'success' });

      const result = await httpClient.postFormDataResilient('/test', mockFormData);

      expect(result).toBe('success');
      expect(mockAxiosInstance.post).toHaveBeenCalled();
    });
  });
});
