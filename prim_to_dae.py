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
    cx = sum(float(p["position"][0]) for p in prims) / len(prims)
    cy = sum(float(p["position"][1]) for p in prims) / len(prims)
    cz = sum(float(p["position"][2]) for p in prims) / len(prims)
    for p in prims:
        p["position"][0] = float(p["position"][0]) - cx
        p["position"][1] = float(p["position"][1]) - cy
        p["position"][2] = float(p["position"][2]) - cz
    return prims

def prims_to_dae(prims):
    prims = normalize_positions(prims)
    all_verts = []
    all_faces = []
    vert_offset = 0
    for prim in prims:
        ptype = prim.get("type", "BOX").upper()
        pos   = [float(x) for x in prim.get("position", [0,0,0])]
        size  = [float(x) for x in prim.get("size", [0.5,0.5,0.5])]
        rot   = prim.get("rotation", [0,0,0,1])
        divs  = int(prim.get("divisions", 16))
        if ptype == "CYLINDER":
            verts, faces = make_cylinder(pos, size, rot, divs)
        elif ptype == "SPHERE":
            verts, faces = make_sphere(pos, size, rot, divs)
        else:
            verts, faces = make_box(pos, size, rot)
        for face in faces:
            all_faces.append([fi + vert_offset for fi in face])
        all_verts.extend(verts)
        vert_offset += len(verts)
    dae = build_dae(all_verts, all_faces)
    return dae

def build_dae(verts, faces):
    pos_parts = []
    for v in verts:
        pos_parts.append(str(round(v[0], 6)))
        pos_parts.append(str(round(v[1], 6)))
        pos_parts.append(str(round(v[2], 6)))
    pos_str = " ".join(pos_parts)

    triangles = []
    for face in faces:
        if len(face) == 3:
            triangles.append(face)
        elif len(face) == 4:
            triangles.append([face[0], face[1], face[2]])
            triangles.append([face[0], face[2], face[3]])
        elif len(face) > 4:
            for i in range(1, len(face) - 1):
                triangles.append([face[0], face[i], face[i+1]])

    tri_parts = []
    for t in triangles:
        tri_parts.append(str(t[0]))
        tri_parts.append(str(t[1]))
        tri_parts.append(str(t[2]))
    tri_str = " ".join(tri_parts)

    vert_count = len(verts)
    tri_count = len(triangles)

    dae = '<?xml version="1.0" encoding="utf-8"?>\n'
    dae += '<COLLADA xmlns="http://www.collada.org/2005/11/COLLADASchema" version="1.4.1">\n'
    dae += '  <asset>\n'
    dae += '    <unit name="meter" meter="1"/>\n'
    dae += '    <up_axis>Z_UP</up_axis>\n'
    dae += '  </asset>\n'
    dae += '  <library_geometries>\n'
    dae += '    <geometry id="mesh0" name="PrimMesh">\n'
    dae += '      <mesh>\n'
    dae += '        <source id="mesh0-positions">\n'
    dae += '          <float_array id="mesh0-positions-array" count="' + str(vert_count * 3) + '">' + pos_str + '</float_array>\n'
    dae += '          <technique_common>\n'
    dae += '            <accessor source="#mesh0-positions-array" count="' + str(vert_count) + '" stride="3">\n'
    dae += '              <param name="X" type="float"/>\n'
    dae += '              <param name="Y" type="float"/>\n'
    dae += '              <param name="Z" type="float"/>\n'
    dae += '            </accessor>\n'
    dae += '          </technique_common>\n'
    dae += '        </source>\n'
    dae += '        <vertices id="mesh0-vertices">\n'
    dae += '          <input semantic="POSITION" source="#mesh0-positions"/>\n'
    dae += '        </vertices>\n'
    dae += '        <triangles count="' + str(tri_count) + '">\n'
    dae += '          <input semantic="VERTEX" source="#mesh0-vertices" offset="0"/>\n'
    dae += '          <p>' + tri_str + '</p>\n'
    dae += '        </triangles>\n'
    dae += '      </mesh>\n'
    dae += '    </geometry>\n'
    dae += '  </library_geometries>\n'
    dae += '  <library_visual_scenes>\n'
    dae += '    <visual_scene id="Scene" name="Scene">\n'
    dae += '      <node id="PrimMesh" name="PrimMesh" type="NODE">\n'
    dae += '        <instance_geometry url="#mesh0"/>\n'
    dae += '      </node>\n'
    dae += '    </visual_scene>\n'
    dae += '  </library_visual_scenes>\n'
    dae += '  <scene>\n'
    dae += '    <instance_visual_scene url="#Scene"/>\n'
    dae += '  </scene>\n'
    dae += '</COLLADA>'
    return dae
