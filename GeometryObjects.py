class Point:
    def __init__(self, pid, px, py):
        self.pid = pid
        self.px = px
        self.py = py
        self.neigbohrs = []

    def get_id(self):
        return self.pid

    def get_coor(self):
        return self.px, self.py

    def add_neighbor(self, new_p):
        if new_p not in self.neigbohrs:
            self.neigbohrs.append(new_p)

    def get_neighbors(self):
        return self.neigbohrs


class Edge:
    def __init__(self, p1: Point, p2: Point):
        self.p1 = p1
        self.p2 = p2
        p1.add_neighbor(p2)
        p2.add_neighbor(p1)
        self.neigbohrs = []

    def get_low(self):
        return min(self.p1.get_id, self.p2.get_id)

    def get_high(self):
        return max(self.p1.get_id, self.p2.get_id)

    def get_points_id(self):
        return self.p1.get_id(), self.p2.get_id()

    def add_neighbor(self, new_e):
        if new_e not in self.neigbohrs:
            self.neigbohrs.append(new_e)

    def get_neighbors(self):
        return self.neigbohrs

    def have_common_points(self, e):
        return len(set(self.get_points_id()) & set(e.get_points_id())) > 0


class Triangle:
    def __init__(self, e1, e2, e3):
        self.e1 = e1
        self.e2 = e2
        self.e3 = e3
        self.all_pid = set(e1.p1.pid, e1.p2.pid, e2.p1.pid, e2.p2.pid, e3.p1.pid, e3.p2.pid)
        e1.add_neighbor(e2)
        e1.add_neighbor(e3)
        e2.add_neighbor(e1)
        e2.add_neighbor(e3)
        e3.add_neighbor(e1)
        e3.add_neighbor(e2)

    def get_points(self):
        return self.all_pid

    def get_edges(self):
        return [self.e1, self.e2, self.e3]

    def is_edge_in_triangle(self, e: Edge):
        p1, p2 = e.get_points_id()
        return (p1 in self.all_pid) and (p2 in self.all_pid)

    def is_point_in_triangle(self, p: Point):
        return p in self.all_pid

    def get_opposite_edge(self, p: Point):
        if p not in self.e1.get_points_id():
            return self.e1
        elif p not in self.e2.get_points_id():
            return self.e2
        else:
            return self.e3
