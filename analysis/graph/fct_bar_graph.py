import argparse

from consts import VALID_BEHAVIORS
from graph_helpers import (
    get_file_suffix,
    get_mix_trace_filename,
    get_out_png_filename,
    plot_bar_chart,
)

def process_fct_trace(fct_trace_path):
    # type: (str) -> int
    """
    Reads multiple files and extracts mean FCT (in ns),
    using FCT values from each line.
    """
    fcts = []
    with open(fct_trace_path, 'r') as f:
        for line in f:
            # Split the line into fields
            fields = line.strip().split()
            if len(fields) < 8:
                continue  # Skip lines that don't match the expected format

            try:
                # Extract the FCT (assume it's the 7th value in each line)
                fct = int(fields[6])
                fcts.append(fct)
            except ValueError:
                print("Skipping line due to invalid data: {}".format(line))

    return sum(fcts) // len(fcts)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='graph window size')
    parser.add_argument('--node', dest='node', action='store', type=int, default=0, help="node id")
    parser.add_argument('--flow', dest='flow', action='store', default='mini_flow', help="the name of the flow file")
    parser.add_argument('--topo', dest='topo', action='store', default='mini_topology', help="the name of the topology file")
    parser.add_argument('--cc_algo', dest='cc_algo', action='store', default='hp95ai50', help="CC algo with params")
    parser.add_argument('--behavior', dest='behavior', action='store', required=True, help="the name of the misreporting profile file")
    parser.add_argument('--step', dest='step', action='store', default=10, help="probability step size, in percentage points")
    args = parser.parse_args()

    node_num = args.node
    topo=args.topo
    cc_algo = args.cc_algo
    flow=args.flow
    behavior=args.behavior
    step=args.step
    
    assert behavior in VALID_BEHAVIORS
    behavior_lower = behavior.lower()

    misrep_profiles = []
    fcts_ms = []
    for p in range(0, 101, step):
        if p == 0:
            misrep = "none".format(
                node_num=node_num, behavior_lower=behavior_lower)
            misrep_profiles.append("none")
        else:
            misrep = "node_{node_num}_{behavior_lower}_p{p}".format(
                node_num=node_num, behavior_lower=behavior_lower, p=p)
            misrep_profiles.append("p{p}".format(p=p))

        file_suffix = get_file_suffix(topo=topo, flow=flow, cc_algo=cc_algo, misrep=misrep)
        trace_file = get_mix_trace_filename(trace_name='fct', file_suffix=file_suffix)
        fct_ns = process_fct_trace(fct_trace_path=trace_file)
        fcts_ms.append(fct_ns / 1e6)
    
    out_png_name = get_out_png_filename(
        graph_metric='fct_bar',
        file_suffix=get_file_suffix(topo=topo, flow=flow, cc_algo=cc_algo, misrep=''),
        node_num=node_num,
    )
    graph_title = "Flow completion times: misrep {behavior}, step size {step}".format(
        behavior=behavior, step=step)
    plot_bar_chart(
        X=misrep_profiles,
        Y=fcts_ms,
        xlabel='Misreporting profile',
        ylabel='FCT (ms)',
        title=graph_title,
        out_file_name=out_png_name,
    )
