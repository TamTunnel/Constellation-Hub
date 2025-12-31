# Open-Source Governance & Supply Chain

*How we manage contributions, dependencies, and security for the Constellation Hub project.*

---

## Purpose

This document describes how Constellation Hub is governed as an open-source project, including contribution processes, dependency management, and security practices.

It is intended for contributors, security reviewers, and organizations evaluating the project for adoption.

---

## Project Governance

### Maintainers

The project is maintained by a core team responsible for:
- Reviewing and merging pull requests
- Triaging issues and feature requests
- Releasing new versions
- Security response

Maintainers are listed in the [MAINTAINERS.md](../../MAINTAINERS.md) file (to be created as the community grows).

### Decision Making

| Decision Type | Process |
|---------------|---------|
| **Bug fixes** | Maintainer review and merge |
| **Minor features** | Discussion in issue, then PR review |
| **Major features** | Proposal in GitHub Discussions, community input, maintainer approval |
| **Architecture changes** | RFC (Request for Comments) document, extended review period |
| **Security issues** | Private disclosure, expedited fix, coordinated release |

---

## Contribution Model

### How to Contribute

1. **Fork the repository** on GitHub
2. **Create a feature branch** from `main`
3. **Make your changes** following code style guidelines
4. **Write tests** for new functionality
5. **Submit a pull request** with a clear description
6. **Respond to review feedback** from maintainers
7. **Merge** after approval

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for detailed guidelines.

### Code Review Requirements

All contributions must:
- Pass automated CI checks (linting, tests, build)
- Be reviewed by at least one maintainer
- Include appropriate documentation updates
- Not introduce known security vulnerabilities

### Contributor License

Contributors retain copyright to their contributions but grant the project a license to use and distribute the code under the Apache 2.0 license.

For significant contributions, we may request a Contributor License Agreement (CLA) to clarify intellectual property rights.

---

## Software Bill of Materials (SBOM)

### What is an SBOM?

A Software Bill of Materials is a comprehensive list of all components, libraries, and dependencies used in a software project. It enables:
- Rapid identification of vulnerable components
- Compliance with software supply chain requirements
- Transparency for security assessments

### SBOM Generation

Constellation Hub generates SBOMs for each release:

| Component | SBOM Format | Tool |
|-----------|-------------|------|
| Python services | CycloneDX, SPDX | `pip-audit`, `cyclonedx-py` |
| Frontend (npm) | CycloneDX, SPDX | `cyclonedx-npm` |
| Container images | CycloneDX | `syft` |

SBOMs are attached to GitHub releases and available for download.

### SBOM Location

- Release artifacts include `sbom.json` files
- Container images include SBOM labels
- CI/CD generates SBOMs on every build

---

## Dependency Management

### Dependency Selection Principles

When adding new dependencies, we consider:

1. **Necessity** — Is this dependency truly needed, or can we use existing tools?
2. **Maintenance** — Is the project actively maintained with recent commits?
3. **Security track record** — How quickly does the project address vulnerabilities?
4. **License compatibility** — Is the license compatible with Apache 2.0?
5. **Transitive dependencies** — How many additional dependencies does it bring?

### Version Pinning

- Production deployments use pinned versions (exact version numbers)
- Development may use version ranges for flexibility
- Lock files (`requirements.txt`, `package-lock.json`) are committed to version control

### Dependency Updates

| Priority | Cadence |
|----------|---------|
| **Security patches** | Within 48 hours of disclosure |
| **Patch versions** | Weekly review |
| **Minor versions** | Monthly review |
| **Major versions** | Quarterly review with testing |

Automated tools (Dependabot, Renovate) create PRs for updates, but human review is required before merge.

---

## Vulnerability Scanning

### Automated Scanning

The CI/CD pipeline includes vulnerability scanning at multiple stages:

| Stage | Tool | What It Scans |
|-------|------|---------------|
| **Code** | CodeQL, Semgrep | Source code for security anti-patterns |
| **Dependencies** | pip-audit, npm audit | Known vulnerabilities in libraries |
| **Containers** | Trivy, Grype | Container images for OS and library vulnerabilities |
| **Secrets** | gitleaks, trufflehog | Accidental credential commits |

### Scan Frequency

- On every pull request
- On every push to `main`
- Nightly scans of deployed images
- On-demand for security reviews

### Handling Findings

| Severity | Response |
|----------|----------|
| **Critical** | Block merge, fix immediately |
| **High** | Block merge, fix within 7 days |
| **Medium** | Track in issue, fix within 30 days |
| **Low** | Track in issue, fix in next release |

---

## Security Issue Handling

### Reporting Security Issues

If you discover a security vulnerability in Constellation Hub:

1. **Do NOT open a public GitHub issue**
2. **Email security@constellation-hub.dev** (or use GitHub Security Advisories)
3. **Include:**
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Any suggested fixes

### Response Process

| Step | Timeline |
|------|----------|
| **Acknowledge receipt** | Within 48 hours |
| **Initial assessment** | Within 5 business days |
| **Fix development** | Depends on severity |
| **Coordinate disclosure** | Agree on timeline with reporter |
| **Release patch** | Before or simultaneous with disclosure |
| **Publish advisory** | After patch is available |

### Security Advisories

Security issues are disclosed via:
- GitHub Security Advisories
- Project mailing list / announcements
- CVE registration (for significant vulnerabilities)

---

## License Compliance

### Project License

Constellation Hub is licensed under the **Apache License 2.0**, which:
- Permits commercial use, modification, and distribution
- Requires preservation of copyright and license notices
- Provides an express grant of patent rights
- Does not require derivative works to be open-sourced

### Dependency Licenses

We accept dependencies with the following licenses:
- Apache 2.0
- MIT
- BSD (2-clause, 3-clause)
- ISC
- MPL 2.0 (with file-level copyleft only)

We avoid:
- GPL (incompatible with Apache 2.0 for combined works)
- AGPL (network copyleft concerns)
- Proprietary / unlicensed

License compliance is checked automatically in CI.

---

## Release Process

### Versioning

We follow Semantic Versioning (SemVer):
- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- MAJOR: Breaking changes
- MINOR: New features, backward compatible
- PATCH: Bug fixes, backward compatible

### Release Checklist

1. Update CHANGELOG.md
2. Update version numbers in source files
3. Run full test suite
4. Generate SBOMs
5. Create GitHub release with release notes
6. Build and push tagged container images
7. Announce release

### Long-Term Support

As the project matures, we may designate certain releases as LTS (Long-Term Support) with extended security updates. This will be documented in the release notes.

---

## Community Guidelines

### Code of Conduct

All contributors are expected to follow our Code of Conduct, which promotes:
- Respectful, inclusive communication
- Constructive feedback
- Collaboration and mentorship
- Zero tolerance for harassment

See [CODE_OF_CONDUCT.md](../../CODE_OF_CONDUCT.md) (to be created).

### Getting Help

- **GitHub Issues:** Bug reports and feature requests
- **GitHub Discussions:** Questions, ideas, community conversation
- **Documentation:** Start with the README and /docs folder

---

## Summary

| Governance Area | Approach |
|-----------------|----------|
| **Contributions** | Fork + PR model with maintainer review |
| **Dependencies** | Careful selection, pinned versions, automated scanning |
| **SBOM** | Generated for every release for transparency |
| **Vulnerabilities** | Automated scanning + responsible disclosure process |
| **Licensing** | Apache 2.0, permissive dependencies only |
| **Community** | Code of Conduct, open discussions |

Constellation Hub is committed to building secure, transparent, and community-driven software for the satellite operations industry.
