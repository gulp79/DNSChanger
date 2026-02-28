#!/usr/bin/env python3
"""
DNS Provider Configuration Validator

This script validates dns_providers.yaml files against the schema.
Usage: python scripts/validate_config.py [config_file]
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.dns_loader import DNSLoader


def validate_config(config_path: Path) -> bool:
    """
    Validate a DNS provider configuration file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        True if valid, False otherwise
    """
    print(f"Validating: {config_path}")
    print("=" * 60)
    
    if not config_path.exists():
        print(f"❌ Error: File not found: {config_path}")
        return False
    
    # Load configuration
    loader = DNSLoader(config_dir=config_path.parent)
    providers = loader.load_providers()
    
    # Check for errors
    errors = loader.get_errors()
    
    if errors:
        print("❌ Validation FAILED")
        print("\nErrors found:")
        for error in errors:
            print(f"\n{error}")
        return False
    
    # Success
    print("✅ Validation PASSED")
    print(f"\nLoaded {len(providers)} DNS providers:")
    print("-" * 60)
    
    for provider in providers:
        print(f"\n📍 {provider.name}")
        print(f"   IPv4: {', '.join(provider.ipv4)}")
        
        if provider.ipv6:
            print(f"   IPv6: {', '.join(provider.ipv6)}")
        
        if provider.doh_template:
            print(f"   🔒 DoH: {provider.doh_template}")
        
        if provider.tags:
            print(f"   🏷️  Tags: {', '.join(provider.tags)}")
        
        print(f"   Policy:")
        print(f"     - Encrypted Only: {provider.policy.encrypted_only}")
        print(f"     - Auto Upgrade: {provider.policy.autoupgrade}")
        print(f"     - UDP Fallback: {provider.policy.allow_udp_fallback}")
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  Total Providers: {len(providers)}")
    
    doh_providers = loader.get_doh_providers()
    print(f"  DoH Providers: {len(doh_providers)}")
    
    # Tag statistics
    all_tags = set()
    for provider in providers:
        all_tags.update(provider.tags)
    
    print(f"  Unique Tags: {len(all_tags)}")
    if all_tags:
        print(f"  Tags: {', '.join(sorted(all_tags))}")
    
    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Validate DNS provider configuration files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/validate_config.py dns_providers.yaml
  python scripts/validate_config.py /path/to/custom_config.yaml
        """
    )
    
    parser.add_argument(
        'config_file',
        nargs='?',
        default='dns_providers.yaml',
        help='Path to configuration file (default: dns_providers.yaml)'
    )
    
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Quiet mode - only show errors'
    )
    
    args = parser.parse_args()
    
    config_path = Path(args.config_file)
    
    try:
        valid = validate_config(config_path)
        sys.exit(0 if valid else 1)
    except KeyboardInterrupt:
        print("\n\nValidation cancelled.")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
