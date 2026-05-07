import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import AdminTab from './AdminTab';
import apiService from '../../services/api';

jest.mock('../../services/api');

describe('AdminTab Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('toggles simulator state', async () => {
    apiService.adminSimulatorStatus.mockResolvedValue({ 
      status: 'success', 
      simulator_active: true, 
      thread_alive: true 
    });
    
    // First, verify initial fetch happens
    render(<AdminTab />);
    
    await waitFor(() => {
      expect(screen.getByText('Running')).toBeInTheDocument();
    });

    // Mock the toggle API
    apiService.adminSimulatorToggle.mockResolvedValue({
      status: 'success',
      simulator_active: false,
      message: 'Simulator stopped'
    });
    
    const stopBtn = screen.getByText('Stop Simulator');
    fireEvent.click(stopBtn);
    
    await waitFor(() => {
      expect(apiService.adminSimulatorToggle).toHaveBeenCalledWith('stop');
      expect(screen.getByText('Simulator stopped')).toBeInTheDocument();
    });
  });

  test('triggers reset cycle', async () => {
    apiService.adminSimulatorStatus.mockResolvedValue({ status: 'success', simulator_active: false });
    apiService.adminTriggerReset.mockResolvedValue({ status: 'success', message: 'Cycle advanced' });
    
    render(<AdminTab />);
    
    // Simulate user asking for auth, but for simple test, let's just click it
    // Note: The UI requires auth prompt 'AQUASYNC_ADMIN'.
    window.prompt = jest.fn().mockReturnValue('AQUASYNC_ADMIN');
    
    const triggerBtn = screen.getByText('Trigger End of Day');
    fireEvent.click(triggerBtn);
    
    await waitFor(() => {
      expect(apiService.adminTriggerReset).toHaveBeenCalled();
      expect(screen.getByText('Cycle advanced')).toBeInTheDocument();
    });
  });
});
