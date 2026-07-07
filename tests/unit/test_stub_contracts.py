"""Curriculum contract tests: every unimplemented stub must raise NotImplementedError.

The from-scratch modules under ``src/`` are scaffolded as stubs that raise
``NotImplementedError`` until their curriculum week implements them. These tests encode
two invariants:

1. An unimplemented function fails loudly rather than silently returning wrong numbers
   (LINV-009 spirit — evidence before claims).
2. The moment a stub is implemented, its contract test here FAILS. The implementer must
   then add the callable's qualified name to ``IMPLEMENTED`` in
   ``src/curriculum_ledger.py``, write real unit tests for it, and add the module's
   companion notebook (LINV-010) — a built-in TDD nudge.

Graduated names are not skipped — their contract flips: they must NO LONGER raise
``NotImplementedError``, so a name cannot be parked in the ledger ahead of its
implementation. ``tools/check_notebooks.py`` imports the same ledger and additionally
demands the companion notebook and a dedicated test reference for every graduated name.

Coverage note: exercising every stub's ``raise`` line is what makes the >=90% coverage
gate meaningful pre-implementation — the gate then measures that *new real code* is
tested, because stub lines are already accounted for. Graduating a stub without real
tests would drop coverage, not maintain it.

Discovery-shape contract: the engine sees module-level functions and classes with
DIRECTLY-DEFINED methods/properties (including static/class methods). Curriculum stubs
must keep that shape — no inherited public methods, callable instances, or re-exported
wrappers. Anything outside the shape must be added to ``EXPECTED_SURFACE`` with an
explicit hand-written case, or the manifest test will not protect it.
"""

import importlib
import inspect
from pathlib import Path
from typing import Any, Callable, FrozenSet, List, Tuple

import numpy as np
import pandas as pd
import pytest

from src.curriculum_ledger import IMPLEMENTED

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

    def _property_invoker(property_name: str) -> Callable[[], Any]:
        def invoke() -> Any:
            instance = _call_with_dummies(cls)
            return getattr(instance, property_name)

        return invoke

    cases = []
    for method_name, member in vars(cls).items():
        if method_name.startswith("_"):
            continue
        qualified = f"{module_name}:{class_name}.{method_name}"
        if isinstance(member, property):
            cases.append((qualified, _property_invoker(method_name)))
        elif isinstance(member, (staticmethod, classmethod)) or inspect.isfunction(member):
            cases.append((qualified, _method_invoker(method_name)))
    return cases


CASES = _collect_cases()

# The pinned curriculum surface. Discovery must match this EXACTLY: a missed callable
# (renamed, re-exported, wrapped in a descriptor the engine cannot see) fails loudly
# instead of silently evading the contract. Adding or removing a public callable in a
# stub module is a deliberate act — update this manifest in the same commit.
EXPECTED_SURFACE: FrozenSet[str] = frozenset(
    {
        "src.data.acquisition:download_nass_yields",
        "src.data.acquisition:download_weather_data",
        "src.data.loader:get_data_summary",
        "src.data.loader:load_yield_data",
        "src.data.loader:validate_data",
        "src.metrics.classification:accuracy",
        "src.metrics.classification:auc",
        "src.metrics.classification:confusion_matrix",
        "src.metrics.classification:f1_score",
        "src.metrics.classification:precision",
        "src.metrics.classification:recall",
        "src.metrics.classification:roc_curve",
        "src.metrics.regression:adjusted_r_squared",
        "src.metrics.regression:mean_absolute_error",
        "src.metrics.regression:mean_squared_error",
        "src.metrics.regression:r_squared",
        "src.metrics.regression:root_mean_squared_error",
        "src.model_selection.cross_validation:cross_val_score",
        "src.model_selection.cross_validation:k_fold_split",
        "src.model_selection.cross_validation:train_test_split",
        "src.models.linear_regression:LinearRegression.fit",
        "src.models.linear_regression:LinearRegression.predict",
        "src.models.linear_regression:LinearRegression.score",
        "src.models.logistic_regression:LogisticRegression.fit",
        "src.models.logistic_regression:LogisticRegression.predict",
        "src.models.logistic_regression:LogisticRegression.predict_proba",
        "src.models.regularized:LassoRegression.fit",
        "src.models.regularized:LassoRegression.predict",
        "src.models.regularized:RidgeRegression.fit",
        "src.models.regularized:RidgeRegression.predict",
        "src.preprocessing.encoders:OneHotEncoder.fit",
        "src.preprocessing.encoders:OneHotEncoder.transform",
        "src.preprocessing.encoders:TargetEncoder.fit",
        "src.preprocessing.encoders:TargetEncoder.transform",
        "src.preprocessing.imputers:SimpleImputer.fit",
        "src.preprocessing.imputers:SimpleImputer.fit_transform",
        "src.preprocessing.imputers:SimpleImputer.transform",
        "src.preprocessing.imputers:calculate_mean_manual",
        "src.preprocessing.imputers:calculate_median_manual",
        "src.preprocessing.outliers:detect_outliers_iqr",
        "src.preprocessing.outliers:detect_outliers_zscore",
        "src.preprocessing.outliers:mahalanobis_distance",
        "src.preprocessing.scalers:MinMaxScaler.fit",
        "src.preprocessing.scalers:MinMaxScaler.transform",
        "src.preprocessing.scalers:StandardScaler.fit",
        "src.preprocessing.scalers:StandardScaler.inverse_transform",
        "src.preprocessing.scalers:StandardScaler.transform",
        "src.statistics.correlation:calculate_vif",
        "src.statistics.correlation:correlation_matrix",
        "src.statistics.correlation:pearson_correlation",
        "src.statistics.correlation:spearman_correlation",
        "src.statistics.descriptive:calculate_kurtosis",
        "src.statistics.descriptive:calculate_mean",
        "src.statistics.descriptive:calculate_skewness",
        "src.statistics.descriptive:calculate_std",
        "src.statistics.descriptive:calculate_variance",
        "src.statistics.descriptive:five_number_summary",
        "src.statistics.hypothesis_tests:calculate_p_value_from_t",
        "src.statistics.hypothesis_tests:chi_squared_test",
        "src.statistics.hypothesis_tests:welch_ttest",
        "src.statistics.hypothesis_tests:z_test_proportion",
        "src.utils.validation:check_array",
    }
)


def test_discovery_matches_pinned_surface_exactly() -> None:
    """Discovery must equal the pinned manifest — no silent misses, no silent growth."""
    discovered = {qualified_name for qualified_name, _ in CASES}
    missed = EXPECTED_SURFACE - discovered
    unexpected = discovered - EXPECTED_SURFACE
    assert not missed, f"discovery no longer sees: {sorted(missed)}"
    assert not unexpected, f"undocumented additions to the surface: {sorted(unexpected)}"


def test_implemented_ledger_names_are_discovered() -> None:
    """Every graduated name must match a discovered case (guards typos and stale entries).

    A name in ``IMPLEMENTED`` that discovery cannot see would silently exempt nothing —
    or worse, mask a misspelt graduation while the real stub stays contract-tested but
    unimplemented-looking to ``tools/check_notebooks.py``.
    """
    discovered = {qualified_name for qualified_name, _ in CASES}
    unknown = IMPLEMENTED - discovered
    assert not unknown, f"IMPLEMENTED contains names discovery cannot see: {sorted(unknown)}"


@pytest.mark.parametrize(("qualified_name", "invoke"), CASES, ids=[c[0] for c in CASES])
def test_stub_raises_not_implemented(qualified_name: str, invoke: Callable[[], Any]) -> None:
    """Ungraduated stubs must raise NotImplementedError; graduated names must not.

    The graduated branch tolerates other exceptions — a real implementation may
    legitimately reject this suite's dummy arguments; its behaviour is pinned by its own
    dedicated tests, whose existence ``tools/check_notebooks.py`` enforces.
    """
    if qualified_name in IMPLEMENTED:
        try:
            invoke()
        except NotImplementedError:
            pytest.fail(f"{qualified_name} is in IMPLEMENTED but still raises NotImplementedError")
        except Exception:
            pass
        return
    with pytest.raises(NotImplementedError):
        invoke()
