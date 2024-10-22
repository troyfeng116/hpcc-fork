import argparse
from typing import List, Tuple

from graph_helpers import get_file_suffix, plot_data_points

def process_node_state_trace_file(file_name, node_number):
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
            if node == node_number:
                if time_ns not in ts_to_tx_bytes_map:
                    ts_to_tx_bytes_map[time_ns] = 0
                ts_to_tx_bytes_map[time_ns] += tx_bytes

    for k, v in sorted(ts_to_tx_bytes_map.items(), lambda a, b : a[0] - b[0]):
        times.append(k)
        tx_bytes_li.append(v)
    return times, tx_bytes_li

def get_tx_bytes_out_png_name(file_suffix, node_num):
    # type: (str, int) -> str
    return "out/tx_bytes_{file_suffix}_node_{node_num}.png".format(
        file_suffix=file_suffix, node_num=node_num
    )

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='graph output bytes')
    parser.add_argument('--node', dest='node', action='store', type=int, default=0, help="node id")
    parser.add_argument('--flow', dest='flow', action='store', default='flow', help="the name of the flow file")
    parser.add_argument('--bw', dest="bw", action='store', default='100', help="the NIC bandwidth")
    parser.add_argument('--topo', dest='topo', action='store', default='fat', help="the name of the topology file")
    parser.add_argument('--cc_algo', dest='cc_algo', action='store', default='hp95ai50', help="CC algo with params")
    args = parser.parse_args()

    node_number = args.node
    topo=args.topo
    flow=args.flow
    cc_algo = args.cc_algo

    file_suffix = get_file_suffix(topo=topo, flow=flow, cc_algo=cc_algo)
    trace_file = '../../simulation/mix/node_trace_{file_suffix}.txt'.format(file_suffix=file_suffix)

    times, tx_bytes = process_node_state_trace_file(file_name=trace_file, node_number=node_number)
    times_ms = [t / 1e6 for t in times]
    plot_data_points(
        times=times_ms,
        data_points=tx_bytes,
        xlabel='Time (ms)',
        ylabel='Transmitted bytes',
        title='Transmitted bytes Over Time for Node {} ({})'.format(node_number, cc_algo),
        out_file_name=get_tx_bytes_out_png_name(file_suffix=file_suffix, node_num=node_number)
    )
