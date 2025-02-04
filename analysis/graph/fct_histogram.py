import argparse
from typing import Dict, Tuple

from consts import VALID_BEHAVIORS
from graph_helpers import (
    get_file_suffix,
    get_mix_trace_filename,
    get_out_png_filename,
    plot_histogram,
    to_flow_key,
)


def process_fct_trace(fct_trace_path):
    # type: (str) -> Dict[str, Tuple[int, int, int]]
    """
    Reads FCT trace file and extracts all FCTs (in ns).
    Returned as {flow_tuple : (start_time, fct, standalone_fct)} map.
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
                fcts_by_flow[flow_key] = (start_time, fct, standalone_fct)
            except ValueError:
                print("Skipping line due to invalid data: {}".format(line))

    return fcts_by_flow

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
    fct_map = process_fct_trace(fct_trace_path=trace_file)

    base_file_suffix = get_file_suffix(topo=topo, flow=flow, cc_algo=cc_algo, misrep='none')
    base_trace_file = get_mix_trace_filename(trace_name='fct', file_suffix=base_file_suffix)
    base_fct_map = process_fct_trace(fct_trace_path=base_trace_file)
    
    assert set(base_fct_map.keys()) == set(fct_map.keys())
    diff_fct_map = {
        flow_key: fct_map[flow_key][1] - base_fct_map[flow_key][1]
        for flow_key in fct_map
    }
    #     fcts_ms.append(fct_ns / 1e6)
    
    out_png_name = get_out_png_filename(
        graph_metric='fct_histogram',
        file_suffix=get_file_suffix(topo=topo, flow=flow, cc_algo=cc_algo, misrep=''),
        node_num=node_num,
        out_label="{misrep}".format(misrep=misrep)
    )
    graph_title = "Diff flow completion times histogram: misrep {misrep}".format(
        misrep=misrep)
    plot_histogram(
        # data=[e[1] for e in fct_map.values()],
        data=diff_fct_map.values(),
        xlabel='Diff flow completion time (ns)',
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
