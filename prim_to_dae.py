import numpy as np
import math

# ─────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────

def make_box(pos, size, rotation):
    """Generate vertices and faces for a box prim."""
    x, y, z = size[0]/2, size[1]/2, size[2]/2
    verts = [
        [-x,-y,-z],[x,-y,-z],[x,y,-z],[-x,y,-z],
        [-x,-y, z],[x,-y, z],[x,y, z],[-x,y, z],
    ]
    faces = [
        [0,1,2,3],  # bottom
        [4,5,6,7],  # top
        [0,1,5,4],  # front
        [2,3,7,6],  # back
        [1,2,6,5],  # right
        [0,3,7,4],  # left
    ]
    verts = apply_transform(verts, pos, rotation)
    return verts, faces

def make_cylinder(pos, size, rotation, divisions=16):
    """Generate vertices and faces for a cylinder prim."""
    verts = []
    faces = []
    r_x, r_y, h = size[0]/2, size[1]/2, size[2]

    # bottom and top circles
    for layer in [0, 1]:
        z = -h/2 + layer * h
        for i in range(divisions):
            angle = 2 * math.pi * i / divisions
            verts.append([
                r_x * math.cos(angle),
                r_y * math.sin(angle),
                z
            ])

    # side faces
    for i in range(divisions):
        next_i = (i + 1) % divisions
        faces.append([i, next_i, next_i + divisions, i + divisions])

    # bottom cap
    bottom = list(range(divisions))
    faces.append(bottom)

    # top cap
    top = list(range(divisions, divisions * 2))
    faces.append(top)

    verts = apply_transform(verts, pos, rotation)
    return verts, faces

def make_sphere(pos, size, rotation, divisions=16):
    """Generate vertices and faces for a sphere prim."""
    verts = []
    faces = []
    r_x, r_y, r_z = size[0]/2, size[1]/2, size[2]/2

    for i in range(divisions + 1):
        lat = math.pi * (-0.5 + i / divisions)
        for j in range(divisions):
            lon = 2 * math.pi * j / divisions
            verts.append([
                r_x * math.cos(lat) * math.cos(lon),
                r_y * math.cos(lat) * math.sin(lon),
                r_z * math.sin(lat)
            ])

    for i in range(divisions):
        for j in range(divisions):
            p1 = i * divisions + j
            p2 = p1 + divisions
            p3 = p2 + 1 if (j + 1) < divisions else p2 - divisions + 1
            p4 = p1 + 1 if (j + 1) < divisions else p1 - divisions + 1
            faces.append([p1, p2, p3, p4])

    verts = apply_transform(verts, pos, rotation)
    return verts, faces

def apply_transform(verts, pos, rotation):
    """Apply position offset to all vertices."""
    result = []
    for v in verts:
        result.append([
            v[0] + pos[0],
            v[1] + pos[1],
            v[2] + pos[2]
        ])
    return result

def normalize_positions(prims):
    """Center the object around origin."""
    if not prims:
        return prims
    cx = sum(p["position"][0] for p in prims) / len(prims)
    cy = sum(p["position"][1] for p in prims) / len(prims)
    cz = sum(p["position"][2] for p in prims) / len(prims)
    for p in prims:
        p["position"][0] -= cx
        p["position"][1] -= cy
        p["position"][2] -= cz
    return prims

# ─────────────────────────────────────────
#  Main converter
# ─────────────────────────────────────────

def prims_to_dae(prims):
    """Convert a list of prim dicts to a .dae (Collada) string."""

    prims = normalize_positions(prims)

    all_verts = []
    all_faces = []
    vert_offset = 0

    for prim in prims:
        ptype   = prim.get("type", "BOX").upper()
        pos     = prim.get("position", [0, 0, 0])
        size    = prim.get("size", [0.5, 0.5, 0.5])
        rot     = prim.get("rotation", [0, 0, 0, 1])
        divs    = prim.get("divisions", 16)

        if ptype == "BOX":
            verts, faces = make_box(pos, size, rot)
        elif ptype == "CYLINDER":
            verts, faces = make_cylinder(pos, size, rot, divs)
        elif ptype == "SPHERE":
            verts, faces = make_sphere(pos, size, rot, divs)
        else:
            # default to box for unsupported types
            verts, faces = make_box(pos, size, rot)

        # offset face indices
        for face in faces:
            all_faces.append([fi + vert_offset for fi in face])

        all_verts.extend(verts)
        vert_offset += len(verts)

    return build_dae(all_verts, all_faces)

# ─────────────────────────────────────────
#  DAE builder
# ─────────────────────────────────────────

def build_dae(verts, faces):
    """Build the actual .dae XML string."""

    # vertex positions string
    pos_str = " ".join(
        f"{v[0]:.6f} {v[1]:.6f} {v[2]:.
