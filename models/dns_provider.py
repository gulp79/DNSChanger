"""DNS Provider data models with Pydantic validation."""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
import ipaddress


class DNSPolicy(BaseModel):
    """DNS policy configuration."""
    
    encrypted_only: bool = Field(
        default=False,
        description="Require DoH encryption on the adapter"
    )
    autoupgrade: bool = Field(
        default=True,
        description="Automatically upgrade to DoH when possible"
    )
    allow_udp_fallback: bool = Field(
        default=False,
        description="Allow fallback to unencrypted DNS"
    )


class DNSProvider(BaseModel):
    """DNS provider configuration model."""
    
    name: str = Field(..., min_length=1, max_length=100, description="Provider name")
    ipv4: List[str] = Field(..., min_length=1, description="List of IPv4 DNS addresses")
    ipv6: Optional[List[str]] = Field(default=None, description="List of IPv6 DNS addresses")
    doh_template: Optional[str] = Field(default=None, description="DoH template URL")
    tags: List[str] = Field(default_factory=list, description="Provider tags")
    policy: DNSPolicy = Field(default_factory=DNSPolicy, description="DNS policy settings")
    
    @field_validator('ipv4')
    @classmethod
    def validate_ipv4(cls, v: List[str]) -> List[str]:
        """Validate IPv4 addresses."""
        for ip in v:
            try:
                addr = ipaddress.ip_address(ip)
                if addr.version != 4:
                    raise ValueError(f"'{ip}' is not a valid IPv4 address")
            except ValueError as e:
                raise ValueError(f"Invalid IPv4 address '{ip}': {e}")
        return v
    
    @field_validator('ipv6')
    @classmethod
    def validate_ipv6(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate IPv6 addresses."""
        if v is None:
            return None
        for ip in v:
            try:
                addr = ipaddress.ip_address(ip)
                if addr.version != 6:
                    raise ValueError(f"'{ip}' is not a valid IPv6 address")
            except ValueError as e:
                raise ValueError(f"Invalid IPv6 address '{ip}': {e}")
        return v
    
    @field_validator('doh_template')
    @classmethod
    def validate_doh_template(cls, v: Optional[str]) -> Optional[str]:
        """Validate DoH template URL."""
        if v is not None and not v.startswith(('https://', 'http://')):
            raise ValueError(f"DoH template must start with https:// or http://")
        return v
    
    @model_validator(mode='after')
    def validate_policy_with_doh(self) -> 'DNSProvider':
        """Validate that policy settings are consistent with DoH availability."""
        if self.policy.encrypted_only and self.doh_template is None:
            raise ValueError(
                f"Provider '{self.name}' has encrypted_only=true but no doh_template defined"
            )
        return self


class DNSProviderList(BaseModel):
    """Container for DNS providers list."""
    
    version: int = Field(..., ge=1, description="Schema version")
    providers: List[DNSProvider] = Field(..., min_length=1, description="List of DNS providers")
    
    @field_validator('providers')
    @classmethod
    def validate_unique_names(cls, v: List[DNSProvider]) -> List[DNSProvider]:
        """Ensure provider names are unique."""
        names = [p.name for p in v]
        if len(names) != len(set(names)):
            duplicates = [name for name in names if names.count(name) > 1]
            raise ValueError(f"Duplicate provider names found: {', '.join(set(duplicates))}")
        return v
