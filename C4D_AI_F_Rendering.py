import c4d, json, os, math, random, sys, io

FILE   = R"E:\AI_F\normalize\results_MD_normalization\graph_json\3_0002.json"
RADIUS = 0.05      
SEG    = 128       

if sys.version_info[0] >= 3:
    def open_utf8(path):
        return open(path, "r", encoding="utf-8")
else:
    def open_utf8(path):
        return io.open(path, "r", encoding="utf-8")

# --------------------------------------------------------------------------- #
def to_vec2d(p):
    """(x , z) → Vector(x , 0 , z)"""
    return c4d.Vector(p[0], 0.0, p[1])

def node_pos(n):

    return n.get("pos", (n["x"], n["y"]))

def build_circle(radius, seg):

    spl = c4d.SplineObject(seg, c4d.SPLINETYPE_LINEAR)
    spl[c4d.SPLINEOBJECT_CLOSED] = True
    pts = [c4d.Vector(math.cos(t) * radius,
                      math.sin(t) * radius,
                      0.0)
           for t in (2.0 * math.pi * i / seg for i in range(seg))]
    spl.SetAllPoints(pts)
    spl.Message(c4d.MSG_UPDATE)
    return spl

def subdivide_edge(p1, p2, base_len):

    length = (p2 - p1).GetLength()
    n_seg = max(1, int(math.ceil(length / base_len)))
    if n_seg == 1:
        return [(p1, p2)]
    segments = []
    delta = p2 - p1
    for i in range(n_seg):
        a = p1 + delta * (float(i)       / n_seg)
        b = p1 + delta * (float(i + 1.0) / n_seg)
        segments.append((a, b))
    return segments

# --------------------------------------------------------------------------- #
def main():

    if not os.path.isfile(FILE):
        raise IOError("JSON file not found:\n" + FILE)

    with open_utf8(FILE) as f:
        data = json.load(f)

    pts = {n["id"]: to_vec2d(node_pos(n)) for n in data["nodes"]}

    xs = [v.x for v in pts.values()]
    zs = [v.z for v in pts.values()]
    span = max(max(xs) - min(xs), max(zs) - min(zs), 1e-6)
    scale = 10.0 / span
    ox, oz = min(xs), min(zs)

    for k, p in pts.items():
        pts[k] = c4d.Vector((p.x - ox) * scale,
                            0.0,
                            (p.z - oz) * scale)

    for p in pts.values():
        p.y = random.uniform(-0.3, 0.3)

    raw_edges = [(l["source"], l["target"])
                 for l in data["links"]
                 if l["source"] in pts and l["target"] in pts
                 and (pts[l["source"]] - pts[l["target"]]).GetLength() > 0.001]

    print("edges:", len(data["links"]), "valid:", len(raw_edges))

    max_len = max((pts[a] - pts[b]).GetLength() for a, b in raw_edges)
    base_len = max_len / 2
    print("base segment length:", base_len, "cm")

    doc.StartUndo()

    circle_profile = build_circle(RADIUS, SEG)

    for sid, tid in raw_edges:
        p1, p2 = pts[sid], pts[tid]
        for a, b in subdivide_edge(p1, p2, base_len):
            path = c4d.SplineObject(2, c4d.SPLINETYPE_LINEAR)
            path.SetAllPoints([a, b])
            path.Message(c4d.MSG_UPDATE)

            profile = circle_profile.GetClone()

            sweep = c4d.BaseObject(c4d.Osweep)
            profile.InsertUnder(sweep)
            path.InsertUnderLast(sweep)

            doc.InsertObject(sweep)
            doc.AddUndo(c4d.UNDOTYPE_NEW, sweep)

    doc.EndUndo()
    c4d.EventAdd()

# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    main()