import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import LeaderboardTab from './LeaderboardTab';
import apiService from '../../services/api';

jest.mock('../../services/api');

describe('LeaderboardTab Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders leaderboard loading state', () => {
    apiService.getLeaderboard.mockReturnValue(new Promise(() => {})); // Never resolves to show loading
    render(<LeaderboardTab />);
    
    expect(screen.getByText(/Eco-Warriors/i)).toBeInTheDocument();
  });

  test('renders top flats from API', async () => {
    const mockData = [
      { flat_id: '101', score: 95, previous_rank: 2, rank: 1, savings_percent: 15 },
      { flat_id: '102', score: 80, previous_rank: 1, rank: 2, savings_percent: 5 },
    ];
    apiService.getLeaderboard.mockResolvedValue(mockData);

    render(<LeaderboardTab />);
    
    await waitFor(() => {
      expect(screen.getByText('Flat 101')).toBeInTheDocument();
      expect(screen.getByText('Flat 102')).toBeInTheDocument();
      expect(screen.getByText('95 pts')).toBeInTheDocument();
    });
  });

  test('renders empty state if no leaderboard data', async () => {
    apiService.getLeaderboard.mockResolvedValue([]);
    
    render(<LeaderboardTab />);
    
    await waitFor(() => {
      expect(screen.getByText(/No leaderboard data available yet/i)).toBeInTheDocument();
    });
  });
});
