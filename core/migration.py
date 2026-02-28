"""Migration utility to convert legacy dns_list.txt to YAML format."""

import logging
from pathlib import Path
from typing import List, Tuple

from models.dns_provider import DNSProvider, DNSPolicy

logger = logging.getLogger(__name__)


def parse_legacy_dns_file(file_path: Path) -> List[Tuple[str, List[str]]]:
    """
    Parse legacy dns_list.txt file.
    
    Format: Name,PrimaryDNS,SecondaryDNS (optional)
    Lines starting with # are ignored.
    
    Returns:
        List of tuples (name, [dns_addresses])
    """
    entries = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                parts = [p.strip() for p in line.split(',')]
                if len(parts) < 2:
                    logger.warning(f"Skipping invalid line {line_num}: {line}")
                    continue
                
                name = parts[0]
                dns_servers = parts[1:]
                
                # Filter out empty DNS entries
                dns_servers = [dns for dns in dns_servers if dns]
                
                if not dns_servers:
                    logger.warning(f"Skipping entry '{name}' with no DNS servers")
                    continue
                
                entries.append((name, dns_servers))
                
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return []
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return []
    
    return entries


def convert_legacy_to_providers(entries: List[Tuple[str, List[str]]]) -> List[DNSProvider]:
    """
    Convert legacy entries to DNSProvider objects.
    
    Args:
        entries: List of (name, dns_list) tuples
        
    Returns:
        List of DNSProvider objects
    """
    providers = []
    
    # Known DoH templates for common providers
    doh_templates = {
        'google': 'https://dns.google/dns-query',
        'cloudflare': 'https://cloudflare-dns.com/dns-query',
        'quad9': 'https://dns.quad9.net/dns-query',
        'opendns': 'https://doh.opendns.com/dns-query',
        'adguard': 'https://dns.adguard-dns.com/dns-query',
    }
    
    # Known tags for common providers
    provider_tags = {
        'google': ['public', 'fast', 'no-filter'],
        'cloudflare': ['public', 'privacy', 'fast', 'no-filter'],
        'quad9': ['public', 'security', 'malware-blocking', 'dnssec'],
        'opendns': ['public', 'security', 'no-filter'],
        'adguard': ['ad-block', 'tracker-block', 'phishing-block'],
    }
    
    for name, dns_servers in entries:
        # Try to detect provider type for DoH and tags
        name_lower = name.lower()
        doh_template = None
        tags = ['migrated']  # Default tag for migrated entries
        
        # Check for known providers
        for key, template in doh_templates.items():
            if key in name_lower:
                doh_template = template
                tags = provider_tags.get(key, ['public'])
                break
        
        # Create policy with DoH if template is available
        policy = DNSPolicy(
            encrypted_only=doh_template is not None,
            autoupgrade=True,
            allow_udp_fallback=False if doh_template else True
        )
        
        try:
            provider = DNSProvider(
                name=name,
                ipv4=dns_servers,
                doh_template=doh_template,
                tags=tags,
                policy=policy
            )
            providers.append(provider)
            logger.info(f"Converted provider: {name}")
            
        except Exception as e:
            logger.error(f"Failed to convert provider '{name}': {e}")
            continue
    
    return providers


def migrate_txt_to_yaml(
    txt_path: Path,
    yaml_path: Path,
    backup: bool = True
) -> Tuple[bool, str]:
    """
    Migrate dns_list.txt to dns_providers.yaml.
    
    Args:
        txt_path: Path to legacy dns_list.txt
        yaml_path: Path to output dns_providers.yaml
        backup: Create backup of existing yaml file
        
    Returns:
        Tuple of (success, message)
    """
    # Check if txt file exists
    if not txt_path.exists():
        return False, f"Legacy file not found: {txt_path}"
    
    # Backup existing yaml if requested
    if backup and yaml_path.exists():
        backup_path = yaml_path.with_suffix('.yaml.bak')
        try:
            import shutil
            shutil.copy2(yaml_path, backup_path)
            logger.info(f"Created backup: {backup_path}")
        except Exception as e:
            logger.warning(f"Could not create backup: {e}")
    
    # Parse legacy file
    entries = parse_legacy_dns_file(txt_path)
    if not entries:
        return False, f"No valid entries found in {txt_path}"
    
    # Convert to providers
    providers = convert_legacy_to_providers(entries)
    if not providers:
        return False, "Failed to convert any entries to valid providers"
    
    # Export to YAML
    from core.dns_loader import DNSLoader
    loader = DNSLoader(config_dir=yaml_path.parent)
    
    if loader.export_to_yaml(yaml_path, providers):
        return True, f"Successfully migrated {len(providers)} providers to {yaml_path}"
    else:
        errors = "\n".join(loader.get_errors())
        return False, f"Failed to export to YAML:\n{errors}"


def can_migrate(txt_path: Path, yaml_path: Path) -> Tuple[bool, str]:
    """
    Check if migration is possible and recommended.
    
    Returns:
        Tuple of (should_migrate, reason)
    """
    txt_exists = txt_path.exists()
    yaml_exists = yaml_path.exists()
    
    if not txt_exists:
        return False, "No legacy dns_list.txt found"
    
    if yaml_exists:
        return False, f"{yaml_path.name} already exists. Delete it first if you want to re-migrate."
    
    # Parse to check if there are valid entries
    entries = parse_legacy_dns_file(txt_path)
    if not entries:
        return False, "No valid entries found in dns_list.txt"
    
    return True, f"Found {len(entries)} entries ready for migration"
