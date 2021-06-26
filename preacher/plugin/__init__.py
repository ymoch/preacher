from pluggy.hooks import HookimplMarker

__all__ = ["hookimpl"]

hookimpl = HookimplMarker("preacher")
"""Marker to be imported and used in plugins (and for own implementations)"""
