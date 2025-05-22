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
    inside_polygon = wkt_points(points_inside(extent), closed=True)
    outside_polygon = wkt_points(points_outside(extent), closed=True)

    return Queries(
        urljoin(base_url, "area") + f"?coords=POLYGON(({inside_polygon}))",
        urljoin(base_url, "area") + f"?coords=POLYGON(({outside_polygon}))"
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

    # Create a square polyogon with center of extent as lower left corner.
    long_left = (extent[0] + extent[2]) / 2
    lat_bottom = (extent[1] + extent[3]) / 2

    long_right = long_left + abs(extent[2] - extent[0]) / 4
    lat_top = lat_bottom + abs(extent[3] - extent[1]) / 4

    return [
        Point(long_left, lat_bottom),
        Point(long_left, lat_top),
        Point(long_right, lat_top),
        Point(long_right, lat_bottom),
    ]


def points_outside(extent: list) -> list:
    """Generate points outside the given extent."""

    # Check if extent is pole to pole. If so, no points can be created
    if extent[1] == -90 and extent[3] == 90:
        return []

    # Create a set of points relatively close to each other.
    # Either north or south of spatial extent. Pick north first if it has most "room".
    long_left = (extent[0] + extent[2]) / 2
    long_right = long_left + abs(extent[2] - extent[0]) / 4
    lat_bottom = None
    lat_top = None
    if abs(extent[3]) < abs(extent[1]):
        lat_bottom = extent[3] + abs(90 - extent[3]) / 4
        lat_top = lat_bottom + abs(90 - extent[3]) / 4
    else:
        lat_bottom = -90 + abs(-90 - extent[1]) / 4
        lat_top = lat_bottom + abs(-90 + extent[1]) / 4

    return [
        Point(long_left, lat_bottom),
        Point(long_left, lat_top),
        Point(long_right, lat_top),
        Point(long_right, lat_bottom),
    ]


def wkt_points(points: list, closed=False) -> str:
    """Convert a list of points to a WKT string."""
    wkt_str = ",".join(f"{p.long} {p.lat}" for p in points)
    if closed:
        wkt_str += f",{points[0].long} {points[0].lat}"

    return wkt_str
