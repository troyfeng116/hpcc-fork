import subprocess
import sys

from graph_helpers import get_file_suffix

def run_trace_reader(file_name, file_suffix):
    output_file = 'qlen_traces/qlen_{file_suffix}.txt'.format(file_suffix=file_suffix)

    command = './trace_reader {file_name}'.format(file_name=file_name)

    with open(output_file, 'w') as output:
        # redirect output to file
        process = subprocess.Popen(command, shell=True, stdout=output)
        process.communicate()

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage: python script.py <topo> <flow> <cc_algo>')
        sys.exit(1)

    topo = sys.argv[1]
    flow = sys.argv[2]
    cc_algo = sys.argv[3]

    file_suffix = get_file_suffix(topo=topo, flow=flow, cc_algo=cc_algo)
    file_name = '../simulation/mix/mix_{file_suffix}.tr'.format(file_suffix=file_suffix)

    run_trace_reader(file_name, file_suffix)
