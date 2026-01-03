# Security Guide

Constellation Hub adheres to security-first principles for data protection and access control.

## Role-Based Access Control (RBAC)

The system enforces three distinct roles to manage operational access.

| Role         | Permissions                                                                                                          | Use Case                                     |
| ------------ | -------------------------------------------------------------------------------------------------------------------- | -------------------------------------------- |
| **Viewer**   | **Read-Only**: Can view dashboards, maps, satellite positions, and schedules. Cannot modify data or execute actions. | Stakeholders, analysts, management.          |
| **Operator** | **Execute**: Can manage TLEs, generate schedules, request AI optimizations, and apply actions.                       | Mission operators, flight dynamics officers. |
| **Admin**    | **Full Access**: Can manage users, configure ground stations, and perform system-level operations.                   | System administrators, senior mission leads. |

### Demo Accounts

For evaluation purposes, the following accounts are pre-configured in Demo Mode:

- Viewer: `demo_viewer` / `viewer123`
- Operator: `demo_ops` / `operator123`
- Admin: `demo_admin` / `admin123`

> [!WARNING]
> These accounts are for development only. Do not use them in production deployments.

## Data Protection

### Encryption

- **In Transit**: All API communication is designed to run over TLS (HTTPS).
- **At Rest**: Database volumes can be encrypted using standard PostgreSQL encryption methods.
- **Passwords**: User passwords are hashed using **bcrypt** before storage.

### AI Safety

AI agents in Constellation Hub are **assistive only**.

- Agents can propose optimizations or analyze logs.
- Agents **cannot** autonomously execute commands or change system state.
- A human operator (role `operator` or `admin`) must explicitly approve any AI-suggested action.

## Network Security

When deploying to production:

1. **API Gateway**: Use a reverse proxy (Nginx, Traefik) to terminate TLS.
2. **Firewall**: Restrict database port access (5432) to internal services only.
3. **secrets**: Use environment variables or a secrets manager for `JWT_SECRET_KEY` and database credentials.

## Compliance

Constellation Hub is designed for unclassified / commercial use. Deployment in classified or regulated environments (ITAR, HIPAA, etc.) requires additional hardening and compliance review.
