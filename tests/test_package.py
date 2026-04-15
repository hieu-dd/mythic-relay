"""Tests for mythic_relay package."""


def test_package_import() -> None:
    """Verify package can be imported."""
    import mythic_relay

    assert mythic_relay.__name__ == "mythic_relay"


def test_version() -> None:
    """Verify version is defined."""
    from mythic_relay import __version__

    assert __version__ == "0.1.0"