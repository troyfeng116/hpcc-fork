import argparse
from typing import List, Tuple

from graph_helpers import (
    get_file_suffix,
    get_graph_title,
    get_out_png_filename,
    plot_data_points,
)

def process_qlen_trace_file(file_name, node_num):
    # type: (str, int) -> Tuple[List[str], List[str]]
    times = []
    queue_lengths = []
    ts_to_qlen_map = {}

    with open(file_name, 'r') as file:
        for line in file:
            parts = line.split()
            if len(parts) < 11:
                print('skipping {}'.format(line))
                continue
            time_ns = int(parts[0]) # time ns
            node = int(parts[1].split(':')[1]) # node number
            queue_length = int(parts[3]) # queue length in bytes
            packet_type = parts[10] # 'U' for data packet

            # Filter by the given node number
            if packet_type == "U" and node == node_num:
                if time_ns not in ts_to_qlen_map:
                    ts_to_qlen_map[time_ns] = 0
                ts_to_qlen_map[time_ns] += queue_length

    for k, v in sorted(ts_to_qlen_map.items(), lambda a, b : a[0] - b[0]):
        times.append(k)
        queue_lengths.append(v)
    return times, queue_lengths

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='graph queue length')
    parser.add_argument('--node', dest='node', action='store', type=int, default=0, help="node id")
    parser.add_argument('--flow', dest='flow', action='store', default='flow', help="the name of the flow file")
    parser.add_argument('--bw', dest="bw", action='store', default='100', help="the NIC bandwidth")
    parser.add_argument('--topo', dest='topo', action='store', default='fat', help="the name of the topology file")
    parser.add_argument('--misrep', dest='misrep', action='store', default='none', help="the name of the misreporting profile file")
    parser.add_argument('--cc_algo', dest='cc_algo', action='store', default='hp95ai50', help="CC algo with params")
    args = parser.parse_args()

    node_num = args.node
    topo=args.topo
    misrep=args.misrep
    flow=args.flow
    cc_algo = args.cc_algo

    file_suffix = get_file_suffix(topo=topo, flow=flow, cc_algo=cc_algo, misrep=misrep)
    # qLen traces are read separately from `simulation/mix` by `trace_reader`
    trace_file = 'qlen_traces/qlen_{file_suffix}.txt'.format(file_suffix=file_suffix)

    times, queue_lengths = process_qlen_trace_file(file_name=trace_file, node_num=node_num)
    times_ms = [t / 1e6 for t in times]
    graph_title = get_graph_title(
        metric_name='Queue Length',
        node_num=node_num,
        cc_algo=cc_algo,
        misrep=misrep,
    )
    out_png_name = get_out_png_filename(
        graph_metric='qlen',
        file_suffix=file_suffix,
        node_num=node_num,
    )
    plot_data_points(
        times=times_ms,
        data_points=queue_lengths,
        xlabel='Time (ms)',
        ylabel='Queue Length (bytes)',
        title=graph_title,
        out_file_name=out_png_name
    )
