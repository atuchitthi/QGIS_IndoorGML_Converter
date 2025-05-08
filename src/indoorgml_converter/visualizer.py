# # src/indoorgml_converter/visualizer.py
#
# import matplotlib.pyplot as plt
# import matplotlib.patches as patches
# from matplotlib.lines import Line2D
# from shapely.geometry import Polygon, LineString, Point
# import logging
#
# from .converter import detect_level
#
# logger = logging.getLogger(__name__)
#
# TYPE_COLORS = {
#     'room':      '#4287f5',
#     'corridor':  '#42f5a1',
#     'door':      '#f5a142',
#     'stairs':    '#f542f2',
#     'elevator':  '#f54242',
#     'default':   '#aaaaaa'
# }
#
# def determine_feature_type(props: dict) -> str:
#     txt = " ".join(str(v).lower() for v in props.values())
#     if any(w in txt for w in ('door', 'entrance', 'exit')):
#         return 'door'
#     if any(w in txt for w in ('corridor', 'hallway', 'passage')):
#         return 'corridor'
#     if any(w in txt for w in ('stair', 'steps')):
#         return 'stairs'
#     if any(w in txt for w in ('elevator', 'lift')):
#         return 'elevator'
#     return 'room'
#
#
# def visualize(cell_spaces, transitions, **_):
#     # map each cell to its floor
#     lvl_map = {cs['id']: detect_level(cs['properties'])
#                for cs in cell_spaces}
#
#     floors = sorted(
#         set(lvl_map.values()),
#         key=lambda x: (-1 if x == 'B' else 0 if x == 'G'
#                         else int(x) if x.isdigit() else 999)
#     )
#
#     # compute global bounding box
#     xs, ys = [], []
#     for cs in cell_spaces:
#         minx, miny, maxx, maxy = cs['geometry'].bounds
#         xs += [minx, maxx]; ys += [miny, maxy]
#     pad = max(max(xs) - min(xs), max(ys) - min(ys)) * 0.05
#     xlim = (min(xs) - pad, max(xs) + pad)
#     ylim = (min(ys) - pad, max(ys) + pad)
#
#     # legend handles
#     handles = [
#         patches.Patch(facecolor=TYPE_COLORS[t], edgecolor='black',
#                       alpha=0.4, label=t.capitalize())
#         for t in ('room', 'corridor', 'door', 'stairs', 'elevator')
#     ] + [Line2D([], [], linestyle=':', color='gray', label='Adjacency')]
#
#     for floor in floors:
#         if floor == 'None':
#             # skip features with no detected floor
#             continue
#
#         fig, ax = plt.subplots(figsize=(8, 8))
#         ax.set_title(f"Floor: {floor}", fontsize=16)
#         ax.set_xlim(*xlim); ax.set_ylim(*ylim)
#
#         # adjacency lines
#         for a, b in transitions:
#             if lvl_map[a] == floor == lvl_map[b]:
#                 pa = next(c for c in cell_spaces if c['id'] == a)['geometry'].centroid
#                 pb = next(c for c in cell_spaces if c['id'] == b)['geometry'].centroid
#                 ax.plot([pa.x, pb.x], [pa.y, pb.y],
#                         linestyle=':', color='gray', alpha=0.6, zorder=1)
#
#         # draw polygons
#         for cs in cell_spaces:
#             if lvl_map[cs['id']] != floor: continue
#             geom, props = cs['geometry'], cs['properties']
#             ftype = determine_feature_type(props)
#             col = TYPE_COLORS.get(ftype, TYPE_COLORS['default'])
#             # choose label: name → room → id
#             txt = props.get('name') or props.get('room') or cs['id']
#             if isinstance(geom, Polygon):
#                 x, y = geom.exterior.xy
#                 ax.fill(x, y, facecolor=col, edgecolor='black', alpha=0.4, zorder=2)
#                 ax.text(geom.centroid.x, geom.centroid.y,
#                         txt, ha='center', va='center', fontsize=9, zorder=3)
#
#         # draw lines
#         for cs in cell_spaces:
#             if lvl_map[cs['id']] != floor: continue
#             geom, props = cs['geometry'], cs['properties']
#             ftype = determine_feature_type(props)
#             col = TYPE_COLORS.get(ftype, TYPE_COLORS['default'])
#             if isinstance(geom, LineString):
#                 x, y = geom.xy
#                 ax.plot(x, y, '--', color=col, linewidth=2, zorder=4)
#                 # label at midpoint
#                 mid = geom.interpolate(0.5, normalized=True)
#                 ax.text(mid.x, mid.y,
#                         props.get('room') or cs['id'],
#                         ha='center', va='center', fontsize=8, zorder=5)
#
#         # draw points
#         for cs in cell_spaces:
#             if lvl_map[cs['id']] != floor: continue
#             geom, props = cs['geometry'], cs['properties']
#             ftype = determine_feature_type(props)
#             col = TYPE_COLORS.get(ftype, TYPE_COLORS['default'])
#             if isinstance(geom, Point):
#                 ax.scatter(geom.x, geom.y, s=50,
#                            color=col, edgecolor='black', zorder=6)
#                 ax.text(geom.x, geom.y,
#                         props.get('room') or cs['id'],
#                         ha='left', va='bottom', fontsize=8, zorder=7)
#
#         ax.set_aspect('equal', 'box')
#         ax.grid(True, linestyle='--', alpha=0.3)
#         ax.legend(handles=handles, loc='upper right', fontsize=8)
#         plt.tight_layout()
#
#     plt.show()



# src/indoorgml_converter/visualizer.py

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.lines import Line2D
from shapely.geometry import Polygon, LineString, Point
import logging

logger = logging.getLogger(__name__)

TYPE_COLORS = {
    'room':      '#4287f5',
    'corridor':  '#42f5a1',
    'door':      '#f5a142',
    'stairs':    '#f542f2',
    'elevator':  '#f54242',
    'default':   '#aaaaaa'
}


def determine_feature_type(props: dict) -> str:
    txt = " ".join(str(v).lower() for v in props.values())
    if any(w in txt for w in ('door', 'entrance', 'exit')):
        return 'door'
    if any(w in txt for w in ('corridor', 'hallway', 'passage')):
        return 'corridor'
    if any(w in txt for w in ('stair', 'steps')):
        return 'stairs'
    if any(w in txt for w in ('elevator', 'lift')):
        return 'elevator'
    return 'room'


def visualize(cell_spaces, transitions, **_):
    from .converter import detect_level
    # build id→level map
    lvl_map = {cs['id']: detect_level(cs['properties']) for cs in cell_spaces}

    # sort floors: B → G → numeric → others
    floors = sorted(
        set(lvl_map.values()),
        key=lambda x: (-1 if x == 'B' else 0 if x == 'G'
                       else int(x) if x.isdigit() else 999)
    )

    # global bounding box
    xs, ys = [], []
    for cs in cell_spaces:
        minx, miny, maxx, maxy = cs['geometry'].bounds
        xs += [minx, maxx]; ys += [miny, maxy]
    pad = max(max(xs) - min(xs), max(ys) - min(ys)) * 0.05
    xlim = (min(xs) - pad, max(xs) + pad)
    ylim = (min(ys) - pad, max(ys) + pad)

    # legend
    handles = [
        patches.Patch(facecolor=TYPE_COLORS[t], edgecolor='black',
                      alpha=0.4, label=t.capitalize())
        for t in ('room', 'corridor', 'door', 'stairs', 'elevator')
    ] + [Line2D([], [], linestyle=':', color='gray', label='Adjacency')]

    for floor in floors:
        if floor == 'None':
            continue  # skip unclassified

        fig, ax = plt.subplots(figsize=(8, 8))
        ax.set_title(f"Floor: {floor}", fontsize=16)
        ax.set_xlim(*xlim); ax.set_ylim(*ylim)

        # adjacency lines
        for a, b in transitions:
            if lvl_map[a] == floor == lvl_map[b]:
                pa = next(c for c in cell_spaces if c['id'] == a)['geometry'].centroid
                pb = next(c for c in cell_spaces if c['id'] == b)['geometry'].centroid
                ax.plot([pa.x, pb.x], [pa.y, pb.y],
                        linestyle=':', color='gray', alpha=0.6, zorder=1)

        # draw polygons
        for cs in cell_spaces:
            if lvl_map[cs['id']] != floor: continue
            geom, props = cs['geometry'], cs['properties']
            ftype = determine_feature_type(props)
            col = TYPE_COLORS.get(ftype, TYPE_COLORS['default'])
            label = props.get('name') or props.get('room') or cs['id']
            if isinstance(geom, Polygon):
                x, y = geom.exterior.xy
                ax.fill(x, y, facecolor=col, edgecolor='black', alpha=0.4, zorder=2)
                ax.text(geom.centroid.x, geom.centroid.y,
                        label, ha='center', va='center', fontsize=9, zorder=3)

        # draw lines
        for cs in cell_spaces:
            if lvl_map[cs['id']] != floor: continue
            geom, props = cs['geometry'], cs['properties']
            ftype = determine_feature_type(props)
            col = TYPE_COLORS.get(ftype, TYPE_COLORS['default'])
            if isinstance(geom, LineString):
                x, y = geom.xy
                ax.plot(x, y, '--', color=col, linewidth=2, zorder=4)
                mid = geom.interpolate(0.5, normalized=True)
                ax.text(mid.x, mid.y,
                        props.get('room') or cs['id'],
                        ha='center', va='center', fontsize=8, zorder=5)

        # draw points
        for cs in cell_spaces:
            if lvl_map[cs['id']] != floor: continue
            geom, props = cs['geometry'], cs['properties']
            ftype = determine_feature_type(props)
            col = TYPE_COLORS.get(ftype, TYPE_COLORS['default'])
            if isinstance(geom, Point):
                ax.scatter(geom.x, geom.y, s=50,
                           color=col, edgecolor='black', zorder=6)
                ax.text(geom.x, geom.y,
                        props.get('room') or cs['id'],
                        ha='left', va='bottom', fontsize=8, zorder=7)

        ax.set_aspect('equal', 'box')
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.legend(handles=handles, loc='upper left', fontsize=8)
        plt.tight_layout()

    plt.show()
