import argparse
import os
import subprocess

from graph_helpers import get_file_suffix, get_mix_trace_filename

script_dir = os.path.dirname(os.path.abspath(__file__))

def run_trace_reader(file_name, file_suffix):
    # (str, str) -> None
    output_file = script_dir + '/qlen_traces/qlen_{file_suffix}.txt'.format(file_suffix=file_suffix)

    command = script_dir + '/../trace_reader {file_name}'.format(file_name=file_name)

    with open(output_file, 'w') as output:
        # redirect output to file
        process = subprocess.Popen(command, shell=True, stdout=output)
        process.communicate()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='generate packet traces using trace_reader')
    parser.add_argument('--flow', dest='flow', action='store', default='flow', help="the name of the flow file")
    parser.add_argument('--topo', dest='topo', action='store', default='fat', help="the name of the topology file")
    parser.add_argument('--misrep', dest='misrep', action='store', default='none', help="the name of the misreporting profile file")
    parser.add_argument('--cc_algo', dest='cc_algo', action='store', default='hp95ai50', help="CC algo with params")
    args = parser.parse_args()

    topo = args.topo
    flow = args.flow
    cc_algo = args.cc_algo
    misrep = args.misrep

    file_suffix = get_file_suffix(topo=topo, flow=flow, cc_algo=cc_algo, misrep=misrep)
    file_name = get_mix_trace_filename(trace_name='mix', file_suffix=file_suffix, file_type='tr')

    run_trace_reader(file_name, file_suffix)
