# DNS Changer

A modern, dark-themed GUI application for Windows that allows you to easily change DNS settings for your network interfaces. Built with Python and CustomTkinter for a sleek, contemporary interface.

![DNS Changer Interface](https://img.shields.io/badge/Platform-Windows-blue) ![Python](https://img.shields.io/badge/Python-3.7+-green) ![License](https://img.shields.io/badge/License-MIT-orange)

## Features

- 🎨 **Modern Dark Interface**: Sleek dark theme with acid green accents
- 🔌 **Smart Interface Detection**: Automatically detects and lists only active physical network adapters
- 📋 **Multiple Interface Support**: Select one or multiple network interfaces simultaneously
- 🔍 **Current DNS Display**: View currently configured DNS settings for selected interfaces
- 📝 **Customizable DNS List**: Easy-to-edit text file for managing DNS server presets
- ⚡ **Quick Actions**: Apply DNS settings or reset to DHCP with one click
- 🔒 **Administrator Rights**: Automatic elevation to administrator privileges when needed
- 📊 **Real-time Status**: Live status updates and error handling

## Screenshots

<img width="707" alt="image" src="https://github.com/user-attachments/assets/209a730b-864b-41eb-a428-bd53e6736dbe" />

*Interface showing network adapters, DNS server options, and current DNS settings*

## Prerequisites

- Windows 10/11
- Python 3.7 or higher
- Administrator privileges (the application will request elevation automatically)

## Installation

### Option 1: Run from Source

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/dns-changer.git
   cd dns-changer
   ```

2. **Install required dependencies**:
   ```bash
   pip install customtkinter
   ```

3. **Run the application**:
   ```bash
   python dns_changer.py
   ```

### Option 2: Standalone Executable

1. Download the latest release from the [Releases](https://github.com/yourusername/dns-changer/releases) page
2. Extract the files to a folder
3. Run `dns_changer.exe`

## Usage

### First Launch
1. The application will automatically request administrator privileges
2. Network interfaces will be loaded and displayed on the left panel
3. A default `dns_list.txt` file will be created with common DNS servers

### Changing DNS Settings
1. **Select Interface(s)**: Check one or more network interfaces from the left panel
2. **View Current Settings**: Selected interfaces' current DNS settings appear in the middle panel
3. **Choose DNS Server**: Select a DNS server preset from the right panel
4. **Apply Changes**: Click "Apply Selected DNS" to update the settings

### Resetting to DHCP
1. Select the interface(s) you want to reset
2. Click "Set to Automatic (DHCP)" to revert to automatic DNS assignment

### Refreshing Interfaces
- Click "Refresh Interfaces" to reload the network adapter list
- Useful when connecting/disconnecting network devices

## DNS Server Configuration

The application reads DNS server presets from `dns_list.txt`. The format is:
```
# DNS Server List
# Format: Name,Primary DNS,Secondary DNS
Google DNS,8.8.8.8,8.8.4.4
Cloudflare DNS,1.1.1.1,1.0.0.1
OpenDNS,208.67.222.222,208.67.220.220
Quad9,9.9.9.9,149.112.112.112
AdGuard DNS,94.140.14.14,94.140.15.15
```

### Adding Custom DNS Servers
1. Open `dns_list.txt` in any text editor
2. Add new entries following the format: `Name,Primary DNS,Secondary DNS`
3. Save the file and restart the application or use "Refresh Interfaces"

## Technical Details

### PowerShell Commands Used
The application uses the following PowerShell commands for DNS management:

- **List Network Adapters**: 
  ```powershell
  Get-NetAdapter | Where-Object { $_.Status -eq 'Up' ... }
  ```

- **Set DNS Servers**:
  ```powershell
  Set-DnsClientServerAddress -InterfaceIndex <ID> -ServerAddresses ("8.8.8.8","1.1.1.1")
  ```

- **Reset to DHCP**:
  ```powershell
  Set-DnsClientServerAddress -InterfaceIndex <ID> -ResetServerAddresses
  ```

- **Get Current DNS**:
  ```powershell
  Get-DnsClientServerAddress -InterfaceIndex <ID>
  ```

### Interface Filtering
The application filters network interfaces to show only:
- Interfaces with "Up" status
- Non-virtual interfaces (excludes VMware, VirtualBox, Hyper-V, etc.)
- Non-loopback interfaces
- Interfaces with valid media types

## Building from Source

To create a standalone executable:

1. **Install PyInstaller**:
   ```bash
   pip install pyinstaller
   ```

2. **Build the executable**:
   ```bash
   pyinstaller --icon="icona.ico" --noconsole --name DNSChanger --onefile --windowed --uac-admin --add-data "dns_list.txt;." dns_changer.py
   ```

3. **The executable will be created in the `dist` folder**

## Troubleshooting

### Common Issues

**"No active network adapters found"**
- Ensure you're running as administrator
- Check that your network adapters are connected and enabled
- Try clicking "Refresh Interfaces"

**"PowerShell Error"**
- Verify PowerShell is installed and accessible
- Check that execution policy allows script execution
- Ensure you have administrator privileges

**"Administrator rights are required"**
- Right-click the application and select "Run as administrator"
- The application should normally request elevation automatically

**DNS changes not taking effect**
- Some applications may cache DNS settings
- Try restarting your browser or flushing DNS cache: `ipconfig /flushdns`
- Restart the network adapter if necessary

### Logging and Debugging
The application provides real-time status updates in the bottom status bar. Error messages will appear in red, warnings in orange, and success messages in green.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly on Windows
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) for the modern GUI
- Uses Windows PowerShell for network configuration
- Inspired by the need for a simple, visual DNS management tool

## Changelog

### v1.0.0
- Initial release
- Basic DNS changing functionality
- Modern dark theme interface
- Multiple interface selection
- Current DNS settings display
- Automatic DNS server list creation

---

**⚠️ Important**: This application modifies system network settings. Always ensure you have a way to revert changes if needed. The "Set to Automatic (DHCP)" function can restore default settings.


![Downloads](https://img.shields.io/github/downloads/gulp79/DNSChanger/total?style=for-the-badge&labelColor=21262d&color=238636)
