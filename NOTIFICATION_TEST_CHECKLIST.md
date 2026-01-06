# Browser Notification Testing Checklist

This document provides a comprehensive testing checklist for validating the browser notification functionality.

## Prerequisites

1. Server is running (via `docker-compose up`)
2. Access the application at `https://localhost:8765`
3. Accept the self-signed SSL certificate warning
4. Create or login to a user account

## Initial Permission Test

- [ ] **First-time permission request**
  - [ ] On first login, browser asks for notification permission
  - [ ] Clicking "Allow" enables notifications
  - [ ] Clicking "Block" disables notifications
  - [ ] Permission choice is remembered

## Notification Settings UI Test

- [ ] **Access notification settings**
  - [ ] Click the ⚙ menu button (bottom left)
  - [ ] Click "Notification Settings"
  - [ ] Modal opens showing notification settings

- [ ] **Settings UI displays correctly**
  - [ ] "Enable Browser Notifications" checkbox is visible
  - [ ] "Enable Notification Sounds" checkbox is visible
  - [ ] "Notification Mode" dropdown is visible with options: All Messages, Mentions Only, None
  - [ ] "Message Sound" dropdown is visible with options: Soft Ping, Gentle Chime, Subtle Pop
  - [ ] "Call Sound" dropdown is visible with options: Classic Ring, Modern Tone, Upbeat Call
  - [ ] Test buttons are visible for both message and call sounds

- [ ] **Settings persistence**
  - [ ] Toggle notifications on/off - setting persists after page reload
  - [ ] Change notification mode - setting persists after page reload
  - [ ] Change sound options - settings persist after page reload

## Sound Test

- [ ] **Message sounds**
  - [ ] Click "Test" button for "Soft Ping" - sound plays
  - [ ] Click "Test" button for "Gentle Chime" - sound plays
  - [ ] Click "Test" button for "Subtle Pop" - sound plays
  - [ ] Each sound is distinct and appropriate

- [ ] **Call sounds**
  - [ ] Click "Test" button for "Classic Ring" - sound plays and loops
  - [ ] Click "Test" button for "Modern Tone" - sound plays and loops
  - [ ] Click "Test" button for "Upbeat Call" - sound plays and loops
  - [ ] Call sounds stop after 3 seconds (test duration)

## Message Notification Test

### Setup
1. Create two user accounts (User A and User B)
2. Add each other as friends
3. Start a DM conversation

### Test Cases

- [ ] **Notification when window is in background**
  - [ ] User A sends a message
  - [ ] User B switches to another tab/window
  - [ ] User A sends another message
  - [ ] User B receives desktop notification popup
  - [ ] Notification shows sender name and message preview
  - [ ] Clicking notification brings chat window to focus
  - [ ] Notification auto-closes after 5 seconds

- [ ] **No notification when window is visible**
  - [ ] User A sends a message
  - [ ] User B has chat window visible and active
  - [ ] User A sends another message
  - [ ] User B does NOT receive notification popup (sound may play)

- [ ] **Notification mode: All Messages**
  - [ ] Set notification mode to "All Messages"
  - [ ] Switch to another tab
  - [ ] Receive message without @mention
  - [ ] Notification appears

- [ ] **Notification mode: Mentions Only**
  - [ ] Set notification mode to "Mentions Only"
  - [ ] Switch to another tab
  - [ ] Receive message without @mention
  - [ ] No notification appears
  - [ ] Receive message with @username mention
  - [ ] Notification appears

- [ ] **Notification mode: None**
  - [ ] Set notification mode to "None"
  - [ ] Switch to another tab
  - [ ] Receive any message
  - [ ] No notification appears

## Voice Call Notification Test

- [ ] **Incoming call notification**
  - [ ] User A calls User B
  - [ ] User B receives notification popup "Incoming Voice Call from [User A]"
  - [ ] Call sound plays (and loops until answered/rejected)
  - [ ] Clicking notification focuses the window
  - [ ] Accepting call stops the notification sound
  - [ ] Rejecting call stops the notification sound

- [ ] **Multiple calls**
  - [ ] Receive multiple calls in sequence
  - [ ] Each call triggers its own notification
  - [ ] Call sounds properly stop/start for each call

## Server Message Notification Test

- [ ] **In server channels**
  - [ ] Join a server with multiple members
  - [ ] Navigate to a text channel
  - [ ] Switch to another tab
  - [ ] Another user sends a message
  - [ ] Notification appears (respects notification mode)

- [ ] **Mention detection in servers**
  - [ ] Set notification mode to "Mentions Only"
  - [ ] Be in a server channel
  - [ ] Switch to another tab
  - [ ] Another user sends message with @yourUsername
  - [ ] Notification appears

## Edge Cases and Error Handling

- [ ] **Blocked permissions**
  - [ ] Block notifications in browser settings
  - [ ] Try to enable notifications in app settings
  - [ ] App handles gracefully (no errors in console)
  - [ ] Re-requesting permission works when unblocked

- [ ] **Rapid message spam**
  - [ ] Receive many messages quickly
  - [ ] Notifications appear for each (or are properly throttled)
  - [ ] No performance issues
  - [ ] Sounds play correctly

- [ ] **Long messages**
  - [ ] Receive message longer than 50 characters
  - [ ] Notification shows truncated message with "..."
  - [ ] Full message visible when clicking notification

- [ ] **Special characters**
  - [ ] Receive messages with emojis, special characters
  - [ ] Notifications display correctly

## Browser Compatibility

Test in multiple browsers (if possible):

- [ ] Chrome/Chromium
- [ ] Firefox
- [ ] Safari (macOS)
- [ ] Edge
- [ ] Opera

## Cleanup

- [ ] Close notification settings modal
- [ ] Log out
- [ ] Verify settings are preserved on next login

## Success Criteria

✅ All notification types work correctly
✅ Settings UI is functional and intuitive
✅ Permissions are properly requested and handled
✅ Sounds play correctly
✅ Notifications respect visibility state
✅ All notification modes work as expected
✅ No console errors during any test
✅ Settings persist across sessions
