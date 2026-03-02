# typedb_client3 API Documentation

## Overview

`typedb_client3` is a Python client library for TypeDB v3 that provides a high-level, programmatic interface for interacting with TypeDB databases. The library removes the dependency on writing raw TypeQL (TypeDB Query Language) syntax, making it easier for LLM agents and developers to construct queries correctly.

**Key Features:**
- TypeDB v3 HTTP API support (fetch, put, links, label, reduce, with)
- Fluent query builder with reusable templates
- Transaction support for multi-operation workflows
- Entity/Relation abstractions with ORM-like functionality
- JWT authentication with secure token management
- Connection pooling and optimized session management
- Database management operations

## Installation

```bash
pip install typedb-client3
```

## Quick Start

```python
from typedb_client3 import TypeDBClient, TransactionType

# Create client with authentication
client = TypeDBClient(
    base_url="http://localhost:8000",
    username="admin",
    password="password"
)

# Execute a simple query
result = client.execute_query(
    database="mydb",
    query='match $a isa actor; fetch $a;',
    transaction_type=TransactionType.READ
)
```

---

## Core Classes

### TypeDBClient

The main client class for interacting with TypeDB v3 HTTP API.

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
- `base_url`: TypeDB server URL (default: "http://localhost:8000")
- `username`: Optional username for authentication
- `password`: Optional password for authentication
- `timeout`: Default request timeout in seconds (default: 30)
- `operation_timeouts`: Optional dict of operation-specific timeouts

**Example:**
```python
client = TypeDBClient(
    base_url="http://localhost:8000",
    username="admin",
    password="password",
    timeout=60
)
```

#### Methods

##### Database Management

###### `connect_database(database: str) -> bool`
Verify database exists and set as current. Creates database if it doesn't exist.

**Parameters:**
- `database`: Database name

**Returns:** True if database exists or was created

**Example:**
```python
client.connect_database("mydb")
```

###### `list_databases() -> List[str]`
List all databases on the server.

**Returns:** List of database names

**Example:**
```python
databases = client.list_databases()
print(f"Available databases: {databases}")
```

###### `create_database(database: str) -> None`
Create a new database.

**Parameters:**
- `database`: Database name to create

**Raises:**
- `TypeDBValidationError`: If database already exists
- `TypeDBServerError`: If server error occurs

**Example:**
```python
client.create_database("mydb")
```

###### `delete_database(database: str) -> None`
Delete a database.

**Parameters:**
- `database`: Database name to delete

**Raises:**
- `TypeDBValidationError`: If database doesn't exist
- `TypeDBServerError`: If server error occurs

**Example:**
```python
client.delete_database("mydb")
```

###### `database_exists(database: str) -> bool`
Check if database exists.

**Parameters:**
- `database`: Database name

**Returns:** True if database exists

**Example:**
```python
if client.database_exists("mydb"):
    print("Database exists")
```

##### Query Execution

###### `execute_query(database: str, query: str, transaction_type: TransactionType = TransactionType.READ) -> Dict[str, Any]`
Execute a raw TypeQL query.

**Parameters:**
- `database`: Database name
- `query`: TypeQL query string
- `transaction_type`: READ or WRITE transaction (default: READ)

**Returns:** Query results as JSON

**Example:**
```python
result = client.execute_query(
    database="mydb",
    query='match $a isa actor; fetch $a;',
    transaction_type=TransactionType.READ
)
```

###### `execute_transaction(database: str, transaction_type: TransactionType, operations: List[Dict[str, Any]]) -> Dict[str, Any]`
Execute multiple operations in a single transaction.

**Parameters:**
- `database`: Database name
- `transaction_type`: READ or WRITE
- `operations`: List of operation dictionaries

**Returns:** Combined results

**Example:**
```python
operations = [
    {"query": 'insert $a isa actor, has actor-id "A1";'},
    {"query": 'insert $a isa actor, has actor-id "A2";'},
]
result = client.execute_transaction(
    "mydb", 
    TransactionType.WRITE, 
    operations
)
```

###### `execute_queries(database: str, *queries: str, transaction_type: TransactionType = TransactionType.WRITE) -> List[Dict[str, Any]]`
Execute multiple queries in a single transaction.

**Parameters:**
- `database`: Database name
- `*queries`: Variable number of TypeQL queries
- `transaction_type`: READ or WRITE (default: WRITE)

**Returns:** List of results for each query

**Example:**
```python
results = client.execute_queries(
    "mydb",
    'insert $a isa actor, has actor-id "A1";',
    'insert $a isa actor, has actor-id "A2";',
    transaction_type=TransactionType.WRITE
)
```

##### Schema Operations

###### `load_schema(database: str, schema_path) -> None`
Load TypeDB schema from TQL file or string.

**Parameters:**
- `database`: Database name
- `schema_path`: Path to .tql schema file (str or Path), or schema string

**Raises:**
- `FileNotFoundError`: If schema file doesn't exist
- `TypeDBQueryError`: If schema is invalid

**Example:**
```python
# From file
client.load_schema("mydb", "schema.tql")

# From string
schema = """
define actor sub entity, has actor-id, has id-label;
"""
client.load_schema("mydb", schema)
```

###### `get_schema(database: str) -> str`
Fetch the database schema as TypeQL define string.

**Parameters:**
- `database`: Database name

**Returns:** TypeQL schema string (plain text)

**Example:**
```python
schema = client.get_schema("mydb")
print(schema)
```

##### Data Management

###### `clear_database(database: str) -> None`
Clear all data from database (keeps schema).

**Parameters:**
- `database`: Database name

**Example:**
```python
client.clear_database("mydb")
```

###### `wipe_database(database: str, verify: bool = True) -> bool`
Wipe all data from database safely (delete in dependency order).

**Parameters:**
- `database`: Database name to wipe
- `verify`: Whether to verify the wipe was complete (default: True)

**Returns:** True if wipe was successful and verified

**Example:**
```python
client.wipe_database("mydb", verify=True)
```

##### Transaction Context

###### `with_transaction(database: str, transaction_type: TransactionType) -> TransactionContext`
Create a transaction context for executing multiple operations.

**Parameters:**
- `database`: Database name
- `transaction_type`: READ or WRITE

**Returns:** TransactionContext manager

**Example:**
```python
with client.with_transaction("mydb", TransactionType.WRITE) as tx:
    tx.execute('insert $a isa actor, has actor-id "A1";')
    tx.execute('insert $a isa actor, has actor-id "A2";')
    # All operations committed when exiting context
```

##### Utility Methods

###### `close() -> None`
Close all connections and cleanup resources.

**Example:**
```python
client.close()
```

###### `get_encrypted_token() -> Optional[str]`
Get the encrypted token for external storage.

**Returns:** Encrypted token string

###### `set_encrypted_token(encrypted_token: str) -> None`
Set an encrypted token retrieved from external storage.

**Parameters:**
- `encrypted_token`: Previously encrypted token string

---

### TransactionType

Enum for transaction types.

```python
class TransactionType(Enum):
    READ = "read"
    WRITE = "write"
```

---

### QueryBuilder

Fluent API for building TypeQL v3 queries without raw syntax.

#### Constructor

```python
QueryBuilder(mode: Optional[str] = None)
```

#### Query Mode Methods

###### `match() -> QueryBuilder`
Start a MATCH query.

**Returns:** Self for method chaining

**Example:**
```python
query = QueryBuilder().match().variable("x", "actor")
```

###### `insert() -> QueryBuilder`
Start an INSERT query.

**Returns:** Self for method chaining

###### `put() -> QueryBuilder`
Start a PUT query (TypeDB v3: idempotent write).

**Returns:** Self for method chaining

**Example:**
```python
query = QueryBuilder().put().variable("x", "actor", {"actor-id": "A1"})
```

###### `delete() -> QueryBuilder`
Start a DELETE query.

**Returns:** Self for method chaining

###### `update() -> QueryBuilder`
Start an UPDATE query (TypeDB v3: modify existing data).

**Returns:** Self for method chaining

###### `define() -> QueryBuilder`
Start a DEFINE query (schema definition).

**Returns:** Self for method chaining

###### `undefine() -> QueryBuilder`
Start a UNDEFINE query (schema removal).

**Returns:** Self for method chaining

###### `redefine() -> QueryBuilder`
Start a REDEFINE query (schema modification).

**Returns:** Self for method chaining

#### Variable Definition

###### `variable(name: str, type_name: Optional[str] = None, attributes: Optional[Dict[str, Any]] = None) -> QueryBuilder`
Define a variable in the query.

**Parameters:**
- `name`: Variable name (without $)
- `type_name`: Optional TypeDB type
- `attributes`: Optional attribute constraints

**Returns:** Self for method chaining

**Example:**
```python
query = QueryBuilder()
    .match()
    .variable("x", "actor", {"actor-id": "A1"})
```

#### Relations

###### `relation(relation_type: str) -> RelationBuilder`
Start defining a relation.

**Parameters:**
- `relation_type`: TypeDB relation type name

**Returns:** RelationBuilder for chaining

**Example:**
```python
query = QueryBuilder()
    .insert()
    .relation("messaging")
        .role("producer", "$p")
        .role("consumer", "$c")
        .role("message", "$m")
    .end_relation()
```

#### Query Clauses

###### `fetch(variables: Union[List[str], Dict[str, Any]]) -> QueryBuilder`
Add FETCH clause (TypeDB v3 syntax).

**Parameters:**
- `variables`: List of variable names or dict for nested fetch

**Returns:** Self for method chaining

**Example:**
```python
# Simple fetch
query.fetch(["message", "aggregate"])

# Nested fetch
query.fetch({
    "name": "$p.name",
    "titles": {
        "match": [...],
        "fetch": [...]
    }
})
```

###### `order_by(variable: str, attribute: str) -> QueryBuilder`
Add ORDER BY clause.

**Parameters:**
- `variable`: Variable name
- `attribute`: Attribute to order by

**Returns:** Self for method chaining

**Example:**
```python
query.order_by("x", "actor-id")
```

###### `offset(count: int) -> QueryBuilder`
Add OFFSET clause.

**Parameters:**
- `count`: Number of rows to skip

**Returns:** Self for method chaining

**Example:**
```python
query.offset(10)
```

###### `limit(count: int) -> QueryBuilder`
Add LIMIT clause.

**Parameters:**
- `count`: Maximum number of rows to return

**Returns:** Self for method chaining

**Example:**
```python
query.limit(100)
```

###### `reduce(variable: str, aggregation: str, groupby: Optional[str] = None) -> QueryBuilder`
Add REDUCE clause for aggregation.

**Parameters:**
- `variable`: Variable to aggregate (e.g., "$s")
- `aggregation`: Aggregation function (e.g., "sum", "count", "mean")
- `groupby`: Optional variable to group by

**Returns:** Self for method chaining

**Example:**
```python
query.reduce("$s", "sum", "$f")  # sum($s) groupby $f
```

###### `with_function(fun_def: str) -> QueryBuilder`
Add WITH clause for ad-hoc function definition.

**Parameters:**
- `fun_def`: Function definition string

**Returns:** Self for method chaining

**Example:**
```python
query.with_function('fun path($start: node) -> { node }: ...')
```

#### Building and Execution

###### `build() -> str`
Build and return the complete TypeQL query string.

**Returns:** Valid TypeDB v3 TypeQL query string

**Example:**
```python
query_str = query.build()
```

###### `get_tql() -> str`
Get the TypeQL string from the query instance.

**Returns:** TypeQL query string (may be cached)

**Example:**
```python
tql = query.get_tql()
```

#### Query Templates

###### `match_template() -> QueryBuilder` (classmethod)
Create a reusable MATCH query template.

**Returns:** New QueryBuilder instance

**Example:**
```python
template = QueryBuilder.match_template()
template.variable("x", "actor")
```

###### `insert_template() -> QueryBuilder` (classmethod)
Create a reusable INSERT query template.

**Returns:** New QueryBuilder instance

###### `put_template() -> QueryBuilder` (classmethod)
Create a reusable PUT query template.

**Returns:** New QueryBuilder instance

###### `delete_template() -> QueryBuilder` (classmethod)
Create a reusable DELETE query template.

**Returns:** New QueryBuilder instance

#### Variable Update Methods

###### `update_variable(name: str, type_name: Optional[str] = None, attributes: Optional[Dict[str, Any]] = None) -> Variable`
Update an existing variable's type or attributes.

**Parameters:**
- `name`: Variable name (without $)
- `type_name`: New TypeDB type (or None to keep existing)
- `attributes`: New attributes (or None to keep existing)

**Returns:** Updated Variable object

**Example:**
```python
# Create reusable insert template
insert_query = QueryBuilder.insert_template()

# Use for first entity
insert_query.update_variable("a", "actor", {"actor-id": "A1"})
tql1 = insert_query.get_tql()

# Update for second entity
insert_query.update_variable("a", "actor", {"actor-id": "A2"})
tql2 = insert_query.get_tql()
```

###### `clear_variable(name: str) -> None`
Remove a variable from the query.

**Parameters:**
- `name`: Variable name (without $)

###### `clear_all_variables() -> None`
Remove all variables from the query.

###### `get_variable(name: str) -> Optional[Variable]`
Get a variable by name.

**Parameters:**
- `name`: Variable name (without $)

**Returns:** Variable object or None

###### `clone() -> QueryBuilder`
Create a deep copy of this query builder for reuse.

**Returns:** New QueryBuilder instance with same configuration

**Example:**
```python
# Create base template
base_query = QueryBuilder.match_template()
base_query.variable("x", "actor")

# Clone for different executions
query1 = base_query.clone()
query1.update_variable("x", "actor", {"actor-id": "A1"})

query2 = base_query.clone()
query2.update_variable("x", "actor", {"actor-id": "A2"})
```

---

### Variable

Represents a TypeQL v3 variable with type and constraints.

#### Constructor

```python
Variable(name: str)
```

#### Methods

###### `isa(type_name: str) -> Variable`
Set the TypeDB type of this variable.

**Parameters:**
- `type_name`: Entity or relation type name

**Returns:** Self for method chaining

**Example:**
```python
var = Variable("x").isa("actor")
```

###### `has(attribute: str, value: Any) -> Variable`
Add an attribute constraint.

**Parameters:**
- `attribute`: Attribute name
- `value`: Attribute value (will be properly escaped)

**Returns:** Self for method chaining

**Example:**
```python
var = Variable("x").isa("actor").has("actor-id", "A1")
```

###### `label(type_label: str) -> Variable`
Add a label constraint (TypeDB v3: label keyword).

**Parameters:**
- `type_label`: Type label string

**Returns:** Self for method chaining

**Example:**
```python
var = Variable("x").label("my-label")
```

---

### RelationBuilder

Builder for relations in queries.

#### Methods

###### `role(role_name: str, variable: str) -> RelationBuilder`
Add a role to the relation.

**Parameters:**
- `role_name`: Role name (e.g., "producer", "consumer")
- `variable`: Variable name (e.g., "$actor")

**Returns:** Self for method chaining

**Example:**
```python
builder.role("producer", "$p")
```

###### `links() -> RelationBuilder`
Use TypeDB v3 links keyword for role players.

**Returns:** Self for method chaining

**Example:**
```python
builder.links()
```

###### `as_variable(var_name: str) -> RelationBuilder`
Assign this relation to a variable name.

**Parameters:**
- `var_name`: Variable name (without $)

**Returns:** Self for method chaining

**Example:**
```python
builder.as_variable("r")
```

###### `end_relation() -> QueryBuilder`
Finish defining relation and return to QueryBuilder.

**Returns:** QueryBuilder for chaining

**Example:**
```python
query = QueryBuilder()
    .relation("messaging")
        .role("producer", "$p")
        .role("consumer", "$c")
        .role("message", "$m")
    .end_relation()
```

---

### Entity and Relation Classes

#### Entity

Base class for TypeDB entities with schema metadata.

##### Attributes
- `_type`: ClassVar[str] - TypeDB entity type name
- `_key_attr`: ClassVar[Optional[str]] - Primary key attribute

##### Methods

###### `get_key_value() -> Any`
Get the value of the key attribute.

**Returns:** Key attribute value

###### `to_insert_query() -> str`
Generate INSERT query for this entity.

**Returns:** TypeQL INSERT query string

**Example:**
```python
actor = Actor(
    actor_id="A1",
    id_label="User1",
    description="Test actor",
    justification="Testing"
)
query = actor.to_insert_query()
```

###### `to_match_query() -> str`
Generate MATCH query to find this entity by key.

**Returns:** TypeQL MATCH query string

**Example:**
```python
query = actor.to_match_query()
```

###### `to_parameterized_insert_query() -> Tuple[str, Dict[str, Any]]`
Generate parameterized INSERT query (secure against injection).

**Returns:** Tuple of (query_string, parameters_dict)

**Example:**
```python
query, params = actor.to_parameterized_insert_query()
```

###### `to_parameterized_match_query() -> Tuple[str, Dict[str, Any]]`
Generate parameterized MATCH query (secure against injection).

**Returns:** Tuple of (query_string, parameters_dict)

#### Predefined Entity Classes

##### Actor
Actor entity representing a system component.

**Fields:**
- `actor_id`: str (key)
- `id_label`: str
- `description`: str
- `justification`: str

**TypeDB Type:** `actor`

##### Action
Action entity representing a system action.

**Fields:**
- `action_id`: str (key)
- `id_label`: str
- `description`: str
- `justification`: str

**TypeDB Type:** `action`

##### Message
Message entity for inter-actor communication.

**Fields:**
- `message_id`: str (key)
- `id_label`: str
- `description`: str
- `justification`: str

**TypeDB Type:** `message`

##### DataEntity
DataEntity entity for domain data.

**Fields:**
- `data_entity_id`: str (key)
- `id_label`: str
- `description`: str
- `justification`: str

**TypeDB Type:** `data-entity`

##### Requirement
Requirement entity for functional/non-functional requirements.

**Fields:**
- `requirement_id`: str (key)
- `requirement_type`: str
- `status`: str
- `priority`: str
- `id_label`: str
- `description`: str
- `justification`: str

**TypeDB Type:** `requirement`

##### ActionAggregate
ActionAggregate entity grouping actions.

**Fields:**
- `action_agg_id`: str (key)
- `id_label`: str
- `description`: str
- `justification`: str

**TypeDB Type:** `action-aggregate`

##### MessageAggregate
MessageAggregate entity grouping messages.

**Fields:**
- `message_agg_id`: str (key)
- `id_label`: str
- `description`: str
- `justification`: str

**TypeDB Type:** `message-aggregate`

##### Constraint
Constraint entity for message constraints.

**Fields:**
- `constraint_id`: str (key)
- `id_label`: str
- `description`: str

**TypeDB Type:** `constraint`

##### Category
Category entity for categorization.

**Fields:**
- `name`: str (key)

**TypeDB Type:** `category`

##### TextBlock
TextBlock entity for anchored text.

**Fields:**
- `anchor_id`: str (key)
- `id_label`: str
- `anchor_type`: str
- `text`: str
- `order`: int

**TypeDB Type:** `text-block`

##### Concept
Concept entity for candidate concepts.

**Fields:**
- `concept_id`: str (key)
- `id_label`: str
- `description`: str

**TypeDB Type:** `concept`

##### SpecDocument
SpecDocument entity for specification documents.

**Fields:**
- `spec_doc_id`: str (key)
- `title`: str
- `version`: str
- `description`: str

**TypeDB Type:** `spec-document`

##### SpecSection
SpecSection entity for specification sections.

**Fields:**
- `spec_section_id`: str (key)
- `title`: str
- `id_label`: str
- `order`: int

**TypeDB Type:** `spec-section`

#### Predefined Relation Classes

##### Messaging
Messaging relation between Actors and Message.

**Fields:**
- `producer`: Actor
- `consumer`: Actor
- `message`: Message

**TypeDB Type:** `messaging`

##### Anchoring
Anchoring relation between TextBlock and domain entities.

**Fields:**
- `anchor`: TextBlock
- `concept`: Entity

**TypeDB Type:** `anchoring`

##### Membership
Membership relation for grouping.

**Fields:**
- `member_of`: Entity
- `member`: Entity

**TypeDB Type:** `membership`

##### MembershipSeq
Ordered membership relation.

**Fields:**
- `member_of`: Entity
- `member`: Entity
- `order`: int

**TypeDB Type:** `membership-seq`

##### Outlining
Outlining relation for hierarchical structure.

**Fields:**
- `section`: Entity
- `subsection`: Entity

**TypeDB Type:** `outlining`

##### Categorization
Categorization relation.

**Fields:**
- `category`: Category
- `object`: Entity

**TypeDB Type:** `categorization`

##### Requiring
Requiring relation between Requirements and Concepts/Messages.

**Fields:**
- `required_by`: Requirement
- `conceptualized_as`: Entity

**TypeDB Type:** `requiring`

##### ConstrainedBy
ConstrainedBy relation.

**Fields:**
- `constraint`: Constraint
- `object`: Entity

**TypeDB Type:** `constrained-by`

##### MessagePayload
MessagePayload relation between Message and DataEntity.

**Fields:**
- `message`: Message
- `payload`: DataEntity

**TypeDB Type:** `message-payload`

##### Filesystem
Filesystem relation for folder/file structure.

**Fields:**
- `folder`: Entity
- `entry`: Entity

**TypeDB Type:** `filesystem`

---

### EntityManager

High-level API for entity operations using the TypeDB client.

#### Constructor

```python
EntityManager(client: TypeDBClient, database: str)
```

**Parameters:**
- `client`: TypeDBClient instance
- `database`: Database name

#### Methods

##### `insert(entity: Entity) -> None`
Insert an entity.

**Parameters:**
- `entity`: Entity instance to insert

**Raises:**
- `TypeDBQueryError`: If entity already exists

**Example:**
```python
manager = EntityManager(client, "mydb")
actor = Actor(
    actor_id="A1",
    id_label="User1",
    description="Test actor",
    justification="Testing"
)
manager.insert(actor)
```

##### `put(entity: Entity) -> None`
Put an entity (idempotent - checks existence first).

**Parameters:**
- `entity`: Entity instance to put

**Example:**
```python
manager.put(actor)
```

##### `fetch_one(entity_type: Type[T], filters: Dict[str, Any]) -> Optional[T]`
Fetch a single entity by filters.

**Parameters:**
- `entity_type`: Entity class to fetch
- `filters`: Attribute constraints

**Returns:** Entity instance or None if not found

**Example:**
```python
actor = manager.fetch_one(Actor, {"actor-id": "A1"})
```

##### `fetch_all(entity_type: Type[T], filters: Optional[Dict[str, Any]] = None) -> List[T]`
Fetch all entities matching filters.

**Parameters:**
- `entity_type`: Entity class to fetch
- `filters`: Optional attribute constraints

**Returns:** List of entity instances

**Example:**
```python
actors = manager.fetch_all(Actor)
```

##### `exists(entity_type: Type[T], key_value: Any) -> bool`
Check if entity exists by key.

**Parameters:**
- `entity_type`: Entity class
- `key_value`: Key attribute value

**Returns:** True if entity exists

**Example:**
```python
if manager.exists(Actor, "A1"):
    print("Actor exists")
```

##### `delete(entity: Entity) -> None`
Delete an entity.

**Parameters:**
- `entity`: Entity instance to delete

**Example:**
```python
manager.delete(actor)
```

##### `insert_relation(relation: Relation) -> None`
Insert a relation.

**Parameters:**
- `relation`: Relation instance

**Example:**
```python
messaging = Messaging(
    producer=actor1,
    consumer=actor2,
    message=msg
)
manager.insert_relation(messaging)
```

---

### TransactionContext

Context manager for executing multiple operations in a single transaction.

#### Constructor

```python
TransactionContext(client: TypeDBClient, database: str, transaction_type: TransactionType)
```

**Parameters:**
- `client`: TypeDBClient instance
- `database`: Database name
- `transaction_type`: READ or WRITE transaction

#### Methods

##### `execute(query: str) -> None`
Add a query to the transaction.

**Parameters:**
- `query`: TypeQL query string

**Example:**
```python
with client.with_transaction("mydb", TransactionType.WRITE) as tx:
    tx.execute('insert $a isa actor, has actor-id "A1";')
    tx.execute('insert $a isa actor, has actor-id "A2";')
```

##### `execute_builder(builder: Any) -> None`
Add a query from a QueryBuilder to the transaction.

**Parameters:**
- `builder`: QueryBuilder or any object with get_tql() method

**Raises:**
- `TypeError`: If builder doesn't have get_tql() method

**Example:**
```python
query = QueryBuilder().insert().variable("a", "actor", {"actor-id": "A1"})
with client.with_transaction("mydb", TransactionType.WRITE) as tx:
    tx.execute_builder(query)
```

---

## Exceptions

All exceptions inherit from `TypeDBError`.

### TypeDBConnectionError
Connection-related errors.

### TypeDBAuthenticationError
Authentication-related errors.

### TypeDBQueryError
Query execution errors.

**Attributes:**
- `query`: The query that caused the error
- `details`: Additional error details

### TypeDBServerError
Server-side errors.

### TypeDBValidationError
Validation errors (e.g., entity already exists).

---

## Authentication & Security

### SecureTokenManager
Manages JWT tokens with encryption for secure storage.

**Usage:**
```python
from typedb_client3 import SecureTokenManager

manager = SecureTokenManager()
token = manager.retrieve_token(encrypted_token)
manager.clear_memory()
```

---

## Validation Functions

### validate_base_url(base_url: str) -> str
Validate and normalize base URL.

### validate_credentials(username: Optional[str], password: Optional[str]) -> None
Validate username and password.

### validate_timeout(timeout: int) -> int
Validate timeout value.

### validate_operation_timeouts(timeouts: Dict[str, int]) -> Dict[str, int]
Validate operation-specific timeouts.

### create_optimized_session() -> requests.Session
Create an HTTP session with connection pooling.

**Default Constants:**
- `DEFAULT_POOL_CONNECTIONS`: 10
- `DEFAULT_POOL_MAXSIZE`: 100
- `DEFAULT_MAX_RETRIES`: 3
- `DEFAULT_BACKOFF_FACTOR`: 0.3

---

## Advanced Examples

### Building Complex Queries

```python
from typedb_client3 import QueryBuilder

# Complex match with relations and filters
query = QueryBuilder().match()
query.variable("a", "actor").has("actor-id", "A1")
query.relation("messaging") \
    .role("producer", "$a") \
    .role("consumer", "$c") \
    .role("message", "$m") \
    .links()
query.fetch(["a", "m"])
query.limit(10)

tql = query.get_tql()
result = client.execute_query("mydb", tql, TransactionType.READ)
```

### Using Query Templates

```python
# Create reusable insert template
insert_template = QueryBuilder.insert_template()
insert_template.variable("a", "actor")

# Insert multiple entities
for actor_data in actor_list:
    insert_template.update_variable("a", "actor", actor_data)
    tql = insert_template.get_tql()
    client.execute_query("mydb", tql, TransactionType.WRITE)
```

### Transaction with Multiple Operations

```python
with client.with_transaction("mydb", TransactionType.WRITE) as tx:
    # Insert entities
    tx.execute('insert $a1 isa actor, has actor-id "A1";')
    tx.execute('insert $a2 isa actor, has actor-id "A2";')
    
    # Insert relations
    tx.execute('insert (producer: $a1, consumer: $a2, message: $m) isa messaging;')
    
    # All operations committed atomically
```

### Entity Manager Usage

```python
manager = EntityManager(client, "mydb")

# Insert entity
actor = Actor(
    actor_id="A1",
    id_label="User1",
    description="Test actor",
    justification="Testing"
)
manager.put(actor)

# Fetch entity
found = manager.fetch_one(Actor, {"actor-id": "A1"})

# Fetch all entities
all_actors = manager.fetch_all(Actor)

# Check existence
if manager.exists(Actor, "A1"):
    print("Actor exists")

# Delete entity
manager.delete(actor)
```

### Schema Management

```python
# Load schema from file
client.load_schema("mydb", "schema.tql")

# Get current schema
schema = client.get_schema("mydb")
print(schema)

# Load schema from string
schema_str = """
define actor sub entity, has actor-id, has id-label;
"""
client.load_schema("mydb", schema_str)
```

### Database Management

```python
# List databases
databases = client.list_databases()
print(f"Databases: {databases}")

# Create database
client.create_database("mydb")

# Check existence
if client.database_exists("mydb"):
    print("Database exists")

# Connect (create if not exists)
client.connect_database("mydb")

# Clear data (keep schema)
client.clear_database("mydb")

# Wipe all data
client.wipe_database("mydb", verify=True)

# Delete database
client.delete_database("mydb")
```

---

## Best Practices

1. **Use Query Templates**: Build query templates once and reuse them for better performance
2. **Use Transactions**: Group multiple operations in transactions for atomicity
3. **Use EntityManager**: Leverage high-level entity operations for common CRUD tasks
4. **Parameterized Queries**: Use `to_parameterized_insert_query()` for security
5. **Connection Pooling**: The client automatically uses connection pooling
6. **Error Handling**: Always catch and handle TypeDB exceptions appropriately
7. **Resource Cleanup**: Call `client.close()` when done to release resources

---

## License

[Add license information here]