import argparse

from graph_helpers import (
    get_file_suffix,
    get_mix_trace_filename,
    get_out_png_filename,
    plot_scatter,
    process_fct_trace,
)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='graph window size')
    parser.add_argument('--node', dest='node', action='store', type=int, default=0, help="node id")
    parser.add_argument('--flow', dest='flow', action='store', default='mini_flow', help="the name of the flow file")
    parser.add_argument('--topo', dest='topo', action='store', default='mini_topology', help="the name of the topology file")
    parser.add_argument('--cc_algo', dest='cc_algo', action='store', default='hp95ai50', help="CC algo with params")
    parser.add_argument('--misrep', dest='misrep', action='store', default='none', help="the name of misreporting profile file")
    # parser.add_argument('--behavior', dest='behavior', action='store', required=True, help="the name of the misreporting profile file")
    # parser.add_argument('--step', dest='step', action='store', default=10, help="probability step size, in percentage points")
    args = parser.parse_args()

    node_num = args.node
    topo=args.topo
    cc_algo = args.cc_algo
    flow=args.flow
    misrep=args.misrep
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
    # {flow_tuple : (start_time, fct, standalone_fct, size)}
    fct_map = process_fct_trace(fct_trace_path=trace_file)

    base_file_suffix = get_file_suffix(topo=topo, flow=flow, cc_algo=cc_algo, misrep='none')
    base_trace_file = get_mix_trace_filename(trace_name='fct', file_suffix=base_file_suffix)
    base_fct_map = process_fct_trace(fct_trace_path=base_trace_file)
    
    assert set(base_fct_map.keys()) == set(fct_map.keys())
    X,Y = [], []
    for flow_key in base_fct_map:
        _, base_fct, _, base_size = base_fct_map[flow_key]
        _, exp_fct, _, exp_size = fct_map[flow_key]
        assert base_size == exp_size
        X.append(base_size)
        Y.append(exp_fct - base_fct)

    #     fcts_ms.append(fct_ns / 1e6)
    
    out_png_name = get_out_png_filename(
        graph_metric='fct_scatter',
        file_suffix=get_file_suffix(topo=topo, flow=flow, cc_algo=cc_algo, misrep=''),
        node_num=node_num,
        out_label="{misrep}".format(misrep=misrep)
    )
    graph_title = "Scatterplot of FCTs against flow size: misrep {misrep}".format(
        misrep=misrep)
    plot_scatter(
        # data=[e[1] for e in fct_map.values()],
        X=X,
        Y=Y,
        xlabel='Flow size (bytes)',
        ylabel='Diff FCT (ns)',
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
