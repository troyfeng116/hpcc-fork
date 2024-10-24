from typing import List, Optional
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def get_file_suffix(topo, flow, cc_algo, misrep):
    # type: (str, str, str, str) -> str
    return '{topo}_{flow}_{cc_algo}_{misrep}'.format(
        topo=topo, flow=flow, cc_algo=cc_algo, misrep=misrep
    )

def get_graph_title(metric_name, node_num, cc_algo, misrep, hop_node_num=None):
    # type: (str, str, str, str, Optional[str]) -> str
    hop_node_str = '' if hop_node_num is None else ', view of hop {hop_node_num}'.format(
        hop_node_num=hop_node_num
    )
    return '{metric_name} Over Time for Node {node_num}{hop_node_str} (CC {cc_algo}, misreport profile {misrep})'.format(
        metric_name=metric_name,
        node_num=node_num,
        hop_node_str=hop_node_str,
        cc_algo=cc_algo,
        misrep=misrep,
    )

# path to simulation output trace file in `simulation/mix/`
def get_mix_trace_filename(trace_name, file_suffix, file_type='txt'):
    # type: (str, str, Optional[str]) -> str
    return '../../simulation/mix/{trace_name}_{file_suffix}.{file_type}'.format(
        trace_name=trace_name, file_suffix=file_suffix, file_type=file_type
    )

# get path to output PNG file name
def get_out_png_filename(graph_metric, file_suffix, node_num, hop_node_num=None):
    # type: (str, str, int, Optional[int]) -> str
    hop_node_str = '' if hop_node_num is None else '_hopnode_{hop_node_num}'.format(
        hop_node_num=hop_node_num
    )
    return "out/{graph_metric}_{file_suffix}_node_{node_num}{hop_node_str}.png".format(
        graph_metric=graph_metric, file_suffix=file_suffix, node_num=node_num, hop_node_str=hop_node_str
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
