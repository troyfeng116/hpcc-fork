import argparse

from graph_helpers import (
    get_file_suffix,
    get_graph_title,
    get_out_png_filename,
    get_mix_trace_filename,
    plot_stacked_data_points,
    process_node_state_trace_file,
)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='graph output bytes')
    parser.add_argument('--node', dest='node', action='store', type=int, required=True, help="node id")
    parser.add_argument('--misrep_profiles', dest='misrep_profiles', action='store', required=True, help="comma-separated list of misreporting profiles to compare")
    parser.add_argument('--flow', dest='flow', action='store', default='mini_flow', help="the name of the flow file")
    parser.add_argument('--topo', dest='topo', action='store', default='mini_topology', help="the name of the topology file")
    parser.add_argument('--cc_algo', dest='cc_algo', action='store', default='hp95ai50', help="CC algo with params")
    parser.add_argument('--out_label', dest='out_label', action='store', required=True, help="label for output PNG file")
    args = parser.parse_args()

    node_num = args.node
    topo=args.topo
    misrep_profiles_str = args.misrep_profiles
    misrep_profiles = set(s.strip() for s in misrep_profiles_str.split(","))
    # do not include baseline first
    if 'none' in misrep_profiles:
        misrep_profiles.remove('none')

    flow=args.flow
    cc_algo = args.cc_algo
    out_label = args.out_label
    # [label, times, tx_bytes]
    data_points_li = []

    for misrep in misrep_profiles:
        file_suffix = get_file_suffix(topo=topo, flow=flow, cc_algo=cc_algo, misrep=misrep)
        trace_file = get_mix_trace_filename(trace_name='node_trace', file_suffix=file_suffix)

        times, tx_bytes = process_node_state_trace_file(file_name=trace_file, node_num=node_num)
        times_ms = [t / 1e6 for t in times]
        data_points_li.append((misrep, times_ms, tx_bytes))

    # get baseline for diffs
    baseline_file_suffix = get_file_suffix(topo=topo, flow=flow, cc_algo=cc_algo, misrep='none')
    baseline_trace_file = get_mix_trace_filename(trace_name='node_trace', file_suffix=baseline_file_suffix)
    baseline_times, baseline_tx_bytes = process_node_state_trace_file(file_name=baseline_trace_file, node_num=node_num)
    baseline_times_ms = [t / 1e6 for t in times]
    data_points_li.append(('none', baseline_times_ms, baseline_tx_bytes))
    baseline_ts_map = {t:tx for t, tx in zip(baseline_times_ms, baseline_tx_bytes)}

    diff_points_li = []
    for misrep, times_ms, tx_bytes in data_points_li:
        truncated_times, diff_points = [], []
        for t, tx in zip(times_ms, tx_bytes):
            if t in baseline_ts_map:
                truncated_times.append(t)
                diff_points.append(tx - baseline_ts_map[t])
        diff_points_li.append((misrep, truncated_times, diff_points))

    stacked_misrep_tok = 'various'
    stacked_file_suffix = get_file_suffix(topo=topo, flow=flow, cc_algo=cc_algo, misrep=stacked_misrep_tok)
    out_png_name = get_out_png_filename(
        graph_metric='stacked_diff_tx_bytes',
        file_suffix=stacked_file_suffix,
        node_num=node_num,
        out_label=out_label,
    )
    graph_title = get_graph_title(
        metric_name='Difference in transmitted bytes',
        node_num=node_num,
        cc_algo=cc_algo,
        misrep=stacked_misrep_tok,
    )
    plot_stacked_data_points(
        data_points_li=diff_points_li,
        xlabel='Time (ms)',
        ylabel='Diff transmitted bytes',
        title=graph_title,
        out_file_name=out_png_name,
    )