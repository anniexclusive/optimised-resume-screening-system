/**
 * Mock for form-data module
 * Used in Jest tests
 */

class FormData {
  constructor() {
    this.data = {};
    // Make append a jest mock function
    this.append = jest.fn((key, value, options) => {
      if (!this.data[key]) {
        this.data[key] = [];
      }
      this.data[key].push({ value, options });
    });
  }

  getHeaders() {
    return {
      'content-type': 'multipart/form-data; boundary=---MockBoundary123'
    };
  }

  getData() {
    return this.data;
  }
}

module.exports = FormData;
