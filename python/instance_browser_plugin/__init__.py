from .instance_browser_core import InstanceRecord, collect_instances, grouped_by_reference

__all__ = ["InstanceRecord", "collect_instances", "grouped_by_reference"]

from .instance_browser_gui import show_instance_browser, hide_instance_browser, instance_browser_visible
