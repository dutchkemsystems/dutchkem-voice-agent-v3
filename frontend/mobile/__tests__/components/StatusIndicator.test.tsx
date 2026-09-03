import React from 'react';
import { render } from '@testing-library/react-native';
import { StatusIndicator } from '../../src/components/StatusIndicator';

describe('StatusIndicator', () => {
  it('shows audio monitoring status', () => {
    const { getByText } = render(
      <StatusIndicator audioActive={true} videoActive={false} batteryLevel={85} />
    );

    expect(getByText('Audio')).toBeTruthy();
  });

  it('shows video monitoring status', () => {
    const { getByText } = render(
      <StatusIndicator audioActive={false} videoActive={true} batteryLevel={90} />
    );

    expect(getByText('Video')).toBeTruthy();
  });

  it('displays battery level', () => {
    const { getByText } = render(
      <StatusIndicator audioActive={true} videoActive={true} batteryLevel={75} />
    );

    expect(getByText('75%')).toBeTruthy();
  });

  it('shows green indicator when active', () => {
    const { getByTestId } = render(
      <StatusIndicator audioActive={true} videoActive={false} batteryLevel={100} />
    );

    expect(getByTestId('audio-indicator')).toBeTruthy();
  });

  it('shows red indicator when inactive', () => {
    const { getByTestId } = render(
      <StatusIndicator audioActive={false} videoActive={false} batteryLevel={100} />
    );

    expect(getByTestId('audio-indicator')).toBeTruthy();
  });
});
