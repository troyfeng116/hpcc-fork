import argparse
from typing import List, Tuple

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from graph_helpers import get_file_suffix

def process_sender_rate_trace_file(file_name, node_number):
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

            if node == node_number:
                times.append(time_ns)
                sender_rates.append(sender_rate)

    print(len(times))
    return times, sender_rates

def get_sender_rate_out_png_name(file_suffix, node_num):
    # type: (str, int) -> str
    return "out/sender_rate_{file_suffix}_node_{node_num}.png".format(
        file_suffix=file_suffix, node_num=node_num
    )

# Plot window size over time
def plot_sender_rate(node_num, cc_algo, times, send_rates, file_suffix):
    # type: (int, str, List[int], List[int], str) -> None
    times_ms = [t / 1e6 for t in times]
    send_rates_b_s = [r / 8 for r in send_rates]  # bit rate to bytes

    plt.figure(figsize=(10, 6))
    plt.plot(times_ms, send_rates_b_s, label='Send rate (Bytes/s)', color='blue')
    plt.xlabel('Time (ms)')
    plt.ylabel('Send rate (B/s)')
    plt.title('Send rate Over Time for Node {} ({})'.format(node_num, cc_algo))
    plt.grid(True)
    # plt.legend()
    # plt.show()
    # Save the plot as a PNG file
    out_file_name = get_sender_rate_out_png_name(file_suffix=file_suffix, node_num=node_num)
    print('saving graph to {}'.format(out_file_name))
    plt.savefig(out_file_name)
    plt.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='graph window size')
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
    trace_file = '../../simulation/mix/wsize_{file_suffix}.txt'.format(file_suffix=file_suffix)

    times, send_rates = process_sender_rate_trace_file(file_name=trace_file, node_number=node_number)
    plot_sender_rate(
        node_num=node_number,
        cc_algo=cc_algo,
        times=times,
        send_rates=send_rates,
        file_suffix=file_suffix
    )
