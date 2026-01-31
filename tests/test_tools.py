"""Tests for architecture tools"""

from arch_mcp.tools import (
    check_architecture,
    get_best_practices,
    get_file_template,
    get_naming_conventions,
    get_project_structure,
    get_rule,
    get_tdd_workflow,
    list_rules,
    validate_code,
)


def test_list_rules():
    result = list_rules()
    assert result["total"] > 0
    assert "security" in result["categories"]


def test_list_rules_by_category():
    result = list_rules(category="security")
    assert result["total"] > 0
    assert all(r["category"] == "security" for r in result["rules"])


def test_get_rule():
    result = get_rule("no-bare-except")
    assert "rule" in result
    assert result["rule"]["id"] == "no-bare-except"


def test_get_rule_not_found():
    result = get_rule("non-existent")
    assert "error" in result


def test_validate_code_clean():
    code = """
def get_user(user_id: str) -> User:
    return user_repository.find_by_id(user_id)
"""
    result = validate_code(code, "src/services/user.py")
    assert result["valid"] is True


def test_validate_code_with_violation():
    code = """
password = "super-secret-123"
"""
    result = validate_code(code, "src/config.py")
    assert result["valid"] is False
    assert result["summary"]["errors"] > 0


def test_validate_code_bare_except():
    code = """
try:
    do_something()
except:
    pass
"""
    result = validate_code(code, "src/service.py")
    assert result["valid"] is False
    assert any(v["rule_id"] == "no-bare-except" for v in result["violations"])


def test_get_project_structure():
    result = get_project_structure("clean-architecture")
    assert result["name"] == "Clean Architecture"
    assert "structure" in result


def test_get_best_practices():
    result = get_best_practices("security")
    assert result["total"] > 0


def test_check_architecture_clean():
    files = [
        {
            "path": "src/application/services/user.py",
            "content": "from domain.entities import User",
        }
    ]
    result = check_architecture(files)
    assert result["consistent"] is True


def test_check_architecture_violation():
    files = [
        {
            "path": "src/domain/entities/user.py",
            "content": "from infrastructure.database import session",
        }
    ]
    result = check_architecture(files)
    assert result["consistent"] is False
    assert result["summary"]["errors"] > 0


def test_get_naming_conventions():
    result = get_naming_conventions()
    assert "conventions" in result
    assert "files" in result["conventions"]
    assert "classes" in result["conventions"]
    assert "functions" in result["conventions"]


def test_get_file_template_service():
    result = get_file_template("service", "user")
    assert result["template_type"] == "service"
    assert result["resource"] == "user"
    assert "UserService" in result["content"]
    assert "user_service.py" in result["filename"]


def test_get_file_template_schemas():
    result = get_file_template("schemas", "product")
    assert "ProductCreate" in result["content"]
    assert "ProductResponse" in result["content"]


def test_get_file_template_invalid():
    result = get_file_template("invalid", "user")
    assert "error" in result
    assert "available" in result


def test_get_tdd_workflow():
    result = get_tdd_workflow("order")
    assert "steps" in result
    assert len(result["steps"]) >= 5
    assert "test_commands" in result
    assert "coverage_requirement" in result
    # Verify it uses the correct resource name
    assert "OrderService" in str(result) or "order" in str(result["steps"][0])


def test_list_rules_includes_naming_category():
    result = list_rules()
    assert "naming" in result["categories"]


def test_list_rules_includes_structure_category():
    result = list_rules()
    assert "structure" in result["categories"]


def test_list_rules_naming_rules():
    result = list_rules(category="naming")
    assert result["total"] > 0
    rule_ids = [r["id"] for r in result["rules"]]
    assert "schema-naming" in rule_ids


def test_list_rules_testing_includes_tdd():
    result = list_rules(category="testing")
    rule_ids = [r["id"] for r in result["rules"]]
    assert "tdd-required" in rule_ids
