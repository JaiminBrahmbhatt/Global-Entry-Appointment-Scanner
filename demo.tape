# VHS tape script for global-entry-scanner demo
Output docs/demo.gif

Set Shell "zsh"
Set FontSize 14
Set Width 900
Set Height 420
Set Theme "Dracula"
Set Padding 20
Set TypingSpeed 50ms

Hide
Type "source /Users/jaiminb/Code/Global-Entry-Appointment-Scanner/.venv/bin/activate && clear"
Enter
Sleep 500ms
Show

# List locations
Type "global-entry-scanner locations"
Sleep 500ms
Enter
Sleep 4s

Type "clear"
Enter
Sleep 300ms

# Scan for specific cities
Type "global-entry-scanner scan --locations 'Austin, San Antonio, Dallas' --notify none"
Sleep 500ms
Enter
Sleep 6s
