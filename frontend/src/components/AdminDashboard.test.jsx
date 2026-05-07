import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import AdminDashboard from './AdminDashboard';
import useStore from '../store/useStore';
import apiService from '../services/api';

// Mock dependencies
jest.mock('../store/useStore');
jest.mock('../services/api');
jest.mock('../firebase', () => ({
  auth: { currentUser: null },
  db: {}
}));

// Mock routing
jest.mock('react-router-dom', () => ({
  useNavigate: () => jest.fn()
}));

// Mock AdminTab
jest.mock('./tabs/AdminTab', () => () => <div data-testid="admin-tab">Admin Tab Content</div>);

describe('AdminDashboard Component', () => {
  const mockUser = { email: 'admin@example.com' };
  
  beforeEach(() => {
    jest.clearAllMocks();
    
    apiService.checkHealth.mockResolvedValue(true);

    useStore.mockReturnValue({
      user: mockUser,
      userProfile: null,
      error: null,
      clearError: jest.fn()
    });
  });

  test('renders AdminDashboard container', () => {
    render(<AdminDashboard />);
    
    expect(screen.getByText('System Admin Console')).toBeInTheDocument();
    expect(screen.getByTestId('admin-tab')).toBeInTheDocument();
  });
});

