# Architecture Controls MCP Server

## Overview

An MCP (Model Context Protocol) server that enforces architectural rules and guidelines in AI-powered IDEs. Works with Cursor and Claude Code to ensure codebase consistency and best practices.

**Key Innovation**: Rules are derived directly from **ADR (Architecture Decision Record)** files checked into the repository. As ADRs are added or updated, rules automatically update.

**Two Components**:
1. **MCP Server** (npm package) - STDIO-based server for Cursor/Claude Code integration
2. **Web Dashboard** (Next.js on Vercel) - View ADRs, rules, and violations in a browser

---

## Goals

1. **ADR-driven rules** - Parse ADR files to extract enforceable architecture rules
2. **Living documentation** - ADRs serve as both documentation AND enforcement
3. **Expose rules** to AI assistants via MCP resources
4. **Validate code** against rules via MCP tools
5. **Guide developers** with actionable feedback linked back to ADRs
6. **Web dashboard** - Visual interface for browsing ADRs and tracking compliance

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACES                                 │
├─────────────────────────────────┬───────────────────────────────────────────┤
│     IDE (Cursor / Claude Code)  │         Web Dashboard (Next.js)           │
│              │                  │                   │                        │
│         MCP Client              │              Browser                       │
└──────────────┬──────────────────┴───────────────────┬───────────────────────┘
               │ STDIO                                │ HTTPS
               ▼                                      ▼
┌──────────────────────────────┐    ┌─────────────────────────────────────────┐
│      arch-mcp-server         │    │        arch-dashboard (Vercel)          │
│        (npm package)         │    │                                         │
├──────────────────────────────┤    ├─────────────────────────────────────────┤
│ ┌──────────┐ ┌─────────────┐ │    │  Pages:                                 │
│ │Resources │ │   Tools     │ │    │  • /              Dashboard home        │
│ │          │ │             │ │    │  • /adrs          ADR list              │
│ │arch://   │ │ validate    │ │    │  • /adrs/[id]     ADR detail            │
│ │adrs/*    │ │ list_rules  │ │    │  • /rules         Rules list            │
│ │rules/*   │ │ explain     │ │    │  • /rules/[id]    Rule detail           │
│ └────┬─────┘ └──────┬──────┘ │    │  • /validate      Validation UI         │
│      │              │        │    │  • /api/*         REST endpoints        │
│      ▼              ▼        │    └──────────────────────┬──────────────────┘
│ ┌────────────────────────┐   │                           │
│ │      Rule Engine       │   │                           │
│ └───────────┬────────────┘   │                           │
│             │                │                           │
│             ▼                │                           │
│ ┌────────────────────────┐   │    ┌─────────────────────────────────────────┐
│ │   ADR Parser + Rules   │◄──┼────│         Shared Core Library             │
│ │                        │   │    │         @arch-mcp/core                  │
│ │  docs/adr/*.md ──► Rules   │    │                                         │
│ └────────────────────────┘   │    │  • ADR Parser                           │
└──────────────────────────────┘    │  • Rule Extractor                       │
                                    │  • Rule Engine                          │
        ▲                           │  • Validation Logic                     │
        │                           └─────────────────────────────────────────┘
        │
┌───────┴───────────────────────────────────────────────────────────────────┐
│                            Git Repository                                  │
│                                                                            │
│  docs/adr/                                                                 │
│  ├── 0001-use-repository-pattern.md                                       │
│  ├── 0002-feature-module-structure.md                                     │
│  └── ...                                                                   │
└────────────────────────────────────────────────────────────────────────────┘
```

### Component Overview

| Component | Description | Tech Stack | Deployment |
|-----------|-------------|------------|------------|
| `arch-mcp-server` | MCP server (SSE transport) | FastMCP (TypeScript) | Railway |
| `arch-dashboard` | Web UI + API | Next.js | Railway |
| Database | Shared PostgreSQL | Supabase | Supabase Cloud |

### Railway Deployment Architecture

Everything deployed on Railway in a single project with internal networking:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENTS                                         │
├───────────────────────────────────┬─────────────────────────────────────────┤
│   IDE (Cursor / Claude Code)      │              Browser                     │
│              │                    │                 │                        │
│         MCP Client                │            Web Client                    │
└──────────────┬────────────────────┴─────────────────┬───────────────────────┘
               │ SSE/HTTP                             │ HTTPS
               │                                      │
               ▼                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Railway Project                                      │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                        Private Network                                  ││
│  │                                                                          ││
│  │  ┌──────────────────────┐        ┌──────────────────────┐              ││
│  │  │   arch-mcp-server    │        │   arch-dashboard     │              ││
│  │  │   (FastMCP + SSE)    │        │   (Next.js)          │              ││
│  │  │                      │        │                      │              ││
│  │  │   Public URL:        │        │   Public URL:        │              ││
│  │  │   mcp.arch.dev       │        │   arch.dev           │              ││
│  │  │                      │        │                      │              ││
│  │  │   Internal:          │        │   Internal:          │              ││
│  │  │   mcp:3001           │        │   dashboard:3000     │              ││
│  │  └──────────┬───────────┘        └──────────┬───────────┘              ││
│  │             │                               │                           ││
│  │             │                               │                           ││
│  │             │                               │                           ││
│  └─────────────┼───────────────────────────────┼───────────────────────────┘│
└────────────────┼───────────────────────────────┼────────────────────────────┘
                 │                               │
                 │    ┌────────────────────┐     │
                 └───►│    Supabase        │◄────┘
                      │    (PostgreSQL)    │
                      │                    │
                      │  • Organizations   │
                      │  • Users/Members   │
                      │  • Repositories    │
                      │  • ADRs            │
                      │  • Rules           │
                      │  • Violations      │
                      │                    │
                      │  + Auth (optional) │
                      │  + Realtime        │
                      │  + Storage         │
                      └────────────────────┘
```

### Why This Stack?

**Railway (Compute):**
| Feature | Benefit |
|---------|---------|
| **Monorepo support** | Deploy multiple services from one repo |
| **Private networking** | Services communicate internally (fast, secure) |
| **Auto-deploy** | Push to main → automatic deployment |
| **Custom domains** | Easy SSL for custom domains |
| **Reasonable pricing** | ~$5-10/mo for compute |

**Supabase (Database):**
| Feature | Benefit |
|---------|---------|
| **Managed Postgres** | Full PostgreSQL with backups, connection pooling |
| **Generous free tier** | 500MB storage, 2 projects free |
| **Realtime** | Subscribe to database changes (useful for live updates) |
| **Auth (optional)** | Can use Supabase Auth instead of NextAuth |
| **Storage** | File storage if needed later |
| **Dashboard** | Built-in SQL editor and table viewer |

### Project Setup

```
┌─────────────────────────────────────────────────────────────┐
│  Railway Project: arch-mcp                                  │
│                                                             │
│  ├── Service: mcp-server                                    │
│  │   ├── Source: /apps/mcp-server                          │
│  │   ├── Public Domain: mcp.arch-controls.dev              │
│  │   └── Env: DATABASE_URL=<supabase-connection-string>    │
│  │                                                          │
│  └── Service: dashboard                                     │
│      ├── Source: /apps/dashboard                           │
│      ├── Public Domain: arch-controls.dev                  │
│      └── Env: DATABASE_URL=<supabase-connection-string>    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ PostgreSQL connection
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Supabase Project: arch-mcp-db                              │
│                                                             │
│  • PostgreSQL Database                                      │
│  • Connection pooling (Supavisor)                          │
│  • Automatic backups                                        │
│  • Optional: Realtime subscriptions                        │
│  • Optional: Supabase Auth                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Remote MCP Configuration

IDEs connect to the deployed MCP server via URL:

**Cursor** (`.cursor/mcp.json`):
```json
{
  "mcpServers": {
    "arch-controls": {
      "url": "https://mcp.arch-controls.dev/sse",
      "headers": {
        "Authorization": "Bearer ${ARCH_API_TOKEN}"
      }
    }
  }
}
```

**Claude Code**:
```bash
claude mcp add arch-controls --transport sse \
  --url "https://mcp.arch-controls.dev/sse" \
  --header "Authorization: Bearer $ARCH_API_TOKEN"
```

### Benefits of Fully Cloud Architecture

1. **No local setup** - Users just configure their IDE with a URL and token
2. **Centralized rules** - Team shares the same rules from the same source
3. **Real-time sync** - Changes to ADRs immediately available to all users
4. **Audit trail** - All validations logged in shared database
5. **Cross-project** - One MCP server can serve multiple projects/repos

---

## Authentication

The web dashboard requires authentication to protect sensitive architecture information and control access.

### Auth Strategy

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Authentication Flow                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   User ──► Dashboard ──► NextAuth.js ──► Provider (GitHub/Google/etc)   │
│                              │                                           │
│                              ▼                                           │
│                         Session/JWT                                      │
│                              │                                           │
│                              ▼                                           │
│                     ┌────────────────┐                                  │
│                     │  Middleware    │                                  │
│                     │  - Check auth  │                                  │
│                     │  - Check org   │                                  │
│                     │  - Check role  │                                  │
│                     └────────┬───────┘                                  │
│                              │                                           │
│                              ▼                                           │
│                     Protected Routes                                     │
│                     /api/*, /adrs/*, etc                                │
└─────────────────────────────────────────────────────────────────────────┘
```

### Supported Auth Providers

| Provider | Use Case |
|----------|----------|
| **GitHub** (recommended) | Teams using GitHub repos - links to org/repo access |
| **Google Workspace** | Enterprise teams using Google |
| **Email/Password** | Standalone deployments |
| **SSO/SAML** | Enterprise (via Auth.js providers) |

### Authorization Levels

| Role | Permissions |
|------|-------------|
| `viewer` | Read ADRs, rules, view violations |
| `developer` | + Run validations, see detailed reports |
| `architect` | + Create/edit ADRs (via UI), manage rules |
| `admin` | + Manage users, org settings, integrations |

### Multi-Tenancy (Organizations)

Each organization/team has isolated:
- ADR repositories (connected via GitHub)
- Rules and configurations
- User access controls
- Validation history

```yaml
# Organization model
organization:
  id: "acme-corp"
  name: "Acme Corporation"
  repositories:
    - url: "github.com/acme/backend"
      adr_path: "docs/adr"
    - url: "github.com/acme/frontend"
      adr_path: "docs/decisions"
  members:
    - email: "alice@acme.com"
      role: "admin"
    - email: "bob@acme.com"
      role: "developer"
```

### API Authentication

For programmatic access (CI/CD, scripts):

```bash
# Generate API token in dashboard
curl -H "Authorization: Bearer arch_token_xxx" \
  https://arch-dashboard.vercel.app/api/validate \
  -d '{"repo": "acme/backend", "path": "src/"}'
```

### MCP Server Auth

The MCP server runs locally and reads files from the local filesystem, so it doesn't need authentication. It uses the local user's file permissions.

For connecting to the dashboard API (optional sync):

```yaml
# .arch-mcp.yaml
dashboard:
  url: "https://arch-dashboard.vercel.app"
  token: "${ARCH_DASHBOARD_TOKEN}"  # from env
  sync: true  # sync violations to dashboard
```

### Implementation (Next.js)

Using **NextAuth.js** (Auth.js):

```typescript
// app/api/auth/[...nextauth]/route.ts
import NextAuth from "next-auth"
import GitHub from "next-auth/providers/github"
import Google from "next-auth/providers/google"

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [
    GitHub({
      clientId: process.env.GITHUB_ID,
      clientSecret: process.env.GITHUB_SECRET,
      // Request repo access to read ADR files
      authorization: {
        params: { scope: "read:user read:org repo" }
      }
    }),
    Google({
      clientId: process.env.GOOGLE_ID,
      clientSecret: process.env.GOOGLE_SECRET,
    }),
  ],
  callbacks: {
    async session({ session, token }) {
      // Add org/role to session
      session.user.organizations = await getOrgsForUser(token.sub)
      return session
    }
  }
})
```

```typescript
// middleware.ts
import { auth } from "./auth"

export default auth((req) => {
  if (!req.auth && req.nextUrl.pathname !== "/login") {
    return Response.redirect(new URL("/login", req.url))
  }
})

export const config = {
  matcher: ["/api/:path*", "/adrs/:path*", "/rules/:path*", "/validate/:path*"]
}
```

### Environment Variables

```bash
# .env.local (Vercel)
NEXTAUTH_URL=https://arch-dashboard.vercel.app
NEXTAUTH_SECRET=your-secret-key

# GitHub OAuth
GITHUB_ID=your-github-client-id
GITHUB_SECRET=your-github-client-secret

# Google OAuth (optional)
GOOGLE_ID=your-google-client-id
GOOGLE_SECRET=your-google-client-secret

# Database (for storing orgs, users, tokens)
DATABASE_URL=postgres://...
```

---

## ADR-Driven Rules

### How It Works

1. **ADRs are checked into the repo** in a standard location (e.g., `docs/adr/`)
2. **Server watches for changes** to ADR files
3. **Parser extracts rules** from a special `## Rules` section in each ADR
4. **Rules are linked to their ADR** for traceability

### ADR Format

We extend the standard ADR format with an optional `## Rules` section that defines enforceable rules.

```markdown
# ADR-001: Use Repository Pattern for Data Access

## Status
Accepted

## Context
Direct database access from services creates tight coupling and makes testing difficult.

## Decision
All data access must go through repository classes. Services should never directly
use Prisma, TypeORM, or other database clients.

## Consequences
- Services are decoupled from database implementation
- Easier to mock data access in tests
- Slightly more boilerplate code

## Rules

<!-- BEGIN_RULES -->
- id: no-direct-db-access
  type: pattern
  severity: error
  pattern: "prisma\\.(findMany|findUnique|create|update|delete)"
  applies_to:
    - "src/services/**/*.ts"
    - "src/controllers/**/*.ts"
  exclude:
    - "src/repositories/**"
  message: "Direct database access violates ADR-001. Use repository pattern."
<!-- END_RULES -->
```

### ADR Directory Structure

```
docs/
└── adr/
    ├── 0001-use-repository-pattern.md
    ├── 0002-feature-module-structure.md
    ├── 0003-no-cross-feature-imports.md
    ├── 0004-api-versioning-strategy.md
    └── template.md
```

### Rule Extraction Process

```
┌─────────────────────────────────────────────────────────────┐
│                    ADR File                                 │
│                                                             │
│  # ADR-001: Repository Pattern                             │
│  ## Status: Accepted                                        │
│  ## Context: ...                                            │
│  ## Decision: ...                                           │
│  ## Rules                                                   │
│  <!-- BEGIN_RULES -->                                       │
│  - id: no-direct-db                                        │
│    type: pattern                                            │
│    ...                                                      │
│  <!-- END_RULES -->                                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼  ADR Parser
┌─────────────────────────────────────────────────────────────┐
│  {                                                          │
│    adr_id: "ADR-001",                                      │
│    title: "Use Repository Pattern",                        │
│    status: "accepted",                                      │
│    file: "docs/adr/0001-use-repository-pattern.md",        │
│    rules: [                                                 │
│      {                                                      │
│        id: "no-direct-db-access",                          │
│        adr_ref: "ADR-001",                                 │
│        ...                                                  │
│      }                                                      │
│    ]                                                        │
│  }                                                          │
└─────────────────────────────────────────────────────────────┘
```

### ADR Status and Rule Activation

| ADR Status | Rules Active? | Behavior |
|------------|---------------|----------|
| `proposed` | No | Rules shown but not enforced |
| `accepted` | Yes | Rules fully enforced |
| `deprecated` | Warning | Rules emit warnings, not errors |
| `superseded` | No | Rules disabled, link to new ADR |

### Configuration

```yaml
# .arch-mcp.yaml
version: "1.0"

adr:
  # Where to find ADR files
  directory: "docs/adr"

  # Glob pattern for ADR files
  pattern: "*.md"

  # How to extract ADR number from filename
  # Supports: numeric-prefix, adr-prefix, or custom regex
  naming: "numeric-prefix"  # matches 0001-*.md, 0002-*.md

  # Watch for file changes (hot reload)
  watch: true

settings:
  # Additional ignores beyond what ADRs specify
  ignore:
    - "**/*.test.ts"
    - "**/node_modules/**"
```

### Example ADRs with Rules

#### ADR-002: Feature Module Structure

```markdown
# ADR-002: Feature Module Structure

## Status
Accepted

## Context
We need a consistent structure for feature modules to improve discoverability
and maintainability.

## Decision
Each feature module must follow a standard structure with required and optional files.

## Rules

<!-- BEGIN_RULES -->
- id: feature-structure
  type: file-structure
  severity: error
  rules:
    - pattern: "src/features/*"
      must_contain:
        - "index.ts"        # Public API
        - "types.ts"        # Type definitions
      may_contain:
        - "components/"     # React components
        - "hooks/"          # Custom hooks
        - "utils/"          # Feature-specific utilities
        - "api.ts"          # API calls
        - "store.ts"        # State management
      must_not_contain:
        - "*.test.ts"       # Tests go in __tests__/
  message: "Feature module structure violates ADR-002"
<!-- END_RULES -->
```

#### ADR-003: Layer Boundaries

```markdown
# ADR-003: Clean Architecture Layer Boundaries

## Status
Accepted

## Context
We're adopting clean architecture to improve testability and maintainability.

## Decision
Strict layer boundaries: Domain → Application → Infrastructure
Inner layers must not depend on outer layers.

## Rules

<!-- BEGIN_RULES -->
- id: domain-layer-purity
  type: import
  severity: error
  rules:
    - from: "src/domain/**"
      cannot_import:
        - "src/infrastructure/**"
        - "src/api/**"
        - "src/ui/**"
      can_import:
        - "src/domain/**"
  message: "Domain layer cannot import from outer layers (ADR-003)"

- id: application-layer-boundaries
  type: import
  severity: error
  rules:
    - from: "src/application/**"
      cannot_import:
        - "src/api/**"
        - "src/ui/**"
      can_import:
        - "src/domain/**"
        - "src/application/**"
  message: "Application layer can only depend on domain (ADR-003)"

- id: no-circular-deps
  type: import
  severity: error
  detect_circular: true
  max_depth: 10
  message: "Circular dependency detected (violates ADR-003)"
<!-- END_RULES -->
```

#### ADR-004: No Cross-Feature Imports

```markdown
# ADR-004: Feature Isolation

## Status
Accepted

## Context
Features directly importing from each other creates coupling and makes
it hard to refactor or extract features.

## Decision
Features must not import directly from other features. Shared code goes
in `src/shared/`. Cross-feature communication uses events or shared state.

## Rules

<!-- BEGIN_RULES -->
- id: feature-isolation
  type: import
  severity: error
  rules:
    - from: "src/features/*//**"
      cannot_import_pattern: "src/features/(?!$1).*"  # Can't import other features
      can_import:
        - "src/shared/**"
        - "src/types/**"
        - "node_modules/**"
  message: "Features cannot import from other features (ADR-004). Use src/shared/ for shared code."
<!-- END_RULES -->
```

---

## Rule Types

### 1. Pattern-Based Rules

Match code patterns using regular expressions.

```yaml
- id: no-direct-db-access
  type: pattern
  name: "No Direct Database Access"
  severity: error
  description: "Services must use repositories, not direct DB calls"
  pattern: "prisma\\.(findMany|findUnique|create|update|delete)"
  applies_to:
    - "src/services/**/*.ts"
  exclude:
    - "src/repositories/**"
  message: "Use repository pattern instead of direct Prisma calls"
  suggestion: "Inject the appropriate repository and use its methods"
```

### 2. File Structure Rules

Enforce directory and file naming conventions.

```yaml
- id: component-location
  type: file-structure
  name: "Component File Location"
  severity: error
  description: "React components must be in the components directory"
  rules:
    - pattern: "**/*.component.tsx"
      must_be_in: "src/components/"
    - pattern: "**/use*.ts"
      must_be_in: "src/hooks/"
  message: "File is in the wrong directory"

- id: naming-convention
  type: file-structure
  name: "File Naming Convention"
  severity: warning
  rules:
    - pattern: "src/components/**/*.tsx"
      filename_must_match: "^[A-Z][a-zA-Z]+\\.tsx$"  # PascalCase
    - pattern: "src/utils/**/*.ts"
      filename_must_match: "^[a-z][a-zA-Z]+\\.ts$"   # camelCase
```

### 3. Import Restriction Rules

Control module dependencies and boundaries.

```yaml
- id: layer-boundaries
  type: import
  name: "Layer Boundaries"
  severity: error
  description: "Enforce clean architecture layer dependencies"
  rules:
    # Domain layer cannot import from infrastructure
    - from: "src/domain/**"
      cannot_import:
        - "src/infrastructure/**"
        - "src/api/**"
      message: "Domain layer must not depend on infrastructure"

    # API layer can only import from services
    - from: "src/api/**"
      can_only_import:
        - "src/services/**"
        - "src/types/**"
        - "node_modules/**"
      message: "API layer should only use services"

- id: no-circular-imports
  type: import
  name: "No Circular Imports"
  severity: error
  detect_circular: true
  max_depth: 5
```

---

## Rule Configuration File

### Project-Level: `.arch-rules.yaml`

```yaml
# .arch-rules.yaml
version: "1.0"

# Extend from presets or other configs
extends:
  - "@arch-mcp/preset-typescript"
  - "@arch-mcp/preset-react"

# Global settings
settings:
  root: "src"
  ignore:
    - "**/*.test.ts"
    - "**/*.spec.ts"
    - "**/node_modules/**"
    - "**/dist/**"
    - "**/__mocks__/**"

# Rule definitions
rules:
  # Pattern-based rules
  - id: no-console
    type: pattern
    name: "No Console Logs"
    severity: warning
    pattern: "console\\.(log|debug|info|warn)"
    exclude:
      - "src/utils/logger.ts"
    message: "Use the logger utility instead of console"
    suggestion: "Import logger from '@/utils/logger' and use logger.info()"

  - id: no-any
    type: pattern
    name: "No Any Type"
    severity: warning
    pattern: ":\\s*any\\b"
    message: "Avoid using 'any' type"
    suggestion: "Use a specific type or 'unknown' if type is truly unknown"

  # File structure rules
  - id: feature-structure
    type: file-structure
    name: "Feature Module Structure"
    severity: error
    rules:
      - pattern: "src/features/*"
        must_contain:
          - "index.ts"
          - "types.ts"
        may_contain:
          - "components/"
          - "hooks/"
          - "utils/"
          - "api.ts"

  # Import rules
  - id: no-relative-parent-imports
    type: import
    name: "No Deep Relative Imports"
    severity: warning
    rules:
      - pattern: "from ['\"]\\.\\./"
        max_depth: 2
        message: "Use path aliases instead of deep relative imports"
        suggestion: "Configure path aliases in tsconfig.json (e.g., @/)"

  - id: feature-isolation
    type: import
    name: "Feature Isolation"
    severity: error
    rules:
      - from: "src/features/auth/**"
        cannot_import:
          - "src/features/billing/**"
          - "src/features/admin/**"
        message: "Features must not directly import from other features"
        suggestion: "Use shared modules or event-based communication"

# Custom rule groups for easy enable/disable
groups:
  strict:
    - no-any
    - no-console
    - layer-boundaries

  recommended:
    - feature-structure
    - naming-convention
```

---

## MCP Interface

### Resources

| URI | Description | Returns |
|-----|-------------|---------|
| `arch://adrs` | List all ADRs | Array of ADR summaries with status |
| `arch://adrs/{id}` | Get specific ADR | Full ADR content + extracted rules |
| `arch://rules` | List all active rules | Array of rule summaries (from all ADRs) |
| `arch://rules/{id}` | Get specific rule | Full rule definition + source ADR link |
| `arch://config` | Current configuration | Merged config |
| `arch://violations` | Recent violations cache | List of recent violations found |

#### Example: `arch://adrs`

```json
{
  "adrs": [
    {
      "id": "ADR-001",
      "title": "Use Repository Pattern for Data Access",
      "status": "accepted",
      "file": "docs/adr/0001-use-repository-pattern.md",
      "rules_count": 1,
      "last_modified": "2024-01-15T10:30:00Z"
    },
    {
      "id": "ADR-002",
      "title": "Feature Module Structure",
      "status": "accepted",
      "file": "docs/adr/0002-feature-module-structure.md",
      "rules_count": 1,
      "last_modified": "2024-01-20T14:00:00Z"
    }
  ],
  "summary": {
    "total": 5,
    "accepted": 4,
    "proposed": 1,
    "deprecated": 0
  }
}
```

#### Example: `arch://rules/{id}`

```json
{
  "id": "no-direct-db-access",
  "name": "No Direct Database Access",
  "type": "pattern",
  "severity": "error",
  "source": {
    "adr_id": "ADR-001",
    "adr_title": "Use Repository Pattern for Data Access",
    "adr_file": "docs/adr/0001-use-repository-pattern.md",
    "adr_status": "accepted"
  },
  "pattern": "prisma\\.(findMany|findUnique|create|update|delete)",
  "applies_to": ["src/services/**/*.ts"],
  "exclude": ["src/repositories/**"],
  "message": "Direct database access violates ADR-001. Use repository pattern."
}
```

### Tools

#### `validate_file`

Validate a single file against applicable rules.

**Input:**
```json
{
  "path": "src/services/user.ts",
  "rules": ["no-console", "layer-boundaries"]  // optional, defaults to all
}
```

**Output:**
```json
{
  "file": "src/services/user.ts",
  "valid": false,
  "violations": [
    {
      "rule_id": "no-console",
      "rule_name": "No Console Logs",
      "severity": "warning",
      "line": 45,
      "column": 5,
      "match": "console.log(user)",
      "message": "Use the logger utility instead of console",
      "suggestion": "Import logger from '@/utils/logger' and use logger.info()"
    }
  ],
  "summary": {
    "errors": 0,
    "warnings": 1
  }
}
```

#### `validate_directory`

Validate all files in a directory.

**Input:**
```json
{
  "path": "src/services",
  "recursive": true,
  "rules": null,  // all rules
  "fail_on": "error"  // "error" | "warning" | "none"
}
```

**Output:**
```json
{
  "directory": "src/services",
  "files_checked": 12,
  "files_with_violations": 3,
  "violations": [
    {
      "file": "src/services/user.ts",
      "violations": [...]
    }
  ],
  "summary": {
    "total_errors": 2,
    "total_warnings": 5
  }
}
```

#### `list_rules`

List all configured rules.

**Input:**
```json
{
  "type": "pattern",  // optional filter
  "severity": "error"  // optional filter
}
```

**Output:**
```json
{
  "rules": [
    {
      "id": "no-console",
      "name": "No Console Logs",
      "type": "pattern",
      "severity": "warning",
      "description": "Use the logger utility instead of console",
      "enabled": true
    }
  ],
  "total": 15,
  "by_type": {
    "pattern": 8,
    "file-structure": 4,
    "import": 3
  }
}
```

#### `explain_rule`

Get detailed explanation of a rule.

**Input:**
```json
{
  "rule_id": "layer-boundaries"
}
```

**Output:**
```json
{
  "id": "layer-boundaries",
  "name": "Layer Boundaries",
  "type": "import",
  "severity": "error",
  "description": "Enforce clean architecture layer dependencies",
  "rationale": "Clean architecture separates concerns into layers. Inner layers should not know about outer layers to maintain flexibility and testability.",
  "examples": {
    "bad": [
      {
        "file": "src/domain/user.ts",
        "code": "import { prisma } from '../infrastructure/db'",
        "explanation": "Domain importing from infrastructure violates layer boundaries"
      }
    ],
    "good": [
      {
        "file": "src/domain/user.ts",
        "code": "import { UserRepository } from './repositories'",
        "explanation": "Domain uses abstractions defined within the domain layer"
      }
    ]
  },
  "references": [
    "https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html"
  ]
}
```

#### `check_imports`

Analyze import graph for a file or module.

**Input:**
```json
{
  "path": "src/features/auth",
  "depth": 3,
  "check_circular": true
}
```

**Output:**
```json
{
  "module": "src/features/auth",
  "imports": {
    "internal": ["./components", "./hooks", "./api"],
    "external": ["react", "axios"],
    "project": ["@/utils/logger", "@/types"]
  },
  "imported_by": ["src/app/routes.tsx", "src/features/settings"],
  "circular_dependencies": [],
  "violations": []
}
```

#### `list_adrs`

List all ADRs and their status.

**Input:**
```json
{
  "status": "accepted"  // optional filter
}
```

**Output:**
```json
{
  "adrs": [
    {
      "id": "ADR-001",
      "title": "Use Repository Pattern",
      "status": "accepted",
      "rules_count": 1,
      "file": "docs/adr/0001-use-repository-pattern.md"
    }
  ]
}
```

#### `get_adr`

Get full ADR content and its rules.

**Input:**
```json
{
  "id": "ADR-001"
}
```

**Output:**
```json
{
  "id": "ADR-001",
  "title": "Use Repository Pattern for Data Access",
  "status": "accepted",
  "file": "docs/adr/0001-use-repository-pattern.md",
  "content": {
    "context": "Direct database access from services creates...",
    "decision": "All data access must go through repository classes...",
    "consequences": ["Services are decoupled...", "..."]
  },
  "rules": [
    {
      "id": "no-direct-db-access",
      "type": "pattern",
      "severity": "error",
      "enabled": true
    }
  ],
  "violations_count": 3
}
```

#### `refresh_adrs`

Force reload ADR files (useful after git pull).

**Input:**
```json
{}
```

**Output:**
```json
{
  "reloaded": 5,
  "added": 1,
  "removed": 0,
  "rules_updated": 2
}
```

### Prompts

#### `architecture_review`

Generate an architecture review for code.

**Arguments:**
```json
{
  "scope": "src/features/billing",
  "focus": ["layer-boundaries", "feature-isolation"]
}
```

**Returns prompt for LLM:**
```
Review the code in src/features/billing for architecture compliance.

Focus areas:
- Layer Boundaries: Ensure proper separation between domain, application, and infrastructure
- Feature Isolation: Check that this feature doesn't have tight coupling to other features

Current violations found:
[... violations injected here ...]

Please analyze the code structure and provide:
1. Summary of architectural issues
2. Specific recommendations for each violation
3. Suggested refactoring approach
```

#### `suggest_fix`

Generate fix suggestions for violations.

**Arguments:**
```json
{
  "file": "src/services/user.ts",
  "violation_id": "v-123"
}
```

---

## IDE Configuration

### Cursor

Create `.cursor/mcp.json` in project root:

```json
{
  "mcpServers": {
    "arch-controls": {
      "command": "npx",
      "args": ["-y", "arch-mcp-server"],
      "env": {
        "ARCH_CONFIG": ".arch-rules.yaml"
      }
    }
  }
}
```

Or globally in `~/.cursor/mcp.json`.

### Claude Code

Add via CLI:

```bash
claude mcp add arch-controls -- npx -y arch-mcp-server
```

Or edit `~/.claude.json`:

```json
{
  "mcpServers": {
    "arch-controls": {
      "command": "npx",
      "args": ["-y", "arch-mcp-server"],
      "env": {
        "ARCH_CONFIG": ".arch-rules.yaml"
      }
    }
  }
}
```

---

## Project Structure

### Monorepo Structure

```
arch-mcp/
├── packages/
│   └── db/                          # @arch-mcp/db - Shared Prisma client
│       ├── prisma/
│       │   └── schema.prisma
│       ├── src/
│       │   └── index.ts             # Export Prisma client
│       └── package.json
│
├── apps/
│   ├── mcp-server/                  # FastMCP Server (Railway/Render)
│   │   ├── src/
│   │   │   ├── index.ts             # Entry point, FastMCP setup
│   │   │   ├── auth.ts              # Token validation
│   │   │   ├── tools/
│   │   │   │   ├── validate.ts      # validate_file, validate_directory
│   │   │   │   ├── rules.ts         # list_rules, explain_rule
│   │   │   │   ├── adrs.ts          # list_adrs, get_adr
│   │   │   │   └── imports.ts       # check_imports
│   │   │   ├── resources/
│   │   │   │   ├── adrs.ts          # arch://adrs/*
│   │   │   │   └── rules.ts         # arch://rules/*
│   │   │   ├── prompts/
│   │   │   │   └── review.ts
│   │   │   └── engine/
│   │   │       ├── pattern.ts       # Regex matching
│   │   │       ├── file-structure.ts
│   │   │       ├── imports.ts
│   │   │       └── index.ts
│   │   ├── Dockerfile               # For Railway/Render
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   └── dashboard/                   # Next.js Web Dashboard (Vercel)
│       ├── app/
│       │   ├── layout.tsx
│       │   ├── page.tsx             # Dashboard home
│       │   ├── (auth)/
│       │   │   ├── login/page.tsx
│       │   │   └── signup/page.tsx
│       │   ├── (dashboard)/
│       │   │   ├── adrs/
│       │   │   │   ├── page.tsx
│       │   │   │   └── [id]/page.tsx
│       │   │   ├── rules/
│       │   │   │   ├── page.tsx
│       │   │   │   └── [id]/page.tsx
│       │   │   ├── validate/page.tsx
│       │   │   ├── repos/page.tsx
│       │   │   └── settings/page.tsx
│       │   └── api/
│       │       ├── auth/[...nextauth]/route.ts
│       │       ├── adrs/route.ts
│       │       ├── adrs/[id]/route.ts
│       │       ├── rules/route.ts
│       │       ├── rules/[id]/route.ts
│       │       ├── validate/route.ts
│       │       ├── repos/route.ts
│       │       ├── repos/[id]/sync/route.ts
│       │       └── tokens/route.ts
│       ├── components/
│       │   ├── ui/                  # shadcn/ui
│       │   ├── adr-card.tsx
│       │   ├── rule-card.tsx
│       │   ├── violation-list.tsx
│       │   ├── code-viewer.tsx
│       │   └── nav.tsx
│       ├── lib/
│       │   ├── auth.ts              # NextAuth config
│       │   └── github.ts            # GitHub API
│       ├── package.json
│       ├── next.config.js
│       ├── tailwind.config.js
│       └── vercel.json
│
├── templates/
│   └── adr-template.md
│
├── package.json                     # pnpm workspace root
├── pnpm-workspace.yaml
├── turbo.json
└── README.md
```

### FastMCP Server Implementation

```typescript
// apps/mcp-server/src/index.ts
import { FastMCP } from "fastmcp";
import { z } from "zod";
import { db } from "@arch-mcp/db";
import { validateFile } from "./tools/validate";
import { listRules, explainRule } from "./tools/rules";
import { listAdrs, getAdr } from "./tools/adrs";
import { validateToken } from "./auth";

const server = new FastMCP({
  name: "arch-controls",
  version: "1.0.0",
});

// Authentication middleware
server.use(async (ctx, next) => {
  const token = ctx.headers?.authorization?.replace("Bearer ", "");
  if (!token) {
    throw new Error("Missing authorization token");
  }
  const org = await validateToken(token);
  ctx.organizationId = org.id;
  return next();
});

// Tools
server.addTool({
  name: "validate_file",
  description: "Validate a file against architecture rules from ADRs",
  parameters: z.object({
    content: z.string().describe("File content to validate"),
    filename: z.string().describe("Filename with extension"),
    path: z.string().optional().describe("File path for context"),
  }),
  execute: async ({ content, filename, path }, ctx) => {
    const rules = await db.rule.findMany({
      where: {
        adr: {
          repository: { organizationId: ctx.organizationId },
          status: "ACCEPTED"
        },
        enabled: true
      },
      include: { adr: true }
    });
    return validateFile(content, filename, path, rules);
  },
});

server.addTool({
  name: "list_rules",
  description: "List all active architecture rules",
  parameters: z.object({
    type: z.enum(["pattern", "file-structure", "import"]).optional(),
    severity: z.enum(["error", "warning", "info"]).optional(),
  }),
  execute: async ({ type, severity }, ctx) => {
    return listRules(ctx.organizationId, { type, severity });
  },
});

server.addTool({
  name: "list_adrs",
  description: "List all Architecture Decision Records",
  parameters: z.object({
    status: z.enum(["proposed", "accepted", "deprecated", "superseded"]).optional(),
  }),
  execute: async ({ status }, ctx) => {
    return listAdrs(ctx.organizationId, { status });
  },
});

server.addTool({
  name: "get_adr",
  description: "Get full ADR content and its rules",
  parameters: z.object({
    id: z.string().describe("ADR ID (e.g., ADR-001)"),
  }),
  execute: async ({ id }, ctx) => {
    return getAdr(ctx.organizationId, id);
  },
});

server.addTool({
  name: "explain_rule",
  description: "Get detailed explanation of a rule with examples",
  parameters: z.object({
    ruleId: z.string().describe("Rule ID"),
  }),
  execute: async ({ ruleId }, ctx) => {
    return explainRule(ctx.organizationId, ruleId);
  },
});

// Resources
server.addResourceTemplate({
  uriTemplate: "arch://adrs",
  name: "ADR List",
  mimeType: "application/json",
  async load(uri, ctx) {
    const adrs = await listAdrs(ctx.organizationId, {});
    return JSON.stringify(adrs, null, 2);
  },
});

server.addResourceTemplate({
  uriTemplate: "arch://adrs/{id}",
  name: "ADR Detail",
  mimeType: "application/json",
  async load(uri, ctx) {
    const id = uri.split("/").pop();
    const adr = await getAdr(ctx.organizationId, id);
    return JSON.stringify(adr, null, 2);
  },
});

server.addResourceTemplate({
  uriTemplate: "arch://rules",
  name: "Rules List",
  mimeType: "application/json",
  async load(uri, ctx) {
    const rules = await listRules(ctx.organizationId, {});
    return JSON.stringify(rules, null, 2);
  },
});

// Start server with SSE transport for cloud deployment
server.start({
  transportType: "sse",
  port: parseInt(process.env.PORT || "3001"),
});

console.log(`MCP Server running on port ${process.env.PORT || 3001}`);
```

### Dockerfile for MCP Server

```dockerfile
# apps/mcp-server/Dockerfile
FROM node:20-slim

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy workspace files
COPY pnpm-workspace.yaml package.json pnpm-lock.yaml ./
COPY packages/db ./packages/db
COPY apps/mcp-server ./apps/mcp-server

# Install dependencies
RUN pnpm install --frozen-lockfile

# Generate Prisma client
RUN pnpm --filter @arch-mcp/db db:generate

# Build
RUN pnpm --filter arch-mcp-server build

EXPOSE 3001

CMD ["node", "apps/mcp-server/dist/index.js"]
```

### Railway Configuration

**railway.json** (in repo root):
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "numReplicas": 1,
    "restartPolicyType": "ON_FAILURE"
  }
}
```

**Service-specific configs:**

```yaml
# apps/mcp-server/railway.toml
[build]
builder = "dockerfile"
dockerfilePath = "Dockerfile"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 30
```

```yaml
# apps/dashboard/railway.toml
[build]
builder = "nixpacks"

[deploy]
healthcheckPath = "/api/health"
```

### Environment Variables

**Supabase (get from Supabase Dashboard → Settings → Database):**
```bash
# Direct connection (for migrations)
DATABASE_URL=postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres

# Pooled connection (for app - recommended)
DATABASE_URL=postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres?pgbouncer=true

# Supabase API (optional, if using Supabase client)
SUPABASE_URL=https://[project-ref].supabase.co
SUPABASE_ANON_KEY=<anon-key>
SUPABASE_SERVICE_KEY=<service-key>
```

**MCP Server (Railway):**
```bash
PORT=3001
NODE_ENV=production
DATABASE_URL=<supabase-pooled-connection-string>
```

**Dashboard (Railway):**
```bash
PORT=3000
NODE_ENV=production
DATABASE_URL=<supabase-pooled-connection-string>

# Auth
NEXTAUTH_URL=https://arch-controls.dev
NEXTAUTH_SECRET=<generated-secret>
GITHUB_ID=<github-oauth-app-id>
GITHUB_SECRET=<github-oauth-app-secret>

# Internal MCP server URL (for dashboard to call MCP)
MCP_INTERNAL_URL=http://mcp-server.railway.internal:3001
```

### Supabase Setup

1. **Create project** at [supabase.com](https://supabase.com)
2. **Get connection string** from Settings → Database → Connection string
3. **Use pooled connection** (port 6543) for Railway services
4. **Run migrations** with direct connection (port 5432)

```bash
# Run Prisma migrations against Supabase
DATABASE_URL="postgresql://postgres.[ref]:[pass]@aws-0-us-east-1.pooler.supabase.com:5432/postgres" \
  pnpm prisma migrate deploy
```

### Optional Supabase Features

**Realtime (Live Updates):**
```typescript
// Subscribe to new violations in dashboard
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)

supabase
  .channel('violations')
  .on('postgres_changes',
    { event: 'INSERT', schema: 'public', table: 'Violation' },
    (payload) => {
      console.log('New violation:', payload.new)
      // Update UI in real-time
    }
  )
  .subscribe()
```

**Supabase Auth (Alternative to NextAuth):**
- Can replace NextAuth.js entirely
- Built-in GitHub OAuth
- Row Level Security (RLS) for multi-tenancy
- Less code to maintain

```typescript
// Using Supabase Auth
const { data, error } = await supabase.auth.signInWithOAuth({
  provider: 'github',
  options: {
    scopes: 'read:user read:org repo'
  }
})
```

**Row Level Security (Multi-tenancy):**
```sql
-- Enable RLS
ALTER TABLE "Adr" ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see ADRs from their organization
CREATE POLICY "Users see own org ADRs" ON "Adr"
  FOR SELECT
  USING (
    repository_id IN (
      SELECT r.id FROM "Repository" r
      JOIN "Member" m ON m.organization_id = r.organization_id
      WHERE m.user_id = auth.uid()
    )
  );
```

### Deploy Commands

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project (first time)
railway init

# Link to existing project
railway link

# Deploy all services
railway up

# View logs
railway logs --service mcp-server
railway logs --service dashboard

# Open dashboard
railway open
```

### Custom Domains

1. In Railway dashboard, go to each service's Settings
2. Add custom domain:
   - `mcp-server` → `mcp.arch-controls.dev`
   - `dashboard` → `arch-controls.dev`
3. Add DNS records at your registrar:
   ```
   mcp.arch-controls.dev  CNAME  <railway-provided>.up.railway.app
   arch-controls.dev      CNAME  <railway-provided>.up.railway.app
   ```

### Web Dashboard Pages

| Route | Description | Auth Required |
|-------|-------------|---------------|
| `/` | Dashboard home - summary stats, recent activity | Yes |
| `/login` | Login page with OAuth providers | No |
| `/adrs` | List all ADRs with status filters | Yes |
| `/adrs/[id]` | ADR detail with full content and rules | Yes |
| `/rules` | List all rules with filters | Yes |
| `/rules/[id]` | Rule detail with violations | Yes |
| `/validate` | Upload/paste code for validation | Yes |
| `/settings` | Org settings, repo connections, members | Admin |

### API Routes

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/auth/*` | * | NextAuth.js handlers | - |
| `/api/adrs` | GET | List ADRs for org | Token/Session |
| `/api/adrs/[id]` | GET | Get ADR detail | Token/Session |
| `/api/rules` | GET | List rules for org | Token/Session |
| `/api/rules/[id]` | GET | Get rule detail | Token/Session |
| `/api/validate` | POST | Validate code against rules | Token/Session |
| `/api/repos` | GET | List connected repos | Session |
| `/api/repos` | POST | Connect a new repo | Admin |
| `/api/repos/[id]/sync` | POST | Sync ADRs from repo | Session |
| `/api/tokens` | GET/POST | Manage API tokens | Admin |

### Database Schema (Prisma)

```prisma
// prisma/schema.prisma

model Organization {
  id        String   @id @default(cuid())
  name      String
  slug      String   @unique
  createdAt DateTime @default(now())

  members     Member[]
  repositories Repository[]
  apiTokens   ApiToken[]
}

model Member {
  id             String       @id @default(cuid())
  userId         String
  organizationId String
  role           Role         @default(VIEWER)
  createdAt      DateTime     @default(now())

  user         User         @relation(fields: [userId], references: [id])
  organization Organization @relation(fields: [organizationId], references: [id])

  @@unique([userId, organizationId])
}

enum Role {
  VIEWER
  DEVELOPER
  ARCHITECT
  ADMIN
}

model Repository {
  id             String       @id @default(cuid())
  organizationId String
  provider       String       @default("github") // github, gitlab, etc
  owner          String       // github org/user
  name           String       // repo name
  adrPath        String       @default("docs/adr")
  branch         String       @default("main")
  lastSyncedAt   DateTime?
  createdAt      DateTime     @default(now())

  organization Organization @relation(fields: [organizationId], references: [id])
  adrs         Adr[]

  @@unique([organizationId, owner, name])
}

model Adr {
  id           String     @id @default(cuid())
  repositoryId String
  adrNumber    String     // "ADR-001"
  title        String
  status       AdrStatus
  filePath     String
  content      String     @db.Text
  rulesJson    Json?      // Extracted rules
  lastSyncedAt DateTime
  createdAt    DateTime   @default(now())

  repository Repository @relation(fields: [repositoryId], references: [id])
  rules      Rule[]

  @@unique([repositoryId, adrNumber])
}

enum AdrStatus {
  PROPOSED
  ACCEPTED
  DEPRECATED
  SUPERSEDED
}

model Rule {
  id          String   @id @default(cuid())
  adrId       String
  ruleId      String   // "no-direct-db-access"
  type        RuleType
  severity    Severity
  name        String
  description String?
  config      Json     // Rule-specific config (pattern, etc)
  enabled     Boolean  @default(true)
  createdAt   DateTime @default(now())

  adr        Adr        @relation(fields: [adrId], references: [id])
  violations Violation[]

  @@unique([adrId, ruleId])
}

enum RuleType {
  PATTERN
  FILE_STRUCTURE
  IMPORT
}

enum Severity {
  ERROR
  WARNING
  INFO
}

model Violation {
  id          String   @id @default(cuid())
  ruleId      String
  filePath    String
  line        Int?
  column      Int?
  message     String
  codeSnippet String?
  detectedAt  DateTime @default(now())

  rule Rule @relation(fields: [ruleId], references: [id])
}

model ApiToken {
  id             String       @id @default(cuid())
  organizationId String
  name           String
  tokenHash      String       @unique
  lastUsedAt     DateTime?
  expiresAt      DateTime?
  createdAt      DateTime     @default(now())

  organization Organization @relation(fields: [organizationId], references: [id])
}

model User {
  id        String   @id @default(cuid())
  email     String   @unique
  name      String?
  image     String?
  createdAt DateTime @default(now())

  members Member[]
  accounts Account[]
  sessions Session[]
}

// NextAuth.js models
model Account {
  // ... standard NextAuth account model
}

model Session {
  // ... standard NextAuth session model
}
```

---

## Implementation Phases

### Phase 1: Project Setup & Database
- [ ] Initialize monorepo (pnpm workspaces + Turborepo)
- [ ] Set up shared Prisma schema (`packages/db`)
- [ ] Create database models (Org, User, Repo, ADR, Rule, Violation)
- [ ] Railway project setup with Postgres
- [ ] Basic auth (NextAuth.js with GitHub provider)

### Phase 2: Dashboard MVP
- [ ] Next.js app with authentication
- [ ] GitHub OAuth + organization access
- [ ] Connect repository flow
- [ ] ADR sync from GitHub (fetch markdown files)
- [ ] ADR list/detail pages
- [ ] Rule list/detail pages
- [ ] Deploy dashboard to Railway

### Phase 3: ADR Parser & Rule Engine
- [ ] ADR markdown parser (extract `## Rules` section)
- [ ] Rule extraction from YAML in ADR
- [ ] Pattern-based rule engine (regex matching)
- [ ] File structure rule engine
- [ ] Store parsed rules in database

### Phase 4: MCP Server
- [ ] FastMCP server setup with SSE transport
- [ ] Token-based authentication
- [ ] `list_adrs`, `get_adr` tools
- [ ] `list_rules`, `explain_rule` tools
- [ ] `validate_file` tool
- [ ] MCP resources (`arch://adrs/*`, `arch://rules/*`)
- [ ] Deploy MCP server to Railway

### Phase 5: Validation & Integration
- [ ] Validation UI in dashboard
- [ ] `validate_directory` tool
- [ ] Import analysis engine
- [ ] Circular dependency detection
- [ ] Violation tracking and history
- [ ] API tokens for CI/CD

### Phase 6: Polish
- [ ] ADR template in dashboard
- [ ] Violation trends/analytics
- [ ] Caching (Redis or in-memory)
- [ ] Documentation
- [ ] Public launch

---

## ADR Template

When creating new ADRs, use this template to ensure rules can be extracted:

```markdown
# ADR-{NUMBER}: {Title}

## Status
{Proposed | Accepted | Deprecated | Superseded by ADR-XXX}

## Context
{What is the issue that we're seeing that is motivating this decision?}

## Decision
{What is the change that we're proposing and/or doing?}

## Consequences
{What becomes easier or more difficult to do because of this change?}

## Rules

<!--
  Rules are optional. If this ADR should enforce code patterns,
  define them below using YAML syntax.

  Supported rule types:
  - pattern: Regex-based code pattern matching
  - file-structure: Directory and file naming rules
  - import: Module dependency restrictions
-->

<!-- BEGIN_RULES -->
- id: {unique-rule-id}
  type: {pattern | file-structure | import}
  severity: {error | warning | info}
  # ... rule-specific fields
  message: "Violation message referencing this ADR"
<!-- END_RULES -->

## References
- {Links to relevant resources}
```

---

## Usage Examples

### Example 1: Validate Before Commit

User asks Claude/Cursor:
> "Check if my changes follow architecture rules before I commit"

AI calls `validate_directory` on changed files, reports violations with ADR links.

### Example 2: Explain a Violation

User asks:
> "Why can't I import from infrastructure in my domain layer?"

AI calls `explain_rule("domain-layer-purity")`:
- Returns rule details
- Links to ADR-003 (Clean Architecture Layer Boundaries)
- Shows the decision context from the ADR
- Provides examples

### Example 3: List All Architecture Decisions

User asks:
> "What architecture decisions have been made for this project?"

AI calls `list_adrs()`:
- Returns all ADRs with status
- Shows which ones have active rules
- Summarizes what each ADR covers

### Example 4: Check Compliance for a Feature

User asks:
> "Does the billing feature comply with our architecture?"

AI calls `validate_directory("src/features/billing")`:
- Checks all ADR-derived rules
- Reports violations grouped by ADR
- Links each violation to the relevant ADR for context

### Example 5: New Developer Onboarding

User asks:
> "What rules should I follow when adding code to this project?"

AI calls `list_rules()` and `list_adrs()`:
- Shows all active rules with their source ADRs
- Provides links to read the full ADR context
- Groups rules by category (patterns, imports, structure)

### Example 6: After Adding a New ADR

Developer commits `docs/adr/0005-use-dependency-injection.md`

Server detects the change, parses the new ADR, and automatically activates any rules defined in it. Next validation will include the new rules.

---

## Future Enhancements

- **AST-based rules**: Use TypeScript compiler API for semantic analysis
- **Custom rule plugins**: Allow users to write custom rule handlers
- **CI/CD integration**: Export results in standard formats (SARIF, JUnit)
- **Rule auto-fix**: Automated code modifications for simple violations
- **IDE decorations**: Real-time violation highlighting via diagnostics
- **ADR generation**: Create new ADRs from natural language descriptions
- **Rule suggestions**: AI suggests rules based on codebase patterns
- **Violation trends**: Track violations over time per ADR
- **Git integration**: Show which commit introduced a violation
- **ADR linking**: Detect when code references an ADR in comments

---

## Summary

This MCP server bridges the gap between architecture documentation (ADRs) and code enforcement. Key benefits:

1. **Single source of truth** - ADRs define both the "why" and the "how"
2. **Living documentation** - Rules update automatically as ADRs change
3. **Traceability** - Every violation links back to its architectural decision
4. **IDE integration** - Works in Cursor and Claude Code out of the box
5. **Developer experience** - AI assistants can explain rules with full context
