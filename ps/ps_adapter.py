"""PowerShell adapter for Windows DNS management."""

import subprocess
import json
import logging
from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class InterfaceType(Enum):
    """Network interface type."""
    PHYSICAL = "physical"
    VIRTUAL = "virtual"
    LOOPBACK = "loopback"
    VPN = "vpn"
    TAP = "tap"
    UNKNOWN = "unknown"


@dataclass
class NetworkAdapter:
    """Network adapter information."""
    name: str
    index: str
    description: str
    status: str
    link_speed: Optional[str] = None
    interface_type: InterfaceType = InterfaceType.UNKNOWN
    is_physical: bool = False
    mac_address: Optional[str] = None
    
    @property
    def display_name(self) -> str:
        """Get formatted display name."""
        speed = f" [{self.link_speed}]" if self.link_speed else ""
        return f"{self.name}{speed}"


class PowerShellAdapter:
    """Adapter for executing PowerShell commands with proper error handling."""
    
    # Virtual interface detection patterns
    VIRTUAL_PATTERNS = [
        'Loopback', 'Virtual', 'VMware', 'VirtualBox', 'Hyper-V',
        'TAP', 'VPN', 'Wi-Fi Direct', 'Bluetooth', 'vEthernet'
    ]
    
    # Default timeout for PowerShell commands (seconds)
    DEFAULT_TIMEOUT = 30
    
    def __init__(self, timeout: int = DEFAULT_TIMEOUT):
        """
        Initialize PowerShell adapter.
        
        Args:
            timeout: Default timeout for PowerShell commands in seconds
        """
        self.timeout = timeout
        self.last_error: Optional[str] = None
    
    def execute(
        self,
        command: str,
        timeout: Optional[int] = None,
        capture_output: bool = True
    ) -> Tuple[bool, str]:
        """
        Execute a PowerShell command.
        
        Args:
            command: PowerShell command to execute
            timeout: Command timeout in seconds. Uses default if None.
            capture_output: Whether to capture and return output
            
        Returns:
            Tuple of (success, output/error_message)
        """
        if timeout is None:
            timeout = self.timeout
        
        self.last_error = None
        
        try:
            logger.debug(f"Executing PowerShell command: {command[:100]}...")
            
            completed_process = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-Command", command],
                capture_output=capture_output,
                text=True,
                timeout=timeout,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0,
                encoding='utf-8',
                errors='replace'
            )
            
            if completed_process.returncode == 0:
                output = completed_process.stdout.strip() if capture_output else ""
                logger.debug(f"Command successful. Output length: {len(output)}")
                return True, output
            else:
                error = completed_process.stderr.strip() if capture_output else "Command failed"
                self.last_error = error
                logger.error(f"PowerShell command failed (code {completed_process.returncode}): {error}")
                return False, self._format_error(error)
                
        except subprocess.TimeoutExpired:
            error_msg = f"Command timed out after {timeout} seconds"
            self.last_error = error_msg
            logger.error(error_msg)
            return False, error_msg
            
        except FileNotFoundError:
            error_msg = "PowerShell is not installed or not in PATH"
            self.last_error = error_msg
            logger.error(error_msg)
            return False, error_msg
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.last_error = error_msg
            logger.error(f"PowerShell execution error: {e}")
            return False, error_msg
    
    def _format_error(self, error: str) -> str:
        """Format PowerShell error message for user display."""
        if not error:
            return "Unknown error occurred"
        
        # Extract meaningful error messages
        if "access is denied" in error.lower():
            return "Access denied. Administrator privileges required."
        elif "does not exist" in error.lower():
            return "Network adapter not found or unavailable."
        elif "parameter is incorrect" in error.lower():
            return "Invalid DNS server address or configuration."
        elif "not supported" in error.lower():
            return "Operation not supported on this Windows version."
        else:
            # Return first meaningful line
            lines = [line.strip() for line in error.split('\n') if line.strip()]
            return lines[0] if lines else error
    
    def get_network_adapters(
        self,
        include_virtual: bool = False,
        include_down: bool = False
    ) -> List[NetworkAdapter]:
        """
        Get list of network adapters.
        
        Args:
            include_virtual: Include virtual adapters (VMware, VirtualBox, etc.)
            include_down: Include disconnected adapters
            
        Returns:
            List of NetworkAdapter objects
        """
        # Build filter conditions
        conditions = []
        if not include_down:
            conditions.append("$_.Status -eq 'Up'")
        
        if not include_virtual:
            for pattern in self.VIRTUAL_PATTERNS:
                conditions.append(f"$_.Name -notlike '*{pattern}*'")
            conditions.append("$_.InterfaceType -ne 'Software Loopback'")
            conditions.append("$_.MediaType -ne $null")
        
        where_clause = " -and ".join(conditions) if conditions else "$true"
        
        command = f"""
        @(Get-NetAdapter | Where-Object {{ {where_clause} }} | 
        Select-Object Name, InterfaceIndex, InterfaceDescription, Status, LinkSpeed, InterfaceType, MacAddress) | 
        ConvertTo-Json
        """
        
        success, output = self.execute(command)
        
        if not success:
            logger.error(f"Failed to get network adapters: {output}")
            return []
        
        try:
            data = json.loads(output) if output else []
            
            # PowerShell returns dict for single item, list for multiple
            if isinstance(data, dict):
                data = [data]
            
            adapters = []
            for item in data:
                adapter_type = self._detect_interface_type(
                    item.get('Name', ''),
                    item.get('InterfaceDescription', ''),
                    item.get('InterfaceType', '')
                )
                
                adapter = NetworkAdapter(
                    name=item.get('Name', 'Unknown'),
                    index=str(item.get('InterfaceIndex', '')),
                    description=item.get('InterfaceDescription', ''),
                    status=item.get('Status', 'Unknown'),
                    link_speed=item.get('LinkSpeed'),
                    interface_type=adapter_type,
                    is_physical=adapter_type == InterfaceType.PHYSICAL,
                    mac_address=item.get('MacAddress')
                )
                adapters.append(adapter)
            
            logger.info(f"Found {len(adapters)} network adapters")
            return adapters
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse adapter JSON: {e}")
            return []
        except Exception as e:
            logger.error(f"Error processing adapters: {e}")
            return []
    
    def _detect_interface_type(self, name: str, description: str, iface_type: str) -> InterfaceType:
        """Detect network interface type based on name and description."""
        combined = f"{name} {description} {iface_type}".lower()
        
        if 'loopback' in combined:
            return InterfaceType.LOOPBACK
        elif any(pattern.lower() in combined for pattern in ['vpn', 'ras', 'pptp', 'l2tp']):
            return InterfaceType.VPN
        elif 'tap' in combined or 'tun' in combined:
            return InterfaceType.TAP
        elif any(pattern.lower() in combined for pattern in self.VIRTUAL_PATTERNS):
            return InterfaceType.VIRTUAL
        else:
            return InterfaceType.PHYSICAL
    
    def get_dns_servers(self, interface_index: str) -> List[str]:
        """
        Get current DNS servers for an interface.
        
        Args:
            interface_index: Network interface index
            
        Returns:
            List of DNS server addresses (empty if DHCP)
        """
        command = f"""
        Get-DnsClientServerAddress -InterfaceIndex {interface_index} | 
        Where-Object {{$_.AddressFamily -eq 2}} | 
        Select-Object ServerAddresses | 
        ConvertTo-Json
        """
        
        success, output = self.execute(command)
        
        if not success:
            logger.error(f"Failed to get DNS servers for interface {interface_index}")
            return []
        
        try:
            if not output:
                return []
            
            data = json.loads(output)
            
            # Handle both single dict and list of dicts
            if isinstance(data, dict):
                return data.get('ServerAddresses', [])
            elif isinstance(data, list) and len(data) > 0:
                return data[0].get('ServerAddresses', [])
            
            return []
            
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.error(f"Failed to parse DNS servers: {e}")
            return []
    
    def set_dns_servers(
        self,
        interface_index: str,
        dns_servers: List[str],
        validate: bool = True
    ) -> Tuple[bool, str]:
        """
        Set DNS servers for an interface.
        
        Args:
            interface_index: Network interface index
            dns_servers: List of DNS server addresses
            validate: Whether to validate DNS configuration
            
        Returns:
            Tuple of (success, message)
        """
        if not dns_servers:
            return False, "No DNS servers provided"
        
        # Format DNS addresses for PowerShell
        formatted_dns = ",".join([f'"{dns.strip()}"' for dns in dns_servers])
        validate_flag = "-Validate" if validate else ""
        
        command = f"""
        Set-DnsClientServerAddress -InterfaceIndex {interface_index} -ServerAddresses ({formatted_dns}) {validate_flag}
        """
        
        success, output = self.execute(command)
        
        if success:
            logger.info(f"Set DNS servers for interface {interface_index}: {dns_servers}")
            return True, f"DNS servers applied successfully"
        else:
            logger.error(f"Failed to set DNS for interface {interface_index}: {output}")
            return False, output
    
    def reset_dns(self, interface_index: str) -> Tuple[bool, str]:
        """
        Reset DNS to automatic (DHCP) for an interface.
        
        Args:
            interface_index: Network interface index
            
        Returns:
            Tuple of (success, message)
        """
        command = f"Set-DnsClientServerAddress -InterfaceIndex {interface_index} -ResetServerAddresses"
        
        success, output = self.execute(command)
        
        if success:
            logger.info(f"Reset DNS to DHCP for interface {interface_index}")
            return True, "DNS reset to automatic (DHCP)"
        else:
            logger.error(f"Failed to reset DNS for interface {interface_index}: {output}")
            return False, output
    
    def resolve_dns(self, domain: str, timeout: int = 5) -> Tuple[bool, str]:
        """
        Test DNS resolution for a domain.
        
        Args:
            domain: Domain name to resolve
            timeout: Timeout in seconds
            
        Returns:
            Tuple of (success, error_message)
        """
        command = f"Resolve-DnsName -Name {domain} -DnsOnly -QuickTimeout -ErrorAction Stop"
        
        success, output = self.execute(command, timeout=timeout)
        
        if success:
            return True, ""
        else:
            return False, output
    
    def flush_dns_cache(self) -> Tuple[bool, str]:
        """
        Flush DNS cache.
        
        Returns:
            Tuple of (success, message)
        """
        # Use ipconfig for cache flush (more reliable than PowerShell)
        try:
            result = subprocess.run(
                ["ipconfig", "/flushdns"],
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            if result.returncode == 0:
                logger.info("DNS cache flushed successfully")
                return True, "DNS cache flushed successfully"
            else:
                error = result.stderr.strip() if result.stderr else "Failed to flush cache"
                return False, error
                
        except Exception as e:
            logger.error(f"Failed to flush DNS cache: {e}")
            return False, str(e)
    
    def get_last_error(self) -> Optional[str]:
        """Get the last error message."""
        return self.last_error
