import argparse
import re

from graph_helpers import (
    get_baseline_interpolation,
    get_file_suffix,
    get_graph_title,
    get_out_png_filename,
    get_mix_trace_filename,
    get_qlen_trace_filename,
    plot_surface_curve,
    process_node_state_trace_file,
    process_qlen_trace_file,
)

# TODO: have nodes report expectation? Then expected qLen will also have a trace
def extract_integer(s):
    match = re.search(r'p(\d+)$', s)
    return int(match.group(1)) if match else None

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='graph (expected) queue length vs utility at fixed timestamp')
    parser.add_argument('--node', dest='node', action='store', type=int, required=True, help="node id")
    parser.add_argument('--ts_step_ns', dest='ts_step_ns', action='store', type=int, required=True, help="timestamp step (ns)")
    parser.add_argument('--flow', dest='flow', action='store', default='mini_flow', help="the name of the flow file")
    parser.add_argument('--topo', dest='topo', action='store', default='mini_topology', help="the name of the topology file")
    parser.add_argument('--misrep_profiles', dest='misrep_profiles', action='store', required=True, help="comma-separated list of misreporting profiles to compare")
    parser.add_argument('--cc_algo', dest='cc_algo', action='store', default='hp95ai50', help="CC algo with params")
    parser.add_argument('--out_label', dest='out_label', action='store', required=True, help="label for output PNG file")
    args = parser.parse_args()

    node_num = args.node
    ts_step_ns = args.ts_step_ns
    topo=args.topo
    misrep_profiles_str = args.misrep_profiles
    misrep_profiles = set(s.strip() for s in misrep_profiles_str.split(","))
    # do not include baseline first
    if 'none' in misrep_profiles:
        misrep_profiles.remove('none')

    flow=args.flow
    cc_algo = args.cc_algo
    out_label = args.out_label
    
    # Get baseline tx_bytes for diffs
    baseline_file_suffix = get_file_suffix(topo=topo, flow=flow, cc_algo=cc_algo, misrep='none')
    baseline_trace_file = get_mix_trace_filename(trace_name='node_trace', file_suffix=baseline_file_suffix)
    baseline_tx_times, baseline_tx_bytes = process_node_state_trace_file(file_name=baseline_trace_file, node_num=node_num)

    min_ts, max_ts = min(baseline_tx_times), max(baseline_tx_times)
    # avoid too many curves
    # assert (max_ts - min_ts) / ts_step_ns < 30
    
    # prob, time, diff_bytes
    probs, timestamps, diff_bytes_li = [], [], []
    for ts_ns in range(min_ts, max_ts + 1, ts_step_ns):
        baseline_tx_bytes_at_t = get_baseline_interpolation(t=ts_ns, baseline_times=baseline_tx_times, baseline_data_points=baseline_tx_bytes)

        expected_qlens_li, diff_tx_bytes_li = [], []

        for misrep in misrep_profiles:
            prob = extract_integer(s=misrep)
            # print(misrep + ' -> ' + str(prob))
            file_suffix = get_file_suffix(topo=topo, flow=flow, cc_algo=cc_algo, misrep=misrep)

            # qLen traces are read separately from `simulation/mix` by `trace_reader`
            qlen_trace_file = get_qlen_trace_filename(file_suffix=file_suffix)
            qlen_times, qlens = process_qlen_trace_file(file_name=qlen_trace_file, node_num=node_num)
            qlen_at_t = get_baseline_interpolation(t=ts_ns, baseline_times=qlen_times, baseline_data_points=qlens)
            expec_qlen_at_t = qlen_at_t * prob / 100

            node_trace_file = get_mix_trace_filename(trace_name='node_trace', file_suffix=file_suffix)
            tx_times, tx_bytes_li = process_node_state_trace_file(file_name=node_trace_file, node_num=node_num)
            tx_bytes_at_t = get_baseline_interpolation(t=ts_ns, baseline_times=tx_times, baseline_data_points=tx_bytes_li)

            probs.append(prob)
            timestamps.append(ts_ns / 1e6)
            diff_bytes_li.append(tx_bytes_at_t - baseline_tx_bytes_at_t)

        # print('ts_ns=' + str(ts_ns) + ' -> expected_qlens_li ' + str(expected_qlens_li) + ', diff_tx_bytes_li ' + str(diff_tx_bytes_li))
        # sorted_points = sorted(zip(expected_qlens_li, diff_tx_bytes_li), key=lambda x: x[0])
        # expected_qlens_li, diff_tx_bytes_li = zip(*sorted_points)
        # data_points_li.append(('t=' + str(ts_ns / 1e6) + 'ms', expected_qlens_li, diff_tx_bytes_li))

    graph_title = 'Prob/time/util surface: node {node_num}, misrep_profiles {misrep_profiles}'.format(
        node_num=node_num, misrep_profiles=','.join(list(misrep_profiles)[:3]) + '...'
    )
    png_suffix = get_file_suffix(topo=topo, flow=flow, cc_algo=cc_algo, misrep='')
    out_png_name = get_out_png_filename(
        graph_metric='prob_time_util_surface',
        file_suffix=png_suffix,
        node_num=node_num,
        out_label=out_label,
    )
    plot_surface_curve(
        X=timestamps,
        Y=probs,
        Z=diff_bytes_li,
        xlabel="Timestamp (ms)",
        ylabel="Probability (%)",
        zlabel="Diff tx_bytes (B)",
        # xlabel='Probability of misreport (%)',
        # ylabel='Diff txBytes (bytes)',
        title=graph_title,
        out_file_name=out_png_name,
    )
