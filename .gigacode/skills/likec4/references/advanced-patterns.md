# LikeC4 Advanced Patterns

## Dynamic Views

```likec4
views {
  dynamic view checkout-flow {
    title 'Checkout Flow'
    variant sequence    // or diagram (default)

    customer -> web 'opens checkout'
    web -> api 'POST /orders'
    api -> api 'process'

    // Flow control
    parallel {
      api -> cache
      api -> db
    }
    opt 'if not cached' {
      api -> db 'load and cache'
    }
    loop 'until success' {
      api -> auth 'retry'
    }
    alt {
      when 'authorized' { web -> api 'requests data' }
      else 'not authorized' { web -> customer 'shows login' }
    }

    include cloud, ui   // non-participating elements
    style cloud { color muted; opacity 0% }
  }
}
```

### Flow Control Keywords
| Keyword | Description |
|---------|-------------|
| `parallel` | Concurrent steps |
| `opt` | Optional step (if condition) |
| `loop` | Repeated step (until condition) |
| `alt` | Alternative paths (when/else) |

## Deployment Views

```likec4
deployment view prod {
  title 'Production'
  description 'Production deployment topology'

  node datacenter 'Data Center' {
    node server1 'Web Server'
    node server2 'App Server'
    node db 'Database Server'
    
    server1 -> db
    server2 -> db
  }
}
```

## Configuration File (`likec4.config.json`)

```json5
{
  "$schema": "https://likec4.dev/schemas/config.json",
  "name": "project-name",
  "title": "Project Title",
  "contactPerson": "Jane Doe",
  "metadata": { "owner": "platform-team" },

  "exclude": ["**/node_modules/**"],

  "include": {
    "paths": ["../shared"],
    "maxDepth": 5,
    "fileThreshold": 50
  },

  "inferTechnologyFromIcon": false,
  "implicitViews": true,

  "landingPage": {
    "redirect": true,
    "include": ["cloud", "#overview"],
    "exclude": ["#internal"]
  },

  "webapp": {
    "exportFormats": ["png", "jpg", "drawio"],
    "relationshipsBrowser": { "defaultScope": "global" }
  },

  "styles": {
    "theme": {
      "colors": {
        "primary": "#FF6B6B",
        "muted": {
          "elements": { "fill": "#2563eb", "stroke": "#1d4ed8" },
          "relationships": { "line": "#1d4ed8" }
        }
      },
      "sizes": { "md": { "width": 200, "height": 200 } }
    },
    "defaults": {
      "border": "dashed",
      "opacity": 100,
      "size": "md",
      "color": "primary",
      "group": { "color": "primary", "opacity": 10, "border": "dashed" },
      "relationship": { "color": "gray", "line": "dashed", "arrow": "normal" },
      "view": { "routing": "ortho" }
    }
  },

  "extends": ["../shared/base-config.json"]
}
```

## Key Operators Summary

| Operator | Meaning |
|----------|---------|
| `->` | Directed relationship |
| `<->` | Bidirectional relationship |
| `-[kind]->` | Kinded directed relationship |
| `.kind` | Dot-prefix kinded relationship |
| `.*` | Children selector (in predicates) |
| `.**` | Descendants selector |
| `._` | Expand selector |
| `where` | Filter by conditions |
| `with { }` | Override element/relationship properties |
| `extends` | Extend a view |
| `#tag` | Inline tag assignment |

## References and Scoping

- LikeC4 uses **lexical scoping with hoisting** (similar to JavaScript)
- Nested elements create scopes; `it` and `this` refer to parent
- Use **fully qualified names** (FQN) for unambiguous references: `service1.backend.api`
- Parts of FQN can be omitted if unambiguous

## Specification - Custom Colors and Tags

```likec4
specification {
  // Element kinds with defaults
  element queue {
    title 'Kafka'
    technology 'kafka topic'
    style { shape queue }
  }

  // Relationship kinds
  relationship async {
    #tcp
    title 'Asynchronous'
    technology 'Kafka'
    color amber
    line dotted
  }

  // Tags
  tag deprecated { color gray }
  tag team2 { color #AABBCC }

  // Custom colors
  color custom-color1 #F00
  color custom-color2 rgba(255, 0, 0, 0.9)
}
```

## Metadata Example

```likec4
model {
  app = application {
    metadata {
      version '2.1.0'
      tags ['frontend', 'react']
      regions ['us-east-1', 'eu-west-1']
      critical true
    }
  }
}
```

## Icon Sources

| Prefix | Example | Description |
|--------|---------|-------------|
| `tech:` | `tech:nodejs`, `tech:react` | Technology icons |
| `aws:` | `aws:lambda`, `aws:s3` | AWS service icons |
| `azure:` | `azure:service` | Azure service icons |
| `gcp:` | `gcp:k8s` | Google Cloud icons |
| `bootstrap:` | `bootstrap:house` | Bootstrap icons |
| `md:` | `md:home` | Material Design icons |
| URL | `https://...` | Custom image URL |
