# VHS tape script for global-entry-scanner demo
Output docs/demo.gif

Set Shell "zsh"
Set FontSize 15
Set Width 900
Set Height 480
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

# Step 1: Run setup
Type "global-entry-scanner setup"
Enter
Sleep 4s

# Select the first city in the list with Space, confirm with Enter
Space
Sleep 800ms
Enter
Sleep 1200ms

# Skip notification channels — defaults to console
Enter
Sleep 1200ms

# Let the "Config saved" message sit for a moment
Sleep 800ms
Type "clear"
Enter
Sleep 400ms

# Step 2: Run scan
Type "global-entry-scanner scan"
Enter
Sleep 7s

# Stop cleanly
Ctrl+C
Sleep 1s
