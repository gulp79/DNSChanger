# DNSChanger Scripts

This directory contains helper scripts for managing DNSChanger configurations.

## Available Scripts

### validate_config.py

Validates DNS provider configuration files against the schema.

**Usage:**
```bash
# Validate default configuration
python scripts/validate_config.py

# Validate specific file
python scripts/validate_config.py path/to/custom_config.yaml

# Quiet mode (only show errors)
python scripts/validate_config.py -q dns_providers.yaml
```

**What it checks:**
- YAML syntax validity
- Schema compliance (Pydantic validation)
- IPv4/IPv6 address validity
- DoH template URL format
- Policy constraints
- Duplicate provider names
- Tag consistency

**Output:**
- ✅ Validation passed with provider summary
- ❌ Validation failed with detailed error messages
- Provider statistics (total, DoH-enabled, tags)

### create_config.py

Interactive tool to create custom DNS provider configurations.

**Usage:**
```bash
python scripts/create_config.py
```

**Features:**
- Interactive prompts for all provider fields
- Input validation
- Preview before saving
- Multiple provider creation
- Automatic schema validation

**Workflow:**
1. Enter provider details (name, IPs, DoH, tags, policy)
2. Preview the configuration
3. Confirm to add provider
4. Optionally add more providers
5. Save to YAML file

**Example Session:**
```
DNS Provider Configuration Generator
============================================================

Create New DNS Provider
============================================================
Provider name [My DNS]: Company DNS
IPv4 DNS servers:
  Enter IPv4 addresses (comma-separated): 10.0.0.1, 10.0.0.2
...
```

## Usage Examples

### Validate Before Deployment

Always validate configuration before deploying:

```bash
# Create custom config
python scripts/create_config.py

# Validate it
python scripts/validate_config.py my_custom_config.yaml

# If valid, rename or copy to dns_providers.yaml
copy my_custom_config.yaml dns_providers.yaml
```

### Check Existing Configuration

Verify your current configuration:

```bash
python scripts/validate_config.py dns_providers.yaml
```

### Enterprise Deployment

For enterprise environments:

```bash
# 1. Copy enterprise example
copy dns_providers_enterprise_example.yaml dns_providers.yaml

# 2. Edit dns_providers.yaml with your internal DNS servers

# 3. Validate
python scripts/validate_config.py

# 4. Deploy with DNSChanger executable
```

## Script Development

### Adding New Scripts

When adding new scripts:

1. Place in `scripts/` directory
2. Add shebang: `#!/usr/bin/env python3`
3. Add docstring with usage
4. Update this README
5. Make executable (optional): `chmod +x script.py`

### Importing DNSChanger Modules

Scripts can import from parent directory:

```python
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Now you can import
from core.dns_loader import DNSLoader
from models.dns_provider import DNSProvider
```

## Integration with Main Application

Scripts are standalone but can be installed as console commands:

```bash
# Install DNSChanger as package
pip install -e .

# Then use as commands
dnschanger-validate dns_providers.yaml
dnschanger-create
```

## Troubleshooting

**"Module not found" errors:**
- Ensure you're running from project root or scripts have correct path setup
- Check that all dependencies are installed: `pip install -r requirements.txt`

**"Permission denied":**
- On Windows, ensure you have write permissions to output directory
- On Unix systems, make script executable: `chmod +x script.py`

**Validation fails with confusing errors:**
- Check YAML syntax (indentation, colons, dashes)
- Verify IP addresses are in correct format
- Ensure DoH URLs start with https://
- Check for duplicate provider names

## Future Scripts

Planned scripts for future versions:

- `import_from_system.py`: Import current system DNS settings
- `benchmark_dns.py`: Test DNS server latency
- `export_to_json.py`: Convert YAML to JSON
- `merge_configs.py`: Merge multiple configuration files
- `deploy_enterprise.py`: Automated enterprise deployment

## Contributing

To contribute new scripts:

1. Follow the code style guidelines in CONTRIBUTING.md
2. Add comprehensive docstrings
3. Include usage examples
4. Add to this README
5. Submit pull request

---

For more information, see the main README.md and CONTRIBUTING.md
