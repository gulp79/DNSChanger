# DNS Changer - Advanced Edition

A modern, feature-rich DNS management tool for Windows with support for DNS over HTTPS (DoH), automatic verification, and intelligent rollback.

<img width="1488" height="1385" alt="image" src="https://github.com/user-attachments/assets/a62b6941-547a-4707-a0f5-26dab398702d" />

![DNS Changer Interface](https://img.shields.io/badge/Platform-Windows-blue) ![Python](https://img.shields.io/badge/Python-3.12+-green) ![License](https://img.shields.io/badge/License-MIT-orange)

## ✨ Features

### Core Functionality
- 🎨 **Modern Dark Interface**: Sleek dark theme with acid green accents
- 🔌 **Smart Interface Detection**: Automatically detects and lists only active physical network adapters
- 📋 **Multiple Interface Support**: Apply DNS settings to one or multiple interfaces simultaneously
- 🔄 **Automatic Verification**: Test DNS functionality after applying changes
- ⏱️ **Smart Rollback**: Automatic rollback if DNS verification fails
- 🔐 **Administrator Rights**: Automatic elevation to administrator privileges when needed

### DNS over HTTPS (DoH)
- 🔒 **Native DoH Support**: Full integration with Windows 11/Server 2022 DoH capabilities
- 🌐 **Encrypted DNS**: Configure encrypted-only DNS when supported
- 🚀 **Auto-Upgrade**: Automatically upgrade to DoH when available
- 📊 **DoH Status Indicators**: Real-time display of DoH configuration status

### Configuration Management
- 📝 **YAML-Based Configuration**: Structured DNS provider definitions
- 🏷️ **Provider Tags**: Filter and organize DNS providers by tags (privacy, security, ad-block, etc.)
- 🔄 **Legacy Migration**: Automatic migration from old `dns_list.txt` format
- ✅ **Schema Validation**: Pydantic-based validation ensures configuration correctness

### Advanced Features
- 🧪 **DNS Verification**: Test DNS resolution before finalizing changes
- 📸 **Snapshot & Rollback**: Create snapshots before changes for easy rollback
- 🗑️ **Cache Flushing**: Optional automatic DNS cache flush after applying changes
- 📋 **Current Status Display**: View configured DNS servers for each interface

## 📋 Prerequisites

### Required
- **Windows 10** (20H2 or later) / **Windows 11** / **Windows Server 2019+**
- **Python 3.12 or higher**
- **Administrator privileges** (application will request elevation)

### For Full DoH Support
- **Windows 11** or **Windows Server 2022** or later
- DoH features are available but limited on Windows 10

## 🚀 Installation

### Option 1: Run from Source

1. **Clone the repository**:
   ```bash
   git clone https://github.com/gulp79/DNSChanger.git
   cd DNSChanger
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python dns_changer.py
   ```

### Option 2: Standalone Executable

1. Download the latest release from the [Releases](https://github.com/gulp79/DNSChanger/releases) page
2. Extract the files to a folder
3. Run `DNSChanger.exe`

## 📖 Usage

### First Launch

1. The application will automatically request administrator privileges
2. Network interfaces will be loaded and displayed in the left panel
3. If you have a legacy `dns_list.txt`, you'll be prompted to migrate to the new YAML format

### Applying DNS Settings

1. **Select Interface(s)**: Check one or more network interfaces from the left panel
2. **Choose DNS Provider**: Select a DNS provider from the right panel
3. **Configure DoH** (optional): Toggle "Use DoH" to enable DNS over HTTPS
4. **Apply Changes**: Click "Apply DNS Settings"
5. **Verification**: DNS will be verified automatically
6. **Confirm**: If verification passes, changes are applied permanently

### DNS over HTTPS (DoH)

When DoH is enabled and supported:
- 🔒 DoH servers are automatically registered with Windows
- 🔐 Encryption mode is configured based on provider policy
- ✅ DoH status is displayed for each interface
- ⚠️ Fallback options are configured according to provider settings

### Automatic Rollback

If DNS verification fails after applying settings:
- ⏱️ A 30-second countdown timer starts
- 🔄 Previous DNS configuration is automatically restored
- ⚠️ You'll be notified of the rollback

### Resetting to DHCP

1. Select the interface(s) you want to reset
2. Click "Reset to DHCP"
3. DNS settings will be restored to automatic configuration

## ⚙️ Configuration

### DNS Providers File (`dns_providers.yaml`)

The application uses a structured YAML file for DNS provider definitions:

```yaml
version: 1
providers:
  - name: "Cloudflare"
    ipv4: ["1.1.1.1", "1.0.0.1"]
    doh_template: "https://cloudflare-dns.com/dns-query"
    tags: ["privacy", "fast", "public"]
    policy:
      encrypted_only: true
      autoupgrade: true
      allow_udp_fallback: false
  
  - name: "Google DNS"
    ipv4: ["8.8.8.8", "8.8.4.4"]
    doh_template: "https://dns.google/dns-query"
    tags: ["public", "fast"]
    policy:
      encrypted_only: true
      autoupgrade: true
      allow_udp_fallback: false
```

### Provider Fields

- **name**: Display name for the provider
- **ipv4**: List of IPv4 DNS server addresses (required)
- **ipv6**: List of IPv6 DNS server addresses (optional)
- **doh_template**: DoH template URL for encrypted DNS (optional)
- **tags**: Categorization tags (privacy, security, ad-block, etc.)
- **policy**: DoH policy configuration
  - **encrypted_only**: Require encrypted DNS only (Windows 11+)
  - **autoupgrade**: Automatically upgrade to DoH when available
  - **allow_udp_fallback**: Allow fallback to unencrypted DNS

### Adding Custom DNS Providers

1. Edit `dns_providers.yaml`
2. Add your provider following the schema above
3. Restart the application or click "Refresh"

## 🔄 Migrating from Legacy Format

If you have an existing `dns_list.txt` file:

1. Click "Migrate from dns_list.txt" button
2. The tool will automatically convert entries to YAML format
3. A backup of any existing `dns_providers.yaml` will be created
4. Review the migrated providers

The legacy format was:
```
# Format: Name,PrimaryDNS,SecondaryDNS
Google,8.8.8.8,8.8.4.4
Cloudflare,1.1.1.1,1.0.0.1
```

## 🛠️ Building from Source

### Using PyInstaller

```bash
pip install pyinstaller
pyinstaller DNSChanger.spec
```

The executable will be created in the `dist/` folder.

### Using Nuitka

```bash
pip install nuitka ordered-set
python -m nuitka --standalone --onefile --windows-console-mode=disable --enable-plugin=tk-inter --windows-icon-from-ico=icona.ico --windows-uac-admin dns_changer.py
```

### GitHub Actions (Automated Builds)

The project includes GitHub Actions workflows for automated builds:
- **PyInstaller Build**: `.github/workflows/build-pyinstaller.yml`
- **Nuitka Build**: `.github/workflows/build-nuitka.yml`

Workflows can be triggered manually from the Actions tab.

## 🔧 Technical Details

### Architecture

```
dnschanger/
├── core/               # Business logic
│   ├── dns_loader.py   # YAML provider loading
│   ├── dns_verifier.py # DNS verification & rollback
│   └── migration.py    # Legacy migration
├── ps/                 # PowerShell integration
│   ├── ps_adapter.py   # Windows DNS management
│   └── doh_manager.py  # DoH configuration
├── models/             # Data models (Pydantic)
│   └── dns_provider.py # Provider schema
└── ui/                 # User interface (CustomTkinter)
    └── main_window.py  # Main application window
```

### PowerShell Commands Used

The application uses the following PowerShell cmdlets:

#### Network Adapters
```powershell
Get-NetAdapter | Where-Object { $_.Status -eq 'Up' }
```

#### DNS Configuration
```powershell
# Set DNS servers
Set-DnsClientServerAddress -InterfaceIndex <ID> -ServerAddresses ("8.8.8.8","1.1.1.1") -Validate

# Reset to DHCP
Set-DnsClientServerAddress -InterfaceIndex <ID> -ResetServerAddresses

# Get current DNS
Get-DnsClientServerAddress -InterfaceIndex <ID>
```

#### DoH Configuration (Windows 11+)
```powershell
# Register DoH server
Add-DnsClientDohServerAddress -ServerAddress "1.1.1.1" `
  -DohTemplate "https://cloudflare-dns.com/dns-query" `
  -AutoUpgrade:$true -AllowFallbackToUdp:$false

# List DoH servers
Get-DnsClientDohServerAddress

# Configure interface encryption
Set-NetDnsTransitionConfiguration -InterfaceIndex <ID> `
  -Protocol DoH -OnlyUseEncryption $true
```

#### DNS Verification
```powershell
# Test DNS resolution
Resolve-DnsName -Name example.com -DnsOnly -QuickTimeout

# Flush DNS cache
ipconfig /flushdns
```

## 🐛 Troubleshooting

### Common Issues

**"DoH not supported"**
- DoH requires Windows 11 or Windows Server 2022 or later
- Check your Windows version: `winver`
- Basic DNS functionality works on Windows 10

**"Access denied" or "Administrator rights required"**
- Right-click the application and select "Run as administrator"
- The application should automatically request elevation

**"No active network adapters found"**
- Ensure you're running as administrator
- Check that your network adapters are connected and enabled
- Try clicking "Refresh Interfaces"

**"DNS changes not taking effect"**
- Some applications may cache DNS settings
- Try flushing DNS cache: `ipconfig /flushdns`
- Restart your browser or the affected application
- Restart the network adapter if necessary

**"DNS verification failed"**
- Check if your DNS servers are reachable
- Verify that firewall rules allow DNS traffic
- Try a different DNS provider
- The application will automatically rollback to previous settings

**"DoH blocked by policy"**
- Your organization may have disabled DoH via Group Policy
- Contact your system administrator
- Basic DNS functionality remains available

### Logging

The application creates a log file: `dnschanger.log`

Check this file for detailed error messages and debugging information.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests if applicable
5. Test thoroughly on Windows
6. Submit a pull request

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Add docstrings to functions and classes
- Keep functions focused and modular

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) for the modern GUI
- Uses [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation
- Uses [PyYAML](https://pyyaml.org/) for configuration parsing
- Windows PowerShell for network configuration
- Inspired by the need for a modern, visual DNS management tool with DoH support

## 📝 Changelog

### v2.0.0 (Advanced Edition)
- ✨ **NEW**: DNS over HTTPS (DoH) support for Windows 11/Server 2022
- ✨ **NEW**: YAML-based DNS provider configuration with schema validation
- ✨ **NEW**: Automatic DNS verification with smart rollback
- ✨ **NEW**: Provider tags and filtering system
- ✨ **NEW**: Migration tool for legacy dns_list.txt format
- ✨ **NEW**: DNS cache flushing option
- ✨ **NEW**: Real-time DoH status indicators
- ✨ **NEW**: Snapshot and rollback functionality
- ✨ **NEW**: Modular architecture with separated concerns
- 🔧 **IMPROVED**: Enhanced error handling and user feedback
- 🔧 **IMPROVED**: More reliable network adapter detection
- 🔧 **IMPROVED**: Better Windows version detection
- 📚 **IMPROVED**: Comprehensive documentation and examples

### v1.0.0
- Initial release
- Basic DNS changing functionality
- Modern dark theme interface
- Multiple interface selection

---

## ⚠️ Important Notes

- This application modifies system network settings
- Always ensure you have a way to revert changes if needed
- The "Reset to DHCP" function can restore default settings
- DoH features require Windows 11 or Server 2022 or later
- Administrator privileges are required for all network changes

---

**Made with ❤️ for better DNS management on Windows**

![Downloads](https://img.shields.io/github/downloads/gulp79/DNSChanger/total?style=for-the-badge&labelColor=21262d&color=238636)
