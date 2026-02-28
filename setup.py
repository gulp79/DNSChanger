"""Setup configuration for DNSChanger."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip() 
        for line in requirements_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="dnschanger",
    version="2.0.0",
    author="gulp79",
    description="Advanced DNS management tool with DoH support for Windows",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gulp79/DNSChanger",
    packages=find_packages(exclude=["tests", "scripts"]),
    include_package_data=True,
    package_data={
        "": ["dns_providers.yaml", "*.yaml"],
    },
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "build": [
            "pyinstaller>=5.0.0",
            "nuitka>=1.5.0",
        ],
    },
    python_requires=">=3.12",
    entry_points={
        "console_scripts": [
            "dnschanger=dns_changer:main",
            "dnschanger-validate=scripts.validate_config:main",
            "dnschanger-create=scripts.create_config:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Networking",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: Microsoft :: Windows :: Windows 11",
    ],
    keywords="dns doh dns-over-https network windows administration",
    project_urls={
        "Bug Reports": "https://github.com/gulp79/DNSChanger/issues",
        "Source": "https://github.com/gulp79/DNSChanger",
        "Documentation": "https://github.com/gulp79/DNSChanger#readme",
    },
)
