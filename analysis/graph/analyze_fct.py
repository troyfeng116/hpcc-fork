import argparse
import numpy as np

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
    
    file_suffix = get_file_suffix(topo=topo, flow=flow, cc_algo=cc_algo, misrep=misrep)
    trace_file = get_mix_trace_filename(trace_name='fct', file_suffix=file_suffix)
    # {flow_tuple : (start_time, fct, standalone_fct, size)}
    fct_map = process_fct_trace(fct_trace_path=trace_file)
    
    base_file_suffix = get_file_suffix(topo=topo, flow=flow, cc_algo=cc_algo, misrep='none')
    base_trace_file = get_mix_trace_filename(trace_name='fct', file_suffix=base_file_suffix)
    base_fct_map = process_fct_trace(fct_trace_path=base_trace_file)
    
    assert set(base_fct_map.keys()) == set(fct_map.keys())
    X, Y = [], []
    for flow_key in base_fct_map:
        _, base_fct, _, base_size = base_fct_map[flow_key]
        _, exp_fct, _, exp_size = fct_map[flow_key]
        assert base_size == exp_size
        X.append(base_size)
        Y.append(exp_fct - base_fct)

    print(str(len([d for d in Y if d < 0])) + " faster")
    print(str(len([d for d in Y if d == 0])) + " equal")
    print(str(len([d for d in Y if d > 0])) + " slower")
    print(str(sum(Y)) + " total diff (ns)")

    data = np.array(Y)
    print(min(data), max(data))
    mean = np.mean(data)
    stddev = np.std(data)
    print("Mean:", mean)
    print("Standard deviation:", stddev)