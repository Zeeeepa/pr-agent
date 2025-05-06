import type { Meta, StoryObj } from '@storybook/react';
import SettingsDialog from './SettingsDialog';

const meta: Meta<typeof SettingsDialog> = {
  title: 'Components/SettingsDialog',
  component: SettingsDialog,
  parameters: {
    layout: 'fullscreen',
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof SettingsDialog>;

export const Open: Story = {
  args: {
    isOpen: true,
    onClose: () => {},
  },
};

export const Closed: Story = {
  args: {
    isOpen: false,
    onClose: () => {},
  },
};

