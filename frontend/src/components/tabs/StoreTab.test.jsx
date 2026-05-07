import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import StoreTab from './StoreTab';
import apiService from '../../services/api';
import useStore from '../../store/useStore';

jest.mock('../../services/api');
jest.mock('../../store/useStore');

describe('StoreTab Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    useStore.mockReturnValue({
      userProfile: { flat_id: '101', score: 500 }
    });
  });

  test('renders user score correctly', async () => {
    render(<StoreTab />);
    
    // The user's score 500 should be visible
    expect(screen.getByText('500')).toBeInTheDocument();
  });

  test('fetches flat info', async () => {
    apiService.getLeaderboard.mockResolvedValue([
      { flat_id: '101', score: 500 }
    ]);
    
    render(<StoreTab />);
    
    await waitFor(() => {
      // 500 points from API syncs over UI text
      expect(screen.getByText('500')).toBeInTheDocument();
    });
  });
});
