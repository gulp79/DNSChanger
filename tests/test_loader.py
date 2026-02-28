"""Tests for DNS loader functionality."""

import pytest
import tempfile
import yaml
from pathlib import Path

from core.dns_loader import DNSLoader
from models.dns_provider import DNSProvider, DNSPolicy


@pytest.fixture
def temp_config_dir():
    """Create a temporary directory for config files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_yaml_config():
    """Sample YAML configuration."""
    return {
        'version': 1,
        'providers': [
            {
                'name': 'Test DNS',
                'ipv4': ['8.8.8.8', '8.8.4.4'],
                'doh_template': 'https://dns.test.com/dns-query',
                'tags': ['test', 'public'],
                'policy': {
                    'encrypted_only': True,
                    'autoupgrade': True,
                    'allow_udp_fallback': False
                }
            }
        ]
    }


def test_load_valid_yaml(temp_config_dir, sample_yaml_config):
    """Test loading valid YAML configuration."""
    yaml_path = temp_config_dir / 'dns_providers.yaml'
    
    with open(yaml_path, 'w') as f:
        yaml.dump(sample_yaml_config, f)
    
    loader = DNSLoader(config_dir=temp_config_dir)
    providers = loader.load_providers()
    
    assert len(providers) == 1
    assert providers[0].name == 'Test DNS'
    assert len(providers[0].ipv4) == 2


def test_load_nonexistent_file(temp_config_dir):
    """Test loading when no config file exists."""
    loader = DNSLoader(config_dir=temp_config_dir)
    providers = loader.load_providers()
    
    assert len(providers) == 0
    assert len(loader.get_errors()) > 0


def test_load_invalid_yaml(temp_config_dir):
    """Test loading invalid YAML."""
    yaml_path = temp_config_dir / 'dns_providers.yaml'
    
    with open(yaml_path, 'w') as f:
        f.write("invalid: yaml: content:\n  - broken")
    
    loader = DNSLoader(config_dir=temp_config_dir)
    providers = loader.load_providers()
    
    assert len(providers) == 0
    assert len(loader.get_errors()) > 0


def test_get_providers_by_tag(temp_config_dir, sample_yaml_config):
    """Test filtering providers by tag."""
    yaml_path = temp_config_dir / 'dns_providers.yaml'
    
    with open(yaml_path, 'w') as f:
        yaml.dump(sample_yaml_config, f)
    
    loader = DNSLoader(config_dir=temp_config_dir)
    loader.load_providers()
    
    test_providers = loader.get_providers_by_tag('test')
    assert len(test_providers) == 1
    
    nonexistent = loader.get_providers_by_tag('nonexistent')
    assert len(nonexistent) == 0


def test_get_doh_providers(temp_config_dir, sample_yaml_config):
    """Test getting only DoH providers."""
    # Add provider without DoH
    sample_yaml_config['providers'].append({
        'name': 'No DoH',
        'ipv4': ['1.1.1.1'],
        'tags': ['test']
    })
    
    yaml_path = temp_config_dir / 'dns_providers.yaml'
    with open(yaml_path, 'w') as f:
        yaml.dump(sample_yaml_config, f)
    
    loader = DNSLoader(config_dir=temp_config_dir)
    loader.load_providers()
    
    doh_providers = loader.get_doh_providers()
    assert len(doh_providers) == 1
    assert doh_providers[0].name == 'Test DNS'


def test_export_to_yaml(temp_config_dir):
    """Test exporting providers to YAML."""
    providers = [
        DNSProvider(
            name='Export Test',
            ipv4=['1.1.1.1'],
            tags=['test']
        )
    ]
    
    loader = DNSLoader(config_dir=temp_config_dir)
    output_path = temp_config_dir / 'exported.yaml'
    
    success = loader.export_to_yaml(output_path, providers)
    assert success
    assert output_path.exists()
    
    # Verify exported content
    with open(output_path, 'r') as f:
        data = yaml.safe_load(f)
    
    assert data['version'] == 1
    assert len(data['providers']) == 1
    assert data['providers'][0]['name'] == 'Export Test'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
