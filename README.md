# typedb_client3 - TypeDB v3 Python Client Library

A modern Python client library for TypeDB v3 that provides a high-level, programmatic interface for database operations. This library removes the dependency on writing raw TypeQL (TypeDB Query Language) syntax, making it easier for LLM agents and developers to construct queries correctly and efficiently.

## 🚀 Key Features

### TypeDB v3 Full Support
- **Complete HTTP API Coverage**: Full support for TypeDB v3 HTTP API including all modern query operations
- **Modern Query Syntax**: Native support for `fetch`, `put`, `links`, `label`, `reduce`, and `with` keywords
- **Schema Operations**: Define, undefine, and redefine schemas programmatically
- **Database Management**: Create, delete, list, and manage databases with ease

### Developer-Friendly Query Building
- **Fluent Query Builder**: Chainable methods for building queries without raw syntax
- **Reusable Query Templates**: Build once, execute many times with parameter updates
- **Method Chaining**: Intuitive API design for rapid development
- **Type Safety**: Clear separation between READ and WRITE operations

### Entity & Relation Abstractions
- **ORM-Like Interface**: Dataclass-based entities with automatic query generation
- **Predefined Schemas**: Ready-to-use entity and relation classes for common patterns
- **Entity Manager**: High-level CRUD operations without writing TypeQL
- **Flexible Relations**: Support for complex relation patterns and role players

### Transaction Support
- **Atomic Operations**: Execute multiple operations in a single transaction
- **Context Managers**: Pythonic `with` statement syntax for transaction handling
- **Batch Operations**: Insert or update multiple entities efficiently
- **Rollback Safety**: Automatic rollback on errors

### Security & Performance
- **JWT Authentication**: Secure token-based authentication with encryption
- **Connection Pooling**: Optimized HTTP sessions with connection reuse
- **Parameterized Queries**: Protection against injection attacks
- **Configurable Timeouts**: Fine-grained control over operation timeouts

## 📦 Installation

```bash
pip install typedb-client3
```

## 🎯 Quick Start

### Basic Usage

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

print(result)
```

### Using the Query Builder

```python
from typedb_client3 import QueryBuilder

# Build a query without raw TypeQL syntax
query = QueryBuilder() \
    .match() \
    .variable("a", "actor") \
    .has("actor-id", "A1") \
    .fetch(["a"]) \
    .limit(10)

# Execute the query
tql = query.get_tql()
result = client.execute_query("mydb", tql, TransactionType.READ)
```

### Entity Manager Usage

```python
from typedb_client3 import EntityManager, Actor

# Create an entity manager
manager = EntityManager(client, "mydb")

# Create and insert an entity
actor = Actor(
    actor_id="A1",
    id_label="User1",
    description="System user",
    justification="Required for authentication"
)
manager.put(actor)

# Fetch entities
all_actors = manager.fetch_all(Actor)
specific_actor = manager.fetch_one(Actor, {"actor-id": "A1"})
```

### Transaction Operations

```python
# Execute multiple operations atomically
with client.with_transaction("mydb", TransactionType.WRITE) as tx:
    tx.execute('insert $a1 isa actor, has actor-id "A1";')
    tx.execute('insert $a2 isa actor, has actor-id "A2";')
    tx.execute('insert (producer: $a1, consumer: $a2, message: $m) isa messaging;')
    # All operations committed when exiting context
```

## 🔧 Core Capabilities

### 1. Database Management

```python
# List all databases
databases = client.list_databases()

# Create a new database
client.create_database("mydb")

# Check if database exists
if client.database_exists("mydb"):
    print("Database exists")

# Connect to database (create if needed)
client.connect_database("mydb")

# Clear all data (keep schema)
client.clear_database("mydb")

# Safely wipe all data with verification
client.wipe_database("mydb", verify=True)

# Delete database
client.delete_database("mydb")
```

### 2. Schema Operations

```python
# Load schema from file
client.load_schema("mydb", "schema.tql")

# Load schema from string
schema = """
define actor sub entity, has actor-id, has id-label;
"""
client.load_schema("mydb", schema)

# Retrieve current schema
current_schema = client.get_schema("mydb")
print(current_schema)
```

### 3. Query Execution

```python
# Raw query execution
result = client.execute_query(
    database="mydb",
    query='match $a isa actor; fetch $a;',
    transaction_type=TransactionType.READ
)

# Multiple queries in one transaction
operations = [
    {"query": 'insert $a isa actor, has actor-id "A1";'},
    {"query": 'insert $a isa actor, has actor-id "A2";'},
]
result = client.execute_transaction(
    "mydb", 
    TransactionType.WRITE, 
    operations
)

# Variable-length query execution
results = client.execute_queries(
    "mydb",
    'insert $a isa actor, has actor-id "A1";',
    'insert $a isa actor, has actor-id "A2";',
    transaction_type=TransactionType.WRITE
)
```

### 4. Advanced Query Building

```python
# Complex queries with relations
query = QueryBuilder() \
    .match() \
    .variable("a", "actor", {"actor-id": "A1"}) \
    .relation("messaging") \
        .role("producer", "$a") \
        .role("consumer", "$c") \
        .role("message", "$m") \
        .links() \
    .end_relation() \
    .fetch(["a", "m"]) \
    .order_by("m", "timestamp") \
    .limit(10)

tql = query.get_tql()
```

### 5. Query Templates & Reuse

```python
# Create reusable insert template
insert_template = QueryBuilder.insert_template()
insert_template.variable("a", "actor")

# Use template for multiple inserts
for actor_id in ["A1", "A2", "A3"]:
    insert_template.update_variable("a", "actor", {"actor-id": actor_id})
    tql = insert_template.get_tql()
    client.execute_query("mydb", tql, TransactionType.WRITE)

# Clone queries for variations
base_query = QueryBuilder.match_template().variable("x", "actor")
query1 = base_query.clone().update_variable("x", "actor", {"actor-id": "A1"})
query2 = base_query.clone().update_variable("x", "actor", {"actor-id": "A2"})
```

### 6. Entity Operations

```python
# Insert entity with parameterized query
actor = Actor(
    actor_id="A1",
    id_label="User1",
    description="Test actor",
    justification="Testing"
)
query, params = actor.to_parameterized_insert_query()
# Execute with parameters for security

# Match query by key
match_query = actor.to_match_query()

# Check existence
if manager.exists(Actor, "A1"):
    print("Actor exists")
```

### 7. Relation Operations

```python
# Create relations between entities
messaging = Messaging(
    producer=actor1,
    consumer=actor2,
    message=msg
)
manager.insert_relation(messaging)
```

## 🏗️ Architecture

### Layered Design

```
┌─────────────────────────────────────┐
│     High-Level Entity Manager        │
│  (ORM-like CRUD operations)          │
└──────────────────┬──────────────────┘
                   │
┌──────────────────┴──────────────────┐
│         Query Builder                │
│  (Fluent API for query building)    │
└──────────────────┬──────────────────┘
                   │
┌──────────────────┴──────────────────┐
│      TypeDB HTTP Client             │
│  (API calls, auth, pooling)         │
└─────────────────────────────────────┘
```

### Core Components

1. **TypeDBClient**: Main client for HTTP API interactions
2. **QueryBuilder**: Fluent API for building queries
3. **EntityManager**: High-level entity operations
4. **Entity/Relation Classes**: Dataclass abstractions
5. **TransactionContext**: Transaction management
6. **SecureTokenManager**: JWT authentication

## 📚 Available Entity Types

The library includes predefined entity classes for common patterns:

- **Actor**: System component representation
- **Action**: System actions
- **Message**: Inter-actor communication
- **DataEntity**: Domain data
- **Requirement**: Functional/non-functional requirements
- **ActionAggregate/MessageAggregate**: Grouping entities
- **Constraint**: Message constraints
- **Category**: Categorization
- **TextBlock**: Anchored text
- **Concept**: Candidate concepts
- **SpecDocument/SpecSection**: Specification structures

## 🔗 Relation Types

Predefined relation classes for common patterns:

- **Messaging**: Producer-consumer-message relationships
- **Anchoring**: Text-to-entity anchoring
- **Membership**: Group membership
- **Outlining**: Hierarchical structures
- **Categorization**: Category classification
- **Requiring**: Requirement dependencies
- **ConstrainedBy**: Constraint relationships
- **MessagePayload**: Message-data associations
- **Filesystem**: Folder/file structures

## 🛡️ Security Features

### Authentication
- JWT token-based authentication
- Secure token encryption for storage
- Token access logging and auditing

### Query Safety
- Parameterized queries to prevent injection
- Automatic value escaping for TypeQL
- Input validation for all parameters

### Connection Security
- Configurable timeout settings
- Connection pooling with limits
- Automatic session cleanup

## ⚡ Performance Optimizations

1. **Connection Pooling**: Reuse HTTP connections for better performance
2. **Query Templates**: Build once, execute many times
3. **Batch Operations**: Group multiple operations in single transactions
4. **Lazy Building**: Queries built only when needed
5. **Optimized Sessions**: Configurable pool sizes and retry logic

## 🧪 Testing

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
pytest tests/ -v

# Run unit tests only
pytest tests/ -v -m unit

# Run integration tests only (requires TypeDB server)
pytest tests/ -v -m integration

# Run with coverage
pytest tests/ --cov=typedb_client3 --cov-report=html
```

## 📖 Documentation

- **API Documentation**: See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for detailed API reference
- **Examples**: Check the `examples/` directory for usage examples
- **TypeDB v3 Docs**: [Official TypeDB v3 Documentation](https://typedb.com/docs/)

## 🤝 Use Cases

### Perfect For:
- **LLM Integration**: Enables AI agents to construct queries programmatically
- **Application Development**: Rapid development of TypeDB-backed applications
- **Data Migration**: Efficient bulk operations with transactions
- **Schema Management**: Programmatic schema definition and modification
- **Complex Queries**: Builder pattern simplifies complex query construction

### Ideal Scenarios:
- Building applications that use TypeDB v3 as backend
- Implementing TypeDB operations in Python microservices
- Creating TypeDB integration for AI/ML workflows
- Developing data ingestion pipelines
- Building analytics dashboards with TypeDB

## 🔄 Comparison with Raw TypeQL

### Raw TypeQL (Without this library):
```python
query = """
match $a isa actor, has actor-id "A1";
    $r isa messaging, links (producer: $a, consumer: $c, message: $m);
fetch $a, $m;
"""
result = client.execute_query("mydb", query)
```

### With typedb_client3:
```python
query = QueryBuilder() \
    .match() \
    .variable("a", "actor", {"actor-id": "A1"}) \
    .relation("messaging") \
        .role("producer", "$a") \
        .role("consumer", "$c") \
        .role("message", "$m") \
        .links() \
    .end_relation() \
    .fetch(["a", "m"])

result = client.execute_query("mydb", query.get_tql())
```

**Benefits:**
- ✅ No raw syntax to remember
- ✅ Type safety and autocomplete
- ✅ Reusable query templates
- ✅ Better error messages
- ✅ Easier refactoring
- ✅ LLM-friendly construction

## 🐛 Error Handling

The library provides specific exception types for different error scenarios:

```python
from typedb_client3 import (
    TypeDBConnectionError,
    TypeDBAuthenticationError,
    TypeDBQueryError,
    TypeDBServerError,
    TypeDBValidationError
)

try:
    client.execute_query("mydb", query, TransactionType.WRITE)
except TypeDBQueryError as e:
    print(f"Query failed: {e}")
    print(f"Query: {e.query}")
    print(f"Details: {e.details}")
except TypeDBConnectionError as e:
    print(f"Connection failed: {e}")
except TypeDBValidationError as e:
    print(f"Validation error: {e}")
```

## 🎨 Customization

### Custom Entities
```python
from typedb_client3 import Entity

@dataclass
class CustomEntity(Entity):
    _type = "custom-entity"
    _key_attr = "custom-id"
    
    custom_id: str
    name: str
    value: int
```

### Custom Relations
```python
from typedb_client3 import Relation

@dataclass
class CustomRelation(Relation):
    _type = "custom-relation"
    _roles = ["role1", "role2"]
    
    entity1: Entity
    entity2: Entity
```

## 📝 Development

### Project Structure
```
typedb_client3/
├── client.py           # Main HTTP client
├── query_builder.py    # Fluent query builder
├── entities.py         # Entity/Relation classes
├── entity_manager.py   # High-level ORM operations
├── transactions.py    # Transaction context
├── auth.py            # JWT authentication
├── validation.py      # Input validation
├── exceptions.py      # Custom exceptions
└── tests/             # Test suite
```

### Contributing
Contributions are welcome! Please ensure all tests pass before submitting PRs.

## 📄 License

[Add license information here]

## 🔗 Links

- **TypeDB v3**: https://typedb.com/
- **Documentation**: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **Issues**: GitHub Issues
- **TypeDB CLI Tools**: Provided by the modellm project

## 💡 Why typedb_client3?

This library was developed to address a critical need: **removing dependencies on TypeDB 3 TQL syntax** which most LLM coding agents struggle to construct correctly. By providing a programmatic, fluent API, we enable:

1. **AI-Friendly**: LLMs can construct queries using method calls instead of raw syntax
2. **Developer-Friendly**: IDE autocomplete and type hints improve productivity
3. **Maintainable**: Query structure is explicit and easy to modify
4. **Reusable**: Query templates reduce code duplication
5. **Safe**: Parameterized queries prevent injection attacks
6. **Modern**: Full support for TypeDB v3 features like `put`, `links`, `reduce`

---

**Built for developers who want the power of TypeDB without the complexity of raw query syntax.**