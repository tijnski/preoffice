# PreOffice Release Process

## Version Numbering

PreOffice uses semantic versioning: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes or major feature releases
- **MINOR**: New features, upstream sync
- **PATCH**: Bug fixes, security updates

Upstream LibreOffice version is tracked in `upstream/VERSION`.

## Release Checklist

### Pre-Release

- [ ] All CI checks pass on `preoffice/main`
- [ ] Upstream security patches applied
- [ ] Changelog updated
- [ ] Version bumped in build config
- [ ] SBOM generated
- [ ] License compliance verified

### Build Artifacts

For each release, produce:

| Platform | Artifacts |
|----------|-----------|
| Windows | `PreOffice-X.Y.Z-win64.msi`, `PreOffice-X.Y.Z-win64.exe` |
| macOS | `PreOffice-X.Y.Z-macos.dmg` |
| Linux | `PreOffice-X.Y.Z-linux-x86_64.AppImage`, `.deb`, `.rpm` |

Plus:
- `checksums.sha256`
- `checksums.sha512`
- `SBOM.json` (CycloneDX format)

### Build Commands

```bash
# Tag the release
git tag -s v1.0.0 -m "Release 1.0.0"
git push origin v1.0.0

# Build all platforms (in CI or locally)
./packaging/build-all.sh v1.0.0
```

### Post-Release

- [ ] Upload artifacts to GitHub Releases
- [ ] Update download page
- [ ] Announce on channels
- [ ] Update documentation site

## Upstream Sync Process

### Monthly Security Sync
1. Monitor LibreOffice security advisories
2. Cherry-pick security commits to `upstream/<version>`
3. Rebase `preoffice/main` onto updated upstream
4. Run full test suite
5. Create patch release if needed

### Major Version Sync
1. Create new branch `upstream/<new-version>`
2. Apply PreOffice patches cleanly
3. Resolve conflicts (document in `docs/REBASE-NOTES.md`)
4. Full QA cycle
5. Release as new MINOR version

## Signing

### macOS
- App must be signed with Apple Developer certificate
- Notarization required for Gatekeeper

### Windows
- MSI/EXE signed with code signing certificate
- Authenticode signature

### Linux
- GPG-signed packages
- Public key published at `presearch.com/keys/`

## Emergency Releases

For critical security issues:
1. Apply patch to affected branches
2. Skip non-essential QA
3. Release within 24-48 hours
4. Post-mortem after release
