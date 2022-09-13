"""
Implementation of Delaunay triangulation algorithm
Outputs file with number of edge flips performed during triangulation
"""
from GeometryObjects import Point, Edge, Triangle

global EDGE_FLIP_COUNTER


def edge_to_flip(e1: Edge, e2: Edge):
    min1, min2 = e1.get_low(), e2.get_low()
    if min1 < min2:
        return e1
    elif min1 == min2:
        max1, max2 = e1.get_high(), e2.get_high()
        if max1 < max2:
            return e1
        else:
            return e2
    else:
        return e2


def get_data_from_file(fpath):
    with open(fpath, 'r') as f:
        f_content = f.readlines()
    n_points, m_triagnles = f_content[0].split()

    points_list = []
    for i in range(1, n_points + 1):
        pid, px, py = f_content[i]
        points_list.append(Point(pid, px, py))

    triangle_list = []
    for i in range(n_points + 1, n_points + 1 + m_triagnles):
        pid1, pid2, pid3 = f_content[i]
        e1, e2, e3 = Edge(pid1, pid2), Edge(pid1, pid3), Edge(pid2, pid3)
        triangle_list.append(Triangle(e1, e2, e3))

    return points_list, triangle_list


def get_min_angle_in_triangle(t, level=1):
    alpha, betta, gamma = t.get_angles()
    if level == 1:
        return min(alpha, betta, gamma)
    elif level == 2:
        first_min = min(alpha, betta, gamma)
        return min([alpha, betta, gamma].remove(first_min))
    else:
        return max(alpha, betta, gamma)


def is_legal_edge(t, adj_t, e):
    """An edge is illegal if flipping it would increase the angle vector of the adjacent triangles"""
    min_angle1 = get_min_angle_in_triangle(t)
    min_angle2 = get_min_angle_in_triangle(adj_t)

    flipped_t, flipped_adj_t = flip_edges(t, adj_t, e, count=False)
    min_angle_flipped1 = get_min_angle_in_triangle(flipped_t)
    min_angle_flipped2 = get_min_angle_in_triangle(flipped_adj_t)

    if min_angle_flipped1 > min_angle1:
        return False
    elif min_angle_flipped1 == min_angle1:
        min_angle_flipped1 = get_min_angle_in_triangle(flipped_t, level=2)
        min_angle_flipped2 = get_min_angle_in_triangle(flipped_adj_t, level=2)
        if min_angle_flipped1 > min_angle1:
            return False
        elif min_angle_flipped1 == min_angle1:
            min_angle_flipped1 = get_min_angle_in_triangle(flipped_t, level=3)
            min_angle_flipped2 = get_min_angle_in_triangle(flipped_adj_t, level=3)
            if min_angle_flipped1 > min_angle1:
                return False
            else:
                return True
    else:
        return True


def get_init_triangle(graph_points: list):
    max_x, max_y, min_x, min_y = 0, 0, 0, 0
    for p in graph_points:
        if p.px > max_x:
            max_x = p.px
        elif p.px < min_x:
            min_x = p.px
        if p.py > max_y:
            max_y = p.py
        elif p.py < min_y:
            min_y = p.py

    mid_x = max_x - min_x / 2
    mid_y = max_y - min_y / 2

    p1 = Point(-1, min_x - 1000, min_y - 1000)
    p2 = Point(-2, mid_x + 1000, mid_y + 1000)
    p3 = Point(-3, max_x + 1000, min_y + 1000)

    return Triangle(p1, p2, p3)


def insert(p: Point, all_triangles: list):
    """
    Inster a new point into the group of triangles t
    :param p: point to insert to t
    :param t: list of triangles
    :return:
    """
    # add edge from p to the other triangle points
    for t in all_triangles:
        e1, e2, e3 = t.get_edges()

        # legalize edges
        legalize_edge(p, e1, all_triangles)
        legalize_edge(p, e2, all_triangles)
        legalize_edge(p, e3, all_triangles)


def flip_edges(t1: Triangle, t2: Triangle, e: Edge, count: bool = True):
    """
    flip edges by creating two new triangles from the same outer edges of the two first triangles.
    flip is counted in global variable for the output.
    If flip is only to check if flip is legal, don't count the flip.
    :param t1: old triangele
    :param t2: old triangle
    :param e: illegal edge
    :return: two new Triangles
    """
    edges1 = t1.get_edges()
    edges2 = t2.get_edges()

    # remove illegal edge
    edges1.pop(e)
    edges2.pop(e)

    # create new flipped edge
    new_point1 = edges1[0].get_points_id() & edges1[2].get_points_id()
    new_point2 = edges2[0].get_points_id() & edges2[2].get_points_id()
    new_edge1 = Edge(new_point1, new_point2)

    # find adjacent edges and create new triangles
    if edges1[0].have_common_points(edges2[0]):
        new_t1 = Triangle(edges1[0], edges2[0], new_edge1)
        new_t2 = Triangle(edges1[1], edges2[1], new_edge1)
    else:
        new_t1 = Triangle(edges1[0], edges2[1], new_edge1)
        new_t2 = Triangle(edges1[1], edges2[0], new_edge1)

    # if flip is applied in algorithm
    if count:
        EDGE_FLIP_COUNTER += 1

    return new_t1, new_t2


def legalize_edge(p: Point, e: Edge, all_triangles: list):
    """
    if edge is illegal, flip edges and check new if new edges are legal recursively
    :param p: new point
    :param e: edge to check if legal
    :param all_triangles: to find adjacent triangle
    :return: if edge is legal (in recursion)
    """
    p1, p2 = e.get_points_id()

    # get triangle and adjacent triangle
    t = Triangle(Edge(p, p1), Edge(p, p2), e)
    adj_t = get_adjacent_triangle(p, e, all_triangles)

    if is_legal_edge(t, adj_t, e):
        return
    else:
        new_t1, new_t2 = flip_edges(t, adj_t, e)
        legalize_edge(p, new_t1.get_opposite_edge(p), all_triangles)
        legalize_edge(p, new_t2.get_opposite_edge(p), all_triangles)


def get_adjacent_triangle(p: Point, e: Edge, all_triangles: list):
    """
    return a new traingle with same edge but different 3rd point
    :param p:
    :param e:
    :param all_triangles:
    :return: Triangle
    """
    for t in all_triangles:
        if t.is_edge_in_triangle(e):
            if not t.is_point_in_triangle(p):
                return t


def run_delaunay_triangulation(triangle_list):
    """run over all points from input, and use the Delaunay algorithm to insert a new point while using legal triangulation"""
    # create the initial triangle and add to traingle list
    after_traingulation_points = []
    init_triangle = get_init_triangle(triangle_list)
    after_traingulation_points.append(init_triangle)

    for t in triangle_list:
        for p in t.get_points():
            insert(p, after_traingulation_points)


def make_out_file(out_path):
    """save output to file"""
    print(EDGE_FLIP_COUNTER)
    with open(out_path, 'w') as f:
        f.write(EDGE_FLIP_COUNTER)


if __name__ == '__main__':
    inpath = 'input.txt'
    out_path = 'output.txt'
    EDGE_FLIP_COUNTER = 0

    # parse the input data
    points_list, triangle_list = get_data_from_file(inpath)

    # run the delaunay triangulation algorithm
    run_delaunay_triangulation(triangle_list)

    # init_tr = get_init_triangle(points_list)
    make_out_file(out_path)
