from collections import namedtuple
from urllib.parse import urlencode, urljoin

Point = namedtuple("Point", ["long", "lat"])
Queries = namedtuple("Queries", ["inside", "outside"])


def position_queries(base_url: str, extent: list) -> Queries:
    point_inside = points_inside(extent)[0]
    point_outside = points_outside(extent)[0]

    return Queries(
        urljoin(base_url, "position")
        + f"?coords=POINT({point_inside.long} {point_inside.lat})",
        urljoin(base_url, "position")
        + f"?coords=POINT({point_outside.long} {point_outside.lat})"
        if point_outside
        else "",
    )


def radius_queries(base_url: str, extent: list) -> Queries:
    """Generate radius queries for a given extent."""
    center = Point(
        (extent[2] + extent[0]) / 2,
        (extent[3] + extent[1]) / 2,
    )
    query_params = {
        "coords": f"POINT({center.long} {center.lat})",
        "within": "1000",
        "within_units": "m",
        "limit": 1,
    }
    return Queries(urljoin(base_url, "position") + "?" + urlencode(query_params), "")


def area_queries(base_url: str, extent: list) -> Queries:
    """Generate area queries for a given extent."""
    inside_polygon = wkt_points(points_inside(extent))
    outside_polygon = wkt_points(points_outside(extent))

    return Queries(
        urljoin(base_url, "area") + f"?coords=POLYGON({inside_polygon})",
        urljoin(base_url, "area") + f"?coords=POLYGON({outside_polygon})"
        if outside_polygon
        else "",
    )


def trajectory_queries(base_url: str, extent: list) -> Queries:
    inside_trajectory = wkt_points(points_inside(extent))
    outside_trajectory = wkt_points(points_outside(extent))

    return Queries(
        urljoin(base_url, "trajectory") + f"?coords=LINESTRING({inside_trajectory})",
        urljoin(base_url, "trajectory") + f"?coords=LINESTRING({outside_trajectory})"
        if outside_trajectory
        else "",
    )


def points_inside(extent: list) -> list:
    """Generate points inside the given extent."""
    n_points = 5
    long_step = (extent[2] - extent[0]) / (n_points * 100)
    lat_step = (extent[3] - extent[1]) / (n_points * 100)

    return [
        Point(extent[0] + long_step * i, extent[1] + lat_step * i)
        for i in range(1, n_points)
    ]


def points_outside(extent: list) -> list:
    """Generate points outside the given extent."""
    n_points = 5

    # Check if extent is global. If so, no points can be created
    if extent[0] == -180 and extent[1] == -90 and extent[2] == 180 and extent[3] == 90:
        return []

    # Create a set of points relatively close to each other.
    # Either north or south of spatial extent. Pick north first if it has most "room".
    long_step = (extent[2] - extent[0]) / (n_points * 100)
    if abs(extent[3]) < abs(extent[1]):
        lat_step = (90 - abs(extent[3])) / (n_points * 100)

        return [
            Point(extent[0] + long_step * i, extent[3] + lat_step * i)
            for i in range(1, n_points)
        ]

    lat_step = (90 - abs(extent[1])) / (n_points * 100)

    return [
        Point(extent[0] + long_step * i, extent[1] - lat_step * i)
        for i in range(1, n_points)
    ]


def wkt_points(points: list) -> str:
    """Convert a list of points to a WKT string."""
    return ",".join(f"{p.long} {p.lat}" for p in points)
