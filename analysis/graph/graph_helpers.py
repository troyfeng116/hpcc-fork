from typing import List
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def get_file_suffix(topo, flow, cc_algo):
    # type: (str, str, str) -> str
    return '{topo}_{flow}_{cc_algo}'.format(
        topo=topo, flow=flow, cc_algo=cc_algo
    )

# Plot data points over time
def plot_data_points(times, data_points, xlabel, ylabel, title, out_file_name):
    # type: (List[int], List[int], str, str, str, str) -> None
    plt.figure(figsize=(10, 6))
    plt.plot(times, data_points, color='blue')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True)
    # plt.legend()
    # plt.show()

    # Save the plot as a PNG file
    print('saving graph to {}'.format(out_file_name))
    plt.savefig(out_file_name)
    plt.close()
