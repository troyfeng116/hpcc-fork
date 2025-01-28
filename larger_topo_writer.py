if __name__ == '__main__':
    with open("simulation/mix/larger_topology.txt", "w") as f:
        # total node #, switch node #, link #
        f.write('323 3 322\n')
        f.write('320 321 322\n')

        # 108 326 100Gbps 1000ns 0.000000
        for i in range(0, 160):
            f.write(' '.join([str(i), '320', '100Gbps', '1000ns', str(0)]))
            f.write('\n')
            f.write(' '.join(['322', str(i+160), '100Gbps', '1000ns', str(0)]))
            f.write('\n')
        f.write(' '.join(['320', '321', '100Gbps', '1000ns', str(0)]))
        f.write('\n')
        f.write(' '.join(['321', '322', '100Gbps', '1000ns', str(0)]))
        f.write('\n')