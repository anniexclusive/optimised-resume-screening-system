/**
 * Circuit Breaker Pattern Implementation
 *
 * SRE Best Practice: Prevent cascading failures in microservices
 *
 * States:
 * - CLOSED: Normal operation, requests pass through
 * - OPEN: Failures exceeded threshold, requests fail fast
 * - HALF_OPEN: Testing if service recovered
 *
 * Benefits:
 * - Fail fast when downstream service is down
 * - Give failing services time to recover
 * - Prevent resource exhaustion from repeated failed requests
 */

const logger = require('./logger');

class CircuitBreaker {
  constructor(options = {}) {
    this.failureThreshold = options.failureThreshold || 5; // Open after 5 failures
    this.successThreshold = options.successThreshold || 2; // Close after 2 successes in half-open
    this.timeout = options.timeout || 60000; // 60 seconds before trying again
    this.name = options.name || 'CircuitBreaker';

    this.state = 'CLOSED'; // CLOSED, OPEN, HALF_OPEN
    this.failureCount = 0;
    this.successCount = 0;
    this.nextAttempt = Date.now();

    logger.info(`[${this.name}] Initialized`, {
      failureThreshold: this.failureThreshold,
      successThreshold: this.successThreshold,
      timeout: this.timeout
    });
  }

  /**
   * Execute function with circuit breaker protection
   */
  async execute(fn) {
    if (this.state === 'OPEN') {
      // Check if timeout has passed
      if (Date.now() < this.nextAttempt) {
        const error = new Error('Circuit breaker is OPEN - failing fast');
        error.circuitBreakerOpen = true;
        logger.warn(`[${this.name}] Circuit OPEN - failing fast`);
        throw error;
      }

      // Timeout passed, try half-open
      this.state = 'HALF_OPEN';
      logger.info(`[${this.name}] Circuit moved to HALF_OPEN - testing recovery`);
    }

    try {
      const result = await fn();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  /**
   * Handle successful execution
   */
  onSuccess() {
    this.failureCount = 0;

    if (this.state === 'HALF_OPEN') {
      this.successCount++;
      logger.info(`[${this.name}] Success in HALF_OPEN (${this.successCount}/${this.successThreshold})`);

      if (this.successCount >= this.successThreshold) {
        this.state = 'CLOSED';
        this.successCount = 0;
        logger.info(`[${this.name}] Circuit CLOSED - service recovered`);
      }
    }
  }

  /**
   * Handle failed execution
   */
  onFailure() {
    this.failureCount++;
    logger.warn(`[${this.name}] Failure recorded (${this.failureCount}/${this.failureThreshold})`);

    if (this.state === 'HALF_OPEN') {
      // Immediately open on failure in half-open
      this.state = 'OPEN';
      this.nextAttempt = Date.now() + this.timeout;
      this.successCount = 0;
      logger.error(`[${this.name}] Circuit OPEN - service still failing`);
    } else if (this.failureCount >= this.failureThreshold) {
      this.state = 'OPEN';
      this.nextAttempt = Date.now() + this.timeout;
      logger.error(`[${this.name}] Circuit OPEN - threshold exceeded`, {
        failureCount: this.failureCount,
        nextAttemptIn: `${this.timeout}ms`
      });
    }
  }

  /**
   * Get current circuit breaker state
   */
  getState() {
    return {
      state: this.state,
      failureCount: this.failureCount,
      successCount: this.successCount,
      nextAttempt: this.state === 'OPEN' ? new Date(this.nextAttempt).toISOString() : null
    };
  }

  /**
   * Manually reset circuit breaker
   */
  reset() {
    this.state = 'CLOSED';
    this.failureCount = 0;
    this.successCount = 0;
    logger.info(`[${this.name}] Circuit manually reset to CLOSED`);
  }
}

module.exports = CircuitBreaker;
