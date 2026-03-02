# typedb_client3 - TypeDB v3 Python Client Library

A modern Python client library for TypeDB v3 that provides a high-level, programmatic interface for database operations. This library removes the dependency on writing raw TypeQL (TypeDB Query Language) syntax, making it easier for LLM agents and developers to construct queries correctly and efficiently against the TypeDB v3 HTTP API.

> **All TypeQL examples in this document use TypeDB v3 / TypeQL 3.0 syntax.**
> Key distinctions from v2: schema uses `entity Foo` (not `Foo sub entity`), fetch uses `fetch { "key": $var.attr }` (not `fetch $a, $b`), and role players use `links (role: $var)`.

## Why typedb_client3?

This library was developed to address a critical need: **removing the dependency on TypeDB 3 TQL syntax** which most LLM coding agents struggle to construct correctly. By providing a programmatic, fluent API, it enables:

- **AI-Friendly Construction**: LLMs generate method calls instead of raw syntax — no more v2/v3 syntax confusion
- **Developer Productivity**: IDE autocomplete and type hints throughout
- **Reusable Templates**: Build query templates once, execute many times with parameter updates
- **Injection Safety**: Parameterized query generation for user-supplied data
- **Full TypeDB v3 Coverage**: Native support for `put`, `links`, `fetch {}`, `reduce`, `with`

---

## Features

### TypeDB v3 Full API Support
- Complete HTTP API coverage for TypeDB v3
- Modern query keywords: `fetch`, `put`, `links`, `label`, `reduce`, `with`
- Schema operations: `define`, `undefine`, `redefine`
- Database management: create, delete, list, wipe

### Fluent Query Builder
- Chainable method API — no raw TypeQL required
- Reusable query templates with parameter updates
- Deep clone support for query variations
- Produces valid TypeQL v3 strings via `get_tql()`

### Entity & Relation Base Classes
- Dataclass-based `Entity` and `Relation` base classes
- Subclass to model any TypeDB v3 schema
- Automatic `snake_case` → `kebab-case` field mapping
- Auto-generated INSERT, MATCH, and parameterized queries

### Transaction Support
- Atomic multi-operation transactions via context manager
- `execute_builder()` for QueryBuilder integration
- Batch operations for efficient bulk writes

### Security & Performance
- JWT authentication with encrypted token storage
- Connection pooling with configurable pool sizes
- Parameterized queries to prevent injection attacks
- Per-operation timeout configuration

---

## Installation

```bash
pip install typedb-client3
```

---

## Quick Start

### Connect and Query

```python
from typedb_client3 import TypeDBClient, TransactionType, QueryBuilder

client = TypeDBClient(
    base_url="http://localhost:8000",
    username="admin",
    password="password"
)

# Build a query — no raw TypeQL needed
qb = QueryBuilder()
qb.match().variable("u", "user", {"username": "jdoe"})
qb.fetch({"username": "$u.username", "full-name": "$u.full-name"})

result = client.execute_query("mydb", qb.get_tql(), TransactionType.READ)
```

### Define Your Schema as Python Classes

```python
from dataclasses import dataclass
from typing import Optional
from typedb_client3 import Entity, Relation

@dataclass
class Person(Entity):
    _type = "person"
    _key_attr = "username"

    username: str
    full_name: str        # maps to TypeDB attribute: full-name
    age: int
    email: Optional[str] = None

@dataclass
class Friendship(Relation):
    _type = "friendship"
    _roles = ["friend"]

    friend1: Person
    friend2: Person
```

### Insert and Query Entities

```python
person = Person(username="jdoe", full_name="Jane Doe", age=30)

# Auto-generated TypeQL v3 INSERT query
client.execute_query("mydb", person.to_insert_query(), TransactionType.WRITE)
# insert $p isa person, has username "jdoe", has full-name "Jane Doe", has age 30;

# Auto-generated MATCH query by key
result = client.execute_query("mydb", person.to_match_query(), TransactionType.READ)
# match $p isa person, has username "jdoe";
```

---

## Core Capabilities

### 1. Database Management

```python
# List, create, check, connect
databases = client.list_databases()
client.create_database("mydb")
client.database_exists("mydb")
client.connect_database("mydb")   # creates if not exists

# Clear data (keep schema) or wipe entirely
client.clear_database("mydb")
client.wipe_database("mydb", verify=True)

# Delete
client.delete_database("mydb")
```

### 2. Schema Operations

```python
# Load from file
client.load_schema("mydb", "schema.tql")

# Load from string — TypeQL v3 syntax
schema = """
define
  entity person, owns username @key, owns full-name, owns age,
    plays friendship:friend;
  attribute username, value string;
  attribute full-name, value string;
  attribute age, value integer;
  relation friendship, relates friend @card(0..);
"""
client.load_schema("mydb", schema)

# Retrieve current schema
print(client.get_schema("mydb"))
```

### 3. Query Execution

```python
# Single query
result = client.execute_query(
    database="mydb",
    query='match $u isa person; fetch { "username": $u.username };',
    transaction_type=TransactionType.READ
)

# Multiple queries in one transaction
client.execute_queries(
    "mydb",
    'insert $u isa person, has username "jdoe", has full-name "Jane Doe";',
    'insert $u isa person, has username "asmith", has full-name "Alice Smith";',
    transaction_type=TransactionType.WRITE
)
```

### 4. Fluent Query Builder

```python
from typedb_client3 import QueryBuilder

# Match with relation using TypeQL v3 links keyword
qb = QueryBuilder()
qb.match()
qb.variable("u", "person", {"username": "jdoe"})
qb.variable("v", "person")
qb.relation("friendship") \
    .role("friend", "$u") \
    .role("friend", "$v") \
    .links() \
    .end_relation()
qb.fetch({"friend": "$v.username"})
qb.limit(10)

result = client.execute_query("mydb", qb.get_tql(), TransactionType.READ)
```

### 5. Reusable Query Templates

```python
# Build once, execute many times
tmpl = QueryBuilder.insert_template()
tmpl.variable("p", "person")

people = [
    {"username": "jdoe",   "full-name": "Jane Doe",   "age": 30},
    {"username": "asmith", "full-name": "Alice Smith", "age": 25},
]

for attrs in people:
    tmpl.update_variable("p", "person", attrs)
    client.execute_query("mydb", tmpl.get_tql(), TransactionType.WRITE)

# Clone for independent variations
base = QueryBuilder.match_template()
base.variable("p", "person")

q1 = base.clone()
q1.update_variable("p", "person", {"username": "jdoe"})

q2 = base.clone()
q2.update_variable("p", "person", {"username": "asmith"})
```

### 6. Transactions

```python
# Context manager — all operations committed atomically
with client.with_transaction("mydb", TransactionType.WRITE) as tx:
    tx.execute('insert $p isa person, has username "jdoe";')
    tx.execute('insert $p isa person, has username "asmith";')

# With QueryBuilder
q1 = QueryBuilder().insert()
q1.variable("p", "person", {"username": "jdoe", "full-name": "Jane Doe"})

q2 = QueryBuilder().insert()
q2.variable("p", "person", {"username": "asmith", "full-name": "Alice Smith"})

with client.with_transaction("mydb", TransactionType.WRITE) as tx:
    tx.execute_builder(q1)
    tx.execute_builder(q2)
```

### 7. Entity Manager

```python
from typedb_client3 import EntityManager

manager = EntityManager(client, "mydb")

person = Person(username="jdoe", full_name="Jane Doe", age=30)

manager.put(person)                                        # idempotent insert
manager.insert(person)                                     # strict insert
manager.exists(Person, "jdoe")                             # check by key
manager.fetch_one(Person, {"username": "jdoe"})            # fetch single
manager.fetch_all(Person)                                  # fetch all
manager.delete(person)                                     # delete
```

### 8. Aggregation and Analytics

```python
# Count instances grouped by type — TypeQL v3 reduce
query = """
match
  $p isa person, has age $a;
reduce $avg_age = mean($a);
"""
result = client.execute_query("mydb", query, TransactionType.READ)

# Structured nested fetch — TypeQL v3
query = """
match $c isa company;
fetch {
  "company": $c.name,
  "employees": [
    match $e isa employee; ($c, $e) isa employment;
    fetch { "name": $e.full-name, "role": $e.role }
  ]
};
"""
result = client.execute_query("hr", query, TransactionType.READ)
```

---

## TypeQL v3 Syntax Reference (Quick Guide)

| Concept | TypeQL v3 ✅ | TypeQL v2 ❌ |
|---|---|---|
| Entity definition | `entity person` | `person sub entity` |
| Attribute definition | `attribute username, value string` | `username sub attribute, datatype string` |
| Relation definition | `relation friendship, relates friend` | `friendship sub relation, relates friend` |
| Role player pattern | `$r isa friendship, links (friend: $u)` | `$r ($u) isa friendship` |
| Fetch output | `fetch { "name": $u.username }` | `fetch $u` |
| Idempotent write | `put $u isa person, has username "x"` | *(not available)* |
| Aggregation | `reduce $c = count groupby $x` | `get; count;` |

---

## Entity & Relation Base Classes

Subclass `Entity` and `Relation` to model your TypeDB v3 schema in Python. Fields use `snake_case` and are automatically converted to `kebab-case` for TypeDB attribute names.

```python
from dataclasses import dataclass
from typing import Optional
from typedb_client3 import Entity, Relation

@dataclass
class Company(Entity):
    _type = "company"
    _key_attr = "company-id"

    company_id: str          # maps to: company-id
    name: str
    industry: Optional[str] = None

@dataclass
class Employee(Entity):
    _type = "employee"
    _key_attr = "employee-id"

    employee_id: str         # maps to: employee-id
    full_name: str           # maps to: full-name
    role: str

@dataclass
class Employment(Relation):
    _type = "employment"
    _roles = ["employer", "employee"]

    employer: Company
    employee: Employee
```

### Auto-Generated Queries

```python
emp = Employee(employee_id="E001", full_name="Jane Doe", role="Engineer")

emp.to_insert_query()
# insert $e isa employee, has employee-id "E001", has full-name "Jane Doe", has role "Engineer";

emp.to_match_query()
# match $e isa employee, has employee-id "E001";

query, params = emp.to_parameterized_insert_query()
# Injection-safe parameterized query
```

---

## Error Handling

```python
from typedb_client3 import (
    TypeDBConnectionError,
    TypeDBAuthenticationError,
    TypeDBQueryError,
    TypeDBServerError,
    TypeDBValidationError
)

try:
    client.execute_query("mydb", tql, TransactionType.WRITE)
except TypeDBQueryError as e:
    print(f"Query failed: {e}")
    print(f"Query:   {e.query}")
    print(f"Details: {e.details}")
except TypeDBConnectionError as e:
    print(f"Connection failed: {e}")
except TypeDBValidationError as e:
    print(f"Validation error: {e}")
finally:
    client.close()
```

---

## Project Structure

```
typedb_client3/
├── client.py            # TypeDBClient — HTTP API, auth, database management
├── query_builder.py     # QueryBuilder, Variable, RelationBuilder
├── entities.py          # Entity and Relation base classes
├── entity_manager.py    # EntityManager — high-level CRUD
├── transactions.py      # TransactionContext
├── auth.py              # SecureTokenManager — JWT handling
├── validation.py        # Input validation and connection pooling
├── exceptions.py        # Exception hierarchy
└── tests/               # Unit and integration test suite
```

---

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest tests/ -v

# Unit tests only
pytest tests/ -v -m unit

# Integration tests (requires running TypeDB server)
pytest tests/ -v -m integration

# With coverage
pytest tests/ --cov=typedb_client3 --cov-report=html
```

**Test server:** `http://localhost:8000` — credentials: `admin` / `password`

---

## Documentation

- **Full API Reference**: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **TypeDB v3**: https://typedb.com/docs/

---

## License

[Add license information here]