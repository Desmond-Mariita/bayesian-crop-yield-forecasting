"""Curriculum contract tests: every unimplemented stub must raise NotImplementedError.

The from-scratch modules under ``src/`` are scaffolded as stubs that raise
``NotImplementedError`` until their curriculum week implements them. These tests encode
two invariants:

1. An unimplemented function fails loudly rather than silently returning wrong numbers
   (LINV-009 spirit — evidence before claims).
2. The moment a stub is implemented, its contract test here FAILS. The implementer must
   then move the callable's qualified name into ``IMPLEMENTED`` and write real unit
   tests for it — a built-in TDD nudge.
"""

import importlib
import inspect
from pathlib import Path
from typing import Any, Callable, List, Tuple

import numpy as np
import pandas as pd
import pytest

# Qualified names ("module:Callable" or "module:Class.method") that have graduated from
# stub to implementation. Names here are skipped by the contract and MUST have real unit
# tests of their own.
IMPLEMENTED: frozenset = frozenset()

STUB_MODULES: Tuple[str, ...] = (
    "src.data.acquisition",
    "src.data.loader",
    "src.metrics.classification",
    "src.metrics.regression",
    "src.models.linear_regression",
    "src.models.logistic_regression",
    "src.models.regularized",
    "src.model_selection.cross_validation",
    "src.preprocessing.encoders",
    "src.preprocessing.imputers",
    "src.preprocessing.outliers",
    "src.preprocessing.scalers",
    "src.statistics.correlation",
    "src.statistics.descriptive",
    "src.statistics.hypothesis_tests",
    "src.utils.validation",
)

VECTOR = np.array([1.0, 2.0, 3.0, 4.0])
MATRIX = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])


def _dummy_value(name: str, annotation: str) -> Any:
    """Build a plausible dummy argument for a stub parameter.

    Stubs raise before using their arguments, so values only need to satisfy the call,
    not the semantics.

    Args:
        name: Parameter name.
        annotation: String form of the parameter annotation.

    Returns:
        A dummy value matching the annotated type as closely as possible.
    """
    if "DataFrame" in annotation:
        return pd.DataFrame({"county": ["a"], "year": [2020], "yield": [2.0]})
    if "Path" in annotation or name.endswith("path") or name.endswith("_dir"):
        return Path("data/raw/dummy.csv")
    if "ndarray" in annotation:
        return MATRIX if name.startswith("X") else VECTOR
    if "float" in annotation:
        return 0.5
    if "int" in annotation:
        return 2
    if "bool" in annotation:
        return False
    if "str" in annotation:
        return "dummy"
    return VECTOR


def _call_with_dummies(func: Callable[..., Any]) -> Any:
    """Call a callable with dummy values for every required parameter.

    Args:
        func: Function, method, or class to invoke.

    Returns:
        Whatever the callable returns (generators are fully consumed so that stub
        generator functions execute their bodies).
    """
    signature = inspect.signature(func)
    kwargs = {}
    for name, parameter in signature.parameters.items():
        if parameter.default is not inspect.Parameter.empty:
            continue
        if parameter.kind in (parameter.VAR_POSITIONAL, parameter.VAR_KEYWORD):
            continue
        kwargs[name] = _dummy_value(name, str(parameter.annotation))
    result = func(**kwargs)
    if inspect.isgenerator(result):
        return list(result)
    return result


def _collect_cases() -> List[Tuple[str, Callable[[], Any]]]:
    """Discover every public stub callable across the curriculum modules.

    Returns:
        ``(qualified_name, invoker)`` pairs; each invoker performs one stub call.
    """
    cases: List[Tuple[str, Callable[[], Any]]] = []
    for module_name in STUB_MODULES:
        module = importlib.import_module(module_name)
        for attr_name, obj in vars(module).items():
            if attr_name.startswith("_") or getattr(obj, "__module__", None) != module_name:
                continue
            if inspect.isfunction(obj):
                cases.append((f"{module_name}:{attr_name}", _function_invoker(obj)))
            elif inspect.isclass(obj):
                cases.extend(_class_cases(module_name, attr_name, obj))
    return cases


def _function_invoker(func: Callable[..., Any]) -> Callable[[], Any]:
    """Wrap a module-level function into a zero-argument invoker.

    Args:
        func: Function to wrap.

    Returns:
        A thunk that calls the function with dummy arguments.
    """
    return lambda: _call_with_dummies(func)


def _class_cases(
    module_name: str, class_name: str, cls: type
) -> List[Tuple[str, Callable[[], Any]]]:
    """Build one contract case per public method of a stub class.

    Instantiation happens inside each invoker: if ``__init__`` itself is the stub, the
    case still observes the expected ``NotImplementedError``.

    Args:
        module_name: Module the class is defined in.
        class_name: Class name.
        cls: The class object.

    Returns:
        ``(qualified_name, invoker)`` pairs for every public method.
    """

    def _method_invoker(method_name: str) -> Callable[[], Any]:
        def invoke() -> Any:
            instance = _call_with_dummies(cls)
            return _call_with_dummies(getattr(instance, method_name))

        return invoke

    cases = []
    for method_name, member in vars(cls).items():
        if method_name.startswith("_") or not inspect.isfunction(member):
            continue
        cases.append((f"{module_name}:{class_name}.{method_name}", _method_invoker(method_name)))
    return cases


CASES = _collect_cases()


def test_discovery_finds_the_curriculum_surface() -> None:
    """The scaffold's public API is discovered (guards against silent misdiscovery)."""
    assert len(CASES) >= 40


@pytest.mark.parametrize(("qualified_name", "invoke"), CASES, ids=[c[0] for c in CASES])
def test_stub_raises_not_implemented(qualified_name: str, invoke: Callable[[], Any]) -> None:
    """Every unimplemented stub raises NotImplementedError when called."""
    if qualified_name in IMPLEMENTED:
        pytest.skip("implemented — covered by its own unit tests")
    with pytest.raises(NotImplementedError):
        invoke()
