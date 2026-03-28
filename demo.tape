# VHS tape script for global-entry-scanner demo
Output docs/demo.gif

Set Shell "zsh"
Set FontSize 14
Set Width 900
Set Height 500
Set Theme "Dracula"
Set Padding 20
Set TypingSpeed 80ms

# Activate venv silently
Hide
Type "source /Users/jaiminb/Code/Global-Entry-Appointment-Scanner/.venv/bin/activate && clear"
Enter
Sleep 500ms
Show

# --- Step 1: Setup ---
Type "global-entry-scanner setup"
Enter
Sleep 4s

# Location picker: select the first city (Space to check, Enter to confirm)
Space
Sleep 500ms
Enter
Sleep 1s

# Notification channels: skip (Enter = defaults to console)
Enter
Sleep 1s

# Config saved
Sleep 500ms

Type "clear"
Enter
Sleep 300ms

# --- Step 2: Scan ---
Type "global-entry-scanner scan"
Enter
Sleep 8s

# Stop after first poll
Ctrl+C
Sleep 500ms
