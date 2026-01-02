# Roles & Permissions

Constellation Hub implements role-based access control (RBAC) with three predefined roles.

---

## Roles Overview

| Role | Description | Typical Users |
|------|-------------|---------------|
| **Viewer** | Read-only access to system data | Analysts, management, external stakeholders |
| **Operator** | Can manage operations and execute actions | Satellite operators, mission control |
| **Admin** | Full system access including user management | System administrators, senior operators |

---

## Permission Matrix

### Dashboard & Visualization

| Action | Viewer | Operator | Admin |
|--------|:------:|:--------:|:-----:|
| View 3D globe | ✅ | ✅ | ✅ |
| View constellation data | ✅ | ✅ | ✅ |
| View satellite positions | ✅ | ✅ | ✅ |
| View ground stations | ✅ | ✅ | ✅ |

### Satellite Operations

| Action | Viewer | Operator | Admin |
|--------|:------:|:--------:|:-----:|
| View satellite list | ✅ | ✅ | ✅ |
| View satellite details | ✅ | ✅ | ✅ |
| View TLE data | ✅ | ✅ | ✅ |
| Refresh TLE data | ❌ | ✅ | ✅ |
| Modify satellite configuration | ❌ | ❌ | ✅ |

### Pass Scheduling

| Action | Viewer | Operator | Admin |
|--------|:------:|:--------:|:-----:|
| View pass predictions | ✅ | ✅ | ✅ |
| View schedules | ✅ | ✅ | ✅ |
| Generate schedules | ❌ | ✅ | ✅ |
| Apply/activate schedules | ❌ | ✅ | ✅ |
| Delete schedules | ❌ | ✅ | ✅ |

### AI-Assisted Operations

| Action | Viewer | Operator | Admin |
|--------|:------:|:--------:|:-----:|
| View AI recommendations | ✅ | ✅ | ✅ |
| Request AI analysis | ✅ | ✅ | ✅ |
| Request AI optimization | ❌ | ✅ | ✅ |
| **Apply AI-generated actions** | ❌ | ✅ | ✅ |

> [!IMPORTANT]
> AI agents are **assistive only**. They propose actions, but human operators (with `operator` role or higher) must review and approve before execution.

### Ground Network

| Action | Viewer | Operator | Admin |
|--------|:------:|:--------:|:-----:|
| View ground stations | ✅ | ✅ | ✅ |
| View antenna status | ✅ | ✅ | ✅ |
| Modify ground station config | ❌ | ❌ | ✅ |
| Add/remove ground stations | ❌ | ❌ | ✅ |

### User Management

| Action | Viewer | Operator | Admin |
|--------|:------:|:--------:|:-----:|
| View own profile | ✅ | ✅ | ✅ |
| Change own password | ✅ | ✅ | ✅ |
| View user list | ❌ | ❌ | ✅ |
| Create users | ❌ | ❌ | ✅ |
| Modify user roles | ❌ | ❌ | ✅ |
| Delete users | ❌ | ❌ | ✅ |

---

## API Endpoints by Role

### Public (No Auth Required)

- `GET /healthz` - Liveness probe
- `GET /readyz` - Readiness probe
- `POST /auth/login` - User login

### Viewer+ (Requires Authentication)

- `GET /constellations` - List constellations
- `GET /satellites` - List satellites
- `GET /satellites/{id}/position` - Get satellite position
- `GET /ground-stations` - List ground stations
- `GET /passes` - List passes
- `GET /schedule` - View schedules
- `GET /tle/status` - TLE ingestion status
- `GET /tle/satellites` - List TLE records
- `GET /ai/ops-copilot/analyze` - Request AI analysis

### Operator+ (Operator or Admin)

- `POST /tle/refresh` - Trigger TLE refresh
- `POST /schedule` - Create schedule
- `PUT /schedule/{id}` - Update schedule
- `DELETE /schedule/{id}` - Delete schedule
- `POST /ai/pass-scheduler/optimize` - Request AI optimization
- `POST /ai/ops-copilot/execute` - Execute AI-recommended action

### Admin Only

- `GET /auth/users` - List users
- `POST /auth/users` - Create user
- `PUT /auth/users/{id}` - Update user
- `DELETE /auth/users/{id}` - Delete user
- `POST /ground-stations` - Add ground station
- `PUT /ground-stations/{id}` - Update ground station
- `DELETE /ground-stations/{id}` - Remove ground station

---

## Demo Users

For local development and demonstrations, three demo users are available:

| Username | Password | Role | Email |
|----------|----------|------|-------|
| `demo_viewer` | `viewer123` | viewer | viewer@demo.constellation-hub.local |
| `demo_ops` | `operator123` | operator | ops@demo.constellation-hub.local |
| `demo_admin` | `admin123` | admin | admin@demo.constellation-hub.local |

> [!CAUTION]
> **Demo users are for local/demo use only.**
> - Never use demo credentials in production
> - Change all passwords before deploying to staging/production
> - Consider disabling demo user creation in production builds

---

## Enforcing RBAC

RBAC is enforced at two levels:

### Backend (FastAPI Dependencies)

```python
from common.auth import require_auth, require_role, Role

# Require authentication
@app.get("/satellites")
async def list_satellites(user: TokenData = Depends(require_auth)):
    # Any authenticated user can access
    pass

# Require specific role
@app.post("/tle/refresh")
async def refresh_tle(user: TokenData = Depends(require_role(Role.OPERATOR))):
    # Only operator or admin can access
    pass
```

### Frontend (Conditional Rendering)

```typescript
import { useAuth } from './hooks/useAuth';

function ScheduleControls() {
    const { user } = useAuth();
    
    // Only show controls to operators
    if (user.role !== 'operator' && user.role !== 'admin') {
        return null;
    }
    
    return <button onClick={applySchedule}>Apply Schedule</button>;
}
```

---

## Best Practices

1. **Principle of Least Privilege**: Assign the minimum role required for job function
2. **Audit Logging**: All privileged actions (operator+) should be logged for audit trails
3. **Periodic Review**: Regularly review user roles and remove unnecessary access
4. **Separation of Duties**: Consider separate roles for different operator teams
5. **MFA for Admin**: Require multi-factor authentication for admin role (future enhancement)

---

## Future Enhancements

- [ ] Custom roles and fine-grained permissions
- [ ] Multi-factor authentication (MFA) for admin
- [ ] OAuth/OIDC integration for enterprise SSO
- [ ] Audit log UI for tracking privileged actions
- [ ] API key scoping (per-service or per-action keys)
