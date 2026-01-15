You are working on "Presearch Office Edition", a no-fork skin + extension layer on top of LibreOffice.

Non-negotiables:
- Do NOT fork LibreOffice unless explicitly instructed.
- Prefer: icon theme + configuration defaults + extension (.oxt) + installer wrapper.
- Always follow LibreOffice's existing icon-theme structure and naming.
- Produce deterministic builds (same inputs -> same outputs).
- Keep licensing and attribution intact.

Brand:
- Primary #2D8EFF
- Text #000000 / #494949
- Backgrounds #EAF3FF / #FAFBFC / #FFFFFF
- Tone: Community, Transparency, Privacy

Deliverables:
1) Icon theme: presearch theme that can fallback to an existing LO theme for missing icons.
2) Branding assets: tokens + logo variants + splash + startcenter visuals.
3) Extension pack (.oxt): "Search with Presearch", "Ask PreGPT", "Export to PreStorage (stub ok)", "Privacy check".
4) Build/packaging automation + CI: produces artifacts for each module and a release bundle.

When unsure about LibreOffice file paths or formats:
- Inspect an existing LibreOffice install OR check LibreOffice source tree in-place.
- Mirror existing conventions exactly.
- Add a short note in README explaining the chosen approach.
