# PreOffice - Claude Code Agent Guidelines

You are working on **PreOffice**, a full LibreOffice fork branded for Presearch and the Pre-suite ecosystem.

## Non-Negotiables

### Licensing & Attribution
- **Do NOT copy LibreOffice trademarks** into product branding (except required attribution)
- Any modifications to **MPL-covered files remain MPL**
- **Keep upstream license notices intact** in all files
- Add `Based on LibreOffice technology` attribution in About dialog
- Maintain clear separation: core fork code vs Presearch assets vs third-party

### Code Organization
- **Prefer adding new code in isolated modules** where possible
- Keep Presearch integrations in `presearch/integrations/*` to minimize rebase conflicts
- Core LO modifications should be minimal and well-documented
- Use feature flags for Presearch-specific features when touching core

### Brand & Style
- All brand styling must use **Presearch tokens** from `presearch/brand/tokens.json`
- Primary color: `#2D8EFF` (Presearch Blue)
- Background tint: `#EAF3FF`
- Background soft: `#FAFBFC`
- Text colors: `#000000` (primary), `#494949` (secondary)
- Use only Presearch-owned assets from `presearch/brand/assets/`

### Build & Release
- Maintain **rebase strategy** from day 1 - security updates are not optional
- Produce **deterministic builds** (same inputs → same outputs)
- Generate SBOM (CycloneDX or SPDX) for every release
- All build scripts and CI must be open source

## Repository Structure

```
preoffice/
├── upstream/                 # Submodule or mirror notes for tracking LO releases
├── core/                     # LibreOffice fork source
├── presearch/
│   ├── brand/               # Tokens, logos, splash, startcenter
│   ├── ui/                  # Icon theme, notebookbar, defaults
│   └── integrations/        # PreGPT, Presearch Search, PreStorage
├── packaging/               # Windows, macOS, Linux installers
├── compliance/              # LICENSES, NOTICE, TRADEMARK, SBOM
├── docs/                    # BUILDING, RELEASE, CONTRIBUTING, SECURITY
└── .github/workflows/       # CI/CD pipelines
```

## Integration Requirements

### Search with Presearch
- Selection → open browser to `presearch.com/search?q=...`
- Must support configurable base URL (for gov/enterprise SKUs)

### Ask PreGPT
- Must support: local endpoint, sovereign cloud, air-gapped mode
- Configurable endpoint URL in settings

### Export to PreStorage
- Export to PDF/ODF with optional upload hook
- Must work offline when integration disabled

### Privacy Check
- Report: tracked changes, comments, author metadata, embedded links, hidden text
- Optional "Clean document" feature

## Defaults to Set

- ODF as default save format
- Privacy-friendly defaults (disable telemetry if present)
- Notebookbar as default UI mode
- Presearch-branded templates in New Document flow

## When Unsure

1. Check existing LibreOffice source or install for conventions
2. Mirror existing patterns exactly
3. Document your approach in the relevant README
4. Prefer conservative changes that are easier to rebase
