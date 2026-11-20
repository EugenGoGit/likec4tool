# LikeC4 Views and Filtering

## Three Kinds of Views

| Kind | Keyword | Description |
|------|---------|-------------|
| Element view | `view` | Elements + relationships, filtered by predicates |
| Dynamic view | `dynamic view` | Scenarios as ordered steps (diagram or sequence) |
| Deployment view | `deployment view` | Deployment nodes and instances |

## Basic View Definition

```likec4
views {
  view index {
    title 'Landscape'
    #overview
    description '''High-level diagram'''
    link https://jira/12 'Epic'
    routing ortho

    include *
  }

  // Scoped view
  view of saas {
    include *
  }

  // Extended view
  view view2 extends view1 {
    title 'More details'
    style * { color muted }
    include some.backend
  }
}
```

## Predicates (Filtering)

### Include Elements
```likec4
view {
  include backend, frontend, authService
  include messageBroker.*        // children
  include messageBroker.**       // descendants
  include customer -> cloud      // directed
  include customer <-> cloud     // any relationship
  include -> cloud.backend       // incoming
  include cloud.* ->             // outgoing
  include -> cloud.* ->          // in/out
}
```

### Exclude Elements
```likec4
view {
  include *
  exclude messageBroker.emailsQueue
}
```

### Filter with `where`
```likec4
view {
  include cloud.*
    where kind is microservice
    and tag is not #deprecated
    and metadata.environment is "production"
}
```

### Override Properties in View
```likec4
view {
  include cloud.backend with {
    title 'Backend components'
    color amber
    shape browser
  }
}
```

## Global Predicate Groups

```likec4
global {
  predicateGroup microservices {
    include cloud.*
      where kind is microservice
    exclude *
      where tag is #deprecated
  }
}

views {
  view of newServices {
    include cloud.new.*
    global predicate microservices
  }
}
```

## Groups (Boundaries)

```likec4
view {
  group 'Frontend' {
    color amber
    opacity 20%
    border solid
    include frontend.*
  }
}
```

## Styles

### Style Properties for Elements

| Property | Values |
|----------|--------|
| `shape` | `rectangle`, `component`, `storage`, `cylinder`, `browser`, `mobile`, `person`, `queue`, `bucket`, `document`, `agent` |
| `color` | `primary`, `secondary`, `muted`, `amber`, `blue`, `gray`, `green`, `indigo`, `red`, `sky`, `slate`, or custom `#FF6B6B` |
| `size` | `xsmall`, `small`, `medium`, `large`, `xlarge` |
| `textSize` | same values |
| `sizing` | `auto` (default), `fixed` |
| `opacity` | percentage |
| `border` | `dashed`, `dotted`, `solid`, `none` |
| `multiple` | `true` / `false` |
| `icon` | `tech:nodejs`, `aws:lambda`, `azure:service`, `gcp:k8s`, `bootstrap:house`, `md:home`, or URL |
| `iconColor` | theme color name |
| `iconSize` | same as size |
| `iconPosition` | `left`, `right`, `top`, `bottom` |

### Style Properties for Relationships

| Property | Values |
|----------|--------|
| `line` | `dashed`, `solid`, `dotted` |
| `head` | `normal`, `onormal`, `diamond`, `odiamond`, `crow`, `vee`, `open`, `none` |
| `tail` | same as head |
| `color` | theme color |
| `multiple` | `true` / `false` |

### Style Predicates in Views
```likec4
view apiApp {
  include *
  style * { color muted; opacity 10% }
  style singlePageApplication, mobileApp { color secondary; size xlarge }
  style element.tag = #deprecated { color muted }
}
```

### Shared Styles

**Local** (within `views` block):
```likec4
views {
  style * { color muted }
  view of apiApp { ... }
}
```

**Global** (in `global` block):
```likec4
global {
  style mute_all * { color muted; opacity 10% }
  styleGroup common_styles {
    style element.tag = #deprecated { color muted }
  }
}

views {
  view of app {
    global style mute_all
    global style common_styles
  }
}
```

## Layout

```likec4
view {
  autoLayout LeftRight 120 110 ortho
  // or
  routing ortho

  rank same { api1, api2 }
  rank source { customer }
  rank sink { analytics }
}
```

Direction: `TopBottom` (default), `BottomTop`, `LeftRight`, `RightLeft`

## Notation

```likec4
// Global (in specification)
element customer {
  notation "Person, Customer"
  style { shape person; color green }
}

// Local (in view)
view {
  style element.tag = #deprecated {
    notation "Deprecated"
    color muted
  }
}
```
