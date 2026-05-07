import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import AnalyticsTab from './AnalyticsTab';
import apiService from '../../services/api';
import useStore from '../../store/useStore';

jest.mock('../../services/api');
jest.mock('../../store/useStore');
jest.mock('react-chartjs-2', () => ({
  Bar: () => <div data-testid="bar-chart" />,
  Line: () => <div data-testid="line-chart" />,
  Doughnut: () => <div data-testid="doughnut-chart" />
}));

describe('AnalyticsTab Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    useStore.mockReturnValue({
      userProfile: { flat_id: '101' }
    });
  });

  test('fetch and render analytics data', async () => {
    const mockReport = {
      daily_total_liters: 150,
      monthly_total_liters: 4500,
      daily_historical: [100, 200, 150],
      leak_risk: false
    };
    
    apiService.getReport.mockResolvedValue(mockReport);
    apiService.generateReport.mockResolvedValue({}); // Mocks button action later
    
    render(<AnalyticsTab />);
    
    await waitFor(() => {
      // It should display daily usage
      expect(screen.getByText('150 L')).toBeInTheDocument();
      expect(screen.getByText(/Daily Consumption/i)).toBeInTheDocument();
      // Charts should render
      expect(screen.getAllByTestId('bar-chart').length).toBeGreaterThan(0);
    });
  });

  test('show error if analytics fails', async () => {
    apiService.getReport.mockRejectedValue(new Error('API Down'));
    
    render(<AnalyticsTab />);
    
    await waitFor(() => {
      expect(screen.getByText(/Failed to load analytics/i)).toBeInTheDocument();
    });
  });
});
