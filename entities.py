"""TypeDB v3 Client Library - Entity and Relation Base Classes

Provides base classes for defining TypeDB v3 entities and relations as Python
dataclasses. These base classes can be extended to model any TypeDB v3 schema.

Usage:
    from dataclasses import dataclass
    from typedb_client3.entities import Entity, Relation

    @dataclass
    class Person(Entity):
        _type = "person"
        _key_attr = "username"

        username: str
        full_name: str
        age: int

    @dataclass
    class Friendship(Relation):
        _type = "friendship"
        _roles = ["friend"]

        friend1: Person
        friend2: Person
"""

import uuid
from typing import ClassVar, Optional, Dict, List, Any, Tuple
from dataclasses import dataclass


@dataclass
class Entity:
    """Base class for TypeDB entities with schema metadata.

    Subclass this to define entities that map to your TypeDB v3 schema.
    Field names use snake_case and are automatically converted to kebab-case
    for TypeDB attribute names (e.g., full_name -> full-name).

    Fields beginning with '_' (such as _type and _key_attr) are treated as
    class-level metadata and are excluded from generated queries.

    Class Variables:
        _type: TypeDB entity type name (e.g., "person")
        _key_attr: Primary key attribute name in kebab-case (e.g., "username")

    Example:
        @dataclass
        class Person(Entity):
            _type = "person"
            _key_attr = "username"

            username: str
            full_name: str
            age: int
    """

    _type: ClassVar[str] = ""  # TypeDB entity type name
    _key_attr: ClassVar[Optional[str]] = None  # Primary key attribute

    def _data_fields(self) -> List[str]:
        """Return dataclass field names that are actual data attributes.

        Excludes private/ClassVar fields (those starting with '_') which
        are used for schema metadata (_type, _key_attr).

        Returns:
            List of field names to use in query generation
        """
        return [
            name for name in self.__dataclass_fields__.keys()
            if not name.startswith('_')
        ]

    def get_key_value(self) -> Any:
        """Get the value of the key attribute."""
        if not self._key_attr:
            raise ValueError(f"No key attribute defined for {self.__class__.__name__}")

        for field_name in self._data_fields():
            db_attr_name = field_name.replace('_', '-')
            if db_attr_name == self._key_attr:
                return getattr(self, field_name)

        raise ValueError(f"Key attribute {self._key_attr} not found in entity")

    def to_insert_query(self) -> str:
        """Generate INSERT query for this entity.

        Returns:
            TypeQL v3 INSERT query string

        Example:
            person = Person(username="jdoe", full_name="Jane Doe", age=30)
            query = person.to_insert_query()
            # insert $p isa person, has username "jdoe", has full-name "Jane Doe", has age 30;
        """
        var_name = self.__class__.__name__.lower()[:1]
        parts = [f"${var_name} isa {self._type}"]

        for field_name in self._data_fields():
            value = getattr(self, field_name)
            if value is not None:
                db_attr_name = field_name.replace('_', '-')
                parts.append(f'has {db_attr_name} {self._escape_value(value)}')

        return f"insert {', '.join(parts)};"

    def to_match_query(self) -> str:
        """Generate MATCH query to find this entity by key.

        Returns:
            TypeQL v3 MATCH query string

        Example:
            person = Person(username="jdoe", full_name="Jane Doe", age=30)
            query = person.to_match_query()
            # match $p isa person, has username "jdoe";
        """
        if not self._key_attr:
            raise ValueError(f"No key attribute defined for {self.__class__.__name__}")

        key_value = self.get_key_value()
        var_name = self.__class__.__name__.lower()[:1]

        return f'match ${var_name} isa {self._type}, has {self._key_attr} {self._escape_value(key_value)};'

    def _escape_value(self, value: Any) -> str:
        """Escape a value for TypeQL.

        WARNING: This method is deprecated and should only be used for backward
        compatibility. Use to_parameterized_insert_query() instead for security.
        """
        if isinstance(value, str):
            escaped = value.replace('\\', '\\\\').replace('"', '\"')
            return f'"{escaped}"'
        elif isinstance(value, bool):
            return str(value).lower()
        elif isinstance(value, (int, float)):
            return str(value)
        else:
            raise ValueError(f"Unsupported value type: {type(value)}")

    def _create_parameterized_value(self, value: Any, attribute_name: str) -> Tuple[str, Any]:
        """Create a parameterized placeholder for a value.

        This method prevents TypeQL injection by using parameterized queries
        instead of string escaping.

        Args:
            value: The value to parameterize
            attribute_name: The attribute name for the placeholder

        Returns:
            Tuple of (placeholder_string, parameter_value)
        """
        if value is None:
            return (None, None)

        unique_suffix = str(uuid.uuid4())[:8]
        placeholder = f"${self._type}_{attribute_name}_{unique_suffix}"

        return (placeholder, value)

    def to_parameterized_insert_query(self) -> Tuple[str, Dict[str, Any]]:
        """Generate parameterized INSERT query for this entity.

        This method is secure against injection attacks as it uses parameterized
        queries instead of string escaping.

        Returns:
            Tuple of (query_string, parameters_dict)
            - query_string: TypeQL INSERT query with placeholders
            - parameters_dict: Dictionary mapping placeholders to values

        Example:
            person = Person(username="jdoe", full_name="Jane Doe", age=30)
            query, params = person.to_parameterized_insert_query()
        """
        var_name = self.__class__.__name__.lower()[:1]
        parameters: Dict[str, Any] = {}
        parts = [f"${var_name} isa {self._type}"]

        for field_name in self._data_fields():
            value = getattr(self, field_name)
            if value is not None:
                db_attr_name = field_name.replace('_', '-')
                placeholder, param_value = self._create_parameterized_value(value, field_name)
                if placeholder:
                    parts.append(f'has {db_attr_name} {placeholder}')
                    parameters[placeholder] = param_value

        query = f"insert {', '.join(parts)};"
        return (query, parameters)

    def to_parameterized_match_query(self) -> Tuple[str, Dict[str, Any]]:
        """Generate parameterized MATCH query to find this entity by key.

        This method is secure against injection attacks as it uses parameterized
        queries instead of string escaping.

        Returns:
            Tuple of (query_string, parameters_dict)
            - query_string: TypeQL MATCH query with placeholders
            - parameters_dict: Dictionary mapping placeholders to values

        Example:
            person = Person(username="jdoe", full_name="Jane Doe", age=30)
            query, params = person.to_parameterized_match_query()
        """
        if not self._key_attr:
            raise ValueError(f"No key attribute defined for {self.__class__.__name__}")

        key_value = self.get_key_value()
        var_name = self.__class__.__name__.lower()[:1]

        key_field_name = self._key_attr.replace('-', '_')
        placeholder, param_value = self._create_parameterized_value(key_value, key_field_name)
        parameters = {placeholder: param_value} if placeholder else {}
        query = f'match ${var_name} isa {self._type}, has {self._key_attr} {placeholder};'

        return (query, parameters)


@dataclass
class Relation:
    """Base class for TypeDB relations.

    Subclass this to define relations that map to your TypeDB v3 schema.
    Relations connect entities via named roles.

    Class Variables:
        _type: TypeDB relation type name (e.g., "friendship")
        _roles: List of role names defined in the schema

    Example:
        @dataclass
        class Friendship(Relation):
            _type = "friendship"
            _roles = ["friend"]

            friend1: Person
            friend2: Person
    """

    _type: ClassVar[str] = ""  # TypeDB relation type name
    _roles: ClassVar[List[str]] = []  # Role names

    def to_insert_query(self, variables: Dict[str, str]) -> str:
        """Generate INSERT query for this relation.

        Args:
            variables: Mapping of role names to variable names

        Returns:
            TypeQL v3 INSERT query string

        Example:
            friendship = Friendship(friend1=p1, friend2=p2)
            query = friendship.to_insert_query({"friend": "p1"})
            # (friend: $p1) isa friendship;
        """
        role_parts = []
        for role in self._roles:
            if role in variables:
                role_parts.append(f"{role}: ${variables[role]}")

        return f"({', '.join(role_parts)}) isa {self._type};"