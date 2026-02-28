# DNSChanger v2.0.0 - Deployment Guide

## 📦 Quick Start

### For Users

1. **Download the executable** from Releases page
2. **Extract** to a folder
3. **Run** `DNSChanger.exe` (will request admin privileges)
4. **Select** network interface and DNS provider
5. **Apply** settings

### For Developers

```bash
# Clone repository
git clone https://github.com/gulp79/DNSChanger.git
cd DNSChanger

# Install dependencies
pip install -r requirements.txt

# Run from source
python dns_changer.py
```

## 🔨 Building from Source

### Prerequisites

- Python 3.12 or higher
- Windows 10/11
- Git (optional)

### Method 1: Using build.py Script

```bash
# Clean and build with PyInstaller (recommended for testing)
python build.py pyinstaller

# Clean and build with Nuitka (recommended for release)
python build.py nuitka

# Build with both
python build.py all

# Clean only
python build.py clean
```

### Method 2: Manual PyInstaller Build

```bash
# Install PyInstaller
pip install pyinstaller

# Build
pyinstaller DNSChanger.spec

# Output: dist/DNSChanger.exe
```

### Method 3: Manual Nuitka Build

```bash
# Install Nuitka
pip install nuitka ordered-set zstandard

# Build (takes 10-15 minutes)
python -m nuitka --standalone --onefile --windows-console-mode=disable \
  --enable-plugin=tk-inter --windows-uac-admin \
  --output-filename=DNSChanger.exe dns_changer.py

# Output: DNSChanger.exe
```

## 🚀 GitHub Actions Deployment

### Triggering Builds

1. Go to **Actions** tab in GitHub
2. Select workflow:
   - "Build with PyInstaller" for fast builds
   - "Build with Nuitka" for optimized builds
3. Click **Run workflow**
4. Enter version (e.g., v2.0.0) or leave as 'dev'
5. Download artifact from workflow run (available for 30 days)

### Workflow Files

- `.github/workflows/build-pyinstaller.yml`
- `.github/workflows/build-nuitka.yml`

Both workflows:
- ✅ Install Python 3.12
- ✅ Install dependencies
- ✅ Build executable
- ✅ Create release package
- ✅ Upload artifacts

## 📋 Pre-Release Checklist

### Code Quality

- [ ] All tests pass: `pytest tests/`
- [ ] Code follows PEP 8
- [ ] Type hints are complete
- [ ] Docstrings are up to date
- [ ] No TODO comments remain
- [ ] Logging is appropriate

### Functionality

- [ ] Application starts correctly
- [ ] Admin elevation works
- [ ] Network adapters load
- [ ] DNS providers load from YAML
- [ ] DNS can be applied successfully
- [ ] DoH works on Windows 11
- [ ] DNS verification works
- [ ] Rollback works correctly
- [ ] Reset to DHCP works
- [ ] Migration from txt works
- [ ] Cache flush works
- [ ] All buttons functional

### Testing Scenarios

1. **Fresh Install**
   - [ ] No config file → creates default
   - [ ] Migration prompt appears if txt exists

2. **DNS Application**
   - [ ] IPv4-only providers work
   - [ ] DoH providers work (Win11)
   - [ ] Multiple interfaces work
   - [ ] Verification passes with good DNS
   - [ ] Rollback triggers on bad DNS

3. **Edge Cases**
   - [ ] No network adapters handled
   - [ ] Invalid YAML handled gracefully
   - [ ] Non-admin start handled
   - [ ] Timeout scenarios work
   - [ ] Virtual interfaces excluded

### Documentation

- [ ] README is current
- [ ] CHANGELOG updated
- [ ] Version number updated in code
- [ ] Screenshots are current
- [ ] API documentation current

## 🎯 Release Process

### Version Numbering

Follow Semantic Versioning (SemVer):
- **Major** (X.0.0): Breaking changes
- **Minor** (x.X.0): New features, backward compatible
- **Patch** (x.x.X): Bug fixes

### Release Steps

1. **Update Version**
   ```python
   # In dnschanger/__init__.py
   __version__ = "2.0.0"
   ```

2. **Update CHANGELOG.md**
   - Add release date
   - Summarize changes
   - Note breaking changes

3. **Create Git Tag**
   ```bash
   git tag -a v2.0.0 -m "Version 2.0.0 - DNS over HTTPS support"
   git push origin v2.0.0
   ```

4. **Build Release Artifacts**
   ```bash
   python build.py all
   ```

5. **Create GitHub Release**
   - Go to Releases → Draft new release
   - Choose tag: v2.0.0
   - Title: "DNSChanger v2.0.0 - Advanced Edition"
   - Description: Copy from CHANGELOG
   - Attach executables:
     - `DNSChanger-PyInstaller-v2.0.0.zip`
     - `DNSChanger-Nuitka-v2.0.0.zip`
   - Mark as pre-release if testing needed

6. **Post-Release**
   - Monitor for issues
   - Respond to user feedback
   - Plan next version

## 🔧 Configuration Deployment

### Deploying dns_providers.yaml

**Default providers** are included in the executable.

To use custom providers:
1. Place `dns_providers.yaml` in same directory as executable
2. Application will load custom file automatically
3. Validate with schema before deploying

### Enterprise Deployment

For organizations deploying to multiple machines:

1. **Create custom dns_providers.yaml**
   ```yaml
   version: 1
   providers:
     - name: "Internal DNS"
       ipv4: ["10.0.0.1", "10.0.0.2"]
       tags: ["internal", "enterprise"]
       policy: {encrypted_only: false, autoupgrade: true, allow_udp_fallback: true}
   ```

2. **Deploy using Group Policy**
   - Package executable with YAML
   - Deploy via GPO software installation

3. **Silent Installation Script**
   ```powershell
   # deploy.ps1
   $installPath = "C:\Program Files\DNSChanger"
   New-Item -ItemType Directory -Force -Path $installPath
   Copy-Item "DNSChanger.exe" -Destination $installPath
   Copy-Item "dns_providers.yaml" -Destination $installPath
   
   # Create shortcut
   $WshShell = New-Object -comObject WScript.Shell
   $Shortcut = $WshShell.CreateShortcut("$env:PUBLIC\Desktop\DNSChanger.lnk")
   $Shortcut.TargetPath = "$installPath\DNSChanger.exe"
   $Shortcut.Save()
   ```

## 🧪 Testing Deployment

### Test Matrix

| OS Version | DoH Support | Priority |
|------------|-------------|----------|
| Windows 10 20H2 | Limited | Medium |
| Windows 10 21H2 | Limited | Medium |
| Windows 11 21H2 | Full | High |
| Windows 11 22H2 | Full | High |
| Server 2019 | Limited | Low |
| Server 2022 | Full | Medium |

### Test Checklist Per Platform

- [ ] Application starts
- [ ] Adapters detected
- [ ] DNS changes applied
- [ ] DoH status (if supported)
- [ ] Verification works
- [ ] Rollback works
- [ ] No errors in log

## 🐛 Troubleshooting Deployment

### Common Issues

**Build Fails**
- Check Python version ≥ 3.12
- Ensure all dependencies installed
- Try `python build.py clean` first

**Executable Won't Start**
- Check Windows Defender / antivirus
- Verify user has admin rights
- Check `dnschanger.log` for errors

**DNS Changes Don't Work**
- Verify admin elevation happened
- Check PowerShell execution policy
- Review log file for PS errors

**DoH Not Available**
- Confirm Windows 11 or Server 2022+
- Check for Group Policy blocks
- Verify no third-party DNS managers

## 📊 Monitoring

### Log File Location

`dnschanger.log` in executable directory

### Log Levels

- **INFO**: Normal operations
- **WARNING**: Recoverable issues
- **ERROR**: Operation failures

### Key Metrics to Monitor

- Successful DNS applications
- Verification pass/fail rate
- Rollback frequency
- DoH registration success
- Average operation time

## 🔒 Security Considerations

### Administrator Privileges

- **Required** for DNS changes
- Requested automatically on start
- UAC manifest in executable

### Data Protection

- No sensitive data stored
- No network communication
- Local operations only

### Code Signing (Optional)

For production:
```bash
# Using signtool.exe
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com DNSChanger.exe
```

## 📱 Distribution Channels

### GitHub Releases (Primary)
- Official release location
- Automatic version tracking
- Download statistics

### Alternative Channels
- Direct download from website
- Enterprise software repositories
- Chocolatey/Scoop (future)

## 🎉 Launch Checklist

Final checks before announcing release:

- [ ] All tests pass
- [ ] Documentation complete
- [ ] Builds successful on GitHub Actions
- [ ] Release notes written
- [ ] Artifacts uploaded to GitHub
- [ ] README updated with download link
- [ ] Screenshots updated
- [ ] Known issues documented
- [ ] Support channels ready

---

## 📞 Support

For deployment issues:
- Check `dnschanger.log`
- Review README troubleshooting
- Open GitHub issue with log excerpt
- Include Windows version and build number

---

**Ready to Deploy!** 🚀
