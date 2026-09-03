import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { InterviewTrigger } from '../../src/components/InterviewTrigger';

describe('InterviewTrigger', () => {
  it('renders inactive state by default', () => {
    const { getByText } = render(
      <InterviewTrigger isActive={false} confidence={0} onPress={jest.fn()} />
    );

    expect(getByText('Interview Detected')).toBeTruthy();
    expect(getByText('Not Active')).toBeTruthy();
  });

  it('renders active state when triggered', () => {
    const { getByText } = render(
      <InterviewTrigger isActive={true} confidence={0.95} onPress={jest.fn()} />
    );

    expect(getByText('Interview Detected')).toBeTruthy();
    expect(getByText(/95%/)).toBeTruthy();
  });

  it('calls onPress when pressed', () => {
    const mockPress = jest.fn();
    const { getByRole } = render(
      <InterviewTrigger isActive={true} confidence={0.8} onPress={mockPress} />
    );

    fireEvent.press(getByRole('button'));
    expect(mockPress).toHaveBeenCalledTimes(1);
  });

  it('displays confidence as percentage', () => {
    const { getByText } = render(
      <InterviewTrigger isActive={true} confidence={0.72} onPress={jest.fn()} />
    );

    expect(getByText(/72%/)).toBeTruthy();
  });

  it('shows disabled button when not active', () => {
    const mockPress = jest.fn();
    const { getByRole } = render(
      <InterviewTrigger isActive={false} confidence={0} onPress={mockPress} />
    );

    const button = getByRole('button');
    fireEvent.press(button);
    expect(mockPress).not.toHaveBeenCalled();
  });
});
