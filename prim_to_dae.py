import math

def make_box(pos, size, rotation):
    x, y, z = size[0]/2, size[1]/2, size[2]/2
    verts = [
        [-x,-y,-z],[x,-y,-z],[x,y,-z],[-x,y,-z],
        [-x,-y, z],[x,-y, z],[x,y, z],[-x,y, z],
    ]
    faces = [
        [0,1,2,3],[4,5,6,7],[0,1,5,4],
        [2,3,7,6],[1,2,6,5],[0,3,7,4],
    ]
    verts = apply_transform(verts, pos)
    return verts, faces

def make_cylinder(pos, size, rotation, divisions=16):
    verts = []
    faces = []
    r_x, r_y, h = size[0]/2, size[1]/2, size[2]
    for layer in [0, 1]:
        z = -h/2 + layer * h
        for i in range(divisions):
            angle = 2 * math.pi * i / divisions
            verts.append([r_x * math.cos(angle), r_y * math.sin(angle), z])
    for i in range(divisions):
        next_i = (i + 1) % divisions
        faces.append([i, next_i, next_i + divisions, i + divisions])
    faces.append(list(range(divisions)))
    faces.append(list(range(divisions, divisions * 2)))
    verts = apply_transform(verts, pos)
    return verts, faces

def make_sphere(pos, size, rotation, divisions=16):
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
    verts = apply_transform(verts, pos)
    return verts, faces

def apply_transform(verts, pos):
    return [[v[0]+pos[0], v[1]+pos[1], v[2]+pos[2]] for v in verts]

def normalize_positions(prims):
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

def prims_to_dae(prims):
    prims = normalize_positions(prims)
    all_verts = []
    all_faces = []
    vert_offset = 0
    for prim in prims:
        ptype = prim.get("type", "BOX").upper()
