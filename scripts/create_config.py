#!/usr/bin/env python3
"""
DNS Provider Configuration Generator

Interactive tool to create custom DNS provider configurations.
Usage: python scripts/create_config.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.dns_provider import DNSProvider, DNSPolicy
from core.dns_loader import DNSLoader


def get_input(prompt: str, default: str = None) -> str:
    """Get user input with optional default."""
    if default:
        prompt = f"{prompt} [{default}]"
    
    value = input(f"{prompt}: ").strip()
    return value if value else default


def get_bool(prompt: str, default: bool = False) -> bool:
    """Get boolean input."""
    default_str = "Y/n" if default else "y/N"
    value = input(f"{prompt} ({default_str}): ").strip().lower()
    
    if not value:
        return default
    
    return value in ['y', 'yes', 'true', '1']


def get_list(prompt: str) -> list:
    """Get comma-separated list input."""
    value = input(f"{prompt} (comma-separated): ").strip()
    
    if not value:
        return []
    
    return [item.strip() for item in value.split(',') if item.strip()]


def create_provider_interactive() -> DNSProvider:
    """Create a DNS provider interactively."""
    print("\n" + "=" * 60)
    print("Create New DNS Provider")
    print("=" * 60)
    
    name = get_input("Provider name", "My DNS")
    
    print("\nIPv4 DNS servers:")
    ipv4 = get_list("  Enter IPv4 addresses")
    
    while not ipv4:
        print("  ⚠️  At least one IPv4 address is required")
        ipv4 = get_list("  Enter IPv4 addresses")
    
    print("\nIPv6 DNS servers (optional):")
    ipv6 = get_list("  Enter IPv6 addresses")
    ipv6 = ipv6 if ipv6 else None
    
    print("\nDNS over HTTPS configuration:")
    has_doh = get_bool("  Enable DoH?", False)
    doh_template = None
    
    if has_doh:
        doh_template = get_input("  DoH template URL", "https://dns.example.com/dns-query")
    
    print("\nProvider tags:")
    print("  Examples: privacy, security, fast, ad-block, public, family")
    tags = get_list("  Enter tags")
    
    print("\nDNS Policy:")
    if has_doh:
        encrypted_only = get_bool("  Require encrypted DNS only?", True)
        autoupgrade = get_bool("  Auto-upgrade to DoH?", True)
        allow_fallback = get_bool("  Allow UDP fallback?", False)
    else:
        encrypted_only = False
        autoupgrade = False
        allow_fallback = True
    
    policy = DNSPolicy(
        encrypted_only=encrypted_only,
        autoupgrade=autoupgrade,
        allow_udp_fallback=allow_fallback
    )
    
    provider = DNSProvider(
        name=name,
        ipv4=ipv4,
        ipv6=ipv6,
        doh_template=doh_template,
        tags=tags,
        policy=policy
    )
    
    return provider


def preview_provider(provider: DNSProvider):
    """Preview provider configuration."""
    print("\n" + "=" * 60)
    print("Provider Preview")
    print("=" * 60)
    print(f"\nName: {provider.name}")
    print(f"IPv4: {', '.join(provider.ipv4)}")
    
    if provider.ipv6:
        print(f"IPv6: {', '.join(provider.ipv6)}")
    
    if provider.doh_template:
        print(f"DoH: {provider.doh_template}")
    
    if provider.tags:
        print(f"Tags: {', '.join(provider.tags)}")
    
    print(f"\nPolicy:")
    print(f"  Encrypted Only: {provider.policy.encrypted_only}")
    print(f"  Auto Upgrade: {provider.policy.autoupgrade}")
    print(f"  UDP Fallback: {provider.policy.allow_udp_fallback}")


def main():
    """Main entry point."""
    print("DNS Provider Configuration Generator")
    print("=" * 60)
    
    providers = []
    
    while True:
        provider = create_provider_interactive()
        preview_provider(provider)
        
        if get_bool("\nAdd this provider?", True):
            providers.append(provider)
            print(f"✅ Provider '{provider.name}' added")
        
        if not get_bool("\nAdd another provider?", False):
            break
    
    if not providers:
        print("\n⚠️  No providers added. Exiting.")
        return
    
    # Save configuration
    print("\n" + "=" * 60)
    print("Save Configuration")
    print("=" * 60)
    
    output_file = get_input("\nOutput filename", "dns_providers.yaml")
    output_path = Path(output_file)
    
    # Check if file exists
    if output_path.exists():
        if not get_bool(f"\n⚠️  {output_file} already exists. Overwrite?", False):
            print("Cancelled.")
            return
    
    # Export
    loader = DNSLoader()
    success = loader.export_to_yaml(output_path, providers)
    
    if success:
        print(f"\n✅ Configuration saved to: {output_path.absolute()}")
        print(f"   Total providers: {len(providers)}")
    else:
        print(f"\n❌ Failed to save configuration")
        errors = loader.get_errors()
        for error in errors:
            print(f"   {error}")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
