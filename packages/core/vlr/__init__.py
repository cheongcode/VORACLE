"""
VLR.gg API Integration

Provides access to live VALORANT esports data from vlr.gg.
"""

from .client import VlrClient, fetch_vlr_data

__all__ = ["VlrClient", "fetch_vlr_data"]
