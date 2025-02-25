import argparse

from graph_helpers import (
    get_file_suffix,
    get_mix_trace_filename,
    get_out_png_filename,
    plot_pos_neg_stacked_line_chart,
    process_fct_trace,
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='graph positive/negative diff FCTs ')
    parser.add_argument('--node', dest='node', action='store', type=int, default=0, help="node id")
    parser.add_argument('--flow', dest='flow', action='store', default='mini_flow', help="the name of the flow file")
    parser.add_argument('--topo', dest='topo', action='store', default='mini_topology', help="the name of the topology file")
    parser.add_argument('--cc_algo', dest='cc_algo', action='store', default='hp95ai50', help="CC algo with params")
    parser.add_argument('--misrep', dest='misrep', action='store', default='none', help="the name of misreporting profile file")
    parser.add_argument('--should_norm', dest='should_norm', action='store_true', help="whether to normalize FCT against flow size")
    parser.add_argument('--should_filter', dest='should_filter', action='store_true', help="whether to filter flows that only traverse given node")
    # parser.add_argument('--behavior', dest='behavior', action='store', required=True, help="the name of the misreporting profile file")
    # parser.add_argument('--step', dest='step', action='store', default=10, help="probability step size, in percentage points")
    args = parser.parse_args()

    node_num = args.node
    topo=args.topo
    cc_algo = args.cc_algo
    flow=args.flow
    misrep=args.misrep
    should_norm=args.should_norm
    # behavior=args.behavior
    # step=args.step
    
    # assert behavior in VALID_BEHAVIORS
    # behavior_lower = behavior.lower()

    # misrep_profiles = []
    # fcts_ms = []
    # for p in range(0, 101, step):
    #     if p == 0:
    #         misrep = "none".format(
    #             node_num=node_num, behavior_lower=behavior_lower)
    #         misrep_profiles.append("none")
    #     else:
    #         misrep = "node_{node_num}_{behavior_lower}_p{p}".format(
    #             node_num=node_num, behavior_lower=behavior_lower, p=p)
    #         misrep_profiles.append("p{p}".format(p=p))

    file_suffix = get_file_suffix(topo=topo, flow=flow, cc_algo=cc_algo, misrep=misrep)
    trace_file = get_mix_trace_filename(trace_name='fct', file_suffix=file_suffix)
    # {flow_tuple : (start_time, fct, standalone_fct, sz)}
    fct_map = process_fct_trace(fct_trace_path=trace_file)

    base_file_suffix = get_file_suffix(topo=topo, flow=flow, cc_algo=cc_algo, misrep='none')
    base_trace_file = get_mix_trace_filename(trace_name='fct', file_suffix=base_file_suffix)
    base_fct_map = process_fct_trace(fct_trace_path=base_trace_file)

    # get nodes involved in these flows
    # TODO

    assert set(base_fct_map.keys()) == set(fct_map.keys())
    diff_fct_map = {
        flow_key: (flow_data[1] - base_fct_map[flow_key][1]) / flow_data[3]
            if should_norm
            else flow_data[1] - base_fct_map[flow_key][1]
        for flow_key, flow_data in fct_map.items()
    }
    #     fcts_ms.append(fct_ns / 1e6)
    
    out_png_name = get_out_png_filename(
        graph_metric='fct_abs_hist_norm' if should_norm  else 'fct_abs_hist',
        file_suffix=get_file_suffix(topo=topo, flow=flow, cc_algo=cc_algo, misrep=''),
        node_num=node_num,
        out_label="{misrep}".format(misrep=misrep)
    )
    norm_str = ' (normalized by flow size)' if should_norm else ''
    graph_title = "Abs (exp-baseline) diff FCT histogram{norm_str}: misrep {misrep}".format(
        misrep=misrep, norm_str=norm_str)
    plot_pos_neg_stacked_line_chart(
        # data=[e[1] for e in fct_map.values()],
        data=diff_fct_map.values(),
        xlabel='Abs diff FCT (ns/byte)',
        ylabel='Number of flows',
        title=graph_title,
        out_file_name=out_png_name,
    )
    # plot_bar_chart(
    #     X=misrep_profiles,
    #     Y=fcts_ms,
    #     xlabel='Misreporting profile',
    #     ylabel='FCT (ms)',
    #     title=graph_title,
    #     out_file_name=out_png_name,
    # )
