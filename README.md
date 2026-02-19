# typedb_client3 - TypeDB v3 Client Library

A Python client library for TypeDB v3 HTTP API with support for:
- TypeDB v3 HTTP API (fetch, put, links, label, reduce, with)
- Query builder with reusable templates
- Transaction support
- Entity/Relation abstractions (generic - can be extended for specific schemas)
- Authentication and connection pooling

## Installation

```bash
pip install typedb-client3
```

## Usage

```python
from typedb_client3 import TypeDBClient, TransactionType

# Create client
client = TypeDBClient(
    base_url="http://localhost:8000",
    username="admin",
    password="password"
)

# Execute query
result = client.execute_query(
    database="mydb",
    query='match $a isa actor; fetch {$a.*};',
    transaction_type=TransactionType.READ
)
```

## CLI Tools

This library does not provide CLI tools. The CLI tools for importing data are provided by the modellm project.

## Development

### Install dependencies

```bash
pip install -e ".[dev]"
```

### Run tests

```bash
# Run all tests
pytest tests/ -v

# Run unit tests only
pytest tests/ -v -m unit

# Run integration tests only (requires TypeDB server)
pytest tests/ -v -m integration

# Run with coverage
pytest tests/ --cov=typedb_client3 --cov-report=html
```

### Test server

For integration tests, a TypeDB test server is available at:
- URL: `http://localhost:8000`
- Credentials: `admin` / `password`

## License

[Add license information here]
