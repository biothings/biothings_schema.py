BASE_SCHEMA = ['schema.org', 'bioschemas']
SCHEMAORG_JSONLD_BASE_URL = 'https://raw.githubusercontent.com/schemaorg/schemaorg/main/data/releases'
SCHEMAORG_VERSION_URL = 'https://raw.githubusercontent.com/schemaorg/schemaorg/main/versions.json'

DATATYPES = ["http://schema.org/DataType", "http://schema.org/Boolean",
             "http://schema.org/False", "http://schema.org/True",
             "http://schema.org/Date", "http://schema.org/DateTime",
             "http://schema.org/Number", "http://schema.org/Integer",
             "http://schema.org/Float", "http://schema.org/Text",
             "http://schema.org/CssSelectorType", "http://schema.org/URL",
             "http://schema.org/XPathType", "http://schema.org/Time"]

IGNORED_CLASS_PROPERTY = ["rdfs:Class", "rdf:type", "rdfs:label"]

# the field name contains JSON-Schema based validation rules
VALIDATION_FIELD = "$validation"
# a list of alternative validation fields for back-compatibility
# in case that we change the default VALIDATION_FIELD at some point
ALT_VALIDATION_FIELDS = []