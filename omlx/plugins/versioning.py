from typing import Optional
from packaging.specifiers import SpecifierSet
from packaging.version import parse, InvalidVersion, Version
import re

class SemanticVersion:
    """
    Utility class for working with semantic versions and npm-like specifiers.
    """

    @staticmethod
    def parse_version(version_str: str) -> Version:
        """Parses a version string into a Version object."""
        try:
            return parse(version_str)
        except InvalidVersion:
            raise ValueError(f"Invalid version string: {version_str}")

    @staticmethod
    def _convert_npm_specifier(specifier: str) -> str:
        """
        Converts a single npm-like specifier (e.g., ^1.2.3 or ~1.2.3) to PEP 440 constraints.
        Returns the original specifier if it doesn't match the npm formats.
        """
        specifier = specifier.strip()

        # Handle caret (^) range: allows changes that do not modify the left-most non-zero digit
        caret_match = re.match(r'^\^(\d+)\.(\d+)(?:\.(\d+))?$', specifier)
        if caret_match:
            major, minor = caret_match.group(1), caret_match.group(2)
            patch = caret_match.group(3) or "0"
            if major == "0" and minor == "0":
                # ^0.0.x is exact match
                return f"~={major}.{minor}.{patch}"
            elif major == "0":
                # ^0.x.y -> >=0.x.y, <0.(x+1).0
                return f">={major}.{minor}.{patch}, <0.{int(minor)+1}.0"
            else:
                # ^x.y.z -> >=x.y.z, <(x+1).0.0
                return f">={major}.{minor}.{patch}, <{int(major)+1}.0.0"

        # Handle tilde (~) range: allows patch-level changes if minor is specified, else minor-level
        tilde_match = re.match(r'^~(\d+)(?:\.(\d+))?(?:\.(\d+))?$', specifier)
        if tilde_match:
            major = tilde_match.group(1)
            minor = tilde_match.group(2)
            patch = tilde_match.group(3)

            if minor is None:
                # ~1 -> >=1.0.0, <2.0.0
                return f">={major}.0.0, <{int(major)+1}.0.0"
            elif patch is None:
                # ~1.2 -> >=1.2.0, <1.3.0
                return f">={major}.{minor}.0, <{major}.{int(minor)+1}.0"
            else:
                # ~1.2.3 -> >=1.2.3, <1.3.0
                return f">={major}.{minor}.{patch}, <{major}.{int(minor)+1}.0"

        return specifier

    @staticmethod
    def parse_constraint(constraint_str: str) -> SpecifierSet:
        """
        Parses a version constraint string, converting npm-like formats if present,
        and returns a PEP 440 SpecifierSet.
        """
        # Split by comma for multiple constraints
        parts = [p.strip() for p in constraint_str.split(',')]

        converted_parts = []
        for part in parts:
            # Further split by space if there are spaces (e.g. ">=1.0.0 <2.0.0")
            sub_parts = part.split()
            for sub_part in sub_parts:
                 converted_parts.append(SemanticVersion._convert_npm_specifier(sub_part))

        # Re-join with commas for SpecifierSet
        final_constraint = ",".join(converted_parts)

        try:
            return SpecifierSet(final_constraint)
        except Exception as e:
             raise ValueError(f"Invalid constraint string '{constraint_str}' (parsed as '{final_constraint}'): {e}")

    @staticmethod
    def is_compatible(version_str: str, constraint_str: str) -> bool:
        """
        Checks if a given version satisfies a given constraint.
        """
        try:
            version = SemanticVersion.parse_version(version_str)
            constraints = SemanticVersion.parse_constraint(constraint_str)
            return version in constraints
        except ValueError:
            return False
