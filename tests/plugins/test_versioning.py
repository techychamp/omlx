import pytest
from packaging.version import Version
from omlx.plugins.versioning import SemanticVersion

def test_parse_version():
    v = SemanticVersion.parse_version("1.2.3")
    assert isinstance(v, Version)
    assert str(v) == "1.2.3"

    with pytest.raises(ValueError):
        SemanticVersion.parse_version("invalid")

def test_convert_npm_specifier():
    # Caret tests
    assert SemanticVersion._convert_npm_specifier("^1.2.3") == ">=1.2.3, <2.0.0"
    assert SemanticVersion._convert_npm_specifier("^0.2.3") == ">=0.2.3, <0.3.0"
    assert SemanticVersion._convert_npm_specifier("^0.0.3") == "~=0.0.3"
    assert SemanticVersion._convert_npm_specifier("^1.2") == ">=1.2.0, <2.0.0"

    # Tilde tests
    assert SemanticVersion._convert_npm_specifier("~1.2.3") == ">=1.2.3, <1.3.0"
    assert SemanticVersion._convert_npm_specifier("~1.2") == ">=1.2.0, <1.3.0"
    assert SemanticVersion._convert_npm_specifier("~1") == ">=1.0.0, <2.0.0"

    # Regular tests
    assert SemanticVersion._convert_npm_specifier(">=1.2.3") == ">=1.2.3"
    assert SemanticVersion._convert_npm_specifier("1.2.3") == "1.2.3"

def test_parse_constraint():
    spec = SemanticVersion.parse_constraint("^1.2.3")
    assert "2.0.0" not in spec
    assert "1.3.0" in spec

def test_is_compatible():
    assert SemanticVersion.is_compatible("1.5.0", "^1.2.3")
    assert not SemanticVersion.is_compatible("2.0.0", "^1.2.3")
    assert SemanticVersion.is_compatible("1.2.4", "~1.2.3")
    assert not SemanticVersion.is_compatible("1.3.0", "~1.2.3")
    assert SemanticVersion.is_compatible("2.0.0", ">=1.0.0, <3.0.0")
