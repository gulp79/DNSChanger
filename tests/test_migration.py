"""Tests for legacy migration functionality."""

import pytest
import tempfile
from pathlib import Path

from core.migration import (
    parse_legacy_dns_file,
    convert_legacy_to_providers,
    migrate_txt_to_yaml,
    can_migrate
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_legacy_file(temp_dir):
    """Create a sample legacy dns_list.txt file."""
    txt_path = temp_dir / 'dns_list.txt'
    content = """# DNS Server List
# Format: Name,PrimaryDNS,SecondaryDNS
Google,8.8.8.8,8.8.4.4
Cloudflare,1.1.1.1,1.0.0.1
Quad9,9.9.9.9,149.112.112.112
OpenDNS,208.67.222.222,208.67.220.220
"""
    txt_path.write_text(content)
    return txt_path


def test_parse_legacy_file(sample_legacy_file):
    """Test parsing legacy DNS file."""
    entries = parse_legacy_dns_file(sample_legacy_file)
    
    assert len(entries) == 4
    assert entries[0] == ('Google', ['8.8.8.8', '8.8.4.4'])
    assert entries[1] == ('Cloudflare', ['1.1.1.1', '1.0.0.1'])


def test_parse_legacy_with_comments(temp_dir):
    """Test parsing file with comments and empty lines."""
    txt_path = temp_dir / 'dns_list.txt'
    content = """# Header comment

Google,8.8.8.8,8.8.4.4
# Another comment

Cloudflare,1.1.1.1
"""
    txt_path.write_text(content)
    
    entries = parse_legacy_dns_file(txt_path)
    assert len(entries) == 2


def test_parse_legacy_invalid_lines(temp_dir):
    """Test parsing file with invalid lines."""
    txt_path = temp_dir / 'dns_list.txt'
    content = """Google,8.8.8.8,8.8.4.4
InvalidLine
NoComma
,OnlyComma,
ValidProvider,1.1.1.1
"""
    txt_path.write_text(content)
    
    entries = parse_legacy_dns_file(txt_path)
    assert len(entries) == 3  # Google, ,OnlyComma,, ValidProvider are valid lines parsed


def test_convert_legacy_to_providers(sample_legacy_file):
    """Test converting legacy entries to providers."""
    entries = parse_legacy_dns_file(sample_legacy_file)
    providers = convert_legacy_to_providers(entries)
    
    assert len(providers) == 4
    
    # Check Google provider
    google = next(p for p in providers if 'Google' in p.name)
    assert google.ipv4 == ['8.8.8.8', '8.8.4.4']
    assert google.doh_template is not None  # Should be detected
    assert 'migrated' in google.tags or 'public' in google.tags


def test_migrate_txt_to_yaml(temp_dir, sample_legacy_file):
    """Test full migration process."""
    yaml_path = temp_dir / 'dns_providers.yaml'
    
    success, message = migrate_txt_to_yaml(
        sample_legacy_file,
        yaml_path,
        backup=False
    )
    
    assert success
    assert yaml_path.exists()
    assert 'migrated' in message.lower() or 'success' in message.lower()


def test_migrate_nonexistent_file(temp_dir):
    """Test migration with nonexistent source file."""
    txt_path = temp_dir / 'nonexistent.txt'
    yaml_path = temp_dir / 'output.yaml'
    
    success, message = migrate_txt_to_yaml(txt_path, yaml_path)
    
    assert not success
    assert 'not found' in message.lower()


def test_can_migrate_valid(temp_dir, sample_legacy_file):
    """Test can_migrate with valid conditions."""
    yaml_path = temp_dir / 'dns_providers.yaml'
    
    can_mig, msg = can_migrate(sample_legacy_file, yaml_path)
    
    assert can_mig
    assert 'entries' in msg.lower()


def test_can_migrate_yaml_exists(temp_dir, sample_legacy_file):
    """Test can_migrate when YAML already exists."""
    yaml_path = temp_dir / 'dns_providers.yaml'
    yaml_path.write_text("version: 1\nproviders: []")
    
    can_mig, msg = can_migrate(sample_legacy_file, yaml_path)
    
    assert not can_mig
    assert 'already exists' in msg.lower()


def test_can_migrate_no_txt(temp_dir):
    """Test can_migrate when TXT doesn't exist."""
    txt_path = temp_dir / 'nonexistent.txt'
    yaml_path = temp_dir / 'output.yaml'
    
    can_mig, msg = can_migrate(txt_path, yaml_path)
    
    assert not can_mig
    assert 'no legacy dns_list.txt found' in msg.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
