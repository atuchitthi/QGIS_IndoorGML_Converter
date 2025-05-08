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



# src/indoorgml_converter/engines/semantic_engine.py

def attach_semantics(cell_spaces, gdf=None):
    """
    Back-fill each cell_space.props so that it has
    'floor_name','level_name','floor_level', 'flevel','floor','level','name','feature' set.
    """
    for cs in cell_spaces:
        props = cs['properties']

        # 1) FLOOR semantics (unchanged)
        from ..converter import detect_level
        lvl = detect_level(props)
        for key in ('floor_name', 'level_name','floor_level', 'flevel', 'floor', 'level'):
            if props.get(key) is None:
                props[key] = lvl

        # 2) NAME semantics: standardize on props['name']
        #    from .properties: label → name, room_id → name, ref → name
        if props.get('label'):
            props.setdefault('name', props['label'])
        elif not props.get('name'):  # only if name is missing/falsey
            if props.get('room_id'):
                props['name'] = props['room_id']
            elif props.get('ref'):
                props['name'] = props['ref']

        # 3) FEATURE semantics: standardize on props['feature']
        #    from .properties: space_use/type/function, or corridor flag
        if props.get('space_use'):
            props.setdefault('feature', props['space_use'])
        elif props.get('type'):
            props.setdefault('feature', props['type'])
        elif props.get('function'):
            props.setdefault('feature', props['function'])
        elif str(props.get('corridor')).lower() in ('yes', 'true', '1'):
            props.setdefault('feature', 'corridor')
        # else leave whatever 'feature' was, or empty

    return cell_spaces
