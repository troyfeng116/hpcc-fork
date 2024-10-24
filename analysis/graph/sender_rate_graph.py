import argparse
from typing import List, Tuple

from graph_helpers import (
    get_file_suffix,
    get_graph_title,
    get_out_png_filename,
    get_mix_trace_filename,
    plot_data_points
)

def process_sender_rate_trace_file(file_name, node_num):
    # type: (str, int) -> Tuple[List[str], List[str]]
    times = []
    sender_rates = []

    with open(file_name, 'r') as file:
        # timestamp, node_id, sip, dip, sport, dport, new_rate
        # 8550 0 0b000001 0b000601 10000 79 95166151454 4295000
        for line in file:
            toks = line.split()
            if len(toks) < 7:
                print('skipping {}'.format(line))
                continue
            time_ns = int(toks[0]) # time in ns
            node = int(toks[1]) # node number
            sender_rate = int(toks[6]) # sender rate in bits (GetBitRate)

            if node == node_num:
                times.append(time_ns)
                sender_rates.append(sender_rate)

    print(len(times))
    return times, sender_rates

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='graph sender rate')
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
    trace_file = get_mix_trace_filename(trace_name='wsize', file_suffix=file_suffix)

    times, send_rates = process_sender_rate_trace_file(file_name=trace_file, node_num=node_num)
    times_ms = [t / 1e6 for t in times]
    graph_title = get_graph_title(
        metric_name='Sender rate',
        node_num=node_num,
        cc_algo=cc_algo,
        misrep=misrep,
    )
    out_png_name = get_out_png_filename(
        graph_metric='sender_rate',
        file_suffix=file_suffix,
        node_num=node_num,
    )
    plot_data_points(
        times=times_ms,
        data_points=send_rates,
        xlabel='Time (ms)',
        ylabel='Send rate (B/s)',
        title=graph_title,
        out_file_name=out_png_name,
    )
