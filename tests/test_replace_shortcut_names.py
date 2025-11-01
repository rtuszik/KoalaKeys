"""Tests for the replace_shortcut_names function."""

import pytest

from generate_cheatsheet import replace_shortcut_names


def test_three_keys():
    """Test Ctrl+Shift+A -> Ctrl<sep>Shift<sep>A"""
    result = replace_shortcut_names("Ctrl+Shift+A", {})
    expected = "Ctrl<sep>Shift<sep>A"
    assert result == expected


def test_plus_key():
    """Test Ctrl++ -> Ctrl<sep>+"""
    result = replace_shortcut_names("Ctrl++", {})
    expected = "Ctrl<sep>+"
    assert result == expected


def test_angle_bracket():
    """Test CTRL+> -> CTRL<sep>>"""
    result = replace_shortcut_names("CTRL+>", {})
    expected = "CTRL<sep>>"
    assert result == expected


def test_simple_chord():
    """Test Super+T>W>S -> Super<sep>T<seq>W<seq>S"""
    result = replace_shortcut_names("Super+T>W>S", {})
    expected = "Super<sep>T<seq>W<seq>S"
    assert result == expected


def test_composed_chord():
    """Test CTRL+C>CTRL+K -> CTRL<sep>C<seq>CTRL<sep>K"""
    result = replace_shortcut_names("CTRL+C>CTRL+K", {})
    expected = "CTRL<sep>C<seq>CTRL<sep>K"
    assert result == expected


def test_angle_bracket_in_chord():
    """Test CTRL>> -> CTRL<seq>>"""
    result = replace_shortcut_names("CTRL>>", {})
    expected = "CTRL<seq>>"
    assert result == expected


def test_plus_key_in_chord():
    """Test CTRL>+ -> CTRL<seq>+"""
    result = replace_shortcut_names("CTRL>+", {})
    expected = "CTRL<seq>+"
    assert result == expected


def test_spaces():
    assert replace_shortcut_names("Ctrl + C", {}) == "Ctrl<sep>C"
    assert replace_shortcut_names("Ctrl + Shift + A", {}) == "Ctrl<sep>Shift<sep>A"
    assert replace_shortcut_names("Ctrl + +", {}) == "Ctrl<sep>+"
    assert replace_shortcut_names("CTRL + >", {}) == "CTRL<sep>>"
    assert replace_shortcut_names("Super + T > W > S", {}) == "Super<sep>T<seq>W<seq>S"
    assert replace_shortcut_names("CTRL + C > CTRL + K", {}) == "CTRL<sep>C<seq>CTRL<sep>K"
    assert replace_shortcut_names("CTRL > >", {}) == "CTRL<seq>>"
    assert replace_shortcut_names("CTRL > +", {}) == "CTRL<seq>+"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
