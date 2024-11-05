import argparse
import os
import subprocess
import sys

from typing import List

script_dir = os.path.dirname(os.path.abspath(__file__))

RUN_PY_SCRIPT = script_dir + '/run.py'
STACKED_GRAPH_PY_SCRIPT = script_dir + '/../analysis/graph/stacked_tx_bytes_graph.py'
STACKED_DIFF_GRAPH_PY_SCRIPT = script_dir + '/../analysis/graph/stacked_diff_tx_bytes_graph.py'

HPCC_ALGO = 'hp95ai50'

VALID_BEHAVIORS = {
    'ZERO',
    'TRIPLE',
    'ADD',
}

def generate_misrep_file(
    file_name,
    node_num,
    behavior_config,
    prob,
):
    # type: (str, int, str, int) -> None
    file_path = '{script_dir}/mix/{file_name}.txt'.format(
        script_dir=script_dir, file_name=file_name
    )
    with open(file_path, 'w') as f:
        target_node_line = '{node_num} {behavior_config} {prob}'.format(
            node_num=node_num, behavior_config=behavior_config, prob=prob
        )
        f.write('1\n' + target_node_line)

def run_hpcc_simulation(misrep_file_name, flow, topo):
    # type: (str, str, str) -> None
    command = [
        'python', RUN_PY_SCRIPT,
        '--cc', 'hp',
        '--trace', flow,
        '--bw', '100',
        '--topo', topo,
        '--hpai', '50',
        '--enable_tr', '1',
        '--utgt', '95',
        '--misrep', misrep_file_name,
    ]

    try:
        # Run command and capture output
        output = subprocess.check_output(command)
        assert 'Running Simulation.' in output
        assert 'setting node 2 reporting function' in output
        assert 'with prob' in output
        print("simulation complete for " + misrep_file_name)
    except subprocess.CalledProcessError as e:
        print("Error:", e)

def run_stacked_graph_visualizations(node_num, flow, topo, misrep_file_names, out_label):
    # type: (int, str, str, List[str], str) -> None

    # python stacked_tx_bytes_graph.py \
    # --node=2 \
    # --misrep_profiles=node_2_triple,node_2_zero,node_2_zero_p50,node_2_add \
    # --flow=mini_flow \
    # --topo=mini_topology \
    # --cc_algo=hp95ai50
    for py_script in [STACKED_GRAPH_PY_SCRIPT, STACKED_DIFF_GRAPH_PY_SCRIPT]:
        misrep_files_str = ','.join(misrep_file_names)
        command = [
            'python', py_script,
            '--node', str(node_num),
            '--flow', flow,
            '--topo', topo,
            '--cc_algo', HPCC_ALGO,
            '--misrep_profiles', misrep_files_str,
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
    parser.add_argument('--flow', dest='flow', action='store', default='mini_flow', help="the name of the flow file")
    parser.add_argument('--topo', dest='topo', action='store', default='mini_topology', help="the name of the topology file")
    parser.add_argument('--behavior', dest='behavior', action='store', required=True, help="misreporting behavior (TRIPLE, ADD, ZERO, etc.)")
    parser.add_argument('--step', dest='step', action='store', type=int, default=50, help="the probability step size")
    parser.add_argument('--out_label', dest='out_label', action='store', required=True, help="label for output PNG file")
    parser.add_argument('--should_skip_sims', dest='should_skip_sims', action='store_true', help="specify to skip sims and only generate graphs")
    args = parser.parse_args()

    node_num = args.node
    flow = args.flow
    topo = args.topo
    behavior_config = args.behavior
    assert behavior_config in VALID_BEHAVIORS
    behavior_label = behavior_config.lower()
    step = args.step
    out_label = args.out_label
    should_skip_sims = args.should_skip_sims
    
    misrep_files = []

    for p in range(step, 101, step):
        misrep_file_name = 'node_{node_num}_{behavior_label}_p{prob}'.format(
            node_num=node_num, behavior_label=behavior_label, prob=p
        )
        misrep_files.append(misrep_file_name)

        if not should_skip_sims:
            generate_misrep_file(
                file_name=misrep_file_name,
                node_num=node_num,
                behavior_config=behavior_config,
                prob=p,
            )
            run_hpcc_simulation(
                flow=flow,
                topo=topo,
                misrep_file_name=misrep_file_name,
            )

    run_stacked_graph_visualizations(
        node_num=node_num,
        flow=flow,
        topo=topo,
        misrep_file_names=misrep_files,
        out_label=out_label,
    )
