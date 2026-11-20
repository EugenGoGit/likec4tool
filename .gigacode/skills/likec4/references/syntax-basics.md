# LikeC4 Syntax Basics

## File Extensions
- `.c4`, `.likec4`, `.like-c4`
- All sources are merged into a single model

## Top-Level Statements
```
specification { ... }   -- defines element kinds, relationship kinds, tags, colors
model { ... }           -- architecture elements, hierarchies, compositions, relationships
views { ... }          -- visualizations (element views, dynamic views, deployment views)
global { ... }         -- shared styles and predicate groups
diff { ... }           -- planned model changes
```

## Element Definition

### Specification
```likec4
specification {
  element actor
  element system
  element component
  element queue {
    title 'Kafka'
    technology 'kafka topic'
    style { shape queue }
  }
}
```

### Model - Basic Elements
```likec4
model {
  actor customer
  system cloud
  component backend
}
```

### Model - With Title
```likec4
model {
  saas = system 'SaaS'
  saas = system 'SaaS' 'Provides services to customers'
}
```

### Model - With Properties (Block Syntax)
```likec4
model {
  saas = system {
    title 'SaaS'
    description 'Provides services to customers'
    technology 'SaaS'
    #deprecated
  }
}
```

### Model - Nested/Hierarchical Elements
```likec4
model {
  service service1 {
    component backend {
      component api
    }
    component frontend
  }
}
```
Fully qualified names: `service1`, `service1.backend`, `service1.backend.api`, `service1.frontend`

## Element Properties

| Property | Description | Example |
|----------|-------------|---------|
| `title` | Display name | `title 'My Service'` |
| `description` | Detailed text (supports Markdown) | `description '...'` |
| `summary` | Short summary for diagrams | `summary '...'` |
| `technology` | Tech label | `technology 'REST'` |
| `tags` | Markers for filtering | `#deprecated`, `#team1` |
| `links` | External links | `link https://... 'Label'` |
| `metadata` | Key-value pairs | `metadata { version '2.1.0' }` |
| `icon` | Visual icon | `icon tech:nodejs`, `icon aws:lambda` |
| `style` | Shape, color, size | `style { shape browser }` |

## Relationships

### Basic Syntax
```likec4
model {
  customer -> cloud                    // directed
  frontend <-> backend 'Sync'          // bidirectional
}
```

### Kinded Relationships
```likec4
specification {
  relationship async
  relationship uses
}

model {
  system1 -[async]-> system2
  system1 -[async]<-> system3
  system1 .uses system2    // dot-prefix style
}
```

### Relationship Properties
```likec4
model {
  customer -> frontend {
    title 'opens in browser'
    description 'Customer opens...'
    technology 'HTTPS'
    #graphql #team1
    link https://... 'Repository'
    navigateTo dashboard-request-flow
    metadata { protocol 'https' }
  }
}
```

### Nested Relationships (Sourceless)
```likec4
model {
  service cloud {
    component backend
    component frontend
    frontend -> backend              // explicit
    customer -> frontend             // source = parent (cloud)
  }
}
```

Use `it` or `this` to refer to the parent element.

## Element Name Rules
- Letters, digits, hyphens, underscores
- Cannot start with digit
- Cannot contain `.`
