/**
 * Unit tests for Circuit Breaker
 * Tests resilience patterns for SRE best practices
 */

const CircuitBreaker = require('../utils/circuitBreaker');

describe('CircuitBreaker', () => {
  let circuitBreaker;

  beforeEach(() => {
    circuitBreaker = new CircuitBreaker({
      name: 'TestCircuit',
      failureThreshold: 3,
      successThreshold: 2,
      timeout: 100 // Short timeout for testing
    });
  });

  describe('Constructor', () => {
    it('should initialize with default config', () => {
      const cb = new CircuitBreaker();
      const state = cb.getState();

      expect(state.state).toBe('CLOSED');
      expect(state.failureCount).toBe(0);
      expect(state.successCount).toBe(0);
    });

    it('should initialize with custom config', () => {
      expect(circuitBreaker.failureThreshold).toBe(3);
      expect(circuitBreaker.successThreshold).toBe(2);
      expect(circuitBreaker.timeout).toBe(100);
    });
  });

  describe('CLOSED State', () => {
    it('should execute function successfully in CLOSED state', async () => {
      const mockFn = jest.fn().mockResolvedValue('success');

      const result = await circuitBreaker.execute(mockFn);

      expect(result).toBe('success');
      expect(mockFn).toHaveBeenCalledTimes(1);
      expect(circuitBreaker.getState().state).toBe('CLOSED');
    });

    it('should increment failure count on error', async () => {
      const mockFn = jest.fn().mockRejectedValue(new Error('Test error'));

      await expect(circuitBreaker.execute(mockFn)).rejects.toThrow('Test error');

      expect(circuitBreaker.getState().failureCount).toBe(1);
      expect(circuitBreaker.getState().state).toBe('CLOSED');
    });

    it('should transition to OPEN after reaching failure threshold', async () => {
      const mockFn = jest.fn().mockRejectedValue(new Error('Test error'));

      // Trigger failures to reach threshold
      for (let i = 0; i < 3; i++) {
        try {
          await circuitBreaker.execute(mockFn);
        } catch (e) {
          // Expected
        }
      }

      expect(circuitBreaker.getState().state).toBe('OPEN');
      expect(circuitBreaker.getState().failureCount).toBe(3);
    });
  });

  describe('OPEN State', () => {
    beforeEach(async () => {
      // Trigger circuit to open
      const mockFn = jest.fn().mockRejectedValue(new Error('Test error'));
      for (let i = 0; i < 3; i++) {
        try {
          await circuitBreaker.execute(mockFn);
        } catch (e) {
          // Expected
        }
      }
    });

    it('should fail fast when circuit is OPEN', async () => {
      const mockFn = jest.fn().mockResolvedValue('success');

      await expect(circuitBreaker.execute(mockFn)).rejects.toThrow('Circuit breaker is OPEN');

      expect(mockFn).not.toHaveBeenCalled();
    });

    it('should transition to HALF_OPEN after timeout', async () => {
      // Wait for timeout
      await new Promise(resolve => setTimeout(resolve, 150));

      const mockFn = jest.fn().mockResolvedValue('success');
      await circuitBreaker.execute(mockFn);

      expect(circuitBreaker.getState().state).toBe('HALF_OPEN');
    });
  });

  describe('HALF_OPEN State', () => {
    beforeEach(async () => {
      // Open circuit
      const failFn = jest.fn().mockRejectedValue(new Error('Test error'));
      for (let i = 0; i < 3; i++) {
        try {
          await circuitBreaker.execute(failFn);
        } catch (e) {
          // Expected
        }
      }

      // Wait for timeout to move to HALF_OPEN
      await new Promise(resolve => setTimeout(resolve, 150));
    });

    it('should close circuit after success threshold', async () => {
      const mockFn = jest.fn().mockResolvedValue('success');

      // First success moves to HALF_OPEN
      await circuitBreaker.execute(mockFn);
      expect(circuitBreaker.getState().state).toBe('HALF_OPEN');

      // Second success closes circuit
      await circuitBreaker.execute(mockFn);
      expect(circuitBreaker.getState().state).toBe('CLOSED');
      expect(circuitBreaker.getState().successCount).toBe(0); // Reset
    });

    it('should reopen on failure in HALF_OPEN state', async () => {
      const successFn = jest.fn().mockResolvedValue('success');
      const failFn = jest.fn().mockRejectedValue(new Error('Test error'));

      // Move to HALF_OPEN
      await circuitBreaker.execute(successFn);
      expect(circuitBreaker.getState().state).toBe('HALF_OPEN');

      // Failure should immediately open circuit
      try {
        await circuitBreaker.execute(failFn);
      } catch (e) {
        // Expected
      }

      expect(circuitBreaker.getState().state).toBe('OPEN');
    });
  });

  describe('getState', () => {
    it('should return current state information', () => {
      const state = circuitBreaker.getState();

      expect(state).toHaveProperty('state');
      expect(state).toHaveProperty('failureCount');
      expect(state).toHaveProperty('successCount');
      expect(state).toHaveProperty('nextAttempt');
    });
  });

  describe('reset', () => {
    it('should reset circuit breaker to CLOSED state', async () => {
      // Open circuit
      const mockFn = jest.fn().mockRejectedValue(new Error('Test error'));
      for (let i = 0; i < 3; i++) {
        try {
          await circuitBreaker.execute(mockFn);
        } catch (e) {
          // Expected
        }
      }

      expect(circuitBreaker.getState().state).toBe('OPEN');

      // Reset
      circuitBreaker.reset();

      const state = circuitBreaker.getState();
      expect(state.state).toBe('CLOSED');
      expect(state.failureCount).toBe(0);
      expect(state.successCount).toBe(0);
    });
  });
});
