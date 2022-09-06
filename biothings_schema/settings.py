BASE_SCHEMA = ['schema.org', 'bioschemas']
# This is a list of namespaces commonly used in @context when defining the schema
# We skip these as the base schemas to load
COMMON_NAMESPACES = ["rdf", "rdfs", "rdfa", "xsd", "owl", "dct", "dwc"]
SCHEMAORG_JSONLD_BASE_URL = 'https://raw.githubusercontent.com/schemaorg/schemaorg/main/data/releases'
# SCHEMAORG_VERSION_URL = 'https://raw.githubusercontent.com/schemaorg/schemaorg/main/versions.json'
# Note that github API has 60/hr rate-limit for unauthorized API call
# we use utils.timed_lru_cache to avoid calling this API too many times
SCHEMAORG_VERSION_URL = 'https://api.github.com/repos/schemaorg/schemaorg/releases/latest'

DDE_SCHEMA_BASE_URL = "https://discovery.biothings.io/api/registry/"

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

# the default $schema value if not provided in validation json schema
DEFAULT_JSONSCHEMA_METASCHEMA = "https://json-schema.org/draft/2020-12/schema"
