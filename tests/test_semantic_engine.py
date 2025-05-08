# tests/test_semantic_engine.py
from indoorgml_converter.engines.semantic_engine import attach_semantics
from indoorgml_converter.converter import detect_level

def test_attach_semantics_backfills():
    # start with some missing floor fields
    cs = {"id":"x","properties": {"floor_name":None, "level":None, "foo":"bar"}}
    level = detect_level({"floor_name":"G"})
    # override props so detection returns 'G'
    cs["properties"]["floor_name"] = None
    cs["properties"]["level"] = None
    attach_semantics([cs])
    for key in ("floor_name","level_name","floor","level"):
        assert cs["properties"][key] == "None" or cs["properties"][key] == level
