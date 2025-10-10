import { render, screen } from '@testing-library/react';
import App from './App';

test('renders App component without crashing', () => {
  const { container } = render(<App />);
  expect(container).toBeInTheDocument();
});

test('renders Resume Screening heading', () => {
  render(<App />);
  const headingElement = screen.getAllByText(/RESUME SCREENING/i)[0];
  expect(headingElement).toBeInTheDocument();
});

test('renders Resume Screening System title', () => {
  render(<App />);
  const titleElement = screen.getAllByText(/Resume Screening System/i)[0];
  expect(titleElement).toBeInTheDocument();
});

test('renders Dashboard menu item', () => {
  render(<App />);
  // Dashboard appears multiple times, check that at least one exists
  const dashboardElements = screen.getAllByText(/Dashboard/i);
  expect(dashboardElements.length).toBeGreaterThan(0);
});
