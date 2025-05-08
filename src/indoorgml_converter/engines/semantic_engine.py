# # src/indoorgml_converter/engines/semantic_engine.py
#
# from ..converter import detect_level
#
# def attach_semantics(cell_spaces, gdf=None):
#     """
#     Ensure every cell_space has a normalized floor_name and level.
#     Any missing or None floor/level fields get back-filled
#     with the detected value.
#     """
#     for cs in cell_spaces:
#         lvl = detect_level(cs['properties'])
#         for key in ('floor_name', 'level_name', 'floor', 'level'):
#             if cs['properties'].get(key) is None:
#                 cs['properties'][key] = lvl
#     # we modify in place; no return needed



def attach_semantics(cell_spaces, gdf=None):
    """
    Back-fill every cell_space.props so that each has
    floor_name, level_name, floor, and level set (if initially missing).
    """
    from ..converter import detect_level
    for cs in cell_spaces:
        lvl = detect_level(cs['properties'])
        for key in ('floor_name', 'level_name', 'floor', 'level'):
            if cs['properties'].get(key) is None:
                cs['properties'][key] = lvl
