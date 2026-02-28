"""DNS over HTTPS (DoH) manager for Windows 11/Server 2022."""

import logging
import platform
from typing import List, Optional, Tuple, Dict
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class DoHStatus(Enum):
    """DoH support status."""
    SUPPORTED = "supported"
    NOT_SUPPORTED = "not_supported"
    POLICY_BLOCKED = "policy_blocked"
    UNKNOWN = "unknown"


@dataclass
class DoHServer:
    """DoH server configuration."""
    server_address: str
    doh_template: str
    auto_upgrade: bool = True
    allow_fallback: bool = False


@dataclass
class DoHState:
    """Current DoH state for an interface."""
    interface_index: str
    interface_name: str
    doh_servers: List[DoHServer]
    encryption_enabled: bool = False
    encryption_mode: Optional[str] = None


class DoHManager:
    """Manages DNS over HTTPS configuration on Windows."""
    
    # Minimum Windows versions that support DoH
    MIN_WIN_VERSION_DOH = (10, 0, 20348)  # Windows Server 2022 / Windows 11
    MIN_WIN_VERSION_ENCRYPTION = (10, 0, 22000)  # Windows 11
    
    def __init__(self, ps_adapter):
        """
        Initialize DoH manager.
        
        Args:
            ps_adapter: PowerShell adapter for executing commands
        """
        self.ps_adapter = ps_adapter
        self._check_support()
    
    def _check_support(self) -> None:
        """Check DoH support on current system."""
        self.doh_supported = self._is_doh_supported()
        self.encryption_supported = self._is_encryption_supported()
        
        if self.doh_supported:
            logger.info("DoH is supported on this system")
        else:
            logger.warning("DoH is not supported on this Windows version")
        
        if self.encryption_supported:
            logger.info("DNS encryption is supported on this system")
        else:
            logger.info("DNS encryption requires Windows 11 or newer")
    
    def _is_doh_supported(self) -> bool:
        """Check if DoH is supported on current Windows version."""
        try:
            version = platform.version().split('.')
            major = int(version[0])
            minor = int(version[1])
            build = int(version[2])
            
            win_version = (major, minor, build)
            return win_version >= self.MIN_WIN_VERSION_DOH
        except:
            # If we can't determine version, assume not supported
            return False
    
    def _is_encryption_supported(self) -> bool:
        """Check if DNS encryption is supported."""
        try:
            version = platform.version().split('.')
            major = int(version[0])
            minor = int(version[1])
            build = int(version[2])
            
            win_version = (major, minor, build)
            return win_version >= self.MIN_WIN_VERSION_ENCRYPTION
        except:
            return False
    
    def is_supported(self) -> Tuple[bool, str]:
        """
        Check if DoH is supported and not blocked by policy.
        
        Returns:
            Tuple of (supported, message)
        """
        if not self.doh_supported:
            return False, (
                "DNS over HTTPS requires Windows 11 or Windows Server 2022 or newer. "
                "Your current Windows version does not support DoH."
            )
        
        # Check if DoH is blocked by policy
        policy_blocked, policy_msg = self._check_policy()
        if policy_blocked:
            return False, policy_msg
        
        return True, "DoH is supported and available"
    
    def _check_policy(self) -> Tuple[bool, str]:
        """Check if DoH is blocked by Group Policy."""
        command = """
        try {
            $policy = Get-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows NT\\DNSClient' -Name EnableAutoDoh -ErrorAction SilentlyContinue
            if ($policy -and $policy.EnableAutoDoh -eq 0) {
                'BLOCKED'
            } else {
                'ALLOWED'
            }
        } catch {
            'ALLOWED'
        }
        """
        
        success, output = self.ps_adapter.execute(command)
        
        if success and output.strip() == 'BLOCKED':
            return True, (
                "DoH is blocked by Group Policy. Contact your system administrator to enable DoH, "
                "or modify the registry key: "
                "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows NT\\DNSClient\\EnableAutoDoh"
            )
        
        return False, ""
    
    def add_doh_server(
        self,
        server_address: str,
        doh_template: str,
        auto_upgrade: bool = True,
        allow_fallback: bool = False
    ) -> Tuple[bool, str]:
        """
        Add or update DoH server configuration.
        
        Args:
            server_address: DNS server IP address
            doh_template: DoH template URL
            auto_upgrade: Enable automatic upgrade to DoH
            allow_fallback: Allow fallback to unencrypted DNS
            
        Returns:
            Tuple of (success, message)
        """
        if not self.doh_supported:
            return False, "DoH is not supported on this Windows version"
        
        # Remove existing entry first
        self.remove_doh_server(server_address)
        
        # Add new DoH server
        command = f"""
        Add-DnsClientDohServerAddress `
            -ServerAddress '{server_address}' `
            -DohTemplate '{doh_template}' `
            -AutoUpgrade:${str(auto_upgrade)} `
            -AllowFallbackToUdp:${str(allow_fallback)}
        """
        
        success, output = self.ps_adapter.execute(command)
        
        if success:
            logger.info(f"Added DoH server: {server_address} -> {doh_template}")
            return True, f"DoH server registered: {server_address}"
        else:
            logger.error(f"Failed to add DoH server {server_address}: {output}")
            return False, output
    
    def remove_doh_server(self, server_address: str) -> Tuple[bool, str]:
        """
        Remove DoH server configuration.
        
        Args:
            server_address: DNS server IP address
            
        Returns:
            Tuple of (success, message)
        """
        if not self.doh_supported:
            return False, "DoH is not supported on this Windows version"
        
        command = f"Remove-DnsClientDohServerAddress -ServerAddress '{server_address}' -ErrorAction SilentlyContinue"
        
        success, output = self.ps_adapter.execute(command)
        
        if success:
            logger.info(f"Removed DoH server: {server_address}")
            return True, f"DoH server removed: {server_address}"
        else:
            # Not an error if server doesn't exist
            logger.debug(f"DoH server {server_address} was not registered or already removed")
            return True, ""
    
    def get_doh_servers(self) -> List[DoHServer]:
        """
        Get list of registered DoH servers.
        
        Returns:
            List of DoHServer objects
        """
        if not self.doh_supported:
            return []
        
        command = """
        Get-DnsClientDohServerAddress | 
        Select-Object ServerAddress, DohTemplate, AutoUpgrade, AllowFallbackToUdp | 
        ConvertTo-Json
        """
        
        success, output = self.ps_adapter.execute(command)
        
        if not success or not output:
            return []
        
        try:
            import json
            data = json.loads(output)
            
            # Handle single item vs array
            if isinstance(data, dict):
                data = [data]
            
            servers = []
            for item in data:
                server = DoHServer(
                    server_address=item.get('ServerAddress', ''),
                    doh_template=item.get('DohTemplate', ''),
                    auto_upgrade=item.get('AutoUpgrade', True),
                    allow_fallback=item.get('AllowFallbackToUdp', False)
                )
                servers.append(server)
            
            return servers
            
        except Exception as e:
            logger.error(f"Failed to parse DoH servers: {e}")
            return []
    
    def set_interface_encryption(
        self,
        interface_index: str,
        encrypted_only: bool = True
    ) -> Tuple[bool, str]:
        """
        Set DNS encryption mode (Windows 11+ only).
        
        Uses the registry key EnableDohEbpf under Dnscache\\Parameters
        to force encrypted DNS when DoH servers are registered.
        This is a system-wide setting: when enabled, Windows will use
        DoH for any server that has a registered DoH template.
        
        Args:
            interface_index: Network interface index (kept for API compat)
            encrypted_only: If True, enable encrypted-only DNS
            
        Returns:
            Tuple of (success, message)
        """
        if not self.encryption_supported:
            return False, "DNS encryption settings require Windows 11 or newer"
        
        reg_path = r"HKLM:\SYSTEM\CurrentControlSet\Services\Dnscache\Parameters"
        value_name = "EnableDohEbpf"
        value = 1 if encrypted_only else 0
        
        command = f"""
        try {{
            $path = '{reg_path}'
            if (-not (Test-Path $path)) {{
                New-Item -Path $path -Force | Out-Null
            }}
            Set-ItemProperty -Path $path -Name '{value_name}' -Value {value} -Type DWord
            # Riavvia il servizio Dnscache per applicare la modifica
            Restart-Service -Name Dnscache -Force -ErrorAction SilentlyContinue
            'OK'
        }} catch {{
            $_.Exception.Message
        }}
        """
        
        success, output = self.ps_adapter.execute(command)
        
        if success and output.strip() == 'OK':
            mode = "Encrypted only (DoH)" if encrypted_only else "Automatic"
            logger.info(f"Set DNS encryption mode to: {mode}")
            return True, f"DNS encryption configured: {mode}"
        else:
            error_msg = output.strip() if output else "Unknown error"
            logger.error(f"Failed to set encryption mode: {error_msg}")
            return False, error_msg
    
    def get_interface_doh_state(self, interface_index: str, interface_name: str) -> DoHState:
        """
        Get DoH state for a network interface.
        
        Args:
            interface_index: Network interface index
            interface_name: Network interface name
            
        Returns:
            DoHState object
        """
        # Get DNS servers for interface
        dns_servers = self.ps_adapter.get_dns_servers(interface_index)
        
        # Get registered DoH servers
        all_doh_servers = self.get_doh_servers()
        
        # Find DoH servers that match interface DNS servers
        interface_doh_servers = [
            doh for doh in all_doh_servers
            if doh.server_address in dns_servers
        ]
        
        state = DoHState(
            interface_index=interface_index,
            interface_name=interface_name,
            doh_servers=interface_doh_servers
        )
        
        # Check encryption status (Windows 11+ only)
        if self.encryption_supported:
            encryption_info = self._get_encryption_info(interface_index)
            state.encryption_enabled = encryption_info[0]
            state.encryption_mode = encryption_info[1]
        
        return state
    
    def _get_encryption_info(self, interface_index: str) -> Tuple[bool, Optional[str]]:
        """Get encryption information by reading the Dnscache registry key."""
        reg_path = r"HKLM:\SYSTEM\CurrentControlSet\Services\Dnscache\Parameters"
        value_name = "EnableDohEbpf"
        
        command = f"""
        try {{
            $val = Get-ItemPropertyValue -Path '{reg_path}' -Name '{value_name}' -ErrorAction Stop
            $val.ToString()
        }} catch {{
            'NOT_SET'
        }}
        """
        
        success, output = self.ps_adapter.execute(command)
        
        if not success:
            return False, None
        
        raw = output.strip()
        if raw == '1':
            return True, "Encrypted only (DoH)"
        elif raw == '0':
            return False, "Automatic (encryption disabled)"
        else:
            # Chiave non presente = comportamento predefinito (automatic)
            return False, None
    
    def configure_provider_doh(
        self,
        interface_index: str,
        dns_servers: List[str],
        doh_template: Optional[str],
        policy_encrypted_only: bool = False,
        policy_auto_upgrade: bool = True,
        policy_allow_fallback: bool = False
    ) -> Tuple[bool, str]:
        """
        Configure DoH for a DNS provider on an interface.
        
        Args:
            interface_index: Network interface index
            dns_servers: List of DNS server IP addresses
            doh_template: DoH template URL (None to skip DoH)
            policy_encrypted_only: Require encrypted DNS only
            policy_auto_upgrade: Auto-upgrade to DoH when possible
            policy_allow_fallback: Allow fallback to unencrypted DNS
            
        Returns:
            Tuple of (success, message)
        """
        messages = []
        
        # Combinare l'impostazione DNS e DoH in un singolo comando PowerShell
        # per evitare l'overhead di avviare ripetutamente powershell.exe
        formatted_dns = ",".join([f'"{dns.strip()}"' for dns in dns_servers])
        
        ps_script = f"""
        $ErrorActionPreference = 'Stop'
        $msgs = @()
        
        try {{
            # 1. Imposta i server DNS
            Set-DnsClientServerAddress -InterfaceIndex {interface_index} -ServerAddresses ({formatted_dns}) -Validate
            $msgs += "DNS servers applied successfully"
            
            # 2. Configura DoH se richiesto e supportato
            $needs_doh = $false
            if ('{doh_template}' -ne 'None' -and '{doh_template}' -ne '') {{
                $needs_doh = $true
            }}
        """
        
        if self.doh_supported:
            ps_script += f"""
            if ($needs_doh) {{
                # Rimuovi eventuali DoH precedenti per i nuovi IP
                foreach ($dns in ({formatted_dns})) {{
                    Remove-DnsClientDohServerAddress -ServerAddress $dns -ErrorAction SilentlyContinue
                    
                    # Aggiungi il nuovo DoH
                    Add-DnsClientDohServerAddress `
                        -ServerAddress $dns `
                        -DohTemplate '{doh_template}' `
                        -AutoUpgrade:${str(policy_auto_upgrade)} `
                        -AllowFallbackToUdp:${str(policy_allow_fallback)}
                        
                    $msgs += "DoH configured for $dns"
                }}
            """
            if self.encryption_supported and policy_encrypted_only:
                ps_script += f"""
                # Imposta Encryption Only Mode (Windows 11+)
                $reg_path = 'HKLM:\\SYSTEM\\CurrentControlSet\\Services\\Dnscache\\Parameters'
                if (-not (Test-Path $reg_path)) {{
                    New-Item -Path $reg_path -Force | Out-Null
                }}
                Set-ItemProperty -Path $reg_path -Name 'EnableDohEbpf' -Value 1 -Type DWord
                Restart-Service -Name Dnscache -Force -ErrorAction SilentlyContinue
                $msgs += "🔒 Encryption: Encrypted only"
                """
            ps_script += """
            }
            """
        else:
            ps_script += """
            if ($needs_doh) {
                $msgs += "⚠️  DoH not supported on this Windows version"
            }
            """
            
        ps_script += """
            $msgs -join "`n"
        } catch {
            Write-Error $_.Exception.Message
            exit 1
        }
        """
        
        success, output = self.ps_adapter.execute(ps_script)
        
        if success:
            logger.info(f"Applied DNS and DoH configuration for interface {interface_index}")
            return True, output.strip()
        else:
            logger.error(f"Failed to apply DNS/DoH configuration: {output}")
            return False, output
