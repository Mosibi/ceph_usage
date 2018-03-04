# ceph_usage

Get usage for a Ceph cluster per crush root.

This script uses the output from 'ceph osd df tree' and returns a formatted list with
usage information about a Ceph crush root. Although the 'ceph osd df tree' command gives
a lot of information, i missed a quick overview where i can see the utilization.

## Usage 
```sh
./ceph_usage.py 
Crush root                OSDs        GB   GB used        GB available           Average utilization
----------------------------------------------------------------------------------------------------
default                      0       0.0       0.0                 0.0                            0%
hdd                       1000   5000.00   2000.00             3000.00                        53.12%
ssd                        500   3000.00    999.99             2000.01                        18.55%
very_very_fast             100   1000.00    100.00              900.00                        10.25%
``` 

The output shown above is totally made up, this is just to give you a idea of what to expect from this
script.