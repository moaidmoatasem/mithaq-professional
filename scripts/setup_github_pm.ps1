# CHERENKOV GitHub PM Setup - Run after: gh auth login
$REPO = "moaidmoatasem/cherenkov-professional"

try { gh auth status 2>&1 | Out-Null } catch { Write-Host "Run gh auth login first" -ForegroundColor Red; exit 1 }

$labels = @(
  @{name="epic"; color="0052CC"; description="Large cross-cutting initiative"}
  @{name="story"; color="008672"; description="User story"}
  @{name="task"; color="C2E0C6"; description="Generic task"}
  @{name="bug"; color="D73A4A"; description="Bug report"}
  @{name="feature"; color="A2EEEF"; description="New feature"}
  @{name="enhancement"; color="84B6EB"; description="Improvement"}
  @{name="chore"; color="BFDADC"; description="Maintenance"}
  @{name="docs"; color="0075CA"; description="Documentation"}
  @{name="refactor"; color="FEF2C0"; description="Code restructuring"}
  @{name="test"; color="FF761A"; description="Testing"}
  @{name="security"; color="5319E7"; description="Security"}
  @{name="priority:critical"; color="B60205"; description="Blocker"}
  @{name="priority:high"; color="D93F0B"; description="Important"}
  @{name="priority:medium"; color="FBCA04"; description="Normal"}
  @{name="priority:low"; color="0E8A16"; description="Low"}
  @{name="phase-0"; color="0D1117"; description="Phase 0: Foundation"}
  @{name="phase-1"; color="1F2937"; description="Phase 1: Orchestration"}
  @{name="phase-2"; color="374151"; description="Phase 2: Tooling"}
  @{name="phase-3"; color="4B5563"; description="Phase 3: Validation"}
  @{name="phase-4"; color="6B7280"; description="Phase 4: Hardening"}
  @{name="phase-5"; color="9CA3AF"; description="Phase 5: Enterprise"}
  @{name="area:scanner"; color="1D76DB"; description="Scanner engine"}
  @{name="area:orchestrator"; color="006B75"; description="Orchestration"}
  @{name="area:ui"; color="3E82F7"; description="UI/Frontend"}
  @{name="area:api"; color="2A5F8F"; description="API layer"}
  @{name="area:docs"; color="0075CA"; description="Documentation"}
  @{name="area:infra"; color="8250DF"; description="Infrastructure"}
  @{name="area:agent"; color="E99695"; description="AI agent"}
  @{name="area:security"; color="5319E7"; description="Security"}
  @{name="status:blocked"; color="B60205"; description="Blocked"}
  @{name="status:in-progress"; color="FBCA04"; description="In progress"}
  @{name="status:review-needed"; color="0E8A16"; description="Needs review"}
  @{name="status:done"; color="C2E0C6"; description="Completed"}
  @{name="ai:generated"; color="F0E6D3"; description="AI generated"}
  @{name="ai:reviewed"; color="D4C5A9"; description="AI reviewed"}
  @{name="ai:autonomous"; color="E8DCC8"; description="AI autonomous"}
  @{name="sprint-1"; color="F9D0C4"; description="Sprint 1"}
  @{name="sprint-2"; color="F9D0C4"; description="Sprint 2"}
  @{name="sprint-3"; color="F9D0C4"; description="Sprint 3"}
  @{name="sprint-4"; color="F9D0C4"; description="Sprint 4"}
  @{name="sprint-5"; color="F9D0C4"; description="Sprint 5"}
)

$existing = gh label list --repo $REPO --json name 2>$null | ConvertFrom-Json
$existingNames = $existing | ForEach-Object { $_.name }
foreach ($l in $labels) {
  if ($existingNames -contains $l.name) { gh label edit $l.name --repo $REPO --color $l.color --description $l.description 2>&1 | Out-Null }
  else { gh label create $l.name --repo $REPO --color $l.color --description $l.description 2>&1 | Out-Null }
}
Write-Host "$($labels.Count) labels" -ForegroundColor Green

$milestones = @(
  @{title="v1.0.0-rc1"; description="Sovereign Foundation"; due_date=(Get-Date).ToString("yyyy-MM-dd")}
  @{title="v1.1.0"; description="Swarm Concurrency"; due_date=(Get-Date).AddMonths(1).ToString("yyyy-MM-dd")}
  @{title="v1.5.0"; description="Enterprise Validation"; due_date=(Get-Date).AddMonths(3).ToString("yyyy-MM-dd")}
  @{title="v2.0.0"; description="Mobile Triad"; due_date=(Get-Date).AddMonths(6).ToString("yyyy-MM-dd")}
  @{title="v2.5.0"; description="Ecosystem Integration"; due_date=(Get-Date).AddMonths(9).ToString("yyyy-MM-dd")}
)
$existingMS = gh milestone list --repo $REPO --json title 2>$null | ConvertFrom-Json
$existingMSNames = $existingMS | ForEach-Object { $_.title }
foreach ($ms in $milestones) {
  if ($existingMSNames -contains $ms.title) { gh milestone edit $ms.title --repo $REPO --due-date $ms.due_date --description $ms.description 2>&1 | Out-Null }
  else { gh milestone create $ms.title --repo $REPO --due-date $ms.due_date --description $ms.description 2>&1 | Out-Null }
}
Write-Host "$($milestones.Count) milestones" -ForegroundColor Green

# Project Board
$projectName = "CHERENKOV Sovereign Roadmap"
$existingP = gh project list --owner moaidmoatasem --limit 50 --json title,id 2>$null | ConvertFrom-Json
$pid = if ($existingP) { ($existingP | Where-Object { $_.title -eq $projectName }).id }
if (-not $pid) {
  $pid = gh project create --owner moaidmoatasem --title $projectName --description "Master roadmap" 2>&1
  Write-Host "Project created" -ForegroundColor Green
}

# Wiki
$wikiDir = "$env:TEMP\cherenkov-wiki"
git clone "https://github.com/$REPO.wiki.git" $wikiDir 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
  $pages = @(
    @{src="README.md"; dst="Home.md"}
    @{src="docs/architecture/SYSTEM_ARCHITECTURE.md"; dst="Architecture.md"}
    @{src="docs/pm/ROADMAP.md"; dst="Roadmap.md"}
    @{src="docs/pm/DEVELOPMENT_PLAN.md"; dst="Development-Plan.md"}
    @{src="docs/github/RELEASES.md"; dst="Release-Strategy.md"}
    @{src="DESIGN_SYSTEM.md"; dst="Design-System.md"}
    @{src="AGENTS.md"; dst="Agent-Instructions.md"}
    @{src="CHERENKOV_SSOT.md"; dst="Single-Source-of-Truth.md"}
    @{src="CONTRIBUTING.md"; dst="Contributing.md"}
    @{src="CHANGELOG.md"; dst="Changelog.md"}
  )
  $root = "C:\Users\moaid\mithaq-professional"
  foreach ($p in $pages) {
    $s = Join-Path $root $p.src
    $d = Join-Path $wikiDir $p.dst
    if (Test-Path $s) { Copy-Item $s $d -Force }
  }
  Set-Content -Path (Join-Path $wikiDir "_Sidebar.md") -Value "# Wiki`n- [[Home]]`n- [[Architecture]]`n- [[Roadmap]]`n- [[Development-Plan]]`n- [[Release-Strategy]]`n- [[Agent-Instructions]]" -Encoding UTF8
  Push-Location $wikiDir; git add -A; git commit -m "docs: initial wiki"; git push origin master; Pop-Location
  Remove-Item -Recurse -Force $wikiDir
  Write-Host "Wiki pushed" -ForegroundColor Green
}
Write-Host "Setup complete!" -ForegroundColor Green
