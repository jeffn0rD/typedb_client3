# typedb_client3 API Documentation

## Overview

`typedb_client3` is a Python client library for TypeDB v3 that provides a high-level, programmatic interface for interacting with TypeDB databases. The library removes the dependency on writing raw TypeQL (TypeDB Query Language) syntax, making it easier for LLM agents and developers to construct queries correctly and consistently against the TypeDB v3 HTTP API.

All TypeQL examples in this document conform to **TypeDB v3 / TypeQL 3.0** syntax. Key distinctions from v2:
- Schema uses `entity Foo` / `relation Bar` / `attribute Baz` — **not** `Foo sub entity`
- Fetch uses `fetch { "key": $var.attr }` — **not** `fetch $a, $b`
- Role players use `links (role: $var)` — **not** bare tuple syntax in match
- `put` is the idempotent write keyword (v3 only)
- `reduce` replaces `aggregate` for grouping/summaries

---

## Installation

```bash
pip install typedb-client3
```

---

## Quick Start

```python
from typedb_client3 import TypeDBClient, TransactionType, QueryBuilder

# Create client with authentication
client = TypeDBClient(
    base_url="http://localhost:8000",
    username="admin",
    password="password"
)

# Build and execute a query using the fluent QueryBuilder
qb = QueryBuilder()
qb.match().variable("u", "user", {"username": "jdoe"})
qb.fetch({"username": "$u.username", "full-name": "$u.full-name"})

result = client.execute_query(
    database="mydb",
    query=qb.get_tql(),
    transaction_type=TransactionType.READ
)
```

---

## Core Classes

---

### TypeDBClient

The main client class for interacting with the TypeDB v3 HTTP API.

#### Constructor

```python
TypeDBClient(
    base_url: str = "http://localhost:8000",
    username: Optional[str] = None,
    password: Optional[str] = None,
    timeout: int = 30,
    operation_timeouts: Optional[Dict[str, int]] = None
) -> None
```

**Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `base_url` | str | `"http://localhost:8000"` | TypeDB server URL |
| `username` | str | None | Username for JWT authentication |
| `password` | str | None | Password for JWT authentication |
| `timeout` | int | 30 | Default request timeout in seconds |
| `operation_timeouts` | dict | None | Per-operation timeout overrides |

**Raises:** `TypeDBValidationError` if any input parameters are invalid.

**Example:**
```python
client = TypeDBClient(
    base_url="http://localhost:8000",
    username="admin",
    password="password",
    timeout=60,
    operation_timeouts={"schema_operation": 120}
)
```

---

#### Database Management Methods

##### `list_databases() -> List[str]`
List all databases on the server.

```python
databases = client.list_databases()
# ["mydb", "testdb"]
```

##### `database_exists(database: str) -> bool`
Check if a database exists.

```python
if client.database_exists("mydb"):
    print("Database exists")
```

##### `connect_database(database: str) -> bool`
Verify a database exists; creates it if it does not. Returns `True` on success.

```python
client.connect_database("mydb")
```

##### `create_database(database: str) -> None`
Create a new database.

**Raises:** `TypeDBValidationError` if the database already exists.

```python
client.create_database("mydb")
```

##### `delete_database(database: str) -> None`
Delete a database.

**Raises:** `TypeDBValidationError` if the database does not exist.

```python
client.delete_database("mydb")
```

---

#### Schema Methods

##### `load_schema(database: str, schema_path) -> None`
Load a TypeDB v3 schema from a `.tql` file path or a schema string.

**Parameters:**
- `database`: Target database name
- `schema_path`: File path (`str` or `Path`) or raw schema string

**Raises:** `FileNotFoundError` if a file path is given but not found. `TypeDBQueryError` if the schema is invalid.

```python
# From file
client.load_schema("mydb", "schema.tql")

# From string — TypeQL v3 syntax
schema = """
define
  entity user, owns username @key, owns full-name, owns age, plays friendship:friend;
  attribute username, value string;
  attribute full-name, value string;
  attribute age, value integer;
  relation friendship, relates friend @card(0..);
"""
client.load_schema("mydb", schema)
```

##### `get_schema(database: str) -> str`
Retrieve the current schema as a TypeQL v3 `define` string.

```python
schema = client.get_schema("mydb")
print(schema)
```

---

#### Query Execution Methods

##### `execute_query(database, query, transaction_type) -> Dict[str, Any]`
Execute a single TypeQL query.

**Parameters:**
- `database`: Database name
- `query`: TypeQL query string
- `transaction_type`: `TransactionType.READ` or `TransactionType.WRITE` (default: READ)

**Returns:** Query results as a JSON dict.

```python
# READ example — fetch all users
result = client.execute_query(
    database="mydb",
    query='match $u isa user; fetch { "username": $u.username };',
    transaction_type=TransactionType.READ
)

# WRITE example — insert a user
client.execute_query(
    database="mydb",
    query='insert $u isa user, has username "jdoe", has full-name "Jane Doe", has age 30;',
    transaction_type=TransactionType.WRITE
)
```

##### `execute_transaction(database, transaction_type, operations) -> Dict[str, Any]`
Execute multiple operations in a single atomic transaction.

**Parameters:**
- `database`: Database name
- `transaction_type`: `TransactionType.READ` or `TransactionType.WRITE`
- `operations`: List of `{"query": "..."}` dicts

```python
operations = [
    {"query": 'insert $u isa user, has username "jdoe", has full-name "Jane Doe";'},
    {"query": 'insert $u isa user, has username "asmith", has full-name "Alice Smith";'},
]
client.execute_transaction("mydb", TransactionType.WRITE, operations)
```

##### `execute_queries(database, *queries, transaction_type) -> List[Dict[str, Any]]`
Execute a variable number of queries in a single transaction.

```python
client.execute_queries(
    "mydb",
    'insert $u isa user, has username "jdoe";',
    'insert $u isa user, has username "asmith";',
    transaction_type=TransactionType.WRITE
)
```

---

#### Transaction Context

##### `with_transaction(database, transaction_type) -> TransactionContext`
Create a context manager for grouping multiple operations into one transaction.

```python
with client.with_transaction("mydb", TransactionType.WRITE) as tx:
    tx.execute('insert $u isa user, has username "jdoe", has full-name "Jane Doe";')
    tx.execute('insert $u isa user, has username "asmith", has full-name "Alice Smith";')
    # All operations committed atomically on context exit
```

---

#### Data Management Methods

##### `clear_database(database: str) -> None`
Delete all entity and relation instances from a database while preserving the schema.

```python
client.clear_database("mydb")
```

##### `wipe_database(database: str, verify: bool = True) -> bool`
Safely wipe all data by parsing the schema and deleting instances in dependency order (relations before entities, subtypes before supertypes).

**Parameters:**
- `database`: Database name
- `verify`: If `True`, verifies the wipe was complete (default: `True`)

**Returns:** `True` if successful.

```python
client.wipe_database("mydb", verify=True)
```

---

#### Utility Methods

##### `close() -> None`
Close all connections and clear sensitive data from memory.

```python
client.close()
```

##### `get_encrypted_token() -> Optional[str]`
Retrieve the encrypted JWT token for external storage.

##### `set_encrypted_token(encrypted_token: str) -> None`
Restore a previously encrypted token from external storage.

##### `get_token_access_log() -> List[Dict[str, Any]]`
Retrieve the token access audit log.

---

### TransactionType

Enum for specifying transaction mode.

```python
from typedb_client3 import TransactionType

TransactionType.READ   # "read"
TransactionType.WRITE  # "write"
```

---

### TransactionContext

Context manager returned by `client.with_transaction()`. Collects queries and commits them atomically on exit.

#### Methods

##### `execute(query: str) -> None`
Add a raw TypeQL query to the transaction.

```python
with client.with_transaction("mydb", TransactionType.WRITE) as tx:
    tx.execute('insert $u isa user, has username "jdoe";')
```

##### `execute_builder(builder: QueryBuilder) -> None`
Add a query from a `QueryBuilder` instance to the transaction.

**Raises:** `TypeError` if the object does not have a `get_tql()` method.

```python
qb = QueryBuilder()
qb.insert().variable("u", "user", {"username": "jdoe", "full-name": "Jane Doe"})

with client.with_transaction("mydb", TransactionType.WRITE) as tx:
    tx.execute_builder(qb)
```

---

### QueryBuilder

Fluent API for constructing TypeQL v3 queries programmatically without writing raw syntax. Queries are built by chaining method calls and finalized with `build()` or `get_tql()`.

#### Constructor

```python
QueryBuilder(mode: Optional[str] = None)
```

---

#### Query Mode Methods

All mode methods return `self` for chaining.

| Method | TypeQL Keyword | Description |
|---|---|---|
| `match()` | `match` | Start a match/filter stage |
| `insert()` | `insert` | Start an insert stage |
| `put()` | `put` | Idempotent write (checks existence first) |
| `delete()` | `delete` | Start a delete stage |
| `update()` | `update` | Modify data with cardinality ≤ 1 |
| `define()` | `define` | Schema definition |
| `undefine()` | `undefine` | Schema removal |
| `redefine()` | `redefine` | Schema modification |

---

#### Class Methods (Templates)

Convenience constructors for creating reusable query templates.

```python
template = QueryBuilder.match_template()
template = QueryBuilder.insert_template()
template = QueryBuilder.put_template()
template = QueryBuilder.delete_template()
```

---

#### Variable Definition

##### `variable(name, type_name=None, attributes=None) -> QueryBuilder`
Define a typed variable with optional attribute constraints.

**Parameters:**
- `name`: Variable name without `$` prefix
- `type_name`: TypeDB type (e.g., `"user"`)
- `attributes`: Dict of `{attribute-name: value}` constraints

```python
qb = QueryBuilder()
qb.match()
qb.variable("u", "user", {"username": "jdoe"})
# Produces: match $u isa user, has username "jdoe";
```

---

#### Relation Definition

##### `relation(relation_type: str) -> RelationBuilder`
Start building a relation pattern. Returns a `RelationBuilder` for chaining roles.

```python
qb = QueryBuilder()
qb.match()
qb.variable("u", "user", {"username": "jdoe"})
qb.variable("v", "user")
qb.relation("friendship") \
    .role("friend", "$u") \
    .role("friend", "$v") \
    .links() \
    .end_relation()
# Produces: match $u isa user, has username "jdoe"; $v isa user;
#           $r isa friendship, links (friend: $u, friend: $v);
```

---

#### Fetch Clause

##### `fetch(variables: Union[List[str], Dict[str, Any]]) -> QueryBuilder`
Add a `fetch` terminal stage for JSON serialization (TypeQL v3).

**Parameters:**
- `variables`: A list of variable names (fetches all attributes with `$var.*`) or a dict for structured output

```python
# Fetch all attributes of $u
qb.fetch(["u"])
# Produces: fetch { "u": {$u.*} }

# Structured fetch — TypeQL v3 style
qb.fetch({
    "username": "$u.username",
    "full-name": "$u.full-name"
})
# Produces: fetch { "username": $u.username, "full-name": $u.full-name }
```

---

#### Aggregation

##### `reduce(variable, aggregation, groupby=None) -> QueryBuilder`
Add a `reduce` stage for aggregation.

**Parameters:**
- `variable`: Variable to aggregate (e.g., `"$age"`)
- `aggregation`: Function name: `"sum"`, `"count"`, `"mean"`, etc.
- `groupby`: Optional variable name to group by

```python
qb = QueryBuilder()
qb.match().variable("u", "user")
qb.reduce("$age", "mean")
# Produces: match $u isa user; reduce mean($age);

# With groupby
qb.reduce("$s", "sum", "$dept")
# Produces: reduce sum($s) groupby $dept;
```

---

#### Pagination

##### `order_by(variable, attribute) -> QueryBuilder`
Sort results by an attribute.

```python
qb.order_by("u", "username")
# Produces: sort $u has username asc;
```

##### `offset(count: int) -> QueryBuilder`
Skip the first `n` results.

```python
qb.offset(20)
```

##### `limit(count: int) -> QueryBuilder`
Limit results to `n` rows.

```python
qb.limit(10)
```

---

#### Ad-hoc Functions

##### `with_function(fun_def: str) -> QueryBuilder`
Add a `with` preamble for query-level function definitions (TypeQL v3).

```python
qb.with_function(
    "fun path($start: node) -> { node }: "
    "match { ($start, $target) isa edge; } "
    "or { let $via in path($start); ($via, $target) isa edge; }; "
    "return { $target };"
)
```

---

#### Building Queries

##### `build() -> str`
Build and return the complete TypeQL v3 query string.

**Raises:** `ValueError` if no mode has been set.

```python
qb = QueryBuilder()
qb.match().variable("u", "user", {"username": "jdoe"})
qb.fetch({"username": "$u.username"})
print(qb.build())
# match $u isa user, has username "jdoe"; fetch { "username": $u.username };
```

##### `get_tql() -> str`
Return the TypeQL string, using a cached result if the query has not changed.

```python
tql = qb.get_tql()
```

---

#### Template & Reuse Methods

##### `update_variable(name, type_name=None, attributes=None) -> Variable`
Update an existing variable's type or attributes. Clears the query cache so `get_tql()` rebuilds.

```python
# Build a reusable insert template
tmpl = QueryBuilder.insert_template()
tmpl.variable("u", "user")

# First insert
tmpl.update_variable("u", "user", {"username": "jdoe", "full-name": "Jane Doe"})
client.execute_query("mydb", tmpl.get_tql(), TransactionType.WRITE)

# Reuse for second insert
tmpl.update_variable("u", "user", {"username": "asmith", "full-name": "Alice Smith"})
client.execute_query("mydb", tmpl.get_tql(), TransactionType.WRITE)
```

##### `clone() -> QueryBuilder`
Create a deep copy of this builder for independent modification.

```python
base = QueryBuilder.match_template()
base.variable("u", "user")

q1 = base.clone()
q1.update_variable("u", "user", {"username": "jdoe"})

q2 = base.clone()
q2.update_variable("u", "user", {"username": "asmith"})
```

##### `clear_variable(name: str) -> None`
Remove a single variable from the query.

##### `clear_all_variables() -> None`
Remove all variables from the query.

##### `get_variable(name: str) -> Optional[Variable]`
Retrieve a `Variable` object by name for direct manipulation.

---

### Variable

Represents a single TypeQL v3 variable with type and attribute constraints.

#### Constructor

```python
Variable(name: str)
```

#### Methods

All methods return `self` for chaining.

##### `isa(type_name: str) -> Variable`
Set the TypeDB type constraint.

```python
var = Variable("u").isa("user")
# $u isa user
```

##### `has(attribute: str, value: Any) -> Variable`
Add an attribute ownership constraint.

```python
var = Variable("u").isa("user").has("username", "jdoe").has("age", 30)
# $u isa user, has username "jdoe", has age 30
```

##### `label(type_label: str) -> Variable`
Add a `label` constraint for polymorphic type queries (TypeQL v3).

```python
var = Variable("t").label("user")
# $t label user
```

---

### RelationBuilder

Builder for relation patterns within a `QueryBuilder`. Obtained via `QueryBuilder.relation()`.

#### Methods

##### `role(role_name: str, variable: str) -> RelationBuilder`
Add a role player to the relation.

```python
builder.role("friend", "$u").role("friend", "$v")
```

##### `links() -> RelationBuilder`
Use the TypeQL v3 `links` keyword for role player patterns.

```python
builder.links()
# Produces: $r isa friendship, links (friend: $u, friend: $v);
```

##### `as_variable(var_name: str) -> RelationBuilder`
Assign the relation to a named variable.

```python
builder.as_variable("f")
# Produces: $f isa friendship, links (...)
```

##### `end_relation() -> QueryBuilder`
Finalize the relation and return to the parent `QueryBuilder`.

---

## Entity and Relation Base Classes

`typedb_client3` provides `Entity` and `Relation` base classes that you subclass to model your own TypeDB v3 schema. These dataclasses automatically generate TypeQL v3 queries from Python objects, eliminating the need to write raw query strings for CRUD operations.

### Entity Base Class

Subclass `Entity` to define a TypeDB entity type. Set `_type` to the TypeDB type name and `_key_attr` to the primary key attribute (in kebab-case). Fields use `snake_case` and are automatically converted to `kebab-case` for TypeDB.

```python
from dataclasses import dataclass
from typing import Optional
from typedb_client3 import Entity

@dataclass
class Person(Entity):
    _type = "person"
    _key_attr = "username"

    username: str
    full_name: str           # maps to TypeDB attribute: full-name
    age: int
    email: Optional[str] = None
```

#### Generating Queries from Entity Instances

```python
person = Person(username="jdoe", full_name="Jane Doe", age=30, email="jdoe@example.com")

# INSERT query
insert_q = person.to_insert_query()
# insert $p isa person, has username "jdoe", has full-name "Jane Doe", has age 30, has email "jdoe@example.com";

# MATCH query (by key attribute)
match_q = person.to_match_query()
# match $p isa person, has username "jdoe";

# Parameterized INSERT (injection-safe)
query, params = person.to_parameterized_insert_query()

# Parameterized MATCH (injection-safe)
query, params = person.to_parameterized_match_query()
```

#### Executing Entity Queries

```python
from typedb_client3 import TypeDBClient, TransactionType

client = TypeDBClient(base_url="http://localhost:8000", username="admin", password="password")

person = Person(username="jdoe", full_name="Jane Doe", age=30)

# Insert
client.execute_query("mydb", person.to_insert_query(), TransactionType.WRITE)

# Match
result = client.execute_query("mydb", person.to_match_query(), TransactionType.READ)
```

---

### Relation Base Class

Subclass `Relation` to define a TypeDB relation type. Set `_type` to the relation type name and `_roles` to the list of role names.

```python
from dataclasses import dataclass
from typedb_client3 import Relation, Entity

@dataclass
class Friendship(Relation):
    _type = "friendship"
    _roles = ["friend"]

    friend1: Person
    friend2: Person

@dataclass
class Employment(Relation):
    _type = "employment"
    _roles = ["employer", "employee"]

    employer: "Company"
    employee: Person
```

#### Generating Relation Queries

```python
p1 = Person(username="jdoe", full_name="Jane Doe", age=30)
p2 = Person(username="asmith", full_name="Alice Smith", age=25)

friendship = Friendship(friend1=p1, friend2=p2)

# Generate INSERT query — pass role-name to variable-name mapping
insert_q = friendship.to_insert_query({"friend": "p1"})
# (friend: $p1) isa friendship;
```

#### Full Relation Insert Workflow

```python
# 1. Insert both entities first
client.execute_query("mydb", p1.to_insert_query(), TransactionType.WRITE)
client.execute_query("mydb", p2.to_insert_query(), TransactionType.WRITE)

# 2. Insert the relation using a match+insert pipeline
relation_query = """
match
  $p1 isa person, has username "jdoe";
  $p2 isa person, has username "asmith";
insert
  (friend: $p1, friend: $p2) isa friendship;
"""
client.execute_query("mydb", relation_query, TransactionType.WRITE)
```

---

### Defining a Complete Schema with Entity and Relation Classes

The following example shows how to model a domain schema using the base classes and load it into TypeDB v3.

```python
from dataclasses import dataclass
from typing import Optional
from typedb_client3 import Entity, Relation, TypeDBClient, TransactionType

# --- Entity Definitions ---

@dataclass
class Company(Entity):
    _type = "company"
    _key_attr = "company-id"

    company_id: str
    name: str
    industry: Optional[str] = None

@dataclass
class Employee(Entity):
    _type = "employee"
    _key_attr = "employee-id"

    employee_id: str
    full_name: str
    role: str

# --- Relation Definitions ---

@dataclass
class Employment(Relation):
    _type = "employment"
    _roles = ["employer", "employee"]

    employer: Company
    employee: Employee

# --- Schema (TypeQL v3) ---

SCHEMA = """
define
  entity company, owns company-id @key, owns name, owns industry,
    plays employment:employer;
  entity employee, owns employee-id @key, owns full-name, owns role,
    plays employment:employee;
  attribute company-id, value string;
  attribute name, value string;
  attribute industry, value string;
  attribute employee-id, value string;
  attribute full-name, value string;
  attribute role, value string;
  relation employment, relates employer, relates employee;
"""

# --- Usage ---

client = TypeDBClient(base_url="http://localhost:8000", username="admin", password="password")
client.create_database("hr")
client.load_schema("hr", SCHEMA)

# Insert entities
acme = Company(company_id="C001", name="Acme Corp", industry="Technology")
emp  = Employee(employee_id="E001", full_name="Jane Doe", role="Engineer")

client.execute_query("hr", acme.to_insert_query(), TransactionType.WRITE)
client.execute_query("hr", emp.to_insert_query(), TransactionType.WRITE)

# Insert relation
relation_query = """
match
  $c isa company, has company-id "C001";
  $e isa employee, has employee-id "E001";
insert
  (employer: $c, employee: $e) isa employment;
"""
client.execute_query("hr", relation_query, TransactionType.WRITE)
```

---

### EntityManager

High-level CRUD manager that wraps `TypeDBClient` and `QueryBuilder` for common entity operations.

#### Constructor

```python
EntityManager(client: TypeDBClient, database: str)
```

```python
from typedb_client3 import EntityManager

manager = EntityManager(client, "mydb")
```

#### Methods

##### `insert(entity: Entity) -> None`
Insert an entity. Raises `TypeDBQueryError` if the entity already exists.

```python
person = Person(username="jdoe", full_name="Jane Doe", age=30)
manager.insert(person)
```

##### `put(entity: Entity) -> None`
Idempotent insert — uses TypeQL v3 `put` to check existence before inserting.

```python
manager.put(person)
```

##### `fetch_one(entity_type, filters) -> Optional[T]`
Fetch a single entity matching the given attribute filters.

```python
person = manager.fetch_one(Person, {"username": "jdoe"})
```

##### `fetch_all(entity_type, filters=None) -> List[T]`
Fetch all entities of a type, with optional attribute filters.

```python
all_persons = manager.fetch_all(Person)
engineers   = manager.fetch_all(Employee, {"role": "Engineer"})
```

##### `exists(entity_type, key_value) -> bool`
Check if an entity with the given key value exists.

```python
if manager.exists(Person, "jdoe"):
    print("Person exists")
```

##### `delete(entity: Entity) -> None`
Delete an entity by matching on its key attribute.

```python
manager.delete(person)
```

---

## Exceptions

All exceptions inherit from `TypeDBError`.

| Exception | Description |
|---|---|
| `TypeDBConnectionError` | Network or connection failure |
| `TypeDBAuthenticationError` | JWT authentication failure |
| `TypeDBQueryError` | Query execution error (includes `.query` and `.details` attributes) |
| `TypeDBServerError` | Server-side error |
| `TypeDBValidationError` | Input validation error (e.g., duplicate database) |

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
```

---

## Authentication & Security

### SecureTokenManager

Manages JWT tokens with in-memory encryption for secure storage and retrieval.

```python
from typedb_client3 import SecureTokenManager

manager = SecureTokenManager()
# Tokens are encrypted at rest and cleared from memory on close
```

### Parameterized Queries

Use `to_parameterized_insert_query()` and `to_parameterized_match_query()` on entity instances to generate injection-safe queries with UUID-based placeholders.

```python
person = Person(username="jdoe", full_name="Jane Doe", age=30)
query, params = person.to_parameterized_insert_query()
# query: "insert $p isa person, has username $person_username_a1b2c3d4, ..."
# params: {"$person_username_a1b2c3d4": "jdoe", ...}
```

---

## Validation & Connection Pooling

### Validation Functions

| Function | Description |
|---|---|
| `validate_base_url(url)` | Normalize and validate server URL |
| `validate_credentials(username, password)` | Validate auth credentials |
| `validate_timeout(timeout)` | Validate timeout value |
| `validate_operation_timeouts(timeouts)` | Validate per-operation timeout dict |

### Connection Pooling

`create_optimized_session()` returns a `requests.Session` with connection pooling configured via:

| Constant | Default | Description |
|---|---|---|
| `DEFAULT_POOL_CONNECTIONS` | 10 | Number of connection pools |
| `DEFAULT_POOL_MAXSIZE` | 100 | Max connections per pool |
| `DEFAULT_MAX_RETRIES` | 3 | Retry attempts on failure |
| `DEFAULT_BACKOFF_FACTOR` | 0.3 | Exponential backoff factor |

---

## Advanced Examples

### Structured Fetch with Nested Output (TypeQL v3)

```python
# Retrieve companies and their employees in nested JSON
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

### Aggregation with reduce (TypeQL v3)

```python
# Count employees per company
query = """
match
  $c isa company;
  $e isa employee;
  ($c, $e) isa employment;
reduce $count = count groupby $c;
"""
result = client.execute_query("hr", query, TransactionType.READ)
```

### Idempotent Writes with put

```python
# put checks existence before inserting — safe for concurrent writes
qb = QueryBuilder()
qb.put().variable("p", "person", {"username": "jdoe", "full-name": "Jane Doe", "age": 30})
client.execute_query("mydb", qb.get_tql(), TransactionType.WRITE)
```

### Polymorphic Query with label (TypeQL v3)

```python
# Retrieve all users with their type label
query = """
match $u isa user, has full-name $n;
fetch {
  "name": $n,
  "type": $u.label
};
"""
result = client.execute_query("mydb", query, TransactionType.READ)
```

### Reusable Template for Bulk Insert

```python
tmpl = QueryBuilder.insert_template()
tmpl.variable("p", "person")

people = [
    {"username": "jdoe",   "full-name": "Jane Doe",    "age": 30},
    {"username": "asmith", "full-name": "Alice Smith",  "age": 25},
    {"username": "bjones", "full-name": "Bob Jones",    "age": 40},
]

for attrs in people:
    tmpl.update_variable("p", "person", attrs)
    client.execute_query("mydb", tmpl.get_tql(), TransactionType.WRITE)
```

### Transaction with QueryBuilder

```python
q1 = QueryBuilder().insert()
q1.variable("p", "person", {"username": "jdoe", "full-name": "Jane Doe"})

q2 = QueryBuilder().insert()
q2.variable("p", "person", {"username": "asmith", "full-name": "Alice Smith"})

with client.with_transaction("mydb", TransactionType.WRITE) as tx:
    tx.execute_builder(q1)
    tx.execute_builder(q2)
```

### Ad-hoc Recursive Function with with (TypeQL v3)

```python
query = """
with fun reachable($start: node) -> { node }:
  match { ($start, $target) isa edge; }
     or { let $via in reachable($start); ($via, $target) isa edge; };
  return { $target };
match $n isa node, has node-id "A";
let $r in reachable($n);
fetch { "reachable": $r.node-id };
"""
result = client.execute_query("graph", query, TransactionType.READ)
```

---

## Best Practices

1. **Use QueryBuilder over raw strings** — avoids syntax errors and is LLM-friendly
2. **Use `put` for idempotent writes** — prevents duplicates in concurrent scenarios
3. **Use transactions for bulk operations** — groups writes atomically for performance and safety
4. **Use parameterized queries** — call `to_parameterized_insert_query()` for user-supplied data
5. **Use `fetch { }` with explicit keys** — TypeQL v3 fetch requires structured JSON output syntax
6. **Use `links` in match patterns** — TypeQL v3 uses `links (role: $var)` not bare tuple syntax
7. **Define schemas with `entity Foo`** — TypeQL v3 schema syntax, not `Foo sub entity`
8. **Call `client.close()`** — releases connections and clears tokens from memory

---

## License

[Add license information here]