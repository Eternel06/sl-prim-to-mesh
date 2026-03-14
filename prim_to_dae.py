def make_cylinder(pos, size, rot, divisions=16, hollow=0.0, 
                  path_cut_begin=0.0, path_cut_end=1.0,
                  taper_x=0.0, taper_y=0.0):
    verts = []
    faces = []
    r_x = size[0]/2
    r_y = size[1]/2
    h = size[2]
    cut_begin = path_cut_begin * 2 * math.pi
    cut_end = path_cut_end * 2 * math.pi
    angle_range = cut_end - cut_begin
    steps = max(3, int(divisions * angle_range / (2 * math.pi)))

    # taper: 1.0 = full cone, 0.0 = cylinder
    top_r_x = r_x * (1.0 - taper_x)
    top_r_y = r_y * (1.0 - taper_y)

    outer_bottom = []
    outer_top = []
    inner_bottom = []
    inner_top = []

    for i in range(steps + 1):
        angle = cut_begin + angle_range * i / steps
        cx = math.cos(angle)
        cy = math.sin(angle)
        outer_bottom.append([r_x * cx, r_y * cy, -h/2])
        outer_top.append([top_r_x * cx, top_r_y * cy, h/2])
        if hollow > 0:
            inner_bottom.append([r_x * hollow * cx, r_y * hollow * cy, -h/2])
            inner_top.append([top_r_x * hollow * cx, top_r_y * hollow * cy, h/2])

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
        # bottom cap
        for i in range(1, steps-1):
            faces.append([ob, ob+i+1, ob+i])
        # top cap — only if not fully tapered to a point
        if top_r_x > 0.01 and top_r_y > 0.01:
            for i in range(1, steps-1):
                faces.append([ot, ot+i, ot+i+1])
        else:
            # cone tip — single apex point
            apex_idx = len(verts)
            verts.append([0, 0, h/2])
            for i in range(steps):
                next_i = (i+1) % steps
                faces.append([apex_idx, ob+i, ob+next_i])

    verts = apply_transform(verts, pos, rot)
    return verts, faces
