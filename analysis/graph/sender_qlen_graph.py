
import argparse
from typing import List, Tuple

from graph_helpers import (
    get_file_suffix,
    get_graph_title,
    get_out_png_filename,
    get_mix_trace_filename,
    plot_data_points,
)

def process_sender_view_trace_file(file_name, target_node, target_hop_node):
    # type: (str, int, int) -> Tuple[List[str], List[str]]
    times = []
    qlens = []

    with open(file_name, 'r') as file:
        # timestamp, node_id, sip, dip, sport, dport, hop_node_id, qlen
        # 8550 0 0b000001 0b000601 10000 79 95166151454 4295000
        for line in file:
            toks = line.split()
            if len(toks) < 7:
                print('skipping {}'.format(line))
                continue
            time_ns = int(toks[0]) # time in ns
            node = int(toks[1]) # node number
            hop_node = int(toks[6]) # hop node number
            qlen = int(toks[7]) # qlen in bytes

            if node == target_node and hop_node == target_hop_node:
                times.append(time_ns)
                qlens.append(qlen)

    print(len(times))
    return times, qlens

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='graph sender view of hop queue length')
    parser.add_argument('--node', dest='node', action='store', type=int, required=True, help="node id")
    parser.add_argument('--hop_node', dest='hop_node', action='store', type=int, required=True, help="hop node id")
    parser.add_argument('--flow', dest='flow', action='store', default='flow', help="the name of the flow file")
    parser.add_argument('--bw', dest="bw", action='store', default='100', help="the NIC bandwidth")
    parser.add_argument('--topo', dest='topo', action='store', default='fat', help="the name of the topology file")
    parser.add_argument('--misrep', dest='misrep', action='store', default='none', help="the name of the misreporting profile file")
    parser.add_argument('--cc_algo', dest='cc_algo', action='store', default='hp95ai50', help="CC algo with params")
    args = parser.parse_args()

    node_num = args.node
    hop_node_num = args.hop_node
    topo=args.topo
    misrep=args.misrep
    flow=args.flow
    cc_algo = args.cc_algo

    file_suffix = get_file_suffix(topo=topo, flow=flow, cc_algo=cc_algo, misrep=misrep)
    trace_file = get_mix_trace_filename(trace_name='sender_view', file_suffix=file_suffix)

    times, sender_qlens = process_sender_view_trace_file(
        file_name=trace_file,
        target_node=node_num,
        target_hop_node=hop_node_num
    )
    times_ms = [t / 1e6 for t in times]
    graph_title = get_graph_title(
        metric_name='Sender view of qLen',
        node_num=node_num,
        cc_algo=cc_algo,
        misrep=misrep,
        hop_node_num=hop_node_num,
    )
    out_png_name = get_out_png_filename(
        graph_metric='sender_qlen',
        file_suffix=file_suffix,
        node_num=node_num,
        hop_node_num=hop_node_num,
    )
    plot_data_points(
        times=times_ms,
        data_points=sender_qlens,
        xlabel='Time (ms)',
        ylabel='Sender view of qLen (bytes)',
        title=graph_title,
        out_file_name=out_png_name,
    )
