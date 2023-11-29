# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-SWH is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Serializer for Invenio-SWH."""

from flask_resources import MarshmallowSerializer
from invenio_swh.schema import SWHCodemetaSchema
from lxml import etree
import xmltodict


class BaseFormatter:
    """Base formatter interface."""

    def to_bytes(self, obj):
        """Converts the object to bytes."""
        raise NotImplementedError

    def to_bytes_list(self, obj):
        """Converts the object list to bytes."""
        raise NotImplementedError

    def to_str(self, obj):
        """Converts the object to string."""
        raise NotImplementedError

    def to_str_list(self, obj):
        """Converts the object list to string."""
        raise NotImplementedError

    def to_etree(self, obj):
        """Converts the object to etree."""
        raise NotImplementedError

    def to_etree_list(self, obj):
        """Converts the object list to etree."""
        raise NotImplementedError


class XMLFormatter(BaseFormatter):
    """XMLFormatter is a class that provides methods for serializing objects to XML format."""

    _namespaces = None

    @property
    def namespaces(self):
        """Get the namespaces used for XML serialization.

        :return: The namespaces used for XML serialization.
        :rtype: dict
        """
        return self._namespaces

    def __init__(self, **kwargs):
        """Initialize the XMLFormatter.

        :param namespaces: A dictionary of namespaces to be used for XML serialization. Defaults to None.
        :type namespaces: dict, optional
        """
        super().__init__()
        if "namespaces" in kwargs:
            self._namespaces = kwargs["namespaces"]

    def serialize_object(self, obj) -> bytes:
        """Serialize an object to XML format.

        :param obj: The object to be serialized.
        :type obj: dict
        :return: The bytes string representation of the object in XML format.
        :rtype: str
        """
        return self.to_bytes(self.to_etree(obj))

    def to_etree(self, obj):
        """
        Convert an object to an ElementTree object.

        :param obj: The object to be converted.
        :type obj: dict or str
        :return: The converted object as an ElementTree object.
        :rtype: ElementTree
        :raises TypeError: If the object is not a dictionary or string.
        """
        if isinstance(obj, dict):
            keys = list(obj.keys())
            # Dict has only one root
            assert len(keys) == 1

            root = keys[0]
            if self.namespaces:
                for k, v in self.namespaces.items():
                    if k == "default":
                        obj[root][f"@xmlns"] = v
                    else:
                        obj[root][f"@xmlns:{k}"] = v
            _etree = etree.fromstring(xmltodict.unparse(obj).encode("utf-8"))
        elif isinstance(obj, str):
            _etree = etree.fromstring(obj.encode("utf-8"))
        else:
            raise TypeError("Invalid type to create etree: expected str or dict.")

        return _etree

    def to_bytes(self, obj, encoding="utf-8") -> bytes:
        """
        Convert an ElementTree object to bytes string.

        :param obj: The ElementTree object to be converted.
        :type obj: ElementTree
        :param encoding: The encoding to be used for the conversion. Defaults to "utf-8".
        :type encoding: str, optional
        :return: The converted object as a bytes string.
        :rtype: str
        """
        return etree.tostring(obj, xml_declaration=True, encoding=encoding)

    def to_str(self, obj) -> str:
        """
        Convert an ElementTree object to a unicode string.

        :param obj: The ElementTree object to be converted.
        :type obj: ElementTree
        :return: The converted object as a unicode string.
        :rtype: str
        """
        return etree.tostring(obj, encoding="unicode")


class SoftwareHeritageXMLSerializer(MarshmallowSerializer):
    """Serializer for Software Heritage XML serialization."""

    @property
    def default_namespaces(self):
        """Default namespaces for Software Heritage serialization."""
        return {
            "default": "https://doi.org/10.5063/SCHEMA/CODEMETA-2.0",
            "atom": "http://www.w3.org/2005/Atom",
        }

    def __init__(self, namespaces=None, **options):
        """Constructor."""

        self.namespaces = namespaces or self.default_namespaces
        super().__init__(
            format_serializer_cls=XMLFormatter,
            object_schema_cls=SWHCodemetaSchema,
            # Passed as kwargs to the formatter
            namespaces=self.namespaces,
        )
