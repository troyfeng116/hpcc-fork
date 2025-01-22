# HPCC simulation
[Project page of HPCC](https://hpcc-group.github.io/) includes latest news of HPCC and extensive evaluation results using this simulator.

This is the simulator for [HPCC: High Precision Congestion Control (SIGCOMM' 2019)](https://rmiao.github.io/publications/hpcc-li.pdf). It also includes the implementation of DCQCN, TIMELY, DCTCP, PFC, ECN and Broadcom shared buffer switch.

We have update this simulator to support HPCC-PINT, which reduces the INT header overhead to 1 to 2 byte. This improves the long flow completion time. See [PINT: Probabilistic In-band Network Telemetry (SIGCOMM' 2020)](https://liyuliang001.github.io/publications/pint.pdf).

## NS-3 simulation
The ns-3 simulation is under `simulation/`. Refer to the README.md under it for more details.

## Traffic generator
The traffic generator is under `traffic_gen/`. Refer to the README.md under it for more details.

## Analysis
We provide a few analysis scripts under `analysis/` to view the packet-level events, and analyzing the fct in the same way as [HPCC](https://liyuliang001.github.io/publications/hpcc.pdf) Figure 11.
Refer to the README.md under it for more details.

## Questions
For technical questions, please create an issue in this repo, so other people can benefit from your questions. 
You may also check the issue list first to see if people have already asked the questions you have :)

For other questions, please contact Rui Miao (miao.rui@alibaba-inc.com).

## Misreporting experiments (new contributions)

Experiments are defined by `(topo, flow, cc_algo, misrep_profile)` tuples.

### Run experiment
To run an experiment with a misreporting profile:
```bash
python run.py --cc hp --trace mini_flow --bw 100 --topo mini_topology --hpai 50 --enable_tr 1 --utgt 95 --misrep node_2_zero
```
The misreporting profiles are specified in `simulation/mix/node_2_zero`, given as `(node_id, misreporting_behavior)` pairs. See `simulation/scratch/third.cc` (in particular `reporting_fn_map`) to view/modify/add supported misreporting behaviors.

### [if needed] Run trace readers
Experiments generate some trace files (ex. queue lengths) that must be parsed first. We wrote a Python utility to run `trace_reader` in `analysis:
```bash
$ python run_trace_reader.py --flow=mini_flow --topo=mini_topology --cc_algo=hp95ai50 --misrep=node_2_zero
```

### Run graph scripts
Finally, scripts in `analysis/graph` read trace files per experiment and plot results.
```bash
$ python qlen_graph.py --node=2 --flow=mini_flow --topo=mini_topology --bw=100 --cc_algo=hp95ai50 --misrep=node_2_zero
```

Source code for generating more complex graphs (stacked graphs, surface curves, etc.) can all be found in `analysis/graph`.
