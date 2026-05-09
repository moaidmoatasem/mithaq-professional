# Enable Discussions in repo settings first: https://github.com/moaidmoatasem/cherenkov-professional/settings
# Then create these categories via the UI: https://github.com/moaidmoatasem/cherenkov-professional/discussions/categories

$categories = @(
  @{name="Announcements"; emoji="📢"; description="Releases and major updates"}
  @{name="Ideas & Feature Requests"; emoji="💡"; description="Suggest features"}
  @{name="Q&A"; emoji="❓"; description="Help and troubleshooting"}
  @{name="Development"; emoji="🛠️"; description="RFCs and technical discussions"}
)

Write-Host "Create these discussion categories:" -ForegroundColor Cyan
foreach ($c in $categories) { Write-Host "  $($c.emoji) $($c.name) — $($c.description)" }
