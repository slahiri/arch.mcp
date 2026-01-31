"""Configuration loader for external rules."""

import os
from pathlib import Path

import yaml

# Default paths to search for custom rules
DEFAULT_RULES_PATHS = [
    Path.cwd() / ".arch-mcp" / "rules.yaml",  # Project-local
    Path.cwd() / "arch-rules.yaml",  # Project root
    Path.home() / ".arch-mcp" / "rules.yaml",  # User home
]


def _get_package_rules_path() -> Path:
    """Get the path to package default rules.

    Handles both:
    - Development: rules/default.yaml at repo root
    - Installed package: bundled default_rules.yaml in package dir
    """
    # First check bundled rules in package (works for both installed and Docker)
    bundled_path = Path(__file__).parent / "default_rules.yaml"
    if bundled_path.exists():
        return bundled_path

    # Try development path (rules/ at repo root)
    dev_path = Path(__file__).parent.parent.parent / "rules" / "default.yaml"
    if dev_path.exists():
        return dev_path

    raise FileNotFoundError("Could not find default rules file")


def find_rules_file() -> Path | None:
    """Find the first existing custom rules file in search paths."""
    # Check environment variable first
    env_path = os.environ.get("ARCH_MCP_RULES")
    if env_path:
        path = Path(env_path)
        if path.exists():
            return path

    # Check default paths
    for path in DEFAULT_RULES_PATHS:
        if path.exists():
            return path

    return None


def load_rules_from_yaml(path: Path) -> dict[str, list[dict]]:
    """Load rules from a YAML file."""
    with open(path) as f:
        data = yaml.safe_load(f)
    return data or {}


def load_rules() -> dict[str, list[dict]]:
    """Load rules from external file or fall back to package defaults.

    Search order:
    1. ARCH_MCP_RULES environment variable
    2. .arch-mcp/rules.yaml in current directory
    3. arch-rules.yaml in current directory
    4. ~/.arch-mcp/rules.yaml in user home
    5. Package default rules (fallback)
    """
    # Try external rules first
    rules_file = find_rules_file()
    if rules_file:
        return load_rules_from_yaml(rules_file)

    # Fall back to package defaults
    return load_rules_from_yaml(_get_package_rules_path())


def get_rules_source() -> str:
    """Return the path of the rules file being used."""
    rules_file = find_rules_file()
    if rules_file:
        return str(rules_file)
    return str(_get_package_rules_path()) + " (default)"


def flatten_rules(rules_by_category: dict[str, list[dict]]) -> list[dict]:
    """Flatten rules dict into a list with category field."""
    all_rules = []
    for category, rules in rules_by_category.items():
        for rule in rules:
            rule["category"] = category
            all_rules.append(rule)
    return all_rules


def get_default_rules_path() -> Path:
    """Get the path to the default rules file for copying."""
    return _get_package_rules_path()


def init_custom_rules(target_dir: Path | None = None) -> Path:
    """Initialize a custom rules file.

    Args:
        target_dir: Directory to create rules in. Defaults to .arch-mcp/ in cwd.

    Returns:
        Path to the created rules file.
    """
    if target_dir is None:
        target_dir = Path.cwd() / ".arch-mcp"

    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / "rules.yaml"

    if target.exists():
        print(f"Rules file already exists: {target}")
        return target

    # Copy default rules
    import shutil
    shutil.copy(_get_package_rules_path(), target)
    print(f"Created custom rules file: {target}")
    print("Edit this file to customize architecture rules for your project.")
    return target
