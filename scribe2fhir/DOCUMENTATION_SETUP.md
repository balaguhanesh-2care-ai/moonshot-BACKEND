# Scribe2FHIR Documentation Deployment Setup

This README documents the complete setup for deploying Scribe2FHIR documentation using Astro Starlight and GitHub Pages.

## What Was Implemented

### 1. GitHub Actions Workflow
- **File**: `.github/workflows/deploy-docs.yml`
- **Purpose**: Automatically builds and deploys documentation to GitHub Pages
- **Triggers**: Push/PR to `main` and `feature/move_to_starlight_docs` branches
- **Process**:
  1. Sets up Python and installs dependencies with `uv`
  2. Generates registry documentation with custom script
  3. Builds Astro documentation site
  4. Deploys to GitHub Pages

### 2. Astro Starlight Documentation Site
- **Location**: `docs/` directory
- **Framework**: Astro with Starlight theme for documentation
- **Features**:
  - Responsive design with sidebar navigation
  - Search functionality
  - Mobile-friendly interface
  - Automatic table of contents
  - Code syntax highlighting

### 3. Documentation Structure
Organized into logical sections with automatic navigation:

```
docs/src/content/docs/
├── index.mdx                    # Homepage with overview
├── introduction.md              # Project introduction
├── installation.md              # Setup instructions
├── fhir-specification/          # FHIR standards documentation
│   ├── ELEMENT_REQUIREMENTS.md
│   ├── IMPLEMENTATION_GUIDE.md
│   ├── README.md
│   └── SDK_SPECIFICATION.md
├── python-sdk/                  # Complete Python SDK docs
│   ├── README.md
│   ├── PATIENT.md
│   ├── ENCOUNTER.md
│   ├── MEDICAL_CONDITION.md
│   ├── VITAL_SIGNS.md
│   ├── MEDICATION_PRESCRIPTION.md
│   ├── [... all other SDK docs]
│   ├── api-registry.md          # Auto-generated API reference
│   └── code-examples.md         # Auto-generated code examples
├── resources/                   # FHIR resource documentation
│   ├── index.md                 # Resource types overview
│   └── patient.md               # Detailed Patient resource guide
└── examples/                    # Practical examples
    └── example-usage.md         # Complete usage examples
```

### 4. Navigation System
The sidebar navigation is automatically generated based on:
- **Manual sections**: Getting Started (Introduction, Installation)
- **Auto-generated sections**: All other directories use `autogenerate: { directory: "folder-name" }`
- **Frontmatter**: Each markdown file has title and description metadata

### 5. Documentation Generation Scripts
- **`scripts/generate_registry_docs.py`**: Creates API registry and code examples
- **`scripts/add_frontmatter.py`**: Adds YAML frontmatter to existing markdown files
- **`scripts/fix_frontmatter.py`**: Fixes YAML syntax issues

### 6. Configuration
- **Site URL**: Configured for GitHub Pages deployment
- **Base path**: Set to `/scribe2fhir` for repository-based deployment
- **Theme**: Starlight with custom branding and GitHub integration

## How the Navigation Works

### Automatic Sidebar Generation
The `astro.config.mjs` defines the sidebar structure:

```javascript
sidebar: [
  {
    label: 'Getting Started',
    items: [
      { label: 'Introduction', slug: 'introduction' },
      { label: 'Installation', slug: 'installation' },
    ],
  },
  {
    label: 'FHIR Specification',
    autogenerate: { directory: 'fhir-specification' },
  },
  {
    label: 'Python SDK',
    autogenerate: { directory: 'python-sdk' },
  },
  {
    label: 'Resource Types',
    autogenerate: { directory: 'resources' },
  },
  {
    label: 'Examples',
    autogenerate: { directory: 'examples' },
  },
],
```

### Markdown File Discovery
- Starlight automatically discovers all `.md` and `.mdx` files in content directories
- File names are converted to URLs (e.g., `PATIENT.md` → `/python-sdk/patient/`)
- Frontmatter `title` is used for navigation labels
- Files are sorted alphabetically within each section

### Search Integration
- Built-in search powered by Pagefind
- Indexes all content for fast client-side search
- Accessible via search box in header

## Deployment Process

### Local Development
```bash
cd docs
npm run dev
```

### Building for Production
```bash
# Generate registry documentation
python scripts/generate_registry_docs.py

# Build Astro site
cd docs
npm run build
```

### GitHub Pages Deployment
The workflow automatically:
1. Triggers on push to specified branches
2. Installs dependencies and generates docs
3. Builds the static site to `docs/dist/`
4. Uploads and deploys to GitHub Pages

## Key Features

### 1. Comprehensive Coverage
- **33 pages** of documentation generated
- All existing markdown files integrated
- New structured content for better UX

### 2. Developer-Friendly
- Code syntax highlighting
- Copy-to-clipboard functionality
- Responsive design for all devices

### 3. Maintainable
- Automatic content discovery
- Script-based doc generation
- Version-controlled configuration

### 4. SEO and Accessibility
- Semantic HTML structure
- Meta descriptions for all pages
- Mobile-responsive design
- Fast loading with static generation

## Customization Options

### Adding New Documentation
1. Create `.md` files in appropriate `src/content/docs/` subdirectory
2. Add YAML frontmatter with `title` and `description`
3. Content automatically appears in navigation

### Modifying Navigation
Edit `astro.config.mjs` to:
- Change section labels
- Reorder sections
- Add manual navigation items
- Modify auto-generation directories

### Styling and Branding
- Update `astro.config.mjs` for site title, social links
- Customize colors and fonts in theme configuration
- Add custom CSS in `src/styles/` directory

## Repository Configuration

### Required GitHub Settings
1. **Enable GitHub Pages** in repository settings
2. **Set source** to "GitHub Actions" (not branch)
3. **Configure environment protection** for `github-pages` environment (optional)

### Branch Protection
Consider protecting the deployment branches:
- `main`: Primary branch
- `feature/move_to_starlight_docs`: Feature branch for docs migration

## Troubleshooting

### Build Failures
- Check YAML frontmatter syntax in markdown files
- Ensure all referenced files exist
- Verify Node.js and Python dependency versions

### Navigation Issues
- Confirm markdown files have proper frontmatter
- Check directory names match `autogenerate` configuration
- Verify file naming conventions (lowercase, hyphens)

### Deployment Issues
- Check GitHub Actions logs for specific errors
- Verify repository permissions for Pages deployment
- Ensure `dist/` directory is generated correctly

## Benefits of This Setup

### For Users
- **Easy navigation** through comprehensive sidebar
- **Fast search** across all documentation
- **Mobile-friendly** interface for on-the-go access
- **Professional appearance** with Starlight design

### For Maintainers
- **Automatic deployment** on code changes
- **Easy content addition** with markdown files
- **Consistent formatting** across all pages
- **Version control** for all documentation changes

### For the Project
- **Professional presentation** of the Scribe2FHIR project
- **Better discoverability** of features and capabilities
- **Reduced support burden** with comprehensive docs
- **Easier onboarding** for new users and contributors

This documentation system provides a solid foundation for the Scribe2FHIR project's documentation needs while being maintainable and scalable for future growth.
