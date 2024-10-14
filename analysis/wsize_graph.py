import argparse
from typing import List, Tuple

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def get_file_suffix(topo, flow, utgt, hpai):
    # type: (str, str, int, int) -> str
    return '{topo}_{flow}_hp{utgt}ai{hpai}'.format(
        topo=topo, flow=flow, utgt=utgt, hpai=hpai
    )

def process_wsize_trace_file(file_name, node_number):
    # type: (str, int) -> Tuple[List[str], List[str]]
    times = []
    w_sizes = []

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
            w_size = int(toks[6]) # window size in bytes

            if node == node_number:
                times.append(time_ns)
                w_sizes.append(w_size)

    print(len(times))
    return times, w_sizes

def get_wsize_out_png_name(file_suffix, node_num):
    # type: (str, int) -> str
    return "out/wsize_{file_suffix}_node_{node_num}.png".format(
        file_suffix=file_suffix, node_num=node_num
    )

# Plot window size over time
def plot_wsize(node_num, times, wsizes, file_suffix):
    # type: (int, List[int], List[int], str) -> None
    times_ms = [t / 1e6 for t in times]

    plt.figure(figsize=(10, 6))
    plt.plot(times_ms, wsizes, label='Window size (Bytes)', color='blue')
    plt.xlabel('Time (ms)')
    plt.ylabel('Window size (Bytes)')
    plt.title('Window size Over Time for Node {}'.format(node_num))
    plt.grid(True)
    # plt.legend()
    # plt.show()
    # Save the plot as a PNG file
    out_file_name = get_wsize_out_png_name(file_suffix=file_suffix, node_num=node_num)
    print('saving graph to {}'.format(out_file_name))
    plt.savefig(out_file_name)
    plt.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='graph window size')
    parser.add_argument('--node', dest='node', action='store', type=int, default=0, help="node id")
    parser.add_argument('--flow', dest='flow', action='store', default='flow', help="the name of the flow file")
    parser.add_argument('--bw', dest="bw", action='store', default='100', help="the NIC bandwidth")
    parser.add_argument('--topo', dest='topo', action='store', default='fat', help="the name of the topology file")
    parser.add_argument('--utgt', dest='utgt', action='store', type=int, default=95, help="eta of HPCC")
    parser.add_argument('--mi', dest='mi', action='store', type=int, default=0, help="MI_THRESH")
    parser.add_argument('--hpai', dest='hpai', action='store', type=int, default=0, help="AI for HPCC")
    args = parser.parse_args()

    node_number = args.node
    topo=args.topo
    flow=args.flow
    utgt = args.utgt
    hpai=args.hpai

    file_suffix = get_file_suffix(topo=topo, flow=flow, utgt=utgt, hpai=hpai)
    trace_file = '../simulation/mix/wsize_{file_suffix}.txt'.format(file_suffix=file_suffix)

    times, wsizes = process_wsize_trace_file(file_name=trace_file, node_number=node_number)
    plot_wsize(
        node_num=node_number,
        times=times,
        wsizes=wsizes,
        file_suffix=file_suffix
    )
