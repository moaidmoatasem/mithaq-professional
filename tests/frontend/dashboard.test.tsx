import { describe, it, expect, beforeAll, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import ScannerDashboard from '../../src/components/ScannerDashboard';

// Mock Web Crypto API for hashing
beforeAll(() => {
  Object.defineProperty(global, 'crypto', {
    value: {
      subtle: {
        digest: async () => new Uint8Array([1, 2, 3]).buffer
      }
    }
  });

  // Mock global fetch
  global.fetch = vi.fn().mockImplementation(() =>
    Promise.resolve({
      ok: true,
      json: () => Promise.resolve({
        rotation_required: true,
        liveness: { uptime_seconds: 10, pid: 1234 },
        readiness: {
          database: { status: "OK", latency_ms: 1.2 },
          inference_runtime: { status: "OK", latency_ms: 2.5 }
        }
      }),
    })
  );
});

describe('Cherenkov Frontend Unit Tests', () => {
  it('renders security credentials locker when rotation is required', async () => {
    render(<ScannerDashboard />);

    // Check credentials locker elements
    expect(screen.getByText('Security Initialization Blocker')).toBeDefined();
    expect(screen.getByText('Rotate Credentials & Unlock')).toBeDefined();
    expect(screen.getByPlaceholderText('Minimum 8 characters...')).toBeDefined();
  });

  it('allows user to input passphrase', async () => {
    render(<ScannerDashboard />);

    const input = screen.getByPlaceholderText('Minimum 8 characters...') as HTMLInputElement;
    fireEvent.change(input, { target: { value: 'mySuperPassphrase123' } });

    expect(input.value).toBe('mySuperPassphrase123');
  });

  it('validates too short passphrase and displays error message', async () => {
    render(<ScannerDashboard />);

    const input = screen.getByPlaceholderText('Minimum 8 characters...') as HTMLInputElement;
    fireEvent.change(input, { target: { value: 'short' } });

    const button = screen.getByText('Rotate Credentials & Unlock');
    fireEvent.click(button);

    expect(screen.getByText('Passphrase must be at least 8 characters long.')).toBeDefined();
  });
});
