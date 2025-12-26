# Tech Deck

## Entwicklungsumgebung

### Hardware-Übersicht

::: {.columns}

:::: {.column width="45%"}
**Mac Workstation**

- MacBook Pro M Max
- 64 GB RAM
- macOS
::::

:::: {.column width="10%"}
::::

:::: {.column width="45%"}
**PC Workstation**

- Intel Core i9-13900K
- NVIDIA GeForce RTX 3090
- 64 GB RAM
- Windows 11
::::

:::

### Software-Stack

| Software | Version | Zweck |
|----------|---------|-------|
| Unreal Engine | 5.5+ | Game Engine |
| Houdini | --- | Procedural Content |
| Houdini Engine | --- | Houdini-Unreal Integration |
| Perforce Helix Core | --- | Versionskontrolle |

### Infrastruktur-Diagramm

```
┌─────────────────────┐                              ┌─────────────────────┐
│   MAC WORKSTATION   │                              │   PC WORKSTATION    │
│                     │                              │                     │
│  MacBook Pro M Max  │                              │  Intel i9-13900K    │
│  64 GB RAM          │                              │  RTX 3090           │
│                     │                              │  64 GB RAM          │
│  ┌───────────────┐  │                              │  ┌───────────────┐  │
│  │ Unreal 5.5+   │◄─┼──────┐                ┌─────►┼──│ Unreal 5.5+   │  │
│  └───────────────┘  │      │                │      │  └───────────────┘  │
│  ┌───────────────┐  │      │                │      │  ┌───────────────┐  │
│  │ Houdini Engine│──┼──────┘                └──────┼──│ Houdini Engine│  │
│  └───────────────┘  │                              │  └───────────────┘  │
│  ┌───────────────┐  │                              │  ┌───────────────┐  │
│  │ Houdini       │  │                              │  │ Houdini       │  │
│  └───────────────┘  │                              │  └───────────────┘  │
│  ┌───────────────┐  │                              │  ┌───────────────┐  │
│  │ P4V Client    │  │                              │  │ P4V Client    │  │
│  └───────────────┘  │                              │  └───────────────┘  │
│                     │                              │                     │
└──────────┬──────────┘                              └──────────┬──────────┘
           │                                                    │
           │              ┌─────────────────────┐               │
           │              │   DIGITAL OCEAN     │               │
           │              │                     │               │
           └──────────────┤  Perforce Server    ├───────────────┘
                          │  (Helix Core)       │
                          │                     │
                          │  ┌───────────────┐  │
                          │  │ Depot         │  │
                          │  │ - //depot/... │  │
                          │  └───────────────┘  │
                          │                     │
                          └─────────────────────┘
```

### Workflow

1. **Entwicklung** erfolgt auf beiden Workstations parallel
2. **Assets** werden via Perforce synchronisiert
3. **Große Binärdateien** (Texturen, Meshes) nutzen Perforce-Locking
4. **Houdini Digital Assets** werden zentral versioniert
