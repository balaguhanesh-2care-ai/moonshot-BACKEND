---
title: Installation
description: Learn how to install and set up the Scribe2FHIR Python SDK in your development environment.
---

# Installation Guide

This guide will help you install and configure Scribe2FHIR in your development environment.

## Prerequisites

Before installing Scribe2FHIR, ensure you have the following prerequisites:

- **Python**: Version 3.8 or higher
- **pip**: Python package installer
- **Virtual Environment**: Recommended for isolation (venv, conda, or similar)

## Installation Methods

### Using pip (Recommended)

Install Scribe2FHIR directly from PyPI:

```bash
pip install scribe2fhir
```

### From Source

For development or to get the latest features:

```bash
# Clone the repository
git clone https://github.com/MedScribeAlliance/scribe2fhir.git
cd scribe2fhir

# Install in development mode
pip install -e .
```

### Using Poetry

If you prefer Poetry for dependency management:

```bash
poetry add scribe2fhir
```

## Virtual Environment Setup

We strongly recommend using a virtual environment to avoid dependency conflicts:

### Using venv

```bash
# Create virtual environment
python -m venv scribe2fhir-env

# Activate virtual environment
# On macOS/Linux:
source scribe2fhir-env/bin/activate
# On Windows:
scribe2fhir-env\Scripts\activate

# Install Scribe2FHIR
pip install scribe2fhir
```

### Using conda

```bash
# Create conda environment
conda create -n scribe2fhir python=3.10

# Activate environment
conda activate scribe2fhir

# Install Scribe2FHIR
pip install scribe2fhir
```

## Dependencies

Scribe2FHIR automatically installs the following key dependencies:

- **fhir.resources**: FHIR resource models and validation
- **pydantic**: Data validation and parsing
- **python-dateutil**: Date parsing utilities
- **typing-extensions**: Enhanced type hints

For a complete list, see the `requirements.txt` file in the repository.

## Verification

Verify your installation by importing Scribe2FHIR in Python:

```python
import scribe2fhir
from scribe2fhir.core import DocumentBuilder

# Check version
print(f"Scribe2FHIR version: {scribe2fhir.__version__}")

# Create a simple document builder to test installation
builder = DocumentBuilder()
print("Installation successful!")
```

## Development Setup

For contributors or advanced users who want to modify the source code:

### Clone and Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/MedScribeAlliance/scribe2fhir.git
cd scribe2fhir

# Create virtual environment
python -m venv dev-env
source dev-env/bin/activate  # On Windows: dev-env\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests to verify setup
python -m pytest tests/
```

### Development Dependencies

Additional packages for development:

- **pytest**: Testing framework
- **black**: Code formatting
- **isort**: Import sorting
- **mypy**: Type checking
- **pre-commit**: Git hooks for code quality

## Configuration

Scribe2FHIR works out of the box with default settings, but you can customize behavior through configuration files or environment variables.

### Environment Variables

Set these optional environment variables:

```bash
# FHIR server endpoint (if using external FHIR server)
export FHIR_SERVER_URL="https://your-fhir-server.com"

# Logging level
export SCRIBE2FHIR_LOG_LEVEL="INFO"
```

### Configuration File

Create a `config.yaml` file for custom settings:

```yaml
fhir:
  version: "R5"
  base_url: "https://your-fhir-server.com"

logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

processing:
  batch_size: 100
  timeout: 30
```

## Troubleshooting

### Common Installation Issues

#### Python Version Compatibility

Ensure you're using Python 3.8+:

```bash
python --version
```

#### Dependency Conflicts

If you encounter dependency conflicts:

```bash
# Create a fresh virtual environment
python -m venv fresh-env
source fresh-env/bin/activate
pip install --upgrade pip
pip install scribe2fhir
```

#### Network Issues

If installation fails due to network issues:

```bash
# Try with increased timeout
pip install --timeout 60 scribe2fhir

# Or use a different index
pip install -i https://pypi.org/simple/ scribe2fhir
```

### Getting Help

If you encounter issues:

1. Check the [troubleshooting section](python-sdk/troubleshooting) in the documentation
2. Search existing [GitHub issues](https://github.com/MedScribeAlliance/scribe2fhir/issues)
3. Create a new issue with detailed error information

## Next Steps

Now that you have Scribe2FHIR installed, you can:

1. **[Explore the Python SDK](python-sdk/readme)** - Learn core concepts and API
2. **[Check out examples](examples/example-usage)** - See practical implementations
3. **[Understand FHIR specification](fhir-specification/readme)** - Learn about FHIR standards

Ready to build your first FHIR resource? Head to the [Python SDK documentation](python-sdk/readme) to get started!
