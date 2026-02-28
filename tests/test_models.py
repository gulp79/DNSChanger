"""Tests for DNS provider models."""

import pytest
from pydantic import ValidationError

from models.dns_provider import DNSProvider, DNSProviderList, DNSPolicy


def test_dns_policy_defaults():
    """Test DNS policy default values."""
    policy = DNSPolicy()
    assert policy.encrypted_only == False
    assert policy.autoupgrade == True
    assert policy.allow_udp_fallback == False


def test_valid_dns_provider():
    """Test creating a valid DNS provider."""
    provider = DNSProvider(
        name="Test DNS",
        ipv4=["8.8.8.8", "8.8.4.4"],
        doh_template="https://dns.example.com/dns-query",
        tags=["test", "public"],
        policy=DNSPolicy(encrypted_only=True)
    )
    
    assert provider.name == "Test DNS"
    assert len(provider.ipv4) == 2
    assert provider.doh_template.startswith("https://")
    assert "test" in provider.tags


def test_invalid_ipv4():
    """Test validation of invalid IPv4 addresses."""
    with pytest.raises(ValidationError):
        DNSProvider(
            name="Invalid DNS",
            ipv4=["256.256.256.256"],  # Invalid IP
        )


def test_invalid_doh_template():
    """Test validation of invalid DoH template."""
    with pytest.raises(ValidationError):
        DNSProvider(
            name="Invalid DoH",
            ipv4=["8.8.8.8"],
            doh_template="not-a-url"  # Invalid URL
        )


def test_encrypted_only_without_doh():
    """Test that encrypted_only requires doh_template."""
    with pytest.raises(ValidationError):
        DNSProvider(
            name="Invalid Policy",
            ipv4=["8.8.8.8"],
            doh_template=None,
            policy=DNSPolicy(encrypted_only=True)  # Requires DoH template
        )


def test_provider_list_validation():
    """Test DNS provider list validation."""
    providers = [
        DNSProvider(name="DNS1", ipv4=["8.8.8.8"]),
        DNSProvider(name="DNS2", ipv4=["1.1.1.1"])
    ]
    
    provider_list = DNSProviderList(version=1, providers=providers)
    assert len(provider_list.providers) == 2


def test_duplicate_provider_names():
    """Test that duplicate provider names are rejected."""
    with pytest.raises(ValidationError):
        DNSProviderList(
            version=1,
            providers=[
                DNSProvider(name="DNS", ipv4=["8.8.8.8"]),
                DNSProvider(name="DNS", ipv4=["1.1.1.1"])  # Duplicate name
            ]
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
