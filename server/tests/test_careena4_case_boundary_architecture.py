import ast
from pathlib import Path


CASE_PACKAGE_DIR = Path(__file__).resolve().parents[1] / "careena4" / "domain" / "case"
CAREENA4_DIR = CASE_PACKAGE_DIR.parents[1]
INTERNAL_CASE_MODULES = {
    "careena4.domain.case._case_reader",
    "careena4.domain.case._case_writer",
    "careena4.domain.case._case_write_planner",
}
NON_PUBLIC_CASE_EXPORTS = {
    "CaseReader",
    "CaseWriter",
    "CaseWritePlanner",
}


def test_internal_case_modules_are_not_imported_outside_case_package() -> None:
    """
    Guard the case boundary by ensuring that productive code imports only
    the public CaseManager API and not the internal reader, writer, or planner.
    """
    violations: list[str] = []

    for path in CAREENA4_DIR.rglob("*.py"):
        if path.is_relative_to(CASE_PACKAGE_DIR):
            continue
        module = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))

        for node in ast.walk(module):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in INTERNAL_CASE_MODULES:
                        violations.append(f"{path}: import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module in INTERNAL_CASE_MODULES:
                    violations.append(f"{path}: from {node.module} import ...")
                if node.module == "careena4.domain.case":
                    for alias in node.names:
                        if alias.name in NON_PUBLIC_CASE_EXPORTS:
                            violations.append(
                                f"{path}: from careena4.domain.case import {alias.name}"
                            )

    assert not violations, "Direct imports of internal case boundary modules found:\n" + "\n".join(violations)
