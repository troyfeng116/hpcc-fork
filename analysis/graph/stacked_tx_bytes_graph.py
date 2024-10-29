import argparse
from typing import List, Tuple

from graph_helpers import (
    get_file_suffix,
    get_graph_title,
    get_out_png_filename,
    get_mix_trace_filename,
    plot_stacked_data_points,
)

def process_node_state_trace_file(file_name, node_num):
    # type: (str, int) -> Tuple[List[str], List[str]]
    times = []
    tx_bytes_li = []
    ts_to_tx_bytes_map = {}

    with open(file_name, 'r') as file:
        for line in file:
            toks = line.split()
            if len(toks) < 3:
                print('skipping {}'.format(line))
                continue
            time_ns = int(toks[0]) # time ns
            node = int(toks[1]) # node number
            tx_bytes = int(toks[2]) # transmitted bytes

            # Filter by the given node number
            if node == node_num:
                if time_ns not in ts_to_tx_bytes_map:
                    ts_to_tx_bytes_map[time_ns] = tx_bytes
                ts_to_tx_bytes_map[time_ns] = max(
                    ts_to_tx_bytes_map[time_ns],
                    tx_bytes,
                )

    for k, v in sorted(ts_to_tx_bytes_map.items(), lambda a, b : a[0] - b[0]):
        times.append(k)
        tx_bytes_li.append(v)
    return times, tx_bytes_li

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='graph output bytes')
    parser.add_argument('--node', dest='node', action='store', type=int, required=True, help="node id")
    parser.add_argument('--misrep_profiles', dest='misrep_profiles', action='store', required=True, help="comma-separated list of misreporting profiles to compare")
    parser.add_argument('--flow', dest='flow', action='store', default='mini_flow', help="the name of the flow file")
    parser.add_argument('--topo', dest='topo', action='store', default='mini_topology', help="the name of the topology file")
    parser.add_argument('--cc_algo', dest='cc_algo', action='store', default='hp95ai50', help="CC algo with params")
    args = parser.parse_args()

    node_num = args.node
    topo=args.topo
    misrep_profiles_str = args.misrep_profiles
    misrep_profiles = set(s.strip() for s in misrep_profiles_str.split(","))
    # include baseline first
    if 'none' in misrep_profiles:
        misrep_profiles.remove('none')
    misrep_profiles = ['none'] + list(misrep_profiles)

    flow=args.flow
    cc_algo = args.cc_algo
    # [label, times, tx_bytes]
    data_points_li = []

    for misrep in misrep_profiles:
        file_suffix = get_file_suffix(topo=topo, flow=flow, cc_algo=cc_algo, misrep=misrep)
        trace_file = get_mix_trace_filename(trace_name='node_trace', file_suffix=file_suffix)

        times, tx_bytes = process_node_state_trace_file(file_name=trace_file, node_num=node_num)
        times_ms = [t / 1e6 for t in times]
        data_points_li.append((misrep, times_ms, tx_bytes))

    stacked_misrep_tok = 'various'
    stacked_file_suffix = get_file_suffix(topo=topo, flow=flow, cc_algo=cc_algo, misrep=stacked_misrep_tok)
    out_png_name = get_out_png_filename(
        graph_metric='stacked_tx_bytes',
        file_suffix=stacked_file_suffix,
        node_num=node_num,
    )
    graph_title = get_graph_title(
        metric_name='Transmitted bytes',
        node_num=node_num,
        cc_algo=cc_algo,
        misrep=stacked_misrep_tok,
    )
    plot_stacked_data_points(
        data_points_li=data_points_li,
        xlabel='Time (ms)',
        ylabel='Transmitted bytes',
        title=graph_title,
        out_file_name=out_png_name,
    )