#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Print formatted Ceph usage per crush root. The user running
this tool, should have the Ceph permissions to run the command
'ceph osd df'.

Richard Arends (richard@unixguru.nl)
4 March 2018
"""

import json
import subprocess
import sys

def get_osd_df():
    """
    Run the command 'ceph osd df tree -f json'

    Args:
        - None

    Returns:
        - A dict with the output from the ceph command
    """
    try:
        output = subprocess.check_output(
            ['ceph', 'osd', 'df', 'tree', '-f', 'json'],
            universal_newlines=True)
        output = output.replace('-nan', '0')
        return json.loads(output)
    except subprocess.CalledProcessError as err:
        print('Could not get stats: {0}'.format(err))


def get_roots(osd_tree):
    """
    Get the crush roots

    Args:
        - osd_tree, the output from function get_osd_df

    Returns:
        - A dict with the 'root' names and their id
    """
    roots = {}
    for item in osd_tree['nodes']:
        if item['type'] == 'root':
            name = item['name']
            item_id = item['id']
            roots[name] = item_id

    return roots

def get_osds(root_id, osd_tree, osds):
    """
    Get the OSDs and their usage information for a specific crush root.

    This function call itself until it can't find anymore 'children' entries
    in 'osd_tree'.

    Args:
        - root_id, the id of a root
        - osd_tree, the output from function get_osd_df
        - osds, dict that contains previous found information from this function

    Returns:
        - A dict with the osd's and their usage information
    """
    for item in osd_tree['nodes']:
        if item['id'] == root_id:
            if item['type'] == 'osd':
                osds.update({
                    item['name']: {
                        'name': item['name'],
                        'id': item['id'],
                        'utilization': item['utilization'],
                        'kb': item['kb'],
                        'kb_avail': item['kb_avail'],
                        'kb_used': item['kb_used']
                    }
                })

            children = item.get('children', None)

            if children:
                for child_id in children:
                    get_osds(child_id, osd_tree, osds)

    return osds

def to_gb(value):
    """
    Convert a kilobyte value to gigabyte value

    Args:
        - A integer or float that contains a kilobyte value

    Returns:
        - A float (rounded to 2 decimals)
    """
    return round(value/1024/1024/1024, 2)

def to_tb(value):
    """
    Convert a kilobyte value to terrabyte value

    Args:
        - A integer or float that contains a kilobyte value

    Returns:
        - A float (rounded to 2 decimals)
    """
    return round(value/1024/1024/1024/1024, 2)

def main():
    """
    Main
    """
    osd_tree = get_osd_df()

    print('{:<20}{:>10}{:>10}{:>10}{:>20}{:>30}'.format(
        'Crush root',
        'OSDs',
        'GB',
        'GB used',
        'GB available',
        'Average utilization'))
    print('{:-^100s}'.format(''))


    for root, root_id in sorted(get_roots(osd_tree).items()):
        osds = get_osds(root_id, osd_tree, {})
        nr_osds = len(osds)

        utilization = 0
        kb = 0
        kb_used = 0
        kb_avail = 0

        for osd, osd_info in osds.items():
            utilization = utilization + osd_info['utilization']
            kb = kb + osd_info['kb']
            kb_used = kb_used + osd_info['kb_used']
            kb_avail = kb_avail + osd_info['kb_avail']

        if nr_osds == 0:
            average = 0
        else:
            average = utilization / nr_osds

        print('{:<20}{:>10}{:>10}{:>10}{:>20}{:>29}%'.format(
            root,
            nr_osds,
            to_gb(kb),
            to_gb(kb_used),
            to_gb(kb_avail),
            round(average, 2)))


if __name__ == "__main__":
    sys.exit(main())
