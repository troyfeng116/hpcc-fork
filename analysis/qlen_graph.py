import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def process_trace_file(file_name, node_number):
    times = []
    queue_lengths = []

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
            if node == node_number and queue_length > 0:
                times.append(time_ns)
                queue_lengths.append(queue_length)

    return times, queue_lengths

def get_qlen_out_png_name(file_name, node_num):
    return "out/qlen_{}_node_{}.png".format(file_name, node_num)

# Plot total queue length over time
def plot_queue_length(node_num, times, queue_lengths, file_name):
    times_ms = [t / 1e6 for t in times]

    plt.figure(figsize=(10, 6))
    plt.plot(times_ms, queue_lengths, label='Queue Length (Bytes)', color='blue')
    plt.xlabel('Time (ms)')
    plt.ylabel('Queue Length (Bytes)')
    plt.title('Queue Length Over Time for Node {}'.format(node_num))
    plt.grid(True)
    # plt.legend()
    # plt.show()
    # Save the plot as a PNG file
    out_file_name = get_qlen_out_png_name(file_name=file_name, node_num=node_num)
    print('saving graph to {}'.format(out_file_name))
    plt.savefig(out_file_name)
    plt.close()

# Main function
if __name__ == '__main__':
    trace_file = 'mini_topology_mini_flow_hp95ai50_TRACE.out'
    node_number = 2

    times, queue_lengths = process_trace_file(trace_file, node_number)
    plot_queue_length(
        node_number,
        times,
        queue_lengths,
        file_name=trace_file
    )
