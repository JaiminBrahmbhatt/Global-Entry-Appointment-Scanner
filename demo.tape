# VHS tape script for global-entry-scanner demo
Output docs/demo.gif

Set Shell "zsh"
Set FontSize 15
Set Width 1000
Set Height 560
Set Theme "Dracula"
Set Padding 24
Set TypingSpeed 60ms
Set PlaybackSpeed 1.0

# Clean up environment silently — set a tidy prompt, activate venv
Hide
Type "source /Users/jaiminb/Code/Global-Entry-Appointment-Scanner/.venv/bin/activate"
Enter
Sleep 200ms
Type "export PS1='$ '"
Enter
Sleep 200ms
Type "clear"
Enter
Sleep 300ms
Show

# Step 1: List locations (Rich table)
Type "global-entry-scanner locations"
Enter
Sleep 5s
Type "clear"
Enter
Sleep 400ms

# Step 2: Run setup — step panels appear at each stage
Type "global-entry-scanner setup"
Enter
Sleep 5s

# Select the first city in the list with Space, confirm with Enter
Space
Sleep 600ms
Enter
Sleep 1500ms

# Step 2 panel: notification channels — accept default (console)
Enter
Sleep 1500ms

# Step 3 panel (no channel config needed for console)
# Step 4 panel + summary appear automatically
# Let the "Config saved" message sit for a moment
Sleep 1500ms
Type "clear"
Enter
Sleep 400ms

# Step 3: Run scan — Rich Live dashboard
Type "global-entry-scanner scan"
Enter
Sleep 9s

# Stop cleanly
Ctrl+C
Sleep 1.5s
