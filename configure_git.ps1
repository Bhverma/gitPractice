# Interactive Git Configuration Script

# Prompt for user information
$userName = Read-Host "Enter your Git username"
$userEmail = Read-Host "Enter your Git email"

# Set Git configuration
git config --global user.name $userName
git config --global user.email $userEmail

# Verify the settings
Write-Host "`nVerifying Git configuration:"
Write-Host "Name: $(git config --global user.name)"
Write-Host "Email: $(git config --global user.email)"

Write-Host "`nGit configuration complete!"
Read-Host "Press Enter to exit"