from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

import pya


@dataclass(frozen=True)
class InstanceRecord:
    ref_cell: str
    parent_cell: str
    path: str
    parent_path: str
    index_in_parent: int
    depth: int
    trans: str
    bbox: Tuple[int, int, int, int]
    cell_index: int
    parent_cell_index: int
    inst_pointer: Optional[int] = None
    index_path: Tuple[int, ...] = ()

    @property
    def label(self) -> str:
        return "{}[{}]".format(self.ref_cell, self.index_in_parent)


def _box_tuple(box: pya.Box) -> Tuple[int, int, int, int]:
    return (int(box.left), int(box.bottom), int(box.right), int(box.top))


def _safe_cell_name(layout: pya.Layout, cell_index: int) -> str:
    try:
        return layout.cell(cell_index).name
    except Exception:
        return "<cell:{}>".format(cell_index)


def _inst_target_cell_index(inst) -> int:
    try:
        return int(inst.cell_index)
    except Exception:
        pass
    try:
        return int(inst.cell.cell_index())
    except Exception:
        pass
    raise RuntimeError("Cannot determine instance target cell index")


def _inst_pointer(inst) -> Optional[int]:
    try:
        return int(inst.__hash__())
    except Exception:
        return None


def _inst_bbox(inst, parent_abs_trans: pya.Trans) -> Tuple[int, int, int, int]:
    try:
        return _box_tuple(inst.bbox().transformed(parent_abs_trans))
    except Exception:
        return (0, 0, 0, 0)


def _inst_trans(inst) -> str:
    try:
        return str(inst.trans)
    except Exception:
        try:
            return str(inst.cplx_trans)
        except Exception:
            return ""


def _iter_instances(cell: pya.Cell):
    for idx, inst in enumerate(cell.each_inst()):
        yield idx, inst


def collect_instances(
    layout: pya.Layout,
    top_cell: Optional[pya.Cell] = None,
    max_depth: Optional[int] = None,
    include_arrays: bool = True,
) -> List[InstanceRecord]:
    """Collect concrete instance records below *top_cell*.

    The traversal walks cell definitions recursively. It records instance
    objects in the parent cells where they are placed. Array instances are kept
    as one record by default because this mirrors how KLayout exposes them in
    the instance list.
    """

    if top_cell is None:
        top_cell = layout.top_cell()
    if top_cell is None:
        return []

    records: List[InstanceRecord] = []

    def visit(
        cell: pya.Cell,
        parent_path: str,
        depth: int,
        stack: Tuple[int, ...],
        parent_abs_trans: pya.Trans,
        parent_index_path: Tuple[int, ...],
    ):
        if max_depth is not None and depth > max_depth:
            return

        parent_name = cell.name
        parent_cell_index = int(cell.cell_index())

        for index_in_parent, inst in _iter_instances(cell):
            if not include_arrays:
                try:
                    if inst.is_regular_array():
                        continue
                except Exception:
                    pass

            try:
                child_index = _inst_target_cell_index(inst)
            except Exception:
                continue

            child_name = _safe_cell_name(layout, child_index)
            label = "{}[{}]".format(child_name, index_in_parent)
            path = label if not parent_path else parent_path + "/" + label
            index_path = parent_index_path + (index_in_parent,)
            records.append(
                InstanceRecord(
                    ref_cell=child_name,
                    parent_cell=parent_name,
                    path=path,
                    parent_path=parent_path,
                    index_in_parent=index_in_parent,
                    depth=depth,
                    trans=_inst_trans(inst),
                    bbox=_inst_bbox(inst, parent_abs_trans),
                    cell_index=child_index,
                    parent_cell_index=parent_cell_index,
                    inst_pointer=_inst_pointer(inst),
                    index_path=index_path,
                )
            )

            if child_index in stack:
                continue
            child_cell = layout.cell(child_index)
            if child_cell is not None:
                try:
                    child_abs_trans = parent_abs_trans * inst.trans
                except Exception:
                    child_abs_trans = parent_abs_trans
                visit(
                    child_cell,
                    path,
                    depth + 1,
                    stack + (child_index,),
                    child_abs_trans,
                    index_path,
                )

    visit(top_cell, "", 0, (int(top_cell.cell_index()),), pya.Trans(), ())
    return records


def grouped_by_reference(records: Iterable[InstanceRecord]) -> Dict[str, List[InstanceRecord]]:
    grouped: Dict[str, List[InstanceRecord]] = {}
    for record in records:
        grouped.setdefault(record.ref_cell, []).append(record)
    return dict(sorted(grouped.items(), key=lambda item: item[0].lower()))


def records_as_tsv(records: Iterable[InstanceRecord]) -> str:
    header = [
        "ref_cell",
        "parent_cell",
        "path",
        "index",
        "depth",
        "trans",
        "bbox_left",
        "bbox_bottom",
        "bbox_right",
        "bbox_top",
        "index_path",
    ]
    lines = ["\t".join(header)]
    for record in records:
        box = record.bbox
        lines.append(
            "\t".join(
                [
                    record.ref_cell,
                    record.parent_cell,
                    record.path,
                    str(record.index_in_parent),
                    str(record.depth),
                    record.trans,
                    str(box[0]),
                    str(box[1]),
                    str(box[2]),
                    str(box[3]),
                    "/".join(str(i) for i in record.index_path),
                ]
            )
        )
    return "\n".join(lines)
