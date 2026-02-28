"""DNS verification and rollback functionality."""

import logging
import time
from typing import List, Optional, Tuple, Dict
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class VerificationStatus(Enum):
    """DNS verification status."""
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    PARTIAL = "partial"


@dataclass
class VerificationResult:
    """Result of DNS verification."""
    status: VerificationStatus
    successful_domains: List[str]
    failed_domains: List[str]
    errors: List[str]
    duration_ms: float
    
    @property
    def is_successful(self) -> bool:
        """Check if verification was successful."""
        return self.status == VerificationStatus.SUCCESS
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        total = len(self.successful_domains) + len(self.failed_domains)
        if total == 0:
            return 0.0
        return len(self.successful_domains) / total
        
    def __str__(self) -> str:
        """String representation showing status and duration."""
        return f"Status: {self.status.value}, Success: {len(self.successful_domains)}/{len(self.successful_domains)+len(self.failed_domains)}, Time: {self.duration_ms:.1f}ms"


@dataclass
class DNSSnapshot:
    """Snapshot of DNS configuration for rollback."""
    interface_index: str
    interface_name: str
    dns_servers: List[str]
    is_dhcp: bool
    timestamp: float


class DNSVerifier:
    """Handles DNS verification and rollback operations."""
    
    # Test domains for verification
    DEFAULT_TEST_DOMAINS = [
        "example.com",
        "google.com",
        "cloudflare.com"
    ]
    
    # Timeout for DNS resolution (seconds)
    DEFAULT_TIMEOUT = 5
    
    def __init__(self, ps_adapter):
        """
        Initialize DNS verifier.
        
        Args:
            ps_adapter: PowerShell adapter for executing commands
        """
        self.ps_adapter = ps_adapter
        self.snapshots: Dict[str, DNSSnapshot] = {}
    
    def create_snapshot(self, interface_index: str, interface_name: str) -> bool:
        """
        Create a snapshot of current DNS configuration before changes.
        
        Args:
            interface_index: Network interface index
            interface_name: Network interface name
            
        Returns:
            True if snapshot created successfully
        """
        try:
            dns_servers = self.ps_adapter.get_dns_servers(interface_index)
            is_dhcp = len(dns_servers) == 0
            
            snapshot = DNSSnapshot(
                interface_index=interface_index,
                interface_name=interface_name,
                dns_servers=dns_servers if not is_dhcp else [],
                is_dhcp=is_dhcp,
                timestamp=time.time()
            )
            
            self.snapshots[interface_index] = snapshot
            logger.info(f"Created DNS snapshot for interface {interface_name} (index: {interface_index})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create snapshot for interface {interface_index}: {e}")
            return False
    
    def rollback(self, interface_index: str) -> Tuple[bool, str]:
        """
        Rollback DNS configuration to snapshot.
        
        Args:
            interface_index: Network interface index
            
        Returns:
            Tuple of (success, message)
        """
        if interface_index not in self.snapshots:
            return False, f"No snapshot found for interface {interface_index}"
        
        snapshot = self.snapshots[interface_index]
        
        try:
            if snapshot.is_dhcp:
                # Restore to DHCP
                success, message = self.ps_adapter.reset_dns(interface_index)
                if success:
                    logger.info(f"Rolled back interface {snapshot.interface_name} to DHCP")
                    return True, f"Rolled back {snapshot.interface_name} to DHCP"
                else:
                    return False, f"Failed to rollback {snapshot.interface_name}: {message}"
            else:
                # Restore previous DNS servers
                success, message = self.ps_adapter.set_dns_servers(
                    interface_index,
                    snapshot.dns_servers,
                    validate=False  # Skip validation on rollback
                )
                if success:
                    logger.info(f"Rolled back interface {snapshot.interface_name} to {snapshot.dns_servers}")
                    return True, f"Rolled back {snapshot.interface_name} to previous DNS"
                else:
                    return False, f"Failed to rollback {snapshot.interface_name}: {message}"
                    
        except Exception as e:
            error_msg = f"Error during rollback for {snapshot.interface_name}: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def verify_dns(
        self,
        test_domains: Optional[List[str]] = None,
        timeout: int = DEFAULT_TIMEOUT
    ) -> VerificationResult:
        """
        Verify DNS functionality by resolving test domains.
        
        Args:
            test_domains: List of domains to test. Uses defaults if None.
            timeout: Timeout in seconds for each resolution
            
        Returns:
            VerificationResult object
        """
        if test_domains is None:
            test_domains = self.DEFAULT_TEST_DOMAINS
        
        start_time = time.time()
        successful_domains = []
        failed_domains = []
        errors = []
        
        for domain in test_domains:
            try:
                success, error = self.ps_adapter.resolve_dns(domain, timeout=timeout)
                
                if success:
                    successful_domains.append(domain)
                    logger.debug(f"Successfully resolved {domain}")
                else:
                    failed_domains.append(domain)
                    errors.append(f"{domain}: {error}")
                    logger.warning(f"Failed to resolve {domain}: {error}")
                    
            except Exception as e:
                failed_domains.append(domain)
                error_msg = f"{domain}: {str(e)}"
                errors.append(error_msg)
                logger.error(f"Error resolving {domain}: {e}")
        
        duration_ms = (time.time() - start_time) * 1000
        
        # Determine status
        if len(successful_domains) == len(test_domains):
            status = VerificationStatus.SUCCESS
        elif len(successful_domains) > 0:
            status = VerificationStatus.PARTIAL
        elif duration_ms > (timeout * 1000 * len(test_domains)):
            status = VerificationStatus.TIMEOUT
        else:
            status = VerificationStatus.FAILED
        
        result = VerificationResult(
            status=status,
            successful_domains=successful_domains,
            failed_domains=failed_domains,
            errors=errors,
            duration_ms=duration_ms
        )
        
        logger.info(
            f"DNS verification completed: {status.value} "
            f"({len(successful_domains)}/{len(test_domains)} successful)"
        )
        
        return result
    
    def verify_and_rollback_on_failure(
        self,
        interface_index: str,
        test_domains: Optional[List[str]] = None,
        timeout: int = DEFAULT_TIMEOUT,
        success_threshold: float = 0.5
    ) -> Tuple[bool, VerificationResult, Optional[str]]:
        """
        Verify DNS and automatically rollback if verification fails.
        
        Args:
            interface_index: Network interface index
            test_domains: List of domains to test
            timeout: Timeout in seconds for each resolution
            success_threshold: Minimum success rate (0.0-1.0) to consider verification passed
            
        Returns:
            Tuple of (verification_passed, verification_result, rollback_message)
        """
        result = self.verify_dns(test_domains, timeout)
        
        if result.success_rate >= success_threshold:
            logger.info(f"DNS verification passed with {result.success_rate:.1%} success rate")
            return True, result, None
        
        # Verification failed, attempt rollback
        logger.warning(
            f"DNS verification failed with {result.success_rate:.1%} success rate. "
            f"Attempting rollback..."
        )
        
        rollback_success, rollback_msg = self.rollback(interface_index)
        
        if rollback_success:
            logger.info(f"Rollback successful: {rollback_msg}")
        else:
            logger.error(f"Rollback failed: {rollback_msg}")
        
        return False, result, rollback_msg
    
    def clear_snapshot(self, interface_index: str) -> None:
        """Clear snapshot for an interface."""
        if interface_index in self.snapshots:
            del self.snapshots[interface_index]
            logger.debug(f"Cleared snapshot for interface {interface_index}")
    
    def clear_all_snapshots(self) -> None:
        """Clear all snapshots."""
        self.snapshots.clear()
        logger.debug("Cleared all DNS snapshots")
    
    def has_snapshot(self, interface_index: str) -> bool:
        """Check if snapshot exists for interface."""
        return interface_index in self.snapshots
    
    def get_snapshot(self, interface_index: str) -> Optional[DNSSnapshot]:
        """Get snapshot for interface."""
        return self.snapshots.get(interface_index)
