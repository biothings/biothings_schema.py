import pytest

from biothings_schema import Schema, SchemaClass, SchemaProperty

SCHEMA_URL = (
    "https://raw.githubusercontent.com/data2health/schemas/biothings/"
    "biothings/biothings_curie_kevin.jsonld"
)


def load_schema(path_or_url: str) -> Schema:
    """Create a Schema from a file path or URL."""
    return Schema(path_or_url)


@pytest.fixture(scope="module")
def se():
    """Shared Schema instance for tests."""
    return load_schema(SCHEMA_URL)


def test_list_all_classes(se):
    """Test list_all_classes function"""
    all_cls = se.list_all_classes()
    all_cls_names = [_cls.name for _cls in all_cls]

    # Assert root-level CURIE class is included
    assert "bts:PlanetaryEntity" in all_cls_names, (
            "'bts:PlanetaryEntity' not found in class names"
        )
    # Assert raw label name is NOT present
    assert "Gene" not in all_cls_names, (
            "'Gene' (non-CURIE) unexpectedly found in class names"
        )
    # Assert all classes are SchemaClass instances
    assert all(isinstance(cls, SchemaClass) for cls in all_cls), (
            "Not all classes are SchemaClass instances"
        )


def test_list_all_properties(se):
    """Test list_all_properties function"""
    all_props = se.list_all_properties()
    all_prop_names = [_prop.name for _prop in all_props]

    assert "schema:author" in all_prop_names, (
        "'schema:author' not found in properties"
    )
    assert "name" not in all_prop_names, (
        "Unexpected plain 'name' found in properties"
    )
    assert "bts:ffff" not in all_prop_names, (
        "Fake property 'bts:ffff' should not exist"
    )
    assert isinstance(all_props[0], SchemaProperty), (
        "First property is not a SchemaProperty"
    )


def test_get_class(se):
    """Test get_class function"""
    scls = se.get_class("bts:Gene")
    assert isinstance(scls, SchemaClass), (
        "Returned class is not a SchemaClass"
    )


def test_get_property(se):
    """Test get_property function"""
    sp = se.get_property("bts:geneticallyInteractsWith")
    assert isinstance(sp, SchemaProperty), (
            "Returned property is not a SchemaProperty"
        )
