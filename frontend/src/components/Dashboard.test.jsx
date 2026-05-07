import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Dashboard from './Dashboard';
import useStore from '../store/useStore';
import apiService from '../services/api';

// Mock dependencies
jest.mock('../store/useStore');
jest.mock('../services/api');
jest.mock('../firebase', () => ({
  auth: { currentUser: null },
}));

// Mock firebase/auth
jest.mock('firebase/auth', () => ({
  signOut: jest.fn(),
  getAuth: jest.fn(),
}));

// Mock child tabs to simplify the test
jest.mock('./tabs/LeaderboardTab', () => () => <div data-testid="leaderboard-tab">Leaderboard Tab Content</div>);
jest.mock('./tabs/AnalyticsTab', () => () => <div data-testid="analytics-tab">Analytics Tab Content</div>);
jest.mock('./tabs/StoreTab', () => () => <div data-testid="store-tab">Store Tab Content</div>);

describe('Dashboard Component', () => {
  const mockUser = { email: 'user@example.com' };
  const mockUserProfile = { flat_id: '101' };

  beforeEach(() => {
    // Reset mocks before each test
    jest.clearAllMocks();

    apiService.checkHealth.mockResolvedValue(true);

    // Mock store implementation
    useStore.mockReturnValue({
      user: mockUser,
      userProfile: mockUserProfile,
      error: null,
      clearError: jest.fn()
    });
  });

  test('renders the Dashboard header correctly', async () => {
    render(<Dashboard />);
    
    // Check branding
    expect(screen.getByText('AquaSync')).toBeInTheDocument();
    
    // Check profile info
    expect(screen.getByText('Flat 101')).toBeInTheDocument();
    expect(screen.getByText('user@example.com')).toBeInTheDocument();
    
    // Verify API health check
    await waitFor(() => {
      expect(screen.getByText(/Connected/i)).toBeInTheDocument();
    });
  });

  test('renders the error banner if error is present in store', () => {
    const clearErrorMock = jest.fn();
    useStore.mockReturnValue({
      user: mockUser,
      userProfile: mockUserProfile,
      error: 'Test Error Message',
      clearError: clearErrorMock
    });

    render(<Dashboard />);
    
    expect(screen.getByText('Test Error Message')).toBeInTheDocument();
    const dismissBtn = screen.getByText('Dismiss');
    
    fireEvent.click(dismissBtn);
    expect(clearErrorMock).toHaveBeenCalled();
  });

  test('navigates tabs correctly', () => {
    render(<Dashboard />);
    
    // Initial tab should be leaderboard
    expect(screen.getByTestId('leaderboard-tab')).toBeInTheDocument();
    expect(screen.queryByTestId('analytics-tab')).not.toBeInTheDocument();
    
    // Click analytics tab
    fireEvent.click(screen.getByText(/My Eco-Analytics/i));
    expect(screen.getByTestId('analytics-tab')).toBeInTheDocument();
    expect(screen.queryByTestId('leaderboard-tab')).not.toBeInTheDocument();

    // Click store tab
    fireEvent.click(screen.getByText(/Swag Store/i));
    expect(screen.getByTestId('store-tab')).toBeInTheDocument();
    expect(screen.queryByTestId('analytics-tab')).not.toBeInTheDocument();
  });
});
