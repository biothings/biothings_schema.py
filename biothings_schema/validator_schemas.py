"""The JSON schemas used to valid a schema.org style JSON-LD schema"""

# validate a class definition
class_json_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "@id": {"type": "string"},
        "@type": {"anyOf": [{"type": "string"}, {"type": "array", "items": {"type": "string"}}]},
        "rdfs:comment": {"anyOf": [{"type": "string"}, {"type": "null"}]},
        "rdfs:label": {
            "anyOf": [
                {"type": "string"},
                {
                    "type": "object",
                    "properties": {"@language": {"type": "string"}, "@value": {"type": "string"}},
                    "required": ["@language", "@value"],
                },
            ]
        },
        "http://schema.org/supersededBy": {
            "anyOf": [
                {"type": "object", "properties": {
                    "@id": {"type": "string"}}, "required": ["@id"]},
                {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {"@id": {"type": "string"}},
                        "required": ["@id"],
                    },
                },
            ]
        },
        "rdfs:subClassOf": {
            "anyOf": [
                {"type": "object", "properties": {
                    "@id": {"type": "string"}}, "required": ["@id"]},
                {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {"@id": {"type": "string"}},
                        "required": ["@id"],
                    },
                },
            ]
        },
        "http://www.w3.org/2002/07/owl#equivalentClass": {
            "anyOf": [
                {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {"@id": {"type": "string"}},
                        "required": ["@id"],
                    },
                },
                {"type": "object", "properties": {
                    "@id": {"type": "string"}}, "required": ["@id"]},
            ]
        },
        "http://schema.org/category": {
            "anyOf": [
                {"type": "string"},
                {"type": "array", "items": {"type": "string"}},
                {
                    "type": "object",
                    "properties": {"@language": {"type": "string"}, "@value": {"type": "string"}},
                    "required": ["@language", "@value"],
                },
            ]
        },
        "http://schema.org/sameAs": {
            "type": "object",
            "properties": {"@id": {"type": "string"}},
            "required": ["@id"],
        },
        "http://www.w3.org/2004/02/skos/core#closeMatch": {
            "anyOf": [
                {"type": "object", "properties": {
                    "@id": {"type": "string"}}, "required": ["@id"]},
                {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {"@id": {"type": "string"}},
                        "required": ["@id"],
                    },
                },
            ]
        },
        "http://schema.org/isPartOf": {
            "type": "object",
            "properties": {"@id": {"type": "string"}},
            "required": ["@id"],
        },
        "http://www.w3.org/2004/02/skos/core#exactMatch": {
            "type": "object",
            "properties": {"@id": {"type": "string"}},
            "required": ["@id"],
        },
    },
    "required": ["@id", "@type", "rdfs:comment", "rdfs:label"],
}

# validate a property definition
property_json_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "@id": {"type": "string"},
        "@type": {"anyOf": [{"type": "string"}, {"type": "array", "items": {"type": "string"}}]},
        "rdfs:comment": {
            "anyOf": [
                {"type": "string"},
                {"$ref": "#/definitions/multi_language"},
                {"type": "null"},
            ]
        },
        "rdfs:label": {"anyOf": [{"type": "string"}, {"$ref": "#/definitions/multi_language"}]},
        "http://schema.org/supersededBy": {
            "anyOf": [
                {"type": "object", "properties": {
                    "@id": {"type": "string"}}, "required": ["@id"]},
                {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {"@id": {"type": "string"}},
                        "required": ["@id"],
                    },
                },
            ]
        },
        "http://schema.org/domainIncludes": {
            "anyOf": [
                {"type": "object", "properties": {
                    "@id": {"type": "string"}}, "required": ["@id"]},
                {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {"@id": {"type": "string"}},
                        "required": ["@id"],
                    },
                },
            ]
        },
        "http://schema.org/rangeIncludes": {
            "anyOf": [
                {"type": "object", "properties": {
                    "@id": {"type": "string"}}, "required": ["@id"]},
                {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {"@id": {"type": "string"}},
                        "required": ["@id"],
                    },
                },
            ]
        },
        "http://www.w3.org/2002/07/owl#equivalentProperty": {
            "type": "object",
            "properties": {"@id": {"type": "string"}},
            "required": ["@id"],
        },
        "rdfs:subPropertyOf": {
            "anyOf": [
                {"type": "object", "properties": {
                    "@id": {"type": "string"}}, "required": ["@id"]},
                {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {"@id": {"type": "string"}},
                        "required": ["@id"],
                    },
                },
            ]
        },
        "http://schema.org/category": {
            "anyOf": [
                {"type": "string"},
                {"type": "array", "items": {"type": "string"}},
                {"$ref": "#/definitions/multi_language"},
            ]
        },
        "http://schema.org/inverseOf": {
            "type": "object",
            "properties": {"@id": {"type": "string"}},
            "required": ["@id"],
        },
        "http://schema.org/sameAs": {
            "type": "object",
            "properties": {"@id": {"type": "string"}},
            "required": ["@id"],
        },
        "http://www.w3.org/2004/02/skos/core#closeMatch": {
            "anyOf": [
                {"type": "object", "properties": {
                    "@id": {"type": "string"}}, "required": ["@id"]},
                {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {"@id": {"type": "string"}},
                        "required": ["@id"],
                    },
                },
            ]
        },
        "http://schema.org/isPartOf": {
            "type": "object",
            "properties": {"@id": {"type": "string"}},
            "required": ["@id"],
        },
        "http://www.w3.org/2004/02/skos/core#exactMatch": {
            "type": "object",
            "properties": {"@id": {"type": "string"}},
            "required": ["@id"],
        },
    },
    "required": [
        "@id",
        "@type",
        "rdfs:comment",
        "rdfs:label",
        "http://schema.org/domainIncludes",
        "http://schema.org/rangeIncludes",
    ],
    "definitions": {
        "multi_language": {
            "type": "object",
            "properties": {"@language": {"type": "string"}, "@value": {"type": "string"}},
            "required": ["@language", "@value"],
        }
    },
}

# validate the whole JSON-LD schema
schema_org_json_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "@context": {
            "type": "object",
            "properties": {
                "rdf": {"type": "string"},
                "rdfs": {"type": "string"},
                "xsd": {"type": "string"},
            },
            "required": ["rdf", "rdfs"],
        },
        "@graph": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "@id": {"type": "string"},
                    "@type": {
                        "anyOf": [
                            {"type": "string"},
                            {"type": "array", "items": {"type": "string"}},
                        ]
                    },
                    "rdfs:comment": {"anyOf": [{"type": "string"}, {"type": "null"}]},
                    "rdfs:label": {
                        "anyOf": [
                            {"type": "string"},
                            {
                                "type": "object",
                                "properties": {
                                    "@language": {"type": "string"},
                                    "@value": {"type": "string"},
                                },
                                "required": ["@language", "@value"],
                            },
                        ]
                    },
                    "rdfs:subClassOf": {
                        "anyOf": [
                            {
                                "type": "object",
                                "properties": {"@id": {"type": "string"}},
                                "required": ["@id"],
                            },
                            {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {"@id": {"type": "string"}},
                                    "required": ["@id"],
                                },
                            },
                        ]
                    },
                    "http://schema.org/supersededBy": {
                        "anyOf": [
                            {
                                "type": "object",
                                "properties": {"@id": {"type": "string"}},
                                "required": ["@id"],
                            },
                            {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {"@id": {"type": "string"}},
                                    "required": ["@id"],
                                },
                            },
                        ]
                    },
                    "http://schema.org/domainIncludes": {
                        "anyOf": [
                            {
                                "type": "object",
                                "properties": {"@id": {"type": "string"}},
                                "required": ["@id"],
                            },
                            {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {"@id": {"type": "string"}},
                                    "required": ["@id"],
                                },
                            },
                        ]
                    },
                    "http://schema.org/rangeIncludes": {
                        "anyOf": [
                            {
                                "type": "object",
                                "properties": {"@id": {"type": "string"}},
                                "required": ["@id"],
                            },
                            {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {"@id": {"type": "string"}},
                                    "required": ["@id"],
                                },
                            },
                        ]
                    },
                    "http://purl.org/dc/terms/source": {
                        "anyOf": [
                            {
                                "type": "object",
                                "properties": {"@id": {"type": "string"}},
                                "required": ["@id"],
                            },
                            {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {"@id": {"type": "string"}},
                                    "required": ["@id"],
                                },
                            },
                        ]
                    },
                    "http://www.w3.org/2002/07/owl#equivalentProperty": {
                        "type": "object",
                        "properties": {"@id": {"type": "string"}},
                        "required": ["@id"],
                    },
                    "rdfs:subPropertyOf": {
                        "type": "object",
                        "properties": {"@id": {"type": "string"}},
                        "required": ["@id"],
                    },
                    "http://schema.org/category": {
                        "anyOf": [
                            {"type": "string"},
                            {"type": "array", "items": {"type": "string"}},
                            {
                                "type": "object",
                                "properties": {
                                    "@language": {"type": "string"},
                                    "@value": {"type": "string"},
                                },
                                "required": ["@language", "@value"],
                            },
                        ]
                    },
                    "http://www.w3.org/2002/07/owl#equivalentClass": {
                        "anyOf": [
                            {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {"@id": {"type": "string"}},
                                    "required": ["@id"],
                                },
                            },
                            {
                                "type": "object",
                                "properties": {"@id": {"type": "string"}},
                                "required": ["@id"],
                            },
                        ]
                    },
                    "http://schema.org/inverseOf": {
                        "type": "object",
                        "properties": {"@id": {"type": "string"}},
                        "required": ["@id"],
                    },
                    "http://schema.org/sameAs": {
                        "type": "object",
                        "properties": {"@id": {"type": "string"}},
                        "required": ["@id"],
                    },
                    "http://www.w3.org/2004/02/skos/core#closeMatch": {
                        "anyOf": [
                            {
                                "type": "object",
                                "properties": {"@id": {"type": "string"}},
                                "required": ["@id"],
                            },
                            {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {"@id": {"type": "string"}},
                                    "required": ["@id"],
                                },
                            },
                        ]
                    },
                    "http://schema.org/isPartOf": {
                        "type": "object",
                        "properties": {"@id": {"type": "string"}},
                        "required": ["@id"],
                    },
                    "http://www.w3.org/ns/rdfa#usesVocabulary": {
                        "type": "object",
                        "properties": {"@id": {"type": "string"}},
                        "required": ["@id"],
                    },
                    "http://www.w3.org/2004/02/skos/core#exactMatch": {
                        "type": "object",
                        "properties": {"@id": {"type": "string"}},
                        "required": ["@id"],
                    },
                    "http://schema.org/softwareVersion": {
                        "type": "object",
                        "properties": {
                            "@language": {"type": "string"},
                            "@value": {"type": "string"},
                        },
                        "required": ["@language", "@value"],
                    },
                },
                "required": ["@id"],
            },
        },
        "@id": {"type": "string"},
    },
    "required": ["@context", "@graph", "@id"],
}
