import bisect
import os
from typing import List, Optional, Tuple
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import textwrap

script_dir = os.path.dirname(os.path.abspath(__file__))

COLORS = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'gray', 'pink', 'lawngreen', 'paleturquoise', 'black']

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
    
# linearly interpolate between two baseline points
def get_baseline_interpolation(t, baseline_times, baseline_data_points):
    # type: (int, List[int], List[int]) -> float

    idx = bisect.bisect_left(baseline_times, t)
    if 0 <= idx < len(baseline_times) and baseline_times[idx] == t:
        return baseline_data_points[idx]
    # range endpoints
    if idx == 0:
        return baseline_data_points[0]
    if idx == len(baseline_times):
        return baseline_data_points[-1]

    t1, t2 = baseline_times[idx - 1], baseline_times[idx]
    tx1, tx2 = baseline_data_points[idx - 1], baseline_data_points[idx]
    return tx1 + (t - t1) * (tx2 - tx1) / (t2 - t1)

# path to simulation output trace file in `simulation/mix/`
def get_mix_trace_filename(trace_name, file_suffix, file_type='txt'):
    # type: (str, str, Optional[str]) -> str
    return script_dir + '/../../simulation/mix/{trace_name}_{file_suffix}.{file_type}'.format(
        trace_name=trace_name, file_suffix=file_suffix, file_type=file_type
    )

# read node_state trace file
# returns cumulative bytes over ordered timestamps (ts, tx_bytes)
def process_node_state_trace_file(file_name, node_num):
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
            if node == node_num:
                if time_ns not in ts_to_tx_bytes_map:
                    ts_to_tx_bytes_map[time_ns] = tx_bytes
                ts_to_tx_bytes_map[time_ns] = max(
                    ts_to_tx_bytes_map[time_ns],
                    tx_bytes,
                )

    for k, v in sorted(ts_to_tx_bytes_map.items(), lambda a, b : a[0] - b[0]):
        times.append(k)
        tx_bytes_li.append(v)
    return times, tx_bytes_li

def get_qlen_trace_filename(file_suffix):
    # type: (str) -> str
    return script_dir + '/qlen_traces/qlen_{file_suffix}.txt'.format(file_suffix=file_suffix)

# process qLen trace file
def process_qlen_trace_file(file_name, node_num):
    # type: (str, int) -> Tuple[List[str], List[str]]
    times = []
    queue_lengths = []
    ts_to_qlen_map = {}

    with open(file_name, 'r') as file:
        # 2000055540 n:338 4:3 100608 Enqu ecn:0 0b00d101 0b012301 10000 100 U 161000 0 3 1048(1000)
        for line in file:
            parts = line.split()
            if len(parts) < 11:
                print('skipping {}'.format(line))
                continue
            time_ns = int(parts[0]) # time ns
            node = int(parts[1].split(':')[1]) # node number
            event_type = parts[4]
            queue_length = int(parts[3]) # queue length in bytes
            packet_type = parts[10] # 'U' for data packet

            # Filter by the given node number
            if event_type == "Dequ" and packet_type == "U" and node == node_num:
                if time_ns not in ts_to_qlen_map:
                    ts_to_qlen_map[time_ns] = 0
                ts_to_qlen_map[time_ns] += queue_length

    for k, v in sorted(ts_to_qlen_map.items(), lambda a, b : a[0] - b[0]):
        times.append(k)
        queue_lengths.append(v)
    return times, queue_lengths

# get path to output PNG file name
def get_out_png_filename(graph_metric, file_suffix, node_num, hop_node_num=None, out_label=None):
    # type: (str, str, int, Optional[int], Optional[str]) -> str
    hop_node_str = '' if hop_node_num is None else '_hopnode_{hop_node_num}'.format(
        hop_node_num=hop_node_num
    )
    out_label = '' if not out_label else '__{out_label}'.format(out_label=out_label)
    return script_dir + "/out/{graph_metric}_{file_suffix}_node_{node_num}{hop_node_str}{out_label}.png".format(
        graph_metric=graph_metric, file_suffix=file_suffix, node_num=node_num, hop_node_str=hop_node_str, out_label=out_label
    )

# Plot data points over time
def plot_data_points(times, data_points, xlabel, ylabel, title, out_file_name):
    # type: (List[int], List[int], str, str, str, str) -> None
    plt.figure(figsize=(10, 6))
    plt.plot(times, data_points, color='blue')
    plt.axhline(y=100e9/50e6, linestyle=':', color='orange')
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

# Plot multiple data points over time in stacks
def plot_stacked_data_points(
    data_points_li,
    xlabel,
    ylabel,
    title,
    out_file_name,
    x_axis_step=None,
):
    # type: (List[Tuple[str, List[int], List[int]]], str, str, str, str, Optional[int]) -> None
    
    # (experiment_name, timestamps, data_points)
    data_points_li.sort(key=lambda x: x[0])
    fig = plt.figure(figsize=(10, 6))
    ax1 = fig.subplots()
    
    cmap = plt.get_cmap('tab10')
    colors = cmap(np.linspace(0, 1, len(data_points_li)))
    for idx, (label, times, data_points) in enumerate(data_points_li):
        ax1.plot(times, data_points, color=colors[idx % len(colors)], label=label)
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)
    ax1.set_title(title, y=1.09)
    ax1.grid(True)
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

    if x_axis_step is not None:
        ax2 = ax1.twiny()
        ax2.set_xlim(ax1.get_xlim())
        min_x = min(min(times) for _, times, _ in data_points_li)
        max_x = max(max(times) for _, times, _ in data_points_li)
        rtt_tick_locs = np.arange(min_x, max_x, x_axis_step)
        ax2.set_xticks(rtt_tick_locs)
        ax2.set_xticklabels(range(len(rtt_tick_locs)))
        ax2.set_xlabel('RTTs')

    # Save the plot as a PNG file
    print('saving graph to {}'.format(out_file_name))
    
    fig.tight_layout()
    fig.savefig(out_file_name)
    plt.close()

# Plot multiple data points over time in stacks
def plot_surface_curve(
    X,
    Y,
    Z,
    xlabel,
    ylabel,
    zlabel,
    title,
    out_file_name,
    x_axis_step=None,
):
    # type: (List[int], List[int], List[int], str, str, str, str, str, Optional[int]) -> None
    
    # (experiment_name, x, y, z)
    # fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
    fig = plt.figure()
    ax = fig.gca(projection='3d')

    # X, Y = np.meshgrid(X, Y)
    # Z = np.array(Z).reshape(X.shape)
    surf = ax.plot_trisurf(X, Y, Z, cmap=cm.coolwarm,
                       linewidth=0, antialiased=False)
    fig.colorbar(surf, shrink=0.5, aspect=5)
    
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.invert_xaxis()
    ax.set_zlabel(zlabel)
    ax_title = ax.set_title("\n".join(textwrap.wrap(title, 60)))

    # Save the plot as a PNG file
    print('saving graph to {}'.format(out_file_name))

    fig.tight_layout()
    ax_title.set_y(1.05)
    fig.subplots_adjust(top=0.8)

    fig.savefig(out_file_name)
    plt.close()
