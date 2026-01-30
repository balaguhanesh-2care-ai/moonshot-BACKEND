# scribe2fhir Repository

A multi-language SDK for creating FHIR documents from clinical data.

[![Documentation](https://img.shields.io/badge/Documentation-medscribealliance.github.io/scribe2fhir-blue?style=flat-square&logo=gitbook)](https://medscribealliance.github.io/scribe2fhir/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![FHIR R5](https://img.shields.io/badge/FHIR-R5-green?style=flat-square)](https://hl7.org/fhir/R5/)

## 📖 Documentation

**Complete documentation is available at: https://medscribealliance.github.io/scribe2fhir/**

The documentation site includes:
- **Getting Started Guide**: Installation and quick start
- **FHIR R5 Specification**: Complete FHIR standards documentation  
- **Python SDK Documentation**: Comprehensive API reference with examples
- **Resource Types Guide**: Detailed FHIR resource documentation
- **Code Examples**: Practical implementation examples

## Repository Structure

```
scribe2fhir/
├── docs/                           # Astro documentation site
│   ├── src/content/docs/          # Markdown documentation content
│   ├── astro.config.mjs           # Site configuration
│   └── dist/                      # Built documentation site
├── python/                         # Python SDK implementation
│   ├── scribe2fhir/               # Python package
│   │   ├── core/                  # Core SDK functionality
│   │   └── __init__.py
│   ├── docs/                      # Python-specific documentation
│   ├── tests/                     # Python test suite
│   ├── requirements.txt           # Python dependencies
│   ├── setup.py                   # Python package setup
│   └── example_usage.py           # Usage examples
└── [future_language]/             # Future language implementations
    ├── core/
    ├── docs/
    └── tests/
```

## Language Implementations

### Python SDK
The Python implementation is located in the `python/` directory and provides:

- **scribe2fhir.core**: Main SDK package
- **Comprehensive documentation**: Element-by-element usage guides
- **Full test suite**: 165+ test methods covering all functionality
- **Example code**: Real-world usage examples

#### Quick Start (Python)
```bash
cd python/
pip install -r requirements.txt
pip install -e .
```

```python
from scribe2fhir.core import FHIRDocumentBuilder
from scribe2fhir.core.types import create_codeable_concept

builder = FHIRDocumentBuilder()
builder.add_patient(name="John Doe", age=30, gender="male")
fhir_json = builder.convert_to_fhir()
```

### Future Language Implementations
Additional language SDKs will follow the same structure:
- `javascript/` - Node.js/TypeScript implementation
- `java/` - Java implementation  
- `csharp/` - C# implementation
- `go/` - Go implementation

## Documentation Structure

### 🌐 Web Documentation
**Primary documentation site**: https://medscribealliance.github.io/scribe2fhir/
- Built with Astro Starlight for optimal user experience
- Comprehensive navigation and search functionality  
- Mobile-responsive design
- Automatically deployed from this repository

### 📁 Source Documentation (`docs/`)
- **Astro Documentation Site**: Modern documentation framework
- **FHIR Specification**: Standards and compliance documentation
- **Resource Documentation**: FHIR resource guides and examples

### 🐍 Python-specific Documentation (`python/docs/`)
- Element-by-element usage guides
- API reference documentation  
- Integration examples
- Best practices

## Contributing
Each language implementation follows consistent patterns:
1. **Core library** in `{language}/core/`
2. **Comprehensive tests** in `{language}/tests/`
3. **Documentation** in `{language}/docs/`
4. **Package configuration** in language-appropriate files

## License
MIT License - see LICENSE file for details.

## Support

- **📖 Documentation**: Visit https://medscribealliance.github.io/scribe2fhir/ for comprehensive guides
- **🐛 Issues**: GitHub issues for bug reports and feature requests
- **💬 Community**: Discussion forums for usage questions
