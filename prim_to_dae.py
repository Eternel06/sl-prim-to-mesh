import math

def rotate_vertex(v, q):
    """Rotate a vertex by a quaternion rotation."""
    x, y, z = v
    qx, qy, qz, qw = q

    # quaternion rotation formula
    ix =  qw*x + qy*z - qz*y
    iy =  qw*y + qz*x - qx*z
    iz =  qw*z + qx*y - qy*x
    iw = -qx*x - qy*y - qz*z

    rx = ix*qw + iw*(-qx) + iy*(-qz) - iz*(-qy)
    ry = iy*qw + iw*(-qy) + iz*(-qx) - ix*(-qz)
    rz = iz*qw + iw*(-qz) + ix*(-qy) - iy*(-qx)

    return [rx, ry, rz]

def apply_transform(verts, pos, rot):
    """Apply rotation then position to all vertices."""
    result = []
    for v in verts:
        rv = rotate_vertex(v, rot)
        result.append([
            rv[0] + pos[0],
            rv[1] + pos[1],
            rv[2] + pos[2]
        ])
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
    r_x, r_y, h = size[0]/2, size[1]/2, size[2]

    cut_begin = path_cut_begin * 2 * math.pi
    cut_end   = path_cut_end   * 2 * math.pi
    angle_range = cut_end - cut_begin
    steps = max(3, int(divisions * angle_range / (2 * math.pi)))

    outer_bottom = []
    outer_top    = []
    inner_bottom = []
    inner_top    = []

    for i in range(steps + 1):
        angle = cut_begin + angle_range * i / steps
        cx = math.cos(angle)
        cy = math.sin(angle)
        outer_bottom.append([r_x * cx, r_y * cy, -h/2])
        outer_top.append   ([r_x * cx, r_y * cy,  h/2])
        if hollow > 0:
            inner_bottom.append([r_x * hollow * cx, r_y * hollow * cy, -h/2])
            inner_top.append   ([r_x * hollow * cx, r_y * hollow * cy,  h/2])

    base = len(verts)
    verts.extend(outer_bottom)
    verts.extend(outer_top)
    ob = base
    ot = base + len(outer_bottom)

    # outer side faces
    for i in range(steps):
        faces.append([ob+i, ob+i+1, ot+i+1, ot+i])

    if hollow > 0:
        ib = len(verts)
        verts.extend(inner_bottom)
        it_ = len(verts)
        verts.extend(inner_top)

        # inner side faces
        for i in range(steps):
            faces.append([ib+i+1, ib+i, it_+i, it_+i+1])

        # top cap
        for i in range(steps):
            faces.append([ot+i, ot+i+1, it_+i+1, it_+i])

        # bottom cap
        for i in range(steps):
            faces.append([ob+i+1, ob+i, ib+i, ib+i+1])

        # end caps for path cut
        if path_cut_begin > 0 or path_cut_end < 1:
            faces.append([ob, ot, it_[0], ib])
            faces.append([ob+steps, ib+steps, it_+steps, ot+steps])
    else:
        # solid caps
        for i in range(1, steps-1):
            faces.append([ot, ot+i, ot+i+1])
            faces.append([ob, ob+i+1, ob+i])

    verts = apply_transform(verts, pos, rot)
    return verts, faces

def make_sphere(pos, size, rot, divisions=16, hollow=0.0, path_cut_begin=0.0, path_cut_end=1.0):
    verts = []
    faces = []
    r_x, r_y, r_z = size[0]/2, size[1]/2, size[2]/2

    lat_begin = -math.pi/2 + path_cut_begin * math.pi
    lat_end   = -math.pi/2 + path_cut_end   * math.pi
    lat_steps = max(3, divisions)
    lon_steps = max(3, divisions)

    for i in range(lat_
