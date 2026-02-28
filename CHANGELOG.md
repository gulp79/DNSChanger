# Changelog

All notable changes to DNSChanger will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-01-30

### Added - Major Feature Release

#### DNS over HTTPS (DoH) Support
- Full native DoH integration for Windows 11/Server 2022+
- Automatic DoH server registration with Windows
- Encrypted-only DNS mode configuration
- Auto-upgrade to DoH when available
- Configurable UDP fallback settings
- Real-time DoH status indicators in UI
- DoH server management (add/remove/list)

#### YAML-Based Configuration
- Structured DNS provider definitions using YAML format
- Pydantic-based schema validation with detailed error messages
- Support for provider metadata: name, IPs, DoH template, tags, policy
- JSON format support as alternative to YAML
- Provider policy configuration for DoH behavior

#### DNS Verification & Rollback
- Automatic DNS verification after applying changes
- Multi-domain resolution testing
- Smart rollback on verification failure
- Snapshot functionality to save previous DNS configuration
- 30-second countdown timer for manual confirmation
- Configurable success threshold for verification

#### Migration & Compatibility
- Automatic migration tool from legacy `dns_list.txt` format
- One-click migration with confirmation dialog
- Backup creation of existing YAML files
- Backward compatibility detection
- Intelligent provider detection for common DNS services

#### UI/UX Improvements
- Provider badges showing DoH support, IPv4/IPv6, and tags
- Real-time current DNS configuration display per interface
- DoH status indicators (🔒 DoH Active)
- Enhanced error messages and user feedback
- Loading states and progress indicators
- Improved interface type detection (physical/virtual/VPN)

#### Architecture & Code Quality
- Modular architecture with separated concerns:
  - `core/`: Business logic (loader, verifier, migration)
  - `ps/`: PowerShell integration (adapter, DoH manager)
  - `models/`: Data models with validation
  - `ui/`: User interface components
- Type hints throughout the codebase
- Structured logging with file output
- Comprehensive docstrings
- Error handling and recovery mechanisms

#### DevOps & Build
- GitHub Actions workflows for automated builds
- PyInstaller and Nuitka build configurations
- Manual workflow triggers with version input
- Artifact retention and download support
- Build information tracking

### Changed

#### Breaking Changes
- **Configuration Format**: Replaced `dns_list.txt` with `dns_providers.yaml`
  - Migration tool provided for automatic conversion
  - Legacy format no longer loaded by default
- **Minimum Python Version**: Now requires Python 3.12+
- **Dependencies**: Added pydantic and pyyaml as required dependencies

#### Improvements
- Enhanced network adapter detection and filtering
- Better virtual interface exclusion (VMware, VirtualBox, Hyper-V, TAP, VPN)
- More reliable PowerShell command execution
- Improved error messages and user guidance
- Better Windows version detection for feature support

### Fixed
- Network adapter listing reliability
- PowerShell output parsing edge cases
- Unicode handling in configuration files
- Interface index tracking consistency
- DNS server validation edge cases

### Documentation
- Complete README rewrite with comprehensive feature documentation
- Added usage examples and troubleshooting guide
- PowerShell command reference
- Architecture documentation
- Migration guide from v1.x
- Build instructions for both PyInstaller and Nuitka

### Security
- Administrator privilege checks before operations
- Validation of DNS server IP addresses
- Sanitization of PowerShell command inputs
- Secure handling of system configuration changes

## [1.0.0] - 2024-XX-XX

### Added
- Initial release
- Basic DNS changing functionality for Windows
- Modern dark theme interface with CustomTkinter
- Multiple network interface selection
- DNS preset management via dns_list.txt
- DHCP reset functionality
- Real-time status updates
- Automatic administrator elevation
- Network adapter filtering

### Features
- Dark theme with acid green accents
- Physical network adapter detection
- Current DNS settings display
- Simple text-based DNS preset configuration
- Basic error handling and status reporting

---

## Upgrade Notes

### From v1.x to v2.0

1. **Configuration Migration**:
   - Your existing `dns_list.txt` is preserved
   - Use the "Migrate from dns_list.txt" button in the application
   - Or manually run migration before upgrading

2. **Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Python Version**:
   - Upgrade to Python 3.12 or later

4. **DoH Support**:
   - DoH features require Windows 11 or Windows Server 2022+
   - Windows 10 users can still use basic DNS functionality

5. **New Features**:
   - Explore the new YAML configuration format
   - Enable DoH toggle for encrypted DNS
   - Use automatic verification and rollback features

### Migration Command Line

```python
from core.migration import migrate_txt_to_yaml
from pathlib import Path

migrate_txt_to_yaml(
    Path("dns_list.txt"),
    Path("dns_providers.yaml"),
    backup=True
)
```

---

## Future Roadmap

### Planned Features
- [ ] IPv6 DNS support
- [ ] DNS-over-TLS (DoT) support
- [ ] Custom DNS resolver testing
- [ ] Export/import configuration profiles
- [ ] Scheduled DNS changes
- [ ] System tray integration
- [ ] Multi-language support
- [ ] DNS latency testing
- [ ] Automatic provider updates
- [ ] Web-based provider database

### Under Consideration
- macOS and Linux support
- Command-line interface (CLI) mode
- DNS leak testing
- Integration with popular VPN services
- Cloud synchronization of settings
- DNS blocking lists management

---

[2.0.0]: https://github.com/gulp79/DNSChanger/releases/tag/v2.0.0
[1.0.0]: https://github.com/gulp79/DNSChanger/releases/tag/v1.0.0
