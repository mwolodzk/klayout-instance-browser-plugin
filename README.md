# Instance Browser Plugin

KLayout Salt package that adds an instance-oriented browser for hierarchical
layouts. The goal is to complement the built-in `Cells` panel: instead of
showing only cell definitions, this tool lists concrete cell instances grouped
by the referenced child cell.

This is useful in analog layout work where many objects share the same source
cell, for example PMOS/NMOS device cells, common-centroid helper cells, guard
ring blocks, or generated device primitives.

## GUI

The GUI macro opens an `Instance Browser` dock from:

```text
Tools -> Instance Browser
View -> Instances
```

Default shortcut:

```text
Ctrl+Alt+I
```

The dock provides:

- grouping by referenced cell,
- filtering by cell name, parent cell, or hierarchy path,
- instance path display,
- select and zoom actions,
- multi-selection with `Shift` and `Ctrl`,
- double-click `Select + Zoom`.

## Usage

1. Open a hierarchical layout.
2. Run `Tools -> Instance Browser`, `View -> Instances`, or press `Ctrl+Alt+I`.
3. Use the filter field to narrow the instance list.
4. Expand a referenced-cell group.
5. Select one or more instance rows.
6. Use `Select`, `Zoom`, or `Select + Zoom`.

The tree supports normal Qt multi-selection behavior:

- click: select one row,
- `Shift + click`: select a range,
- `Ctrl + click`: add or remove individual rows.

Group header rows are informational. The actions operate only on actual
instance rows.

## Actions

### Select

Reconstructs the KLayout `ObjectInstPath` for each selected instance and
assigns the resulting list to `LayoutView.object_selection`.

### Zoom

Computes one combined bounding box for all selected instance records and calls
`LayoutView.zoom_box(...)`.

### Select + Zoom

Runs `Select`, then `Zoom`.

### Double Click

Double-clicking an instance row runs `Select + Zoom`. If multiple rows are
already selected, the action is applied to the current multi-selection.

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

## Notes and Limitations

- The plugin lists KLayout instances. If a GDS/OASIS file was flattened before
  writing, the browser has no instances to show.
- Instance labels are generated from the referenced cell name and the local
  instance index, for example `SG13_devpmos[2]`.
- Hierarchical labels include the full path, for example
  `input_common_centroid_BL[0]/SG13_devpmos[2]`.
- The plugin currently operates on instance rows only. It does not list shapes
  inside flattened cells.
- Bounding boxes are reported in database units internally and converted to
  micrometers for zoom operations through the active layout DBU.

## Installation

### From Salt.Mine

Install `Instance Browser Plugin` from Salt.Mine when the package is available
in the KLayout package manager.

### Manual

Copy this repository into your KLayout Salt directory so that `grain.xml` sits
at the package root:

```text
~/.klayout/salt/InstanceBrowserPlugin/
```

In an IHP flow with a dedicated KLayout configuration directory this may be:

```text
/foss/designs/.klayout-ihp/salt/InstanceBrowserPlugin/
```

Restart KLayout, or reload macros from `Macros -> Macro Development`.

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
