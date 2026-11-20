---
name: likec4
description: LikeC4 DSL syntax for creating and editing software architecture diagrams. Use when working with .c4, .likec4, or .like-c4 files, when creating C4 model diagrams, when configuring views/filters/styles, or when reading LikeC4 architecture documentation.
---

# LikeC4

Write, edit, and debug LikeC4 architecture files (`.c4`, `.likec4`, `.like-c4`). This skill covers the full LikeC4 language: specification, model, views, dynamic views, deployment views, styling, and configuration.

## Quick Reference

LikeC4 has 5 top-level blocks:
- `specification { ... }` — element kinds, relationship kinds, tags, custom colors
- `model { ... }` — architecture elements, hierarchies, relationships
- `views { ... }` — element views, dynamic views, deployment views
- `global { ... }` — shared styles and predicate groups
- `diff { ... }` — planned model changes

## Workflow

### 1. Create New Architecture File
Create a `.c4` file with three sections:
```likec4
specification { ... }
model { ... }
views { ... }
```

### 2. Define Element Kinds (specification)
```likec4
specification {
  element actor
  element system
  element component
}
```

### 3. Define Architecture (model)
```likec4
model {
  actor customer
  system cloud
  customer -> cloud
}
```

### 4. Define Views (views)
```likec4
views {
  view index {
    title 'Landscape'
    #overview
    include *
  }
}
```

## Core Syntax

### Elements
```likec4
actor customer
saas = system 'SaaS' 'Description here'
saas = system { title 'SaaS'; technology 'SaaS' }
```

### Hierarchical Elements
```likec4
model {
  service cloud {
    component backend {
      component api
    }
  }
}
// FQN: cloud, cloud.backend, cloud.backend.api
```

### Relationships
```likec4
customer -> cloud                 // directed
frontend <-> backend 'Sync'       // bidirectional
system1 -[async]-> system2        // kinded
```

### View Predicates
```likec4
view {
  include backend, frontend
  include messageBroker.*         // children
  include messageBroker.**        // descendants
  include cloud.*
    where kind is microservice
    and tag is not #deprecated
  exclude emailsQueue
}
```

## Key Operators

| Operator | Meaning |
|----------|---------|
| `->` | Directed relationship |
| `<->` | Bidirectional |
| `-[kind]->` | Kinded relationship |
| `.*` / `.**` | Children / descendants |
| `where` | Filter conditions |
| `with { }` | Override properties |
| `#tag` | Inline tag |
| `extends` | Extend a view |

## Element Properties
`title`, `description`, `summary`, `technology`, `tags` (`#tag`), `links`, `metadata { ... }`, `icon` (`tech:nodejs`, `aws:lambda`), `style { shape ... color ... }`

## View Types
- `view` — element view (default)
- `dynamic view` — scenario flow (sequence or diagram variant)
- `deployment view` — infrastructure topology

## Styling

### Element Styles
`shape` (rectangle, component, storage, cylinder, browser, mobile, person, queue, bucket, document, agent), `color`, `size`, `opacity`, `border`, `icon`, `multiple`

### Relationship Styles
`line` (dashed, solid, dotted), `head`, `tail`, `color`, `multiple`

### Style Predicates
```likec4
style * { color muted; opacity 10% }
style singlePageApplication { color secondary; size xlarge }
style element.tag = #deprecated { color muted }
```

## Layout
```likec4
autoLayout LeftRight 120 110 ortho
routing ortho
rank same { api1, api2 }
```

## Configuration
Check for `likec4.config.json` in project root. Key options: `name`, `include.paths`, `exclude`, `implicitViews`, `styles.defaults`, `styles.theme`.

## Resources

- **references/syntax-basics.md** — Core syntax: specification, model, elements, relationships
- **references/views-and-filtering.md** — Views, predicates, filtering, groups, styles, layout
- **references/advanced-patterns.md** — Dynamic views, deployment views, config, operators, icons

When writing LikeC4 code, consult the relevant reference file for detailed examples and full property lists.
