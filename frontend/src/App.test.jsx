import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

// Mock the Zustand store
jest.mock('./store/useStore', () => ({
  useStore: () => ({
    user: null,
    userProfile: null,
    authLoading: false,
    setUser: jest.fn(),
    setUserProfile: jest.fn(),
    setAuthLoading: jest.fn()
  })
}));

// Mock the Firebase services
jest.mock('./firebase', () => ({
  auth: { currentUser: null },
  db: {},
}));

jest.mock('firebase/auth', () => {
  return {
    onAuthStateChanged: () => {
      return () => {}; // unsubscribe function
    },
    getAuth: () => ({})
  };
});

jest.mock('firebase/database', () => ({
  ref: jest.fn(),
  get: jest.fn(),
}));

test('renders landing page for unauthenticated users', () => {
  render(<App />);
  // Matches "AquaSync" text typically found on the App Header/Landing Page
  const brandingElements = screen.getAllByText(/AquaSync/i);
  expect(brandingElements.length).toBeGreaterThan(0);
});
