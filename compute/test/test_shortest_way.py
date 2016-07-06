# -*- coding: utf-8 -*-
"""
@author: Zhanhong Cheng
"""
from transpy.test.load_data import load_test_data
from transpy.compute.shortest_way import single_source_shortest_way
import numpy as np
import nose.tools as nt

NULL = 65535

_, _, _, net, _ = load_test_data()


class Test_single_source_shortest_way():
    def test_multi_path(self):
        """Test normal condition, find link DIR to all node """
        dist, path = single_source_shortest_way(net, 'LENGTH', 26)
        nt.assert_almost_equal(dist[16], 2596.16645, 3)
        nt.assert_almost_equal(dist[18], 1740.7363, 3)
        nt.assert_almost_equal(dist[12], 1550.9641, 3)
        nt.assert_equal(path[16], [32, 4, 12, 11, 17, 18, 18, 20, 23])
        nt.assert_equal(path[18], [32, 4, 12, 11, 17, 18, 27])
        nt.assert_equal(path[12], [32, 4, 12, 11, 17, 33, 19])

    def test_multi_node(self):
        """Test normal condition, find node DIR to all node """
        dist, node_seq = single_source_shortest_way(net, 'LENGTH', 26,
                                                    return_type='node')
        nt.assert_equal(node_seq[16], [26, 1, 7, 8, 24, 13, 20, 13, 17, 16])
        nt.assert_equal(node_seq[18], [26, 1, 7, 8, 24, 13, 20, 18])
        nt.assert_equal(node_seq[12], [26, 1, 7, 8, 24, 13, 27, 12])

    def test_max_dist(self):
        """Test whether algorithm stop when reach max_dist."""
        dist, node_pred, _ = single_source_shortest_way(net, 'LENGTH', 26,
                                                        max_dist=402,
                                                        return_type='pred')
        for line in node_pred[node_pred != NULL]:
            nt.assert_true(dist[line] < 402, 'Search range out of max_dist')

    def test_max_node(self):
        """Test whether algorithm stop when reach max_node."""
        dist, node_pred, arc_pred = single_source_shortest_way(net, 'LENGTH',
                                                               26,
                                                               max_node=10,
                                                               return_type='pred')
        nt.assert_equal(sum(node_pred != NULL), 9,
                        'Search range out of max_node')

    def test_no_way(self):
        """Test when there is no DIR from source to target."""
        dist, link_path = single_source_shortest_way(net, 'LENGTH', 26, 16,
                                                     max_dist=500,
                                                     return_type='link')
        nt.assert_equal(dist, {})
        nt.assert_equal(link_path, {})

        dist, node_path = single_source_shortest_way(net, 'LENGTH', 26, 16,
                                                     max_dist=500,
                                                     return_type='node')
        nt.assert_equal(dist, {})
        nt.assert_equal(node_path, {})
