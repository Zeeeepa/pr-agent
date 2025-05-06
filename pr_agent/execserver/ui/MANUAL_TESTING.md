# PR Review Automator UI Manual Testing Checklist

This document provides a checklist for manual testing of the PR Review Automator UI.

## General UI

- [ ] Verify that the UI loads correctly without errors
- [ ] Check that all tabs (Home, Event Triggers, GitHub Workflows, AI Assistant) are visible
- [ ] Verify that the theme toggle button works and changes the UI theme
- [ ] Check that the settings button opens the settings dialog
- [ ] Verify that the UI is responsive and works on different screen sizes
- [ ] Check that all UI elements are properly aligned and styled

## Home Tab

- [ ] Verify that the Active Triggers card shows the correct number of triggers
- [ ] Check that the System Status card shows the correct status
- [ ] Verify that the "Last updated" timestamp is current
- [ ] Check that the "Manage Triggers" button navigates to the Event Triggers tab

## Event Triggers Tab

- [ ] Verify that the list of triggers loads correctly
- [ ] Check that active and inactive triggers are properly indicated
- [ ] Verify that the "Create Trigger" button works
- [ ] Check that editing a trigger works correctly
- [ ] Verify that toggling a trigger's status works
- [ ] Check that deleting a trigger works

## GitHub Workflows Tab

- [ ] Verify that the list of workflows loads correctly
- [ ] Check that workflow status is properly indicated
- [ ] Verify that workflow details can be viewed
- [ ] Check that triggering a workflow works correctly

## AI Assistant Tab

- [ ] Verify that the chat interface loads correctly
- [ ] Check that sending messages works
- [ ] Verify that AI responses are displayed correctly
- [ ] Check that the chat history is preserved

## Settings Dialog

- [ ] Verify that the settings dialog opens and closes correctly
- [ ] Check that all form fields are properly labeled and accessible
- [ ] Verify that validation works for required fields
- [ ] Check that the "Validate" button tests the credentials correctly
- [ ] Verify that the "Save" button saves the settings
- [ ] Check that settings are persisted between page reloads

## Error Handling

- [ ] Verify that API errors are properly handled and displayed
- [ ] Check that form validation errors are clearly indicated
- [ ] Verify that network connectivity issues are handled gracefully
- [ ] Check that the UI recovers properly after errors

## Performance

- [ ] Verify that the UI loads quickly (under 3 seconds)
- [ ] Check that interactions are responsive with no noticeable lag
- [ ] Verify that large data sets (many triggers/workflows) load efficiently
- [ ] Check that the UI remains responsive during API calls

## Accessibility

- [ ] Verify that all interactive elements are keyboard accessible
- [ ] Check that focus states are visible for all interactive elements
- [ ] Verify that screen readers can access all content
- [ ] Check that color contrast meets WCAG AA standards
- [ ] Verify that form inputs have proper labels and ARIA attributes

## Cross-Browser Testing

- [ ] Verify that the UI works correctly in Chrome
- [ ] Check that the UI works correctly in Firefox
- [ ] Verify that the UI works correctly in Safari
- [ ] Check that the UI works correctly in Edge

## Mobile Testing

- [ ] Verify that the UI is usable on mobile devices
- [ ] Check that touch interactions work correctly
- [ ] Verify that the layout adapts appropriately to small screens
- [ ] Check that forms are usable on mobile devices

## Integration Testing

- [ ] Verify that changes made in the UI are reflected in the backend
- [ ] Check that real GitHub webhooks trigger the appropriate actions
- [ ] Verify that workflow triggers work with actual GitHub workflows
- [ ] Check that the UI correctly displays real-time updates from the backend

## Regression Testing

- [ ] Verify that previously fixed issues have not regressed
- [ ] Check that all features from previous versions still work correctly
- [ ] Verify that UI appearance is consistent with previous versions
- [ ] Check that performance has not degraded from previous versions

