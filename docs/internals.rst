*********
Internals
*********

Entity Store
============

Several mongodb collections are used for within the entity store:

entity
    The main collection, used to store all "active" entities.
merged
    Entity graveyard, stores any entities removed from ``entity``.


Records
-------

Each record within the ``entity`` collection has several special attributes:

_id
    A 128-bit hex string used as a unique identifier.
    If not specified it will be created at insert time.
_suid
    64-bit truncation of ``_id`` used for Sphinx search.
_count
    Number of occurrences of the entity in data.
_type
    String describing the type of the entity.
_timestamp
    Timestamp recording when entity was added.
_merged_from
    List of ids of entities that were merged to create this (may be empty)
_source
    String describing what user/script created the entity.
name
    Name of entity.
aliases
    Alternate names for this entity (may be empty)

In addition to these attributes you are free to add as many additional
attributes you require, the only limitation being that none of them share a
name with any of the above.
