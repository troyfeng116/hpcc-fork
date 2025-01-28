import requests
import xml.etree.ElementTree as ET

from typing import List, Optional, Tuple

GML_URL = 'https://topology-zoo.org/files/Kdl.graphml'
OUT_FILE_NAME = 'ky_dl'

# return list of mapped edges, and num nodes N
def read_graph(graph_gml_node):
    # type: (ET.Element) -> Tuple[List[Tuple[int, int]], int]
    edges = []
    node_id_map = {}
    cur_node_ct = 0
    for edge_gml_node in graph_gml_node.iter('{http://graphml.graphdrawing.org/xmlns}edge'):
        src = int(edge_gml_node.attrib['source'])
        tgt = int(edge_gml_node.attrib['target'])
        for node in [src, tgt]:
            if node not in node_id_map:
                node_id_map[node] = cur_node_ct
                cur_node_ct += 1
        edges.append((node_id_map[src], node_id_map[tgt]))
    return edges, cur_node_ct

# switches have ID `node_id+N`, where N is `max_node+1`
def write_graph_to_topo_file(N, edges, topo_file_name, bw_gbps=100):
    # type: (int, List[Tuple[int, int]], str, Optional[int]) -> None
    N = max(max(u, v) for (u, v) in edges) + 1
    # attach one node to each switch
    total_links = len(edges) + N
    bw_str = '{bw_gbps}Gbps'.format(bw_gbps=bw_gbps)
    with open(topo_file_name, 'w') as out_file:
        # nodes+switches, switches, links
        out_file.write('{N} {N} {total_links}\n'.format(N=N, total_links=total_links))
        # switch IDs
        switch_ids = [node_id + N for node_id in range(N)]
        out_file.write(' '.join(str(sid) for sid in switch_ids))
        out_file.write('\n')
        # node-to-switch links
        for node_id in range(N):
            # TODO: delay 1000ns or .01ms?
            out_file.write(' '.join([str(node_id), str(node_id + N), bw_str, '1000ns', str(0)]))
            out_file.write('\n')
        # switch-to-switch links
        for u, v in edges:
            out_file.write(' '.join([str(u + N), str(v + N), bw_str, '1000ns', str(0)]))
            out_file.write('\n')

def main():
    # type: () -> int
    res = requests.get(GML_URL)
    if res.status_code != 200:
        print(res.status_code)
        print(res.reason)
        return 1

    gml_str = str(res.text)
    gml_root = ET.fromstring(gml_str)
    if gml_root is None:
        print(gml_str)
        print("Error parsing GML")
        return 1
    
    graph_gml_node = None
    for child in gml_root:
        if child.tag.endswith('graph'):
            graph_gml_node = child
            break
    # graph_gml_node = gml_root.find("{{http://graphml.graphdrawing.org/xmlns}}graph")
    assert graph_gml_node is not None
    assert graph_gml_node.attrib["edgedefault"] == "undirected"
    
    edges, N = read_graph(graph_gml_node=graph_gml_node)
    write_graph_to_topo_file(
        N=N,
        edges=edges,
        topo_file_name='simulation/mix/{out_file}.txt'.format(out_file=OUT_FILE_NAME)
    )
    print('{N} nodes, {M} edges', N=N, M=len(edges))

    return 0

if __name__ == '__main__':
    exit(main())
