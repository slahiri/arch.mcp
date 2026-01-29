"""MCP Tools for architecture validation"""

import fnmatch
import os
import re

# Static fallbacks
from .rules import ALL_RULES, RULES
from .structures import STRUCTURES

# Check if DB is configured
USE_DB = bool(os.environ.get("DATABASE_URL"))


def _get_all_rules() -> list[dict]:
    """Get all rules from DB or static fallback."""
    if USE_DB:
        from .db import fetch_rules
        rules = fetch_rules()
        if rules:
            return rules
    return ALL_RULES


def _get_rules_by_category() -> dict[str, list[dict]]:
    """Get rules grouped by category."""
    if USE_DB:
        from .db import fetch_rules, get_categories
        categories = get_categories()
        if categories:
            return {cat: fetch_rules(category=cat) for cat in categories}
    return RULES


def _get_structures() -> dict[str, dict]:
    """Get structures from DB or static fallback."""
    if USE_DB:
        from .db import fetch_structures
        structures = fetch_structures()
        if structures:
            return structures
    return STRUCTURES


def list_rules(category: str | None = None, severity: str | None = None) -> dict:
    """List Python API architecture rules."""
    if USE_DB:
        from .db import fetch_rules, get_categories
        rules = fetch_rules(category, severity)
        categories = get_categories() or list(RULES.keys())
    else:
        rules = ALL_RULES
        if category:
            rules = [r for r in rules if r.get("category") == category.lower()]
        if severity:
            rules = [r for r in rules if r.get("severity") == severity.lower()]
        categories = list(RULES.keys())

    return {
        "rules": [
            {
                "id": r["id"],
                "name": r["name"],
                "severity": r.get("severity", "info"),
                "category": r["category"],
                "description": r.get("description", r.get("message", "")),
            }
            for r in rules
        ],
        "total": len(rules),
        "categories": categories,
    }


def get_rule(rule_id: str) -> dict:
    """Get full details of a rule including code examples."""
    if USE_DB:
        from .db import fetch_rule
        rule = fetch_rule(rule_id)
    else:
        rule = next((r for r in ALL_RULES if r["id"] == rule_id), None)

    if not rule:
        return {"error": f"Rule '{rule_id}' not found"}
    return {"rule": rule}


def validate_code(content: str, file_path: str) -> dict:
    """Validate Python code against architecture rules."""
    if not file_path.endswith(".py"):
        return {"valid": True, "violations": [], "message": "Not a Python file"}

    violations = []
    all_rules = _get_all_rules()

    for rule in all_rules:
        pattern = rule.get("pattern")
        if not pattern:
            continue

        applies_to = rule.get("applies_to", ["**/*.py"])
        exclude = rule.get("exclude", [])

        # Handle JSONB fields from DB
        if isinstance(applies_to, str):
            applies_to = [applies_to]
        if isinstance(exclude, str):
            exclude = [exclude]

        applies = any(fnmatch.fnmatch(file_path, p) for p in applies_to)
        excluded = any(fnmatch.fnmatch(file_path, p) for p in exclude)

        if not applies or excluded:
            continue

        for line_num, line in enumerate(content.split("\n"), 1):
            try:
                for match in re.finditer(pattern, line, re.IGNORECASE):
                    violations.append({
                        "rule_id": rule["id"],
                        "rule_name": rule["name"],
                        "severity": rule.get("severity", "warning"),
                        "category": rule["category"],
                        "line": line_num,
                        "column": match.start() + 1,
                        "match": match.group(0)[:50],
                        "message": rule.get("message", rule.get("description", "")),
                        "fix": rule.get("fix"),
                    })
            except re.error:
                continue

    errors = sum(1 for v in violations if v["severity"] == "error")
    warnings = sum(1 for v in violations if v["severity"] == "warning")

    return {
        "file_path": file_path,
        "valid": errors == 0,
        "violations": violations,
        "summary": {"errors": errors, "warnings": warnings},
    }


def get_project_structure(pattern: str = "clean-architecture") -> dict:
    """Get recommended Python API project structure."""
    structures = _get_structures()
    if pattern not in structures:
        return {"error": f"Unknown pattern '{pattern}'", "available": list(structures.keys())}
    return {"pattern": pattern, **structures[pattern]}


def get_best_practices(category: str) -> dict:
    """Get best practices for a category with code examples."""
    rules_by_cat = _get_rules_by_category()
    if category not in rules_by_cat:
        return {"error": f"Unknown category '{category}'", "categories": list(rules_by_cat.keys())}

    practices = [r for r in rules_by_cat[category] if r.get("best_practice") or r.get("example")]
    return {"category": category, "best_practices": practices, "total": len(practices)}


def check_architecture(files: list[dict], pattern: str = "clean-architecture") -> dict:
    """Check if a codebase follows the architecture pattern consistently."""
    issues = []
    structures = _get_structures()
    structure = structures.get(pattern, {})
    layers = structure.get("layers", {})

    for file in files:
        path = file.get("path", "")
        content = file.get("content", "")

        # Determine current layer
        current_layer = None
        for layer in layers:
            in_layer = (
                f"/{layer}/" in path
                or path.startswith(f"{layer}/")
                or path.startswith(f"src/{layer}/")
            )
            if in_layer:
                current_layer = layer
                break

        if current_layer:
            layer_rules = layers.get(current_layer, {})
            cannot_import = layer_rules.get("cannot_import", [])

            import_pattern = r"from\s+(\S+)\s+import|import\s+(\S+)"
            for line_num, line in enumerate(content.split("\n"), 1):
                for match in re.finditer(import_pattern, line):
                    imported = match.group(1) or match.group(2)
                    for forbidden in cannot_import:
                        if forbidden in imported:
                            msg = f"Layer '{current_layer}' cannot import from '{forbidden}'"
                            issues.append({
                                "type": "layer-violation",
                                "severity": "error",
                                "file": path,
                                "line": line_num,
                                "message": msg,
                                "import": imported,
                            })

        # Code violations
        for v in validate_code(content, path).get("violations", []):
            issues.append({
                "type": "code-violation",
                "severity": v["severity"],
                "file": path,
                "line": v["line"],
                "message": v["message"],
                "rule_id": v["rule_id"],
            })

    errors = sum(1 for i in issues if i["severity"] == "error")
    warnings = sum(1 for i in issues if i["severity"] == "warning")

    return {
        "pattern": pattern,
        "files_checked": len(files),
        "consistent": errors == 0,
        "issues": issues,
        "summary": {"errors": errors, "warnings": warnings},
    }


def get_architecture_guide() -> dict:
    """Get a complete guide for building consistent Python APIs."""
    rules_by_cat = _get_rules_by_category()
    return {
        "overview": "Architecture guide for Python APIs with FastAPI",
        "recommended_pattern": "clean-architecture",
        "layers": {
            "api": {
                "purpose": "HTTP layer - request handling, validation, routing",
                "rules": ["Use Pydantic schemas", "No business logic", "No direct DB access"],
            },
            "application": {
                "purpose": "Business logic and use cases",
                "rules": ["Orchestrate domain logic", "Define interfaces", "No HTTP concerns"],
            },
            "domain": {
                "purpose": "Core business entities and rules",
                "rules": ["NO external dependencies", "Pure Python only", "Framework agnostic"],
            },
            "infrastructure": {
                "purpose": "External concerns - database, APIs",
                "rules": ["Implement interfaces", "SQLAlchemy models here"],
            },
            "core": {
                "purpose": "Configuration and cross-cutting",
                "rules": ["Can be imported by any layer", "No business logic"],
            },
        },
        "dependency_flow": "api → application → domain ← infrastructure",
        "categories": list(rules_by_cat.keys()),
    }
