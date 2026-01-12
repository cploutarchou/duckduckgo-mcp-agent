# Create release packages for GitHub releases

$VERSION = "1.2.1"
$RELEASE_DIR = "releases"

# Create releases directory
if (-not (Test-Path $RELEASE_DIR)) {
    New-Item -ItemType Directory -Path $RELEASE_DIR | Out-Null
}

# Files and directories to exclude
$EXCLUDE_PATTERNS = @(
    '.git',
    '.venv',
    '__pycache__',
    '.pytest_cache',
    '.mypy_cache',
    '.ruff_cache',
    '.vscode',
    '.idea',
    '*.pyc',
    'releases'
)

# Create ZIP file using built-in compression
Write-Host "Creating ZIP archive..." -ForegroundColor Green

# PowerShell 5.0+
Compress-Archive -Path @(
    'mcp_http_sse_server.py',
    'requirements.txt',
    'test_smoke.py',
    'test-mcp-sse.py',
    'README.md',
    'CHANGELOG.md',
    'LICENSE',
    'Makefile',
    'Dockerfile',
    'docker-compose.yml',
    'mcp-config.json',
    '.github'
) -DestinationPath "$RELEASE_DIR/duckduckgo-mcp-agent-v${VERSION}.zip" -Force

Write-Host "✅ Release package created:" -ForegroundColor Green
Get-Item "$RELEASE_DIR/duckduckgo-mcp-agent-v${VERSION}.zip" | Format-List Name, Length
