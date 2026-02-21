"""TypeDB v3 Client Library

A Python library for TypeDB v3 operations with support for:
- TypeDB v3 HTTP API (fetch, put, links, label, reduce, with)
- Query builder with reusable templates
- Transaction support
- Entity/Relation abstractions
- Authentication and connection pooling
"""

# Version
__version__ = "0.1.0"

# Main exports
from .client import (
    TypeDBClient, TransactionType, TransactionContext,
)
from .auth import (
    SecureTokenManager,
)
from .validation import (
    validate_base_url, validate_credentials, validate_timeout,
    validate_operation_timeouts,
    create_optimized_session,
    DEFAULT_POOL_CONNECTIONS, DEFAULT_POOL_MAXSIZE,
    DEFAULT_MAX_RETRIES, DEFAULT_BACKOFF_FACTOR
)
from .query_builder import QueryBuilder, Variable, RelationBuilder
from .entities import (
    Entity, Relation,
    Actor, Action, Message, DataEntity, Requirement,
    ActionAggregate, MessageAggregate, Constraint, Category,
    TextBlock, Concept, SpecDocument, SpecSection,
    Messaging, Anchoring, Membership, MembershipSeq,
    Outlining, Categorization, Requiring, ConstrainedBy,
    MessagePayload, Filesystem
)
from .exceptions import (
    TypeDBError, TypeDBConnectionError, TypeDBAuthenticationError,
    TypeDBQueryError, TypeDBServerError, TypeDBValidationError
)
from .entity_manager import EntityManager

__all__ = [
    # Client
    "TypeDBClient",
    "TransactionType",
    "TransactionContext",
    "SecureTokenManager",
    "validate_base_url",
    "validate_credentials",
    "validate_timeout",
    "validate_operation_timeouts",
    "create_optimized_session",
    "DEFAULT_POOL_CONNECTIONS",
    "DEFAULT_POOL_MAXSIZE",
    "DEFAULT_MAX_RETRIES",
    "DEFAULT_BACKOFF_FACTOR",
    
    # Query Builder
    "QueryBuilder",
    "Variable",
    "RelationBuilder",
    
    # Entities
    "Entity",
    "Relation",
    "Actor",
    "Action",
    "Message",
    "DataEntity",
    "Requirement",
    "ActionAggregate",
    "MessageAggregate",
    "Constraint",
    "Category",
    "TextBlock",
    "Concept",
    "SpecDocument",
    "SpecSection",
    
    # Relations
    "Messaging",
    "Anchoring",
    "Membership",
    "MembershipSeq",
    "Outlining",
    "Categorization",
    "Requiring",
    "ConstrainedBy",
    "MessagePayload",
    "Filesystem",
    
    # Entity Manager
    "EntityManager",
    
    # Exceptions
    "TypeDBError",
    "TypeDBConnectionError",
    "TypeDBAuthenticationError",
    "TypeDBQueryError",
    "TypeDBServerError",
    "TypeDBValidationError",
]
