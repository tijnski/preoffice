# Security Policy

## Reporting a Vulnerability

**Do NOT open a public issue for security vulnerabilities.**

### Contact
Email: security@presearch.com

### What to Include
- Description of the vulnerability
- Steps to reproduce
- Affected versions
- Potential impact
- Any suggested fixes

### Response Timeline
- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 1 week
- **Fix Timeline**: Depends on severity
  - Critical: 24-48 hours
  - High: 1 week
  - Medium: 2-4 weeks
  - Low: Next regular release

## Security Update Policy

PreOffice tracks upstream LibreOffice security releases:
- Security patches applied within 1 week of upstream release
- Critical vulnerabilities may trigger immediate patch release
- Security advisories published at [presearch.com/security](https://presearch.com/security)

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x     | Yes       |
| < 1.0   | No        |

## Security Features

### Privacy by Default
- No telemetry or usage tracking
- ODF as default format
- Privacy Check tool for document metadata

### Air-Gapped Mode
- All network features can be disabled
- Full offline functionality
- No external dependencies required

### Build Security
- SBOM generated for every release
- Reproducible builds
- Signed packages and installers

## Known Security Considerations

### Document Handling
- Macros are disabled by default
- External content requires user confirmation
- Embedded objects are sandboxed

### Network Features
- PreGPT/PreStorage require explicit configuration
- All connections use HTTPS
- No automatic external connections

## Acknowledgments

We thank the following researchers for responsible disclosure:
- (List will be maintained as disclosures occur)
