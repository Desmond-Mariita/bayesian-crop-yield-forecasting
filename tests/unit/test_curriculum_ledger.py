"""Unit tests for the graduation ledger (src/curriculum_ledger.py).

Closes guidelines self-audit deviation 3: beyond the contract suite's cross-checks,
this pins the ledger's own integrity — every entry must be a well-formed qualified
name that resolves to a real, callable object.
"""

import importlib

from src.curriculum_ledger import IMPLEMENTED


def test_ledger_is_a_frozenset_of_strings() -> None:
    """The ledger type contract both consumers rely on."""
    assert isinstance(IMPLEMENTED, frozenset)
    assert all(isinstance(name, str) for name in IMPLEMENTED)


def test_every_entry_is_well_formed() -> None:
    """Entries are 'src.<module>:<Callable>' or 'src.<module>:<Class>.<method>'."""
    for name in IMPLEMENTED:
        module_part, separator, callable_part = name.partition(":")
        assert separator == ":", f"missing ':' in {name!r}"
        assert module_part.startswith("src."), f"{name!r} must live under src."
        assert callable_part, f"{name!r} names no callable"
        assert callable_part.count(".") <= 1, f"{name!r} nests deeper than Class.method"


def test_every_entry_resolves_to_a_real_callable() -> None:
    """A graduated name must point at something that actually exists and is callable."""
    for name in sorted(IMPLEMENTED):
        module_part, _, callable_part = name.partition(":")
        obj = importlib.import_module(module_part)
        for attribute in callable_part.split("."):
            obj = getattr(obj, attribute)
        assert callable(obj), f"{name!r} resolves to a non-callable"
