
import argparse
from typing import List, Tuple

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from graph_helpers import get_file_suffix

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
            hop_node = int(toks[6]) # node number
            qlen = int(toks[7]) # qlen in bytes

            if node == target_node and hop_node == target_hop_node:
                times.append(time_ns)
                qlens.append(qlen)

    print(len(times))
    return times, qlens

def get_sender_qlen_out_png_name(file_suffix, node_num, target_node_num):
    # type: (str, int, int) -> str
    return "out/sender_qlen_{file_suffix}_node_{node_num}_hopnode_{target_node_num}.png".format(
        file_suffix=file_suffix, node_num=node_num, target_node_num=target_node_num
    )

# Plot queue length at hop_node, seen by node, over time
def plot_sender_qlen(node, hop_node, cc_algo, times, sender_qlens, file_suffix):
    # type: (int, int, str, List[int], List[int], str) -> None
    times_ms = [t / 1e6 for t in times]
    # sender_qlens = [w / 1e9 for w in sender_qlens]

    plt.figure(figsize=(10, 6))
    plt.plot(times_ms, sender_qlens, label='Sender View of qLen (B)', color='blue')
    plt.xlabel('Time (ms)')
    plt.ylabel('Sender View of qLen (B)')
    plt.title('Sender View of qLen Over Time for Hop Node {}, POV Node {} ({})'.format(node, hop_node, cc_algo))
    plt.grid(True)
    # plt.legend()
    # plt.show()
    # Save the plot as a PNG file
    out_file_name = get_sender_qlen_out_png_name(
        file_suffix=file_suffix,
        node_num=node,
        target_node_num=hop_node_number,
    )
    print('saving graph to {}'.format(out_file_name))
    plt.savefig(out_file_name)
    plt.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='graph sender view of hop queue length')
    parser.add_argument('--node', dest='node', action='store', type=int, default=0, help="node id")
    parser.add_argument('--hop_node', dest='hop_node', action='store', type=int, default=0, help="hop node id")
    parser.add_argument('--flow', dest='flow', action='store', default='flow', help="the name of the flow file")
    parser.add_argument('--bw', dest="bw", action='store', default='100', help="the NIC bandwidth")
    parser.add_argument('--topo', dest='topo', action='store', default='fat', help="the name of the topology file")
    parser.add_argument('--cc_algo', dest='cc_algo', action='store', default='hp95ai50', help="CC algo with params")
    args = parser.parse_args()

    node_number = args.node
    hop_node_number = args.hop_node
    topo=args.topo
    flow=args.flow
    cc_algo = args.cc_algo

    file_suffix = get_file_suffix(topo=topo, flow=flow, cc_algo=cc_algo)
    trace_file = '../../simulation/mix/sender_view_{file_suffix}.txt'.format(file_suffix=file_suffix)

    times, sender_qlens = process_sender_view_trace_file(
        file_name=trace_file,
        target_node=node_number,
        target_hop_node=hop_node_number
    )
    plot_sender_qlen(
        node=node_number,
        hop_node=hop_node_number,
        cc_algo=cc_algo,
        times=times,
        sender_qlens=sender_qlens,
        file_suffix=file_suffix
    )
