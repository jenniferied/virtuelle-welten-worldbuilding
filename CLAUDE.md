# ПАНЕЛЬКИ / Virtuelle Welten Worldbuilding

## What This Is
Master Medienproduktion project for "Virtuelle Welten" course at TH OWL. A worldbuilding bible and process documentation for a 30-second cinematic set in Soviet-inspired eternal winter, using Houdini, OSM data, and ALOS DEM terrain.

## Build Commands
```bash
make worldbuilding   # Build worldbuilding bible PDF
make gdd            # Build game design document PDF
make all            # Build both documents
make clean          # Remove build artifacts
```

## Worldbuilding Agents
| Agent | Purpose | Invocation |
|-------|---------|------------|
| `panelki` | Orchestrator — interviews, suggests, spawns workers | "Use panelki agent" |
| `worldbuild-analyst` | Framework analysis (Zaidi/Wolf) | Spawned by panelki or direct |
| `faction-developer` | Faction/character development | Spawned by panelki or direct |
| `lore-checker` | Consistency verification (Tolkien) | Auto-delegated or direct |
| `location-designer` | Environmental storytelling (Jenkins) | Spawned by panelki or direct |

## Framework Skills (preloaded into agents)
| Skill | Source | Used by |
|-------|--------|---------|
| `zaidi-foundations` | Zaidi 2019 | worldbuild-analyst, faction-developer, panelki |
| `wolf-subcreation` | Wolf 2012 | worldbuild-analyst |
| `jenkins-environmental` | Jenkins 2004 | location-designer |
| `tolkien-belief` | Tolkien/Brierly | lore-checker |
| `panelki-world-rules` | 04-die-welt.md | all agents |

## Document Skills
| Skill | Trigger | Purpose |
|-------|---------|---------|
| `/layout` | Image overflow, white space, column issues | Fix PDF layout problems |
| `/content-review` | Missing text, incomplete sections | Check content completeness |
| `/build` | PDF errors, visual regression | Build and test workflow |
| `/houdini` | Asset docs, screenshots | Houdini project management |

## Guardrails
- **Language**: Document content in German, code/config in English
- **Build often**: Test PDF after changes, catch layout issues early
- **Images**: Use `width=\columnwidth`, never fixed sizes
- **Large files**: YugoKoral55.blend/fbx use Git LFS (>100MB)

## When To Read More
- **Layout fixes**: `.claude/skills/layout/skill.md` · **Content**: `.claude/skills/content-review/skill.md`
- **Build pipeline**: `.claude/skills/build-test/skill.md` · **Quality**: `.claude/rules/quality-standards.md`
