"""Unit tests for entities module

Tests the Entity and Relation base classes using generic test fixtures
(Person, Company, Employment) that model a simple domain schema.
"""

import pytest
from dataclasses import dataclass
from typing import Optional
from typedb_client3.entities import Entity, Relation


# ---------------------------------------------------------------------------
# Generic test fixtures — subclasses of Entity and Relation base classes
# ---------------------------------------------------------------------------

@dataclass
class Person(Entity):
    """Generic person entity for testing."""
    _type = "person"
    _key_attr = "username"

    username: str
    full_name: str
    age: int
    email: Optional[str] = None


@dataclass
class Company(Entity):
    """Generic company entity for testing."""
    _type = "company"
    _key_attr = "company-id"

    company_id: str
    name: str
    industry: Optional[str] = None


@dataclass
class TextItem(Entity):
    """Entity with integer field for testing numeric escaping."""
    _type = "text-item"
    _key_attr = "item-id"

    item_id: str
    label: str
    order: int


@dataclass
class Friendship(Relation):
    """Generic friendship relation for testing."""
    _type = "friendship"
    _roles = ["friend"]

    friend1: Person
    friend2: Person


@dataclass
class Employment(Relation):
    """Generic employment relation for testing."""
    _type = "employment"
    _roles = ["employer", "employee"]

    employer: Company
    employee: Person


# ---------------------------------------------------------------------------
# Tests: Entity base class
# ---------------------------------------------------------------------------

class TestEntityBaseClass:
    """Test Entity base class defaults and behaviour."""

    def test_entity_base_class_type_default(self):
        """Entity base class has empty _type by default."""
        assert Entity._type == ""

    def test_entity_base_class_key_attr_default(self):
        """Entity base class has None _key_attr by default."""
        assert Entity._key_attr is None

    def test_entity_without_key_raises_on_get_key_value(self):
        """get_key_value raises ValueError when no key attribute defined."""
        entity = Entity()
        with pytest.raises(ValueError, match="No key attribute"):
            entity.get_key_value()

    def test_entity_without_key_raises_on_match_query(self):
        """to_match_query raises ValueError when no key attribute defined."""
        entity = Entity()
        with pytest.raises(ValueError, match="No key attribute"):
            entity.to_match_query()

    def test_escape_value_string(self):
        """String values are quoted and escaped."""
        entity = Entity()
        assert entity._escape_value("hello") == '"hello"'

    def test_escape_value_string_with_quotes(self):
        """Strings with double quotes are escaped."""
        entity = Entity()
        result = entity._escape_value('say "hi"')
        # The double quotes inside the string should be backslash-escaped
        assert '"say \"hi\""' == result

    def test_escape_value_string_with_backslash(self):
        """Strings with backslashes are escaped."""
        entity = Entity()
        result = entity._escape_value("C:\\test")
        assert "C:\\\\test" in result

    def test_escape_value_integer(self):
        """Integer values are converted to string without quotes."""
        entity = Entity()
        assert entity._escape_value(42) == "42"

    def test_escape_value_float(self):
        """Float values are converted to string without quotes."""
        entity = Entity()
        assert entity._escape_value(3.14) == "3.14"

    def test_escape_value_boolean_true(self):
        """Boolean True is lowercased."""
        entity = Entity()
        assert entity._escape_value(True) == "true"

    def test_escape_value_boolean_false(self):
        """Boolean False is lowercased."""
        entity = Entity()
        assert entity._escape_value(False) == "false"

    def test_escape_value_unsupported_type_raises(self):
        """Unsupported value types raise ValueError."""
        entity = Entity()
        with pytest.raises(ValueError, match="Unsupported value type"):
            entity._escape_value([1, 2, 3])


# ---------------------------------------------------------------------------
# Tests: Entity subclass — class attributes
# ---------------------------------------------------------------------------

class TestEntitySubclassAttributes:
    """Test that Entity subclasses correctly set _type and _key_attr."""

    def test_person_type(self):
        assert Person._type == "person"

    def test_person_key_attr(self):
        assert Person._key_attr == "username"

    def test_company_type(self):
        assert Company._type == "company"

    def test_company_key_attr(self):
        assert Company._key_attr == "company-id"

    def test_text_item_type(self):
        assert TextItem._type == "text-item"

    def test_text_item_key_attr(self):
        assert TextItem._key_attr == "item-id"


# ---------------------------------------------------------------------------
# Tests: Entity creation and field access
# ---------------------------------------------------------------------------

class TestEntityCreation:
    """Test creating Entity subclass instances."""

    def test_person_creation_all_fields(self):
        """Person can be created with all fields."""
        p = Person(username="jdoe", full_name="Jane Doe", age=30, email="jdoe@example.com")
        assert p.username == "jdoe"
        assert p.full_name == "Jane Doe"
        assert p.age == 30
        assert p.email == "jdoe@example.com"

    def test_person_creation_optional_field_defaults_none(self):
        """Optional fields default to None."""
        p = Person(username="jdoe", full_name="Jane Doe", age=30)
        assert p.email is None

    def test_company_creation(self):
        """Company can be created with required fields."""
        c = Company(company_id="C001", name="Acme Corp")
        assert c.company_id == "C001"
        assert c.name == "Acme Corp"
        assert c.industry is None

    def test_company_creation_with_optional(self):
        """Company can be created with optional industry field."""
        c = Company(company_id="C001", name="Acme Corp", industry="Technology")
        assert c.industry == "Technology"

    def test_text_item_creation_with_integer(self):
        """TextItem can be created with integer order field."""
        t = TextItem(item_id="T1", label="First", order=1)
        assert t.order == 1


# ---------------------------------------------------------------------------
# Tests: get_key_value
# ---------------------------------------------------------------------------

class TestGetKeyValue:
    """Test get_key_value on Entity subclasses."""

    def test_person_get_key_value(self):
        """Person returns username as key value."""
        p = Person(username="jdoe", full_name="Jane Doe", age=30)
        assert p.get_key_value() == "jdoe"

    def test_company_get_key_value(self):
        """Company returns company_id as key value (kebab-case key maps to snake_case field)."""
        c = Company(company_id="C001", name="Acme Corp")
        assert c.get_key_value() == "C001"

    def test_text_item_get_key_value(self):
        """TextItem returns item_id as key value."""
        t = TextItem(item_id="T1", label="First", order=1)
        assert t.get_key_value() == "T1"


# ---------------------------------------------------------------------------
# Tests: to_insert_query
# ---------------------------------------------------------------------------

class TestToInsertQuery:
    """Test to_insert_query generates correct TypeQL v3 INSERT statements."""

    def test_person_insert_query_contains_isa(self):
        """INSERT query contains isa type constraint."""
        p = Person(username="jdoe", full_name="Jane Doe", age=30)
        query = p.to_insert_query()
        assert "$p isa person" in query

    def test_person_insert_query_contains_key_attribute(self):
        """INSERT query contains key attribute."""
        p = Person(username="jdoe", full_name="Jane Doe", age=30)
        query = p.to_insert_query()
        assert 'has username "jdoe"' in query

    def test_person_insert_query_snake_to_kebab_conversion(self):
        """INSERT query converts snake_case field names to kebab-case."""
        p = Person(username="jdoe", full_name="Jane Doe", age=30)
        query = p.to_insert_query()
        assert 'has full-name "Jane Doe"' in query
        assert "full_name" not in query

    def test_person_insert_query_integer_field(self):
        """INSERT query handles integer fields without quotes."""
        p = Person(username="jdoe", full_name="Jane Doe", age=30)
        query = p.to_insert_query()
        assert "has age 30" in query

    def test_person_insert_query_none_field_excluded(self):
        """INSERT query excludes None optional fields."""
        p = Person(username="jdoe", full_name="Jane Doe", age=30, email=None)
        query = p.to_insert_query()
        assert "email" not in query

    def test_person_insert_query_optional_field_included_when_set(self):
        """INSERT query includes optional fields when they have values."""
        p = Person(username="jdoe", full_name="Jane Doe", age=30, email="jdoe@example.com")
        query = p.to_insert_query()
        assert 'has email "jdoe@example.com"' in query

    def test_insert_query_starts_with_insert(self):
        """INSERT query starts with 'insert' keyword."""
        p = Person(username="jdoe", full_name="Jane Doe", age=30)
        query = p.to_insert_query()
        assert query.startswith("insert")

    def test_insert_query_ends_with_semicolon(self):
        """INSERT query ends with semicolon."""
        p = Person(username="jdoe", full_name="Jane Doe", age=30)
        query = p.to_insert_query()
        assert query.endswith(";")

    def test_company_insert_query(self):
        """Company INSERT query uses correct type and attributes."""
        c = Company(company_id="C001", name="Acme Corp", industry="Technology")
        query = c.to_insert_query()
        assert "$c isa company" in query
        assert 'has company-id "C001"' in query
        assert 'has name "Acme Corp"' in query
        assert 'has industry "Technology"' in query

    def test_text_item_insert_query_integer_order(self):
        """TextItem INSERT query includes integer order without quotes."""
        t = TextItem(item_id="T1", label="First", order=42)
        query = t.to_insert_query()
        assert "$t isa text-item" in query
        assert 'has item-id "T1"' in query
        assert "has order 42" in query

    def test_insert_query_escapes_double_quotes_in_string(self):
        """INSERT query escapes double quotes in string values."""
        p = Person(username="jdoe", full_name='He said "hello"', age=30)
        query = p.to_insert_query()
        # Double quotes inside the value should be backslash-escaped in the query
        assert 'He said \"hello\"' in query

    def test_insert_query_escapes_backslash_in_string(self):
        """INSERT query escapes backslashes in string values."""
        p = Person(username="jdoe", full_name="C:\\test", age=30)
        query = p.to_insert_query()
        assert "C:\\\\test" in query


# ---------------------------------------------------------------------------
# Tests: to_match_query
# ---------------------------------------------------------------------------

class TestToMatchQuery:
    """Test to_match_query generates correct TypeQL v3 MATCH statements."""

    def test_person_match_query_contains_match(self):
        """MATCH query starts with 'match' keyword."""
        p = Person(username="jdoe", full_name="Jane Doe", age=30)
        query = p.to_match_query()
        assert query.startswith("match")

    def test_person_match_query_contains_isa(self):
        """MATCH query contains isa type constraint."""
        p = Person(username="jdoe", full_name="Jane Doe", age=30)
        query = p.to_match_query()
        assert "$p isa person" in query

    def test_person_match_query_contains_key_attribute(self):
        """MATCH query filters by key attribute only."""
        p = Person(username="jdoe", full_name="Jane Doe", age=30)
        query = p.to_match_query()
        assert 'has username "jdoe"' in query

    def test_person_match_query_excludes_non_key_attributes(self):
        """MATCH query only uses key attribute, not all fields."""
        p = Person(username="jdoe", full_name="Jane Doe", age=30)
        query = p.to_match_query()
        assert "full-name" not in query
        assert "age" not in query

    def test_match_query_ends_with_semicolon(self):
        """MATCH query ends with semicolon."""
        p = Person(username="jdoe", full_name="Jane Doe", age=30)
        query = p.to_match_query()
        assert query.endswith(";")

    def test_company_match_query(self):
        """Company MATCH query uses correct type and key attribute."""
        c = Company(company_id="C001", name="Acme Corp")
        query = c.to_match_query()
        assert "$c isa company" in query
        assert 'has company-id "C001"' in query


# ---------------------------------------------------------------------------
# Tests: to_parameterized_insert_query
# ---------------------------------------------------------------------------

class TestParameterizedInsertQuery:
    """Test to_parameterized_insert_query generates safe parameterized queries."""

    def test_returns_tuple(self):
        """Returns a (query_string, params_dict) tuple."""
        p = Person(username="jdoe", full_name="Jane Doe", age=30)
        result = p.to_parameterized_insert_query()
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_query_contains_isa(self):
        """Parameterized query contains isa type constraint."""
        p = Person(username="jdoe", full_name="Jane Doe", age=30)
        query, params = p.to_parameterized_insert_query()
        assert "$p isa person" in query

    def test_params_dict_contains_all_fields(self):
        """Parameters dict contains entries for all non-None data fields."""
        p = Person(username="jdoe", full_name="Jane Doe", age=30)
        query, params = p.to_parameterized_insert_query()
        # username, full_name, age — _type and _key_attr are ClassVars, excluded
        assert len(params) == 3

    def test_params_dict_excludes_none_fields(self):
        """Parameters dict excludes None optional fields."""
        p = Person(username="jdoe", full_name="Jane Doe", age=30, email=None)
        query, params = p.to_parameterized_insert_query()
        # email should not be in params
        for key in params:
            assert "email" not in key

    def test_params_values_match_entity_fields(self):
        """Parameter values match the entity field values."""
        p = Person(username="jdoe", full_name="Jane Doe", age=30)
        query, params = p.to_parameterized_insert_query()
        values = list(params.values())
        assert "jdoe" in values
        assert "Jane Doe" in values
        assert 30 in values

    def test_query_contains_placeholders(self):
        """Parameterized query contains $ placeholders instead of raw values."""
        p = Person(username="jdoe", full_name="Jane Doe", age=30)
        query, params = p.to_parameterized_insert_query()
        # Raw values should not appear directly in query
        assert '"jdoe"' not in query
        assert '"Jane Doe"' not in query


# ---------------------------------------------------------------------------
# Tests: to_parameterized_match_query
# ---------------------------------------------------------------------------

class TestParameterizedMatchQuery:
    """Test to_parameterized_match_query generates safe parameterized queries."""

    def test_returns_tuple(self):
        """Returns a (query_string, params_dict) tuple."""
        p = Person(username="jdoe", full_name="Jane Doe", age=30)
        result = p.to_parameterized_match_query()
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_query_contains_match_and_isa(self):
        """Parameterized match query contains match and isa."""
        p = Person(username="jdoe", full_name="Jane Doe", age=30)
        query, params = p.to_parameterized_match_query()
        assert "match" in query
        assert "isa person" in query

    def test_params_contains_key_value(self):
        """Parameters dict contains the key attribute value."""
        p = Person(username="jdoe", full_name="Jane Doe", age=30)
        query, params = p.to_parameterized_match_query()
        assert "jdoe" in params.values()

    def test_params_contains_only_key(self):
        """Parameters dict contains only the key attribute (not all fields)."""
        p = Person(username="jdoe", full_name="Jane Doe", age=30)
        query, params = p.to_parameterized_match_query()
        assert len(params) == 1


# ---------------------------------------------------------------------------
# Tests: Relation base class
# ---------------------------------------------------------------------------

class TestRelationBaseClass:
    """Test Relation base class defaults and behaviour."""

    def test_relation_base_class_type_default(self):
        """Relation base class has empty _type by default."""
        assert Relation._type == ""

    def test_relation_base_class_roles_default(self):
        """Relation base class has empty _roles list by default."""
        assert Relation._roles == []


# ---------------------------------------------------------------------------
# Tests: Relation subclass — class attributes
# ---------------------------------------------------------------------------

class TestRelationSubclassAttributes:
    """Test that Relation subclasses correctly set _type and _roles."""

    def test_friendship_type(self):
        assert Friendship._type == "friendship"

    def test_friendship_roles(self):
        assert Friendship._roles == ["friend"]

    def test_employment_type(self):
        assert Employment._type == "employment"

    def test_employment_roles(self):
        assert Employment._roles == ["employer", "employee"]


# ---------------------------------------------------------------------------
# Tests: Relation to_insert_query
# ---------------------------------------------------------------------------

class TestRelationToInsertQuery:
    """Test Relation to_insert_query generates correct TypeQL v3 INSERT statements."""

    def test_friendship_insert_query(self):
        """Friendship INSERT query uses correct role and type."""
        p1 = Person(username="jdoe", full_name="Jane Doe", age=30)
        p2 = Person(username="asmith", full_name="Alice Smith", age=25)
        f = Friendship(friend1=p1, friend2=p2)

        query = f.to_insert_query({"friend": "p1"})
        assert "(friend: $p1) isa friendship;" == query

    def test_employment_insert_query_both_roles(self):
        """Employment INSERT query includes both employer and employee roles."""
        c = Company(company_id="C001", name="Acme Corp")
        p = Person(username="jdoe", full_name="Jane Doe", age=30)
        e = Employment(employer=c, employee=p)

        query = e.to_insert_query({"employer": "c", "employee": "p"})
        assert "(employer: $c, employee: $p) isa employment;" == query

    def test_relation_insert_query_partial_roles(self):
        """INSERT query only includes roles present in the variables mapping."""
        c = Company(company_id="C001", name="Acme Corp")
        p = Person(username="jdoe", full_name="Jane Doe", age=30)
        e = Employment(employer=c, employee=p)

        # Only pass employer role
        query = e.to_insert_query({"employer": "c"})
        assert "employer: $c" in query
        assert "employee" not in query

    def test_relation_insert_query_ends_with_semicolon(self):
        """Relation INSERT query ends with semicolon."""
        p1 = Person(username="jdoe", full_name="Jane Doe", age=30)
        p2 = Person(username="asmith", full_name="Alice Smith", age=25)
        f = Friendship(friend1=p1, friend2=p2)

        query = f.to_insert_query({"friend": "p1"})
        assert query.endswith(";")

    def test_relation_insert_query_empty_variables(self):
        """INSERT query with empty variables produces empty role list."""
        p1 = Person(username="jdoe", full_name="Jane Doe", age=30)
        p2 = Person(username="asmith", full_name="Alice Smith", age=25)
        f = Friendship(friend1=p1, friend2=p2)

        query = f.to_insert_query({})
        assert "() isa friendship;" == query


if __name__ == "__main__":
    pytest.main([__file__, "-v"])