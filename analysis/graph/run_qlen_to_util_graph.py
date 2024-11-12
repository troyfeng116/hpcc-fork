import argparse
import os
import subprocess
import sys

from typing import List

script_dir = os.path.dirname(os.path.abspath(__file__))

TRACE_READER_SCRIPT = script_dir + '/run_trace_reader.py'
QLEN_TO_DIFF_TX_BYTES_GRAPH_SCRIPT = script_dir + '/qlen_to_diff_tx_bytes_graph.py'

HPCC_ALGO = 'hp95ai50'

VALID_BEHAVIORS = {
    'ZERO',
    'TRIPLE',
    'ADD',
}

def run_trace_reader_script(misrep_file_name, flow, topo):
    # type: (str, str, str) -> None
    
    # python run_trace_reader.py \
    # --flow=mini_flow \
    # --topo=mini_topology \
    # --cc_algo=hp95ai50 \
    # --misrep=node_2_zero_p25
    command = [
        'python', TRACE_READER_SCRIPT,
        '--cc_algo', HPCC_ALGO,
        '--flow', flow,
        '--topo', topo,
        '--misrep', misrep_file_name,
    ]

    try:
        # Run command and capture output
        output = subprocess.check_output(command)
        print("trace_reader complete for " + misrep_file_name)
    except subprocess.CalledProcessError as e:
        print("Error:", e)

def run_qlen_to_diff_tx_bytes_graph_script(node_num, flow, topo, misrep_file_names, ts_step_ns, out_label):
    # type: (int, str, str, List[str], int, str) -> None

    # python qlen_to_diff_tx_bytes_graph.py \
    # --node=2 \
    # --ts_step_ns=8320 \
    # --flow=mini_flow \
    # --topo=mini_topology \
    # --misrep_profiles=node_2_zero_p25,node_2_zero_p50 \
    # --cc_algo=hp95ai50 \
    # --out_label=ZERO
    for py_script in [QLEN_TO_DIFF_TX_BYTES_GRAPH_SCRIPT]:
        misrep_files_str = ','.join(misrep_file_names)
        command = [
            'python', py_script,
            '--node', str(node_num),
            '--flow', flow,
            '--topo', topo,
            '--cc_algo', HPCC_ALGO,
            '--misrep_profiles', misrep_files_str,
            '--ts_step_ns', str(ts_step_ns),
            '--out_label', out_label,
        ]

        try:
            # Run command and capture output
            output = subprocess.check_output(command)
            print("Output:\n" + output)
        except subprocess.CalledProcessError as e:
            print("Error:", e)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='run probability matrix sim')
    parser.add_argument('--node', dest='node', action='store', type=int, required=True, help="node id")
    parser.add_argument('--ts_step_ns', dest='ts_step_ns', action='store', type=int, required=True, help="timestamp slice (ns)")
    parser.add_argument('--flow', dest='flow', action='store', default='mini_flow', help="the name of the flow file")
    parser.add_argument('--topo', dest='topo', action='store', default='mini_topology', help="the name of the topology file")
    parser.add_argument('--behavior', dest='behavior', action='store', required=True, help="misreporting behavior (TRIPLE, ADD, ZERO, etc.)")
    parser.add_argument('--step', dest='step', action='store', type=int, default=50, help="the probability step size")
    parser.add_argument('--should_skip_trace_reader', dest='should_skip_trace_reader', action='store_true', help="specify to skip trace reader and only generate graphs")
    args = parser.parse_args()

    node_num = args.node
    ts_step_ns = args.ts_step_ns
    flow = args.flow
    topo = args.topo
    behavior_config = args.behavior
    assert behavior_config in VALID_BEHAVIORS
    behavior_label = behavior_config.lower()
    step = args.step
    should_skip_trace_reader = args.should_skip_trace_reader
    
    misrep_files = []

    for p in range(step, 101, step):
        misrep_file_name = 'node_{node_num}_{behavior_label}_p{prob}'.format(
            node_num=node_num, behavior_label=behavior_label, prob=p
        )
        misrep_files.append(misrep_file_name)

        if not should_skip_trace_reader:
            run_trace_reader_script(misrep_file_name=misrep_file_name, flow=flow, topo=topo)

    out_label = '{behavior_config}_pstep_{step}_tstep_{ts_step_ns}'.format(
        behavior_config=behavior_config, step=step, ts_step_ns=ts_step_ns,
    )
    run_qlen_to_diff_tx_bytes_graph_script(
        node_num=node_num,
        flow=flow,
        topo=topo,
        misrep_file_names=misrep_files,
        ts_step_ns=ts_step_ns,
        out_label=out_label,
    )
