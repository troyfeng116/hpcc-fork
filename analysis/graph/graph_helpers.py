def get_file_suffix(topo, flow, cc_algo):
    # type: (str, str, str) -> str
    return '{topo}_{flow}_{cc_algo}'.format(
        topo=topo, flow=flow, cc_algo=cc_algo
    )
