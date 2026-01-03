# Limitations & Scope (MVP)

Constellation Hub is an early-stage, production-ready MVP. Please be aware of the following limitations.

## 1. Multi-Tenancy

- **Current State**: Single-tenant only.
- **Limitation**: The system does not strictly isolate data between different "organizations" or "tenants". All users can potentially see all data if they have the appropriate role.
- **Guidance**: Deploy separate instances for separate customers or missions.

## 2. AI Safety

- **Current State**: Human-in-the-loop.
- **Limitation**: AI agents cannot autonomous execute actions.
- **Guidance**: Use AI for analysis and optimization recommendations, but rely on human operators for execution.

## 3. High-Security Environments

- **Current State**: Not certified.
- **Limitation**: Not vetted for classified/Top Secret data handling.
- **Guidance**: Requires a security audit and hardening phase before deployment in classified networks. No standard FIPS-140-2 crypto implementation is guaranteed beyond standard library usage.

## 4. Simulation

- **Current State**: Live operations focus.
- **Limitation**: No high-fidelity physics simulator for constellation design or "what-if" scenarios.
- **Guidance**: Use dedicated mission planning tools (STK, GMAT) for design, and Constellation Hub for operations.

## 5. Scale

- **Current State**: Optimized for 10-500 satellites.
- **Limitation**: UI performance and scheduling optimization may degrade with mega-constellations (1000+ sats).
- **Guidance**: For large constellations, ensure sufficient backend resources and consider partitioning the fleet.
