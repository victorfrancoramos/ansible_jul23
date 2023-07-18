#! /usr/bin/env python3.7

"""
COMMAND: python qos_george2.py -c cluster1 -v Vol1 -vs VServer1 -q Qtree2 -un admin -sh 1000000 -fh 1000 -u admin -p Netapp1!

ONTAP 9.7 REST API Python Client Library Scripts
uthor: Vish Hulikal
This script performs the following:
        - Create a volume
        - List all volumes
        - Move a volume to another aggregate
        - Resize a volume to a new (bigger) size
        - Delete a volume

usage: python3.7 volume.py [-h] -c CLUSTER -v VOLUME_NAME -vs VSERVER_NAME -a AGGR_NAME -ma MOVE_AGGR_NAME
               -rs VOLUME_RESIZE -s VOLUME_SIZE [-u API_USER] [-p API_PASS]
The following arguments are required: -c/--cluster, -v/--volume_name, -vs/--vserver_name,
                -a/--aggr_name, -ma/--move_aggr_name, -rs/--volume_resize, -s/--volume_size
"""

import argparse
from getpass import getpass
import logging

from netapp_ontap import config, HostConnection, NetAppRestError
from netapp_ontap.resources import Volume, Qtree, QosPolicy, QuotaRule
from netapp_ontap.models import VolumeMovement

def make_volume(volume_name: str, vserver_name: str, aggr_name: str, volume_size: int) -> None:
    """Creates a new volume in a SVM"""

    data = {
        'name': volume_name,
        'svm': {'name': vserver_name},
        'aggregates': [{'name': aggr_name }],
        'size': volume_size
    }

    volume = Volume(**data)

    try:
        volume.post()
        print("Volume %s created successfully" % volume.name)
    except NetAppRestError as err:
        print("Error: Volume was not created: %s" % err)
    return

def list_volumes(vserver_name: str) -> None:
    """List Volumes in a SVM """

    print ("\nList of Volumes:-")
    try:
        for volume in Volume.get_collection(**{"svm.name": vserver_name}):
            volume.get()
            print (volume.name)
    except NetAppRestError as err:
        print("Error: Volume list was not created: %s" % err)
    return

def get_volume(volume_name: str) -> None:
    """Get the details of a volume"""

    volume = Volume.find(name=volume_name)

    try:
        volume.get()
        print (volume.name)
        print("Volume details for %s obtained successfully" % volume.name)
    except NetAppRestError as err:
        print("Error: Volume details not obtained: %s" % err)
    return

def delete_volume(volume_name: str) -> None:
    """Delete a volume in a SVM"""

    volume = Volume.find(name=volume_name)

    try:
        volume.delete()
        print("Volume %s deleted successfully" % volume.name)
    except NetAppRestError as err:
        print("Error: Volume was not deleted: %s" % err)
    return

def resize_volume(volume_name: str, volume_resize: int) -> None:
    """Resize a volume in a SVM"""

    volume = Volume.find(name=volume_name)
    volume.size = volume_resize

    try:
        volume.patch()
        print("Volume %s resized successfully" % volume.name)
    except NetAppRestError as err:
        print("Error: Volume was not resized: %s" % err)
    return

def move_volume(volume_name: str, move_aggr_name: str) -> None:
    """Move the volume to a new aggregate"""

    volume = Volume.find(name=volume_name)
    volume.movement = VolumeMovement(destination_aggregate={'name': move_aggr_name})

    try:
        volume.patch()
        print("Volume %s moved successfully" % volume.name)
    except NetAppRestError as err:
        print("Error: Volume was not moved: %s" % err)
    return

def create_qtree(vserver_name: str, volume_name: str, qtree_name: str) -> None:
    '''Creates a qtree'''

    data = {
        'name': qtree_name,
        'svm': {'name': vserver_name},
        'volume': {'name': volume_name}
    }

    qtree = Qtree(**data)

    try:
        qtree.post()
        print("Qtree %s created successfully" % qtree.name)
    except NetAppRestError as err:
        print("Error: Qtree was not created: %s" % err)
    return

def create_quotapolicyrule(vserver_name: str, volume_name: str, user_name:str, qtree_name: str, space_hard_limit: int, file_hard_limit: int)-> None:
    '''Create a quota policy rule'''

    data = {
        'svm':{'name':vserver_name},
        'volume': {'name':volume_name},
        'type': "tree",
        'users': {'name':user_name},
        'user_mapping': 'on',
        'qtree': {'name':qtree_name},
        'space': {'hard_limit':space_hard_limit, 'soft_limit':100},
        'files': {'hard_limit':file_hard_limit, 'soft_limit':100}
    }

    quota = QuotaRule(**data)

    try:
        quota.post()
        print("Quota applied")
    except NetAppRestError as err:
        print("Error: Quota was not applied: %s" % err)
    return

def set_qos(space_hard_limit: int, file_hard_limit: int, qtree_name: str)-> None:
    '''Modify QoS policy for qtree'''

    data = QosPolicy()
    data.fixed = {
        'space_hard_limit':space_hard_limit,
        'file_hard_limit':file_hard_limit
    }


def parse_args() -> argparse.Namespace:
    """Parse the command line arguments from the user"""

    parser = argparse.ArgumentParser(
        description="This script will create a new volume."
    )
    parser.add_argument(
        "-c", "--cluster", required=True, help="API server IP:port details"
    )
    parser.add_argument(
        "-v", "--volume_name", required=True, help="Volume to create or clone from"
    )
    parser.add_argument(
        "-vs", "--vserver_name", required=True, help="SVM to create the volume from"
    )
    parser.add_argument(
        "-q", "--qtree_name", required=True, help="qtree to create"
    )
    parser.add_argument(
        "-un", "--user_name", required=True, help="username to map to qtree"
    )
    parser.add_argument(
        "-sh", "--space_hard_limit", required=True, help="Space Hard Limit"
    )
    parser.add_argument(
        "-fh", "--file_hard_limit", required=True, help="File Hard Limit"
    )
    parser.add_argument("-u", "--api_user", default="admin", help="API Username")
    parser.add_argument("-p", "--api_pass", help="API Password")
    parsed_args = parser.parse_args()

    # collect the password without echo if not already provided
    if not parsed_args.api_pass:
        parsed_args.api_pass = getpass()

    return parsed_args


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)5s] [%(module)s:%(lineno)s] %(message)s",
    )
    args = parse_args()
    config.CONNECTION = HostConnection(
        args.cluster, username=args.api_user, password=args.api_pass, verify=False,
    )

    # Create a Qtree
    create_qtree(args.vserver_name, args.volume_name, args.qtree_name)
    print("Finished create_qtree code")

    # Apply Quota policy to the qtree created
    create_quotapolicyrule(args.vserver_name, args.volume_name, args.user_name, args.qtree_name, args.space_hard_limit, args.file_hard_limit)
    print("Finished create_quotapolicyrule code")

    # Create a Volume
    #make_volume(args.volume_name, args.vserver_name, args.aggr_name , args.volume_size)

    # List all volumes in the VServer
    #list_volumes(args.vserver_name)

    # Get the volume details
    #get_volume(args.volume_name)

    # Move the volume to a new aggregate
    #move_volume(args.volume_name, args.move_aggr_name)

    # Resize a volume
    #resize_volume(args.volume_name, args.volume_resize)

    # Delete a volume
    #delete_volume(args.volume_name)

'''
'''