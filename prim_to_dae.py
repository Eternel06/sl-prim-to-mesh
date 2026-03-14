import math

def rotate_vertex(v, q):
    x, y, z = v
    qx, qy, qz, qw = q
    ix =  qw*x + qy*z - qz*y
    iy =  qw*y + qz*x - qx*z
    iz =  qw*z + qx*y - qy*x
    iw = -qx*x - qy*y - qz*z
    rx = ix*qw + iw*(-qx) + iy*(-qz) - iz*(-qy)
    ry = iy*qw + iw*(-qy) + iz*(-qx) - ix*(-qz)
    rz = iz*qw + iw*(-qz) + ix*(-qy) - iy*(-qx)
    return [rx, ry, rz]

def apply_transform(verts, pos, rot):
    result = []
    for v in verts:
        rv = rotate_vertex(v, rot)
        result.append([rv[0]+pos[0], rv[1]+pos[1], rv[2]+pos[2]])
    return result

def make_box(pos, size, rot):
    x, y, z = size[0]/2, size[1]/2, size[2]/2
    verts = [
        [-x,-y,-z],[x,-y,-z],[x,y,-z],[-x,y,-z],
        [-x,-y, z],[x,-y, z],[x,y, z],[-x,y, z],
    ]
    faces = [
        [0,1,2,3],[4,7,6,5],[0,4,5,1],
        [2,6,7,3],[1,5,6,2],[0,3,7,4],
    ]
    verts = apply_transform(verts, pos, rot)
    return verts, faces

def make_cylinder(pos, size, rot, divisions=16, hollow=0.0, path_cut_begin=0.0, path_cut_end=1.0):
    verts = []
    faces = []
    r_x = size[0]/2
    r_y = size[1]/2
    h = size[2]
    cut_begin = path_cut_begin * 2 * math.pi
    cut_end = path_cut_end * 2 * math.pi
    angle_range = cut_end - cut_begin
    steps = max(3, int(divisions * angle_range / (2 * math.pi)))
    outer_bottom = []
    outer_top = []
    inner_bottom = []
    inner_top = []
    for i in range(steps + 1):
        angle = cut_begin + angle_range * i / steps
        cx = math.cos(angle)
        cy = math.sin(angle)
        outer_bottom.append([r_x * cx, r_y * cy, -h/2])
        outer_top.append([r_x * cx, r_y * cy, h/2])
        if hollow > 0:
            inner_bottom.append([r_x * hollow * cx, r_y * hollow * cy, -h/2])
            inner_top.append([r_x * hollow * cx, r_y * hollow * cy, h/2])
    ob = 0
    verts.extend(outer_bottom)
    ot = len(verts)
    verts.extend(outer_top)
    for i in range(steps):
        faces.append([ob+i, ob+i+1, ot+i+1, ot+i])
    if hollow > 0:
        ib = len(verts)
        verts.extend(inner_bottom)
        it2 = len(verts)
        verts.extend(inner_top)
        for i in range(steps):
            faces.append([ib+i+1, ib+i, it2+i, it2+i+1])
        for i in range(steps):
            faces.append([ot+i, ot+i+1, it2+i+1, it2+i])
        for i in range(steps):
            faces.append([ob+i+1, ob+i, ib+i, ib+i+1])
    else:
        for i in range(1, steps-1):
            faces.append([ot, ot+i, ot+i+1])
            faces.append([ob, ob+i+1, ob+i])
    verts = apply_transform(verts, pos, rot)
    return verts, faces

def make_sphere(pos, size, rot, divisions=16):
    verts = []
    faces = []
    r_x = size[0]/2
    r_y = size[1]/2
    r_z = size[2]/2
    lat_steps = max(3, divisions)
    lon_steps = max(3, divisions)
    for i in range(lat_steps + 1):
        lat = math.pi * (-0.5 + i / lat_steps)
        for j in range(lon_steps):
            lon = 2 * math.pi * j / lon_steps
            verts.append([
                r_x * math.cos(lat) * math.cos(lon),
                r_y * math.cos(lat) * math.sin(lon),
                r_z * math.sin(lat)
            ])
    for i in range(lat_steps):
        for j in range(lon_steps):
            p1 = i * lon_steps + j
            p2 = p1 + lon_steps
            p3 = p2 + 1 if (j+1) < lon_steps else p2 - lon_steps + 1
            p4 = p1 + 1 if (j+1) < lon_steps else p1 - lon_steps + 1
            faces.append([p1, p2, p3, p4])
    verts = apply_transform(verts, pos, rot)
    return verts, faces

def make_prism(pos, size, rot):
    x, y, z = size[0]/2, size[1]/2, size[2]/2
    verts = [
        [0,-y,-z],[x,y,-z],[-x,y,-z],
        [0,-y, z],[x,y, z],[-x,y, z],
    ]
    faces = [
        [0,1,2],[3,5,4],
        [0,3,4,1],[1,4,5,2],[2,5,3,0],
    ]
    verts = apply_transform(verts, pos, rot)
    return verts, faces

def make_torus(pos, size, rot, divisions=16):
    verts = []
    faces = []
    R = size[0]/2
    r = size[2]/4
    for i in range(divisions):
        phi = 2 * math.pi * i / divisions
        for j in range(divisions):
            theta = 2 * math.pi * j / divisions
            x = (R + r * math.cos(theta)) * math.cos(phi)
            y = (R + r * math.cos(theta)) * math.sin(phi)
            z = r * math.sin(theta)
            verts.append([x, y, z])
    for i in range(divisions):
        for j in range(divisions):
            p1 = i * divisions + j
            p2 = ((i+1) % divisions) * divisions + j
            p3 = ((i+1) % divisions) * divisions + (j+1) % divisions
            p4 = i * divisions + (j+1) % divisions
            faces.append([p1, p2, p3, p4])
    verts = apply_transform(verts, pos, rot)
    return verts, faces

def make_tube(pos, size, rot, divisions=16):
    verts = []
    faces = []
    R = size[0]/2
    rx = size[0]/4
    ry = size[1]/4
    for i in range(divisions):
        phi = 2 * math.pi * i / divisions
        for j in range(divisions):
            theta = 2 * math.pi * j / divisions
            x = (R + rx * math.cos(theta)) * math.cos(phi)
            y = (R + ry * math.cos(theta)) * math.sin(phi)
            z = rx * math.sin(theta)
            verts.append([x, y, z])
    for i in range(divisions):
        for j in range(divisions):
            p1 = i * divisions + j
            p2 = ((i+1) % divisions) * divisions + j
            p3 = ((i+1) % divisions) * divisions + (j+1) % divisions
            p4 = i * divisions + (j+1) % divisions
            faces.append([p1, p2, p3, p4])
    verts = apply_transform(verts, pos, rot)
    return verts, faces

def make_ring(pos, size, rot, divisions=16):
    return make_torus(pos, size, rot, divisions)

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
        ptype  = prim.get("type", "BOX").upper()
        pos    = [float(x) for x in prim.get("position", [0,0,0])]
        size   = [float(x) for x in prim.get("size", [0.5,0.5,0.5])]
        rot    = [float(x) for x in prim.get("rotation", [0,0,0,1])]
        divs   = int(prim.get("divisions", 16))
        hollow = float(prim.get("hollow", 0.0))
        pcut_b = float(prim.get("path_cut_begin", 0.0))
        pcut_e = float(prim.get("path_cut_end", 1.0))
        if ptype == "CYLINDER":
            verts, faces = make_cylinder(pos, size, rot, divs, hollow, pcut_b, pcut_e)
        elif ptype == "SPHERE":
            verts, faces = make_sphere(pos, size, rot, divs)
        elif ptype == "PRISM":
            verts, faces = make_prism(pos, size, rot)
        elif ptype == "TORUS":
            verts, faces = make_torus(pos, size, rot, divs)
        elif ptype == "TUBE":
            verts, faces = make_tube(pos, size, rot, divs)
        elif ptype == "RING":
            verts, faces = make_ring(pos, size, rot, divs)
        else:
            verts, faces = make_box(pos, size, rot)
        for face in faces:
            all_faces.append([fi + vert_offset for fi in face])
        all_verts.extend(verts)
        vert_offset += len(verts)
    return build_dae(all_verts, all_faces)

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
            for i in range(1, len(face)-1):
                triangles.append([face[0], face[i], face[i+1]])
    tri_parts = []
    for t in triangles:
        tri_parts.append(str(t[0]))
        tri_parts.append(str(t[1]))
        tri_parts.append(str(t[2]))
    tri_str = " ".join(tri_parts)
    vert_count = len(verts)
    tri_count = len(triangles)
    dae  = '<?xml version="1.0" encoding="utf-8"?>\n'
    dae += '<COLLADA xmlns="http://www.collada.org/2005/11/COLLADASchema" version="1.4.1">\n'
    dae += '  <asset><unit name="meter" meter="1"/><up_axis>Z_UP</up_axis></asset>\n'
    dae += '  <library_geometries>\n'
    dae += '    <geometry id="mesh0" name="PrimMesh">\n'
    dae += '      <mesh>\n'
    dae += '        <source id="mesh0-positions">\n'
    dae += '          <float_array id="mesh0-positions-array" count="' + str(vert_count*3) + '">' + pos_str + '</float_array>\n'
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
    dae += '  <scene><instance_visual_scene url="#Scene"/></scene>\n'
    dae += '</COLLADA>'
    return dae
