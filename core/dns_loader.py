"""DNS provider loader with YAML/JSON support and backward compatibility."""

import os
import yaml
import json
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
from pydantic import ValidationError

from models.dns_provider import DNSProvider, DNSProviderList

logger = logging.getLogger(__name__)


class DNSLoader:
    """Loads and validates DNS providers from YAML/JSON files."""
    
    DEFAULT_YAML_FILE = "dns_providers.yaml"
    DEFAULT_JSON_FILE = "dns_providers.json"
    LEGACY_TXT_FILE = "dns_list.txt"
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize DNS loader.
        
        Args:
            config_dir: Directory containing configuration files. Defaults to current directory.
        """
        self.config_dir = Path(config_dir) if config_dir else Path.cwd()
        self.providers: List[DNSProvider] = []
        self.errors: List[str] = []
        
    def load_providers(self, prefer_yaml: bool = True) -> List[DNSProvider]:
        """
        Load DNS providers from available configuration files.
        
        Args:
            prefer_yaml: Prefer YAML over JSON if both exist
            
        Returns:
            List of validated DNS providers
        """
        self.providers = []
        self.errors = []
        
        yaml_path = self.config_dir / self.DEFAULT_YAML_FILE
        json_path = self.config_dir / self.DEFAULT_JSON_FILE
        
        # Try loading YAML first
        if prefer_yaml and yaml_path.exists():
            logger.info(f"Loading DNS providers from {yaml_path}")
            return self._load_yaml(yaml_path)
        
        # Try JSON as fallback
        if json_path.exists():
            logger.info(f"Loading DNS providers from {json_path}")
            return self._load_json(json_path)
        
        # Try YAML even if not preferred
        if yaml_path.exists():
            logger.info(f"Loading DNS providers from {yaml_path}")
            return self._load_yaml(yaml_path)
        
        # No structured file found
        logger.warning("No dns_providers.yaml or dns_providers.json found")
        self.errors.append(
            f"No configuration file found. Please create '{self.DEFAULT_YAML_FILE}' "
            "or use the migration tool if you have a legacy dns_list.txt file."
        )
        return []
    
    def _load_yaml(self, file_path: Path) -> List[DNSProvider]:
        """Load and validate providers from YAML file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not data:
                self.errors.append(f"Empty or invalid YAML file: {file_path}")
                return []
            
            return self._validate_and_load(data, file_path)
            
        except yaml.YAMLError as e:
            error_msg = f"YAML syntax error in {file_path}: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return []
        except FileNotFoundError:
            error_msg = f"File not found: {file_path}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return []
        except Exception as e:
            error_msg = f"Unexpected error loading {file_path}: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return []
    
    def _load_json(self, file_path: Path) -> List[DNSProvider]:
        """Load and validate providers from JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return self._validate_and_load(data, file_path)
            
        except json.JSONDecodeError as e:
            error_msg = f"JSON syntax error in {file_path}: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return []
        except FileNotFoundError:
            error_msg = f"File not found: {file_path}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return []
        except Exception as e:
            error_msg = f"Unexpected error loading {file_path}: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return []
    
    def _validate_and_load(self, data: Dict[str, Any], file_path: Path) -> List[DNSProvider]:
        """Validate data against schema and load providers."""
        try:
            provider_list = DNSProviderList(**data)
            self.providers = provider_list.providers
            logger.info(f"Successfully loaded {len(self.providers)} DNS providers from {file_path}")
            return self.providers
            
        except ValidationError as e:
            error_msg = self._format_validation_error(e, file_path)
            logger.error(error_msg)
            self.errors.append(error_msg)
            return []
    
    def _format_validation_error(self, error: ValidationError, file_path: Path) -> str:
        """Format Pydantic validation errors in a user-friendly way."""
        error_lines = [f"Validation errors in {file_path}:"]
        
        for err in error.errors():
            location = " -> ".join(str(loc) for loc in err['loc'])
            message = err['msg']
            error_lines.append(f"  • {location}: {message}")
        
        return "\n".join(error_lines)
    
    def has_legacy_file(self) -> bool:
        """Check if legacy dns_list.txt exists."""
        return (self.config_dir / self.LEGACY_TXT_FILE).exists()
    
    def has_yaml_file(self) -> bool:
        """Check if dns_providers.yaml exists."""
        return (self.config_dir / self.DEFAULT_YAML_FILE).exists()
    
    def get_errors(self) -> List[str]:
        """Get list of loading errors."""
        return self.errors
    
    def get_providers_by_tag(self, tag: str) -> List[DNSProvider]:
        """Get providers filtered by tag."""
        return [p for p in self.providers if tag in p.tags]
    
    def get_provider_by_name(self, name: str) -> Optional[DNSProvider]:
        """Get provider by exact name match."""
        for provider in self.providers:
            if provider.name == name:
                return provider
        return None
    
    def get_doh_providers(self) -> List[DNSProvider]:
        """Get only providers that support DoH."""
        return [p for p in self.providers if p.doh_template is not None]
    
    def export_to_yaml(self, output_path: Path, providers: Optional[List[DNSProvider]] = None) -> bool:
        """
        Export providers to YAML file.
        
        Args:
            output_path: Path to output YAML file
            providers: Providers to export. Uses loaded providers if None.
            
        Returns:
            True if successful, False otherwise
        """
        if providers is None:
            providers = self.providers
        
        if not providers:
            logger.warning("No providers to export")
            return False
        
        try:
            provider_list = DNSProviderList(version=1, providers=providers)
            data = provider_list.model_dump(mode='python', exclude_none=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            
            logger.info(f"Successfully exported {len(providers)} providers to {output_path}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to export providers to {output_path}: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return False
