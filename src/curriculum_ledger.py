"""Curriculum graduation ledger — the single source of truth for implemented stubs.

Qualified names ("module:Callable" or "module:Class.method", e.g.
``src.statistics.descriptive:calculate_mean``) of curriculum callables that have
graduated from stub to real implementation.

Graduating a name here has mechanical consequences, enforced by CI:

* ``tests/unit/test_stub_contracts.py`` flips that name's contract from
  "must raise NotImplementedError" to "must NOT raise NotImplementedError".
* ``tools/check_notebooks.py`` demands the module's companion notebook at the mirrored
  ``notebooks/`` path (LINV-010) and a dedicated test reference outside the contract
  suites for the graduated callable.

Both consumers import this module directly — keep it dependency-free.
"""

from __future__ import annotations

from typing import FrozenSet

IMPLEMENTED: FrozenSet[str] = frozenset(
    {
        "src.data.acquisition:download_nass_yields",  # Week 1, 2026-07-07
    }
)
