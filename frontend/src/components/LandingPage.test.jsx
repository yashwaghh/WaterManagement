import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import LandingPage from './LandingPage';

describe('LandingPage Component', () => {
  test('renders the landing page hero text', () => {
    render(
      <BrowserRouter>
        <LandingPage />
      </BrowserRouter>
    );
    
    // Check if the main heading is present
    const headingElement = screen.getByText(/Intelligent water management/i);
    expect(headingElement).toBeInTheDocument();
    
    // Check if the logo/brand name is present
    const brandElements = screen.getAllByText(/AquaSync/i);
    expect(brandElements.length).toBeGreaterThan(0);

    // Check if the Get Started button is present
    const getStartedLink = screen.getByText(/Get Started/i);
    expect(getStartedLink).toBeInTheDocument();
  });

  test('renders the features section', () => {
    render(
      <BrowserRouter>
        <LandingPage />
      </BrowserRouter>
    );
    
    const featureHeading = screen.getByText(/Enterprise-grade infrastructure for everyday users/i);
    expect(featureHeading).toBeInTheDocument();
    
    // Check for specific feature cards
    expect(screen.getByText(/Granular Analytics/i)).toBeInTheDocument();
    expect(screen.getByText(/Gamified Conservation/i)).toBeInTheDocument();
    expect(screen.getByText(/Secure & Transparent/i)).toBeInTheDocument();
  });
});
