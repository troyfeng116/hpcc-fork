import bisect
import os
from typing import Dict, List, Optional, Tuple
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


# process qLen trace file: extract map of {node_num : [flow tuples involved]}
def process_qlen_trace_file_for_involved_nodes(file_name, node_num):
    # type: (str, int) -> Dict[int, List[str]]
    node_to_flows = {}

    with open(file_name, 'r') as file:
        # 2000055540 n:338 4:3 100608 Enqu ecn:0 0b00d101 0b012301 10000 100 U 161000 0 3 1048(1000)
        for line in file:
            parts = line.split()
            if len(parts) < 11:
                print('skipping {}'.format(line))
                continue
            node = int(parts[1].split(':')[1]) # node number
            sip, dip = parts[6], parts[7]
            sport, dport = parts[7], parts[8]
            flow_key = to_flow_key(sip=sip, sport=sport, dip=dip, dport=dport, start_time=-1)
            
            if node not in node_to_flows:
                node_to_flows[node] = []
            node_to_flows.append(flow_key)
    return node_to_flows

def process_fct_trace(fct_trace_path):
    # type: (str) -> Dict[str, Tuple[int, int, int, int]]
    """
    Reads FCT trace file and extracts all FCTs (in ns).
    Returned as {flow_tuple : (start_time, fct, standalone_fct, sz)} map.
    """
    fcts_by_flow = {}
    with open(fct_trace_path, 'r') as f:
        # sip, dip, sport, dport, size (B), start_time, fct (ns), standalone_fct (ns)
        for line in f:
            # Split the line into fields
            fields = line.strip().split()
            if len(fields) < 8:
                continue  # Skip lines that don't match the expected format

            try:
                # Extract the FCT (assume it's the 7th value in each line)
                sip, dip = int(fields[0][2:], 8), int(fields[1][2:], 8)
                sport, dport = int(fields[2]), int(fields[3])
                sz = int(fields[4])
                start_time = int(fields[5])
                fct, standalone_fct = int(fields[6]), int(fields[7])
                
                flow_key = to_flow_key(sip=sip, sport=sport, dip=dip, dport=dport, start_time=start_time)
                fcts_by_flow[flow_key] = (start_time, fct, standalone_fct, sz)
            except ValueError:
                print("Skipping line due to invalid data: {}".format(line))

    return fcts_by_flow

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
    # ax.invert_xaxis()
    ax.set_zlabel(zlabel)
    ax_title = ax.set_title("\n".join(textwrap.wrap(title, 60)))

    # Save the plot as a PNG file
    print('saving graph to {}'.format(out_file_name))

    fig.tight_layout()
    ax_title.set_y(1.05)
    fig.subplots_adjust(top=0.8)

    fig.savefig(out_file_name)
    plt.close()
    
# Plot multiple data points over time in stacks
def plot_contour_curve(
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
    
    Z_grid = np.array(Z)
    Z_grid = Z_grid.reshape((len(X), len(Y)))
    cset = ax.contour(X, Y, Z_grid, levels=10, colors='black', offset=-1)
    ax.clabel(cset, inline=1, fontsize=10)
    # CS = ax.contour(X, Y, Z)
    # ax.clabel(CS, inline=True, fontsize=10)
    
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    # ax.invert_xaxis()
    ax.set_zlabel(zlabel)
    ax_title = ax.set_title("\n".join(textwrap.wrap(title, 60)))

    # Save the plot as a PNG file
    print('saving graph to {}'.format(out_file_name))

    fig.tight_layout()
    ax_title.set_y(1.05)
    fig.subplots_adjust(top=0.8)

    fig.savefig(out_file_name)
    plt.close()

# Plot data points over time
def plot_bar_chart(X, Y, xlabel, ylabel, title, out_file_name):
    # type: (List[int], List[int], str, str, str, str) -> None
    plt.figure(figsize=(10, 6))
    plt.bar(X, Y, color='blue')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    # plt.legend()
    # plt.show()

    # Save the plot as a PNG file
    print('saving graph to {}'.format(out_file_name))
    plt.savefig(out_file_name)
    plt.close()


# Plot data points in histogram
def plot_histogram(data, xlabel, ylabel, title, out_file_name):
    # type: (List[int], str, str, str, str) -> None

    # Create the histogram
    data = np.array(data)

    filtered_data = remove_outliers_iqr(data)
    plt.hist(filtered_data, bins=100)

    # Add a title and labels
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    print('saving graph to {}'.format(out_file_name))
    plt.savefig(out_file_name)
    plt.close()

def plot_pos_neg_stacked_line_chart(data, xlabel, ylabel, title, out_file_name):
    # type: (List[int], str, str, str, str) -> None
    data = np.array(data)
    filtered_data = remove_outliers_iqr(data)
    abs_values = np.abs(filtered_data)
    
    # Separate positive and negative values
    pos_values = filtered_data[filtered_data > 0]
    neg_values = filtered_data[filtered_data < 0]
    
    # Create bins
    bins = np.linspace(min(abs_values), max(abs_values), num=20)
    pos_hist, _ = np.histogram(pos_values, bins=bins)
    neg_hist, _ = np.histogram(-neg_values, bins=bins)

    bin_centers = (bins[:-1] + bins[1:]) / 2
    width = (bins[1] - bins[0]) * 0.4
    
    plt.figure(figsize=(10, 6))
    plt.bar(bin_centers - width/2, pos_hist, width=width, label='Positive Values', color='blue', alpha=0.7)
    plt.bar(bin_centers + width/2, neg_hist, width=width, label='Negative Values', color='red', alpha=0.7)
    
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    
    print('saving graph to {out_file_name}'.format(out_file_name=out_file_name))
    plt.savefig(out_file_name)
    plt.close()

def plot_scatter(X, Y, xlabel, ylabel, title, out_file_name):
    # type: (List[int], List[int], str, str, str, str) -> None

    # filtered_data = remove_outliers_iqr(data)
    plt.scatter(X, Y)

    # Add a title and labels
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    print('saving graph to {}'.format(out_file_name))
    plt.savefig(out_file_name)
    plt.close()

# TODO: ignore start time?
# sip, dip, sport, dport, start_time -> hash key
def to_flow_key(sip, sport, dip, dport, start_time):
    # return "{sip}:{sport}${dip}:{dport}${start_time}".format(
    #     sip=sip, sport=sport, dip=dip, dport=dport, start_time=start_time
    # )
    return "{sip}:{sport}${dip}:{dport}".format(
        sip=sip, sport=sport, dip=dip, dport=dport
    )

def remove_outliers_iqr(data):
    """Removes outliers from a NumPy array using the IQR method."""

    q1 = np.percentile(data, 25)
    q3 = np.percentile(data, 75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    return data[(data >= lower_bound) & (data <= upper_bound)]
