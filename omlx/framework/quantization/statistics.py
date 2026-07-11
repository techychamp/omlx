# SPDX-License-Identifier: Apache-2.0
"""
Quantization Statistics.
"""

from typing import Dict, Any, List
from .descriptor import QuantizationDescriptor

class QuantizationStatistics:
    """
    Collects statistics on quantization usage.
    """

    def __init__(self):
        # We would typically aggregate these over many models
        pass

    def aggregate(self, descriptors: List[QuantizationDescriptor]) -> Dict[str, Any]:
        family_dist = {}
        precision_dist = {}

        for desc in descriptors:
             family = desc.quantization_family.value
             precision = desc.weight_precision

             family_dist[family] = family_dist.get(family, 0) + 1
             precision_dist[precision] = precision_dist.get(precision, 0) + 1

        return {
            "family_distribution": family_dist,
            "precision_distribution": precision_dist,
            "total_count": len(descriptors)
        }
