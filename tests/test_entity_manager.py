"""Unit tests for entity_manager module

Tests EntityManager using generic test fixtures (Person, Company, Employment)
that subclass the Entity and Relation base classes.
"""

import pytest
from unittest.mock import Mock
from dataclasses import dataclass
from typing import Optional

from typedb_client3.entity_manager import EntityManager
from typedb_client3.entities import Entity, Relation
from typedb_client3.client import TypeDBClient, TransactionType


# ---------------------------------------------------------------------------
# Generic test fixtures
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
class Employment(Relation):
    """Generic employment relation for testing."""
    _type = "employment"
    _roles = ["employer", "employee"]

    employer: Company
    employee: Person


# ---------------------------------------------------------------------------
# Tests: EntityManager initialization
# ---------------------------------------------------------------------------

class TestEntityManagerInit:
    """Test EntityManager initialization."""

    @pytest.fixture
    def mock_client(self):
        return Mock(spec=TypeDBClient)

    def test_entity_manager_stores_client(self, mock_client):
        """EntityManager stores the client reference."""
        manager = EntityManager(mock_client, "mydb")
        assert manager.client is mock_client

    def test_entity_manager_stores_database(self, mock_client):
        """EntityManager stores the database name."""
        manager = EntityManager(mock_client, "mydb")
        assert manager.database == "mydb"


# ---------------------------------------------------------------------------
# Tests: insert
# ---------------------------------------------------------------------------

class TestEntityManagerInsert:
    """Test EntityManager.insert method."""

    @pytest.fixture
    def mock_client(self):
        return Mock(spec=TypeDBClient)

    @pytest.fixture
    def manager(self, mock_client):
        return EntityManager(mock_client, "mydb")

    def test_insert_calls_execute_query(self, manager, mock_client):
        """insert calls client.execute_query once."""
        p = Person(username="jdoe", full_name="Jane Doe", age=30)
        manager.insert(p)
        mock_client.execute_query.assert_called_once()

    def test_insert_uses_correct_database(self, manager, mock_client):
        """insert passes the correct database name."""
        p = Person(username="jdoe", full_name="Jane Doe", age=30)
        manager.insert(p)
        call_kwargs = mock_client.execute_query.call_args
        assert call_kwargs.kwargs["database"] == "mydb"

    def test_insert_uses_write_transaction(self, manager, mock_client):
        """insert uses WRITE transaction type."""
        p = Person(username="jdoe", full_name="Jane Doe", age=30)
        manager.insert(p)
        call_kwargs = mock_client.execute_query.call_args
        assert call_kwargs.kwargs["transaction_type"] == TransactionType.WRITE

    def test_insert_query_contains_insert_keyword(self, manager, mock_client):
        """insert query contains 'insert' keyword."""
        p = Person(username="jdoe", full_name="Jane Doe", age=30)
        manager.insert(p)
        call_kwargs = mock_client.execute_query.call_args
        assert "insert" in call_kwargs.kwargs["query"]

    def test_insert_query_contains_entity_type(self, manager, mock_client):
        """insert query contains the entity type."""
        p = Person(username="jdoe", full_name="Jane Doe", age=30)
        manager.insert(p)
        call_kwargs = mock_client.execute_query.call_args
        assert "person" in call_kwargs.kwargs["query"]

    def test_insert_query_contains_key_attribute(self, manager, mock_client):
        """insert query contains the key attribute value."""
        p = Person(username="jdoe", full_name="Jane Doe", age=30)
        manager.insert(p)
        call_kwargs = mock_client.execute_query.call_args
        assert 'username "jdoe"' in call_kwargs.kwargs["query"]

    def test_insert_company_entity(self, manager, mock_client):
        """insert works for Company entity type."""
        c = Company(company_id="C001", name="Acme Corp", industry="Technology")
        manager.insert(c)
        call_kwargs = mock_client.execute_query.call_args
        assert "company" in call_kwargs.kwargs["query"]
        assert 'company-id "C001"' in call_kwargs.kwargs["query"]


# ---------------------------------------------------------------------------
# Tests: put
# ---------------------------------------------------------------------------

class TestEntityManagerPut:
    """Test EntityManager.put method."""

    @pytest.fixture
    def mock_client(self):
        return Mock(spec=TypeDBClient)

    @pytest.fixture
    def manager(self, mock_client):
        return EntityManager(mock_client, "mydb")

    def test_put_calls_execute_query(self, manager, mock_client):
        """put calls client.execute_query once."""
        p = Person(username="jdoe", full_name="Jane Doe", age=30)
        manager.put(p)
        mock_client.execute_query.assert_called_once()

    def test_put_uses_write_transaction(self, manager, mock_client):
        """put uses WRITE transaction type."""
        p = Person(username="jdoe", full_name="Jane Doe", age=30)
        manager.put(p)
        call_kwargs = mock_client.execute_query.call_args
        assert call_kwargs.kwargs["transaction_type"] == TransactionType.WRITE

    def test_put_query_contains_put_keyword(self, manager, mock_client):
        """put query contains 'put' keyword (TypeQL v3 idempotent write)."""
        p = Person(username="jdoe", full_name="Jane Doe", age=30)
        manager.put(p)
        call_kwargs = mock_client.execute_query.call_args
        assert "put" in call_kwargs.kwargs["query"]

    def test_put_query_contains_key_attribute(self, manager, mock_client):
        """put query contains the key attribute value."""
        p = Person(username="jdoe", full_name="Jane Doe", age=30)
        manager.put(p)
        call_kwargs = mock_client.execute_query.call_args
        assert 'username "jdoe"' in call_kwargs.kwargs["query"]

    def test_put_company_entity(self, manager, mock_client):
        """put works for Company entity type."""
        c = Company(company_id="C001", name="Acme Corp")
        manager.put(c)
        call_kwargs = mock_client.execute_query.call_args
        assert "put" in call_kwargs.kwargs["query"]
        assert 'company-id "C001"' in call_kwargs.kwargs["query"]


# ---------------------------------------------------------------------------
# Tests: exists
# ---------------------------------------------------------------------------

class TestEntityManagerExists:
    """Test EntityManager.exists method."""

    @pytest.fixture
    def mock_client(self):
        return Mock(spec=TypeDBClient)

    @pytest.fixture
    def manager(self, mock_client):
        return EntityManager(mock_client, "mydb")

    def test_exists_returns_true_when_answers_present(self, manager, mock_client):
        """exists returns True when query returns answers."""
        mock_client.execute_query.return_value = {"answers": [{"id": "test"}]}
        assert manager.exists(Person, "jdoe") is True

    def test_exists_returns_false_when_no_answers(self, manager, mock_client):
        """exists returns False when query returns empty answers."""
        mock_client.execute_query.return_value = {"answers": []}
        assert manager.exists(Person, "jdoe") is False

    def test_exists_calls_execute_query(self, manager, mock_client):
        """exists calls client.execute_query."""
        mock_client.execute_query.return_value = {"answers": []}
        manager.exists(Person, "jdoe")
        mock_client.execute_query.assert_called_once()

    def test_exists_uses_read_transaction(self, manager, mock_client):
        """exists uses READ transaction type."""
        mock_client.execute_query.return_value = {"answers": []}
        manager.exists(Person, "jdoe")
        call_kwargs = mock_client.execute_query.call_args
        assert call_kwargs.kwargs["transaction_type"] == TransactionType.READ

    def test_exists_query_contains_entity_type(self, manager, mock_client):
        """exists query references the correct entity type."""
        mock_client.execute_query.return_value = {"answers": []}
        manager.exists(Person, "jdoe")
        call_kwargs = mock_client.execute_query.call_args
        assert "person" in call_kwargs.kwargs["query"]

    def test_exists_query_contains_key_value(self, manager, mock_client):
        """exists query contains the key value being searched."""
        mock_client.execute_query.return_value = {"answers": []}
        manager.exists(Person, "jdoe")
        call_kwargs = mock_client.execute_query.call_args
        assert "jdoe" in call_kwargs.kwargs["query"]

    def test_exists_company_entity(self, manager, mock_client):
        """exists works for Company entity type."""
        mock_client.execute_query.return_value = {"answers": [{"id": "test"}]}
        assert manager.exists(Company, "C001") is True


# ---------------------------------------------------------------------------
# Tests: delete
# ---------------------------------------------------------------------------

class TestEntityManagerDelete:
    """Test EntityManager.delete method."""

    @pytest.fixture
    def mock_client(self):
        return Mock(spec=TypeDBClient)

    @pytest.fixture
    def manager(self, mock_client):
        return EntityManager(mock_client, "mydb")

    def test_delete_calls_execute_query(self, manager, mock_client):
        """delete calls client.execute_query."""
        p = Person(username="jdoe", full_name="Jane Doe", age=30)
        manager.delete(p)
        mock_client.execute_query.assert_called_once()

    def test_delete_uses_write_transaction(self, manager, mock_client):
        """delete uses WRITE transaction type."""
        p = Person(username="jdoe", full_name="Jane Doe", age=30)
        manager.delete(p)
        call_kwargs = mock_client.execute_query.call_args
        assert call_kwargs.kwargs["transaction_type"] == TransactionType.WRITE

    def test_delete_query_contains_delete_keyword(self, manager, mock_client):
        """delete query contains 'delete' keyword."""
        p = Person(username="jdoe", full_name="Jane Doe", age=30)
        manager.delete(p)
        call_kwargs = mock_client.execute_query.call_args
        assert "delete" in call_kwargs.kwargs["query"]


# ---------------------------------------------------------------------------
# Tests: fetch_one
# ---------------------------------------------------------------------------

class TestEntityManagerFetchOne:
    """Test EntityManager.fetch_one method."""

    @pytest.fixture
    def mock_client(self):
        return Mock(spec=TypeDBClient)

    @pytest.fixture
    def manager(self, mock_client):
        return EntityManager(mock_client, "mydb")

    def test_fetch_one_returns_none_when_empty(self, manager, mock_client):
        """fetch_one returns None when no results."""
        mock_client.execute_query.return_value = {"answers": []}
        result = manager.fetch_one(Person, {"username": "jdoe"})
        assert result is None

    def test_fetch_one_calls_execute_query(self, manager, mock_client):
        """fetch_one calls client.execute_query."""
        mock_client.execute_query.return_value = {"answers": []}
        manager.fetch_one(Person, {"username": "jdoe"})
        mock_client.execute_query.assert_called_once()

    def test_fetch_one_uses_read_transaction(self, manager, mock_client):
        """fetch_one uses READ transaction type."""
        mock_client.execute_query.return_value = {"answers": []}
        manager.fetch_one(Person, {"username": "jdoe"})
        call_kwargs = mock_client.execute_query.call_args
        assert call_kwargs.kwargs["transaction_type"] == TransactionType.READ

    def test_fetch_one_query_contains_match(self, manager, mock_client):
        """fetch_one query contains 'match' keyword."""
        mock_client.execute_query.return_value = {"answers": []}
        manager.fetch_one(Person, {"username": "jdoe"})
        call_kwargs = mock_client.execute_query.call_args
        assert "match" in call_kwargs.kwargs["query"]

    def test_fetch_one_query_contains_fetch(self, manager, mock_client):
        """fetch_one query contains 'fetch' keyword."""
        mock_client.execute_query.return_value = {"answers": []}
        manager.fetch_one(Person, {"username": "jdoe"})
        call_kwargs = mock_client.execute_query.call_args
        assert "fetch" in call_kwargs.kwargs["query"]

    def test_fetch_one_query_contains_entity_type(self, manager, mock_client):
        """fetch_one query references the correct entity type."""
        mock_client.execute_query.return_value = {"answers": []}
        manager.fetch_one(Person, {"username": "jdoe"})
        call_kwargs = mock_client.execute_query.call_args
        assert "person" in call_kwargs.kwargs["query"]

    def test_fetch_one_query_contains_filter_attribute(self, manager, mock_client):
        """fetch_one query includes the filter attribute."""
        mock_client.execute_query.return_value = {"answers": []}
        manager.fetch_one(Person, {"username": "jdoe", "full-name": "Jane Doe"})
        call_kwargs = mock_client.execute_query.call_args
        assert "person" in call_kwargs.kwargs["query"]

    def test_fetch_one_company(self, manager, mock_client):
        """fetch_one works for Company entity type."""
        mock_client.execute_query.return_value = {"answers": []}
        manager.fetch_one(Company, {"company-id": "C001"})
        call_kwargs = mock_client.execute_query.call_args
        assert "company" in call_kwargs.kwargs["query"]


# ---------------------------------------------------------------------------
# Tests: fetch_all
# ---------------------------------------------------------------------------

class TestEntityManagerFetchAll:
    """Test EntityManager.fetch_all method."""

    @pytest.fixture
    def mock_client(self):
        return Mock(spec=TypeDBClient)

    @pytest.fixture
    def manager(self, mock_client):
        return EntityManager(mock_client, "mydb")

    def test_fetch_all_returns_empty_list_when_no_results(self, manager, mock_client):
        """fetch_all returns empty list when no results."""
        mock_client.execute_query.return_value = {"answers": []}
        result = manager.fetch_all(Person)
        assert result == []

    def test_fetch_all_calls_execute_query(self, manager, mock_client):
        """fetch_all calls client.execute_query."""
        mock_client.execute_query.return_value = {"answers": []}
        manager.fetch_all(Person)
        mock_client.execute_query.assert_called_once()

    def test_fetch_all_uses_read_transaction(self, manager, mock_client):
        """fetch_all uses READ transaction type."""
        mock_client.execute_query.return_value = {"answers": []}
        manager.fetch_all(Person)
        call_kwargs = mock_client.execute_query.call_args
        assert call_kwargs.kwargs["transaction_type"] == TransactionType.READ

    def test_fetch_all_query_contains_match_and_fetch(self, manager, mock_client):
        """fetch_all query contains both 'match' and 'fetch' keywords."""
        mock_client.execute_query.return_value = {"answers": []}
        manager.fetch_all(Person)
        call_kwargs = mock_client.execute_query.call_args
        query = call_kwargs.kwargs["query"]
        assert "match" in query
        assert "fetch" in query

    def test_fetch_all_query_contains_entity_type(self, manager, mock_client):
        """fetch_all query references the correct entity type."""
        mock_client.execute_query.return_value = {"answers": []}
        manager.fetch_all(Person)
        call_kwargs = mock_client.execute_query.call_args
        assert "person" in call_kwargs.kwargs["query"]

    def test_fetch_all_with_filters(self, manager, mock_client):
        """fetch_all with filters includes filter in query."""
        mock_client.execute_query.return_value = {"answers": []}
        manager.fetch_all(Person, {"full-name": "Jane Doe"})
        call_kwargs = mock_client.execute_query.call_args
        assert "person" in call_kwargs.kwargs["query"]

    def test_fetch_all_company(self, manager, mock_client):
        """fetch_all works for Company entity type."""
        mock_client.execute_query.return_value = {"answers": []}
        manager.fetch_all(Company)
        call_kwargs = mock_client.execute_query.call_args
        assert "company" in call_kwargs.kwargs["query"]


# ---------------------------------------------------------------------------
# Tests: insert_relation
# ---------------------------------------------------------------------------

class TestEntityManagerRelation:
    """Test EntityManager relation methods."""

    @pytest.fixture
    def mock_client(self):
        return Mock(spec=TypeDBClient)

    @pytest.fixture
    def manager(self, mock_client):
        return EntityManager(mock_client, "mydb")

    def test_insert_relation_does_not_raise(self, manager):
        """insert_relation does not raise (stub implementation)."""
        c = Company(company_id="C001", name="Acme Corp")
        p = Person(username="jdoe", full_name="Jane Doe", age=30)
        emp = Employment(employer=c, employee=p)
        # Should not raise — method is a stub
        manager.insert_relation(emp)


# ---------------------------------------------------------------------------
# Tests: _escape_value
# ---------------------------------------------------------------------------

class TestEntityManagerEscapeValue:
    """Test EntityManager._escape_value helper method."""

    @pytest.fixture
    def manager(self):
        mock_client = Mock(spec=TypeDBClient)
        return EntityManager(mock_client, "mydb")

    def test_escape_string(self, manager):
        """Strings are quoted."""
        assert manager._escape_value("hello") == '"hello"'

    def test_escape_string_with_double_quotes(self, manager):
        """Strings with double quotes are escaped."""
        result = manager._escape_value('test"string')
        # The double quote inside the string should be backslash-escaped
        assert result == chr(34)+"test"+chr(92)+chr(34)+"string"+chr(34)

    def test_escape_integer(self, manager):
        """Integers are converted to string without quotes."""
        assert manager._escape_value(42) == "42"

    def test_escape_float(self, manager):
        """Floats are converted to string without quotes."""
        assert manager._escape_value(3.14) == "3.14"

    def test_escape_boolean_true(self, manager):
        """Boolean True becomes lowercase 'true'."""
        assert manager._escape_value(True) == "true"

    def test_escape_boolean_false(self, manager):
        """Boolean False becomes lowercase 'false'."""
        assert manager._escape_value(False) == "false"

    def test_escape_unsupported_type_raises(self, manager):
        """Unsupported types raise ValueError."""
        with pytest.raises(ValueError, match="Unsupported value type"):
            manager._escape_value([1, 2, 3])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])