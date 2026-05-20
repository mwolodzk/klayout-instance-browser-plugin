# Instance Browser Plugin

KLayout Salt package that adds an instance-oriented browser for hierarchical
layouts. The goal is to complement the built-in `Cells` panel: instead of
showing only cell definitions, this tool lists concrete cell instances grouped
by the referenced child cell.

This is useful in analog layout work where many objects share the same source
cell, for example PMOS/NMOS device cells, common-centroid helper cells, guard
ring blocks, or generated device primitives.

## Planned GUI

The GUI macro opens an `Instance Browser` dock from:

```text
Tools -> Instance Browser
```

The dock is intended to provide:

- grouping by referenced cell,
- filtering by cell name, parent cell, or hierarchy path,
- instance path display,
- select and zoom actions for the selected instance.

## Headless Core

The first implementation separates hierarchy scanning from the GUI. The core
collector can be run in KLayout batch mode and returns deterministic instance
records with:

- referenced cell name,
- parent cell name,
- hierarchy path,
- local instance index inside the parent,
- transformation,
- bounding box in database units,
- hierarchy depth.

This makes the behavior testable without opening a graphical KLayout session.

## Package Files

- `grain.xml`: Salt package metadata.
- `python/instance_browser_plugin/instance_browser_core.py`: testable
  instance collection logic.
- `pymacros/instance_browser.lym`: KLayout GUI entry point.

## Authorship

Author: Michał Wołodźko

Implementation and documentation assistance: OpenAI Codex coding agent.
Project attribution requested by the maintainer: `gpt-5.5 medium thinking`.

## License

MIT
