# Frequently Asked Questions (FAQ)

## General Questions

### What is DNSChanger?

DNSChanger is an advanced DNS management tool for Windows that allows you to easily change DNS servers on your network adapters. It features support for DNS over HTTPS (DoH), automatic verification, and smart rollback capabilities.

### Is DNSChanger free?

Yes, DNSChanger is completely free and open-source under the MIT License.

### What Windows versions are supported?

- **Windows 10** (20H2 or later): Full DNS functionality, limited DoH
- **Windows 11**: Full functionality including advanced DoH features
- **Windows Server 2019+**: Full functionality
- **Windows Server 2022+**: Full DoH support

### Do I need administrator rights?

Yes, changing DNS settings requires administrator privileges. The application will automatically request elevation when started.

## DNS over HTTPS (DoH)

### What is DNS over HTTPS?

DNS over HTTPS (DoH) is a protocol that encrypts DNS queries, preventing eavesdropping and manipulation of DNS data. It improves privacy and security.

### Does my Windows version support DoH?

- **Windows 11 / Server 2022+**: Full DoH support with encrypted-only mode
- **Windows 10**: Limited DoH support (basic configuration only)
- Check the application - it will display DoH status based on your system

### Why is the DoH toggle disabled?

The DoH toggle is disabled when:
- Your Windows version doesn't support DoH (older than Windows 11/Server 2022)
- Group Policy has disabled DoH on your system
- Check the warning message next to the toggle for details

### Can I use DoH with my company's internal DNS?

Internal DNS servers typically don't support DoH. For internal DNS:
- Use standard DNS (not DoH)
- Set `encrypted_only: false` in provider policy
- DoH is more suitable for public DNS providers

### What happens if DoH fails?

Depending on the policy settings:
- If `allow_udp_fallback: true`, it falls back to regular DNS
- If `allow_udp_fallback: false`, DNS queries will fail until DoH is restored
- The application will show warnings if DoH configuration fails

## Configuration

### Where is the configuration file located?

The configuration file `dns_providers.yaml` should be in the same directory as the executable or the current working directory when running from source.

### Can I use JSON instead of YAML?

Yes, the application supports both formats:
- `dns_providers.yaml` (preferred)
- `dns_providers.json` (alternative)

YAML is preferred for readability and comments.

### How do I add custom DNS providers?

**Option 1 - Edit YAML file:**
```yaml
- name: "My Custom DNS"
  ipv4: ["10.0.0.1", "10.0.0.2"]
  tags: ["custom"]
  policy:
    encrypted_only: false
    autoupgrade: false
    allow_udp_fallback: true
```

**Option 2 - Use the creation script:**
```bash
python scripts/create_config.py
```

### What do the provider tags mean?

Common tags:
- `public`: Public DNS service
- `privacy`: Privacy-focused
- `security`: Security-enhanced (malware blocking)
- `ad-block`: Blocks advertisements
- `family`: Family-friendly filtering
- `fast`: Optimized for speed
- `no-filter`: No content filtering

### How do I migrate from the old dns_list.txt format?

1. Keep your `dns_list.txt` file
2. Click "Migrate from dns_list.txt" in the application
3. Or run: Migration happens automatically if no YAML file exists

## Usage

### Why aren't my DNS changes taking effect?

Try these steps:
1. Flush DNS cache: Run as admin: `ipconfig /flushdns`
2. Restart your browser or application
3. Check if a VPN is overriding DNS settings
4. Verify the changes in Network Settings manually

### What is the verification feature?

After applying DNS settings, DNSChanger:
1. Tests DNS resolution with multiple domains
2. If tests fail, automatically rolls back to previous settings
3. Shows a 30-second confirmation timer
4. Prevents you from getting stuck with broken DNS

### Can I change DNS for multiple adapters at once?

Yes! Simply check multiple network interfaces before clicking "Apply DNS Settings". The same DNS will be applied to all selected interfaces.

### What's the difference between "Apply" and "Reset to DHCP"?

- **Apply DNS Settings**: Sets specific DNS servers you choose
- **Reset to DHCP**: Reverts to automatic DNS (from router/network)

### Why are some interfaces grayed out or missing?

The application filters out:
- Virtual adapters (VMware, VirtualBox, Hyper-V)
- VPN/TAP interfaces (shown with warning icon)
- Disconnected adapters
- Loopback interfaces

This prevents accidental configuration of non-relevant interfaces.

## Troubleshooting

### "No active network adapters found"

**Causes:**
- Not running as administrator
- All adapters are disconnected
- Only virtual adapters present

**Solutions:**
- Right-click → Run as Administrator
- Connect to a network
- Enable physical network adapter
- Click "Refresh Interfaces"

### "PowerShell Error" messages

**Causes:**
- PowerShell not available
- Execution policy restrictions
- Insufficient permissions

**Solutions:**
- Ensure running as administrator
- Check PowerShell is installed (built-in on Windows)
- Review dnschanger.log for details

### DNS changes don't persist after reboot

**Causes:**
- Another application managing DNS (VPN, antivirus)
- DHCP overriding settings
- Group Policy enforcement

**Solutions:**
- Disable DNS management in other applications
- Ensure you didn't use "Reset to DHCP"
- Check Group Policy settings

### Application crashes on startup

**Solutions:**
1. Check `dnschanger.log` for errors
2. Verify all dependencies installed: `pip install -r requirements.txt`
3. Try running from command line to see errors
4. Delete any corrupted configuration files

### "Access Denied" even as administrator

**Causes:**
- Anti-virus blocking
- Windows security policies
- Corrupted user account

**Solutions:**
- Add exception in anti-virus
- Check Windows security settings
- Try from different admin account

## Features

### What is the rollback timer?

After applying DNS settings, if verification fails:
- A 30-second countdown starts
- Previous DNS settings are automatically restored
- You can manually rollback before timer expires
- Prevents permanent DNS configuration issues

### Can I schedule DNS changes?

This feature is not currently implemented but is planned for future versions.

### Does it support IPv6 DNS?

The infrastructure supports IPv6, but the current version focuses on IPv4. IPv6 support is planned for future releases.

### Can I export/import settings?

Currently, you can:
- Edit `dns_providers.yaml` manually
- Copy the file to other machines
- Use scripts to validate and create configurations

Full export/import UI is planned for future versions.

## Performance

### Does DoH slow down DNS lookups?

Initial DoH connections may be slightly slower due to TLS handshake, but:
- Subsequent queries use cached connections
- Modern implementations are highly optimized
- The privacy benefits usually outweigh minimal latency

### How much memory does DNSChanger use?

DNSChanger is lightweight:
- ~50-100MB RAM when running
- Minimal CPU usage
- No background services

### Does it run in the background?

No, DNSChanger only runs when you open it. Changes are applied to Windows and persist after closing the application.

## Security & Privacy

### Does DNSChanger collect any data?

No. DNSChanger:
- Operates entirely locally
- Makes no network connections (except DNS tests)
- Collects no telemetry
- Stores no personal data

### Is it safe to use?

Yes, but understand that:
- It modifies system network settings (requires admin)
- Uses trusted PowerShell commands
- Open-source code can be audited
- Always have a way to revert changes (DHCP reset)

### Can my ISP still see my DNS queries?

- **Without DoH**: Yes, DNS queries are visible
- **With DoH**: Encrypted, ISP sees only connection to DoH server
- **Note**: ISP can still see website IPs you connect to

## Building & Development

### How do I build from source?

```bash
# Install dependencies
pip install -r requirements.txt

# Run from source
python dns_changer.py

# Build executable
python build.py pyinstaller
```

See DEPLOYMENT.md for detailed instructions.

### Can I contribute?

Absolutely! See CONTRIBUTING.md for guidelines.

### What technologies are used?

- **Python 3.12+**: Core language
- **CustomTkinter**: Modern GUI framework
- **Pydantic**: Data validation
- **PyYAML**: Configuration parsing
- **PowerShell**: Windows DNS management

## Enterprise Deployment

### Can I deploy this in my organization?

Yes! DNSChanger is suitable for enterprise use:
- Create custom `dns_providers.yaml` with internal DNS
- Deploy executable + configuration via Group Policy
- See `dns_providers_enterprise_example.yaml` for template

### How do I lock down configuration?

1. Place `dns_providers.yaml` in read-only location
2. Use Group Policy to restrict DNS changes
3. Remove migration and creation features if needed
4. Customize UI to show only approved providers

### Can I integrate with our IT management system?

The application can be:
- Deployed via standard software deployment tools
- Configured with pre-defined YAML files
- Scripted using command-line operations
- Contact for custom integration needs

## Versions & Updates

### How do I check my version?

- Check "About" in application (if implemented)
- Run: `python dns_changer.py --version`
- Check DNSChanger.exe properties

### How do I update?

1. Download latest release from GitHub
2. Replace executable
3. Keep your `dns_providers.yaml` (backup first)
4. Check CHANGELOG.md for breaking changes

### What's new in v2.0?

Major features in v2.0:
- DNS over HTTPS (DoH) support
- YAML-based configuration
- Automatic verification and rollback
- Enhanced UI with badges
- Migration from legacy format

See CHANGELOG.md for complete history.

## Getting Help

### Where can I get support?

1. Check this FAQ
2. Read README.md troubleshooting section
3. Review dnschanger.log
4. Search GitHub issues
5. Open new GitHub issue with details

### How do I report a bug?

See CONTRIBUTING.md for bug report template. Include:
- Windows version
- DNSChanger version
- Steps to reproduce
- Log file excerpts
- Screenshots if applicable

### Can I request features?

Yes! Open a GitHub issue with:
- Feature description
- Use case
- Why it would be valuable
- Suggested implementation (optional)

---

**Still have questions?** Open an issue on GitHub or check the documentation:
- README.md - User guide
- DEPLOYMENT.md - Build and deployment
- CONTRIBUTING.md - Development guide
