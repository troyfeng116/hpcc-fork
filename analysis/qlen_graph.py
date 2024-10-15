import argparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from graph_helpers import get_file_suffix

def process_qlen_trace_file(file_name, node_number):
    # type: (str, int) -> Tuple[List[str], List[str]]
    times = []
    queue_lengths = []
    ts_to_qlen_map = {}

    with open(file_name, 'r') as file:
        for line in file:
            parts = line.split()
            if len(parts) < 4:
                print('skipping {}'.format(line))
                continue
            time_ns = int(parts[0]) # time ns
            node = int(parts[1].split(':')[1]) # node number
            queue_length = int(parts[3]) # queue length in bytes

            # Filter by the given node number
            if node == node_number:
                if time_ns not in ts_to_qlen_map:
                    ts_to_qlen_map[time_ns] = 0
                ts_to_qlen_map[time_ns] += queue_length

    for k, v in sorted(ts_to_qlen_map.items(), lambda a, b : a[0] - b[0]):
        times.append(k)
        queue_lengths.append(v)
    return times, queue_lengths

def get_qlen_out_png_name(file_suffix, node_num):
    # type: (str, int) -> str
    return "out/qlen_{file_suffix}_node_{node_num}.png".format(
        file_suffix=file_suffix, node_num=node_num
    )

# Plot total queue length over time
def plot_qlen(node_num, cc_algo, times, queue_lengths, file_suffix):
    # type: (int, str, List[int], List[int], str) -> None
    times_ms = [t / 1e6 for t in times]

    plt.figure(figsize=(10, 6))
    plt.plot(times_ms, queue_lengths, label='Queue Length (Bytes)', color='blue')
    plt.xlabel('Time (ms)')
    plt.ylabel('Queue Length (Bytes)')
    plt.title('Queue Length Over Time for Node {} ({})'.format(node_num, cc_algo))
    plt.grid(True)
    # plt.legend()
    # plt.show()
    # Save the plot as a PNG file
    out_file_name = get_qlen_out_png_name(file_suffix=file_suffix, node_num=node_num)
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
    trace_file = 'qlen_traces/qlen_{file_suffix}.txt'.format(file_suffix=file_suffix)

    times, queue_lengths = process_qlen_trace_file(file_name=trace_file, node_number=node_number)
    plot_qlen(
        node_num=node_number,
        cc_algo=cc_algo,
        times=times,
        queue_lengths=queue_lengths,
        file_suffix=file_suffix
    )
