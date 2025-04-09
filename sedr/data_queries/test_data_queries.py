import unittest
import data_queries as dq

from urllib.parse import urljoin


class TestDataQueries(unittest.TestCase):
    __version__ = "testversion"

    def test_points_outside(self):
        points = dq.points_outside(4, [-180, -90, 180, 90])
        self.assertTrue(len(points) == 0)

        points = dq.points_outside(4, [-180, -90, 40, 50])

        self.assertTrue(len(points) == 4, f"Expected 4 points; Got {len(points)}")
        self.assertTrue(len([p for p in points if p.lat >= 50]) == 4, 
                        f"Expected all points equal or above lat 50; Got {points}")

    def test_points_inside(self):
        extent = [-100, 5, 100, 85]
        points = dq.points_inside(10, extent)

        self.assertTrue(
            len(
                [
                    p
                    for p in points
                    if (
                        p.long >= extent[0]
                        and p.lat >= extent[1]
                        and p.long <= extent[2]
                        and p.lat <= extent[3]
                    )
                ]
            )
            == 10
        )

    def test_area_queries(self):
        extent = [-100, 5, 100, 85]
        base_url = "http://example.com/edr/collections/test/"
        match_prefix = urljoin(base_url, "area") + "?coords=POLYGON("

        queries = dq.area_queries(base_url, extent)

        self.assertTrue(queries.inside.startswith(match_prefix), 
                        f"Expected prefix match {match_prefix}; Got {queries.inside}")
        self.assertTrue(queries.inside.startswith(match_prefix), 
                        f"Expected prefix match {match_prefix}; Got {queries.outside} ")


if __name__ == "__main__":
    unittest.main()
