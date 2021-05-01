import sys
import boto3
import argparse
import pprint
from time import sleep

def remove_target_group(arn, elb_client):
    request_id = None
    response = None

    try:
        response = elb_client.delete_target_group(
            TargetGroupArn=arn,
        )
    except Exception as e:
        print(("Error removing target group " + arn + " (" + str(e) + ")"))
        sleep(0.5) # We could be throttled so we will delay here if so...

    if response:
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            request_id = response['ResponseMetadata']['RequestId']

    return request_id


def main(argv):
    plugin_results = dict()
    groups_removed_count = 0
    prefix = ""

    parser = argparse.ArgumentParser(description='Remove ALB target groups not assigned to load balancers')
    parser.add_argument('-f','--force', help='Perform the actual deletes (will run in dryrun mode by default)', action='store_true')
    parser.add_argument('-r','--region', help='AWS region to process', required=True)
    parser.add_argument('-p','--prefix', help='Only process target groups with this prefix in their name', required=False)

    args = parser.parse_args()

    if args.prefix:
        print(("Prefix specified - only evaluating target groups beginning with " + args.prefix))
        prefix = args.prefix

    if args.force:
        print("Force flag specified - doing deletion")

    session = boto3.session.Session(region_name=args.region)
    elb_client = session.client("elbv2")

    tg_paginator = elb_client.get_paginator('describe_target_groups')
    tg_iterator = tg_paginator.paginate()
    for response in tg_iterator:
        # pprint.pprint(response)

        for target_group in response['TargetGroups']:
            punt = False

            target_group_name = target_group['TargetGroupName']
            target_group_load_balancers = target_group['LoadBalancerArns']
            target_group_arn = target_group['TargetGroupArn']

            if prefix:
                if target_group_name.startswith(prefix):
                    if not target_group_load_balancers:
                        punt = True
            else:
                if not target_group_load_balancers:
                    punt = True

            if punt:
                sys.stdout.write("Target group " + target_group_name + " has no load balancers - removing....")

                if args.force:
                    request_id = remove_target_group(target_group_arn, elb_client)
                    if request_id:
                        print(("REMOVED (request id " + request_id + ")"))
                        groups_removed_count += 1
                    else:
                        print("ERROR")
                    sleep(0.3) # try not to over-run LB api throughput
                else:
                    print("DRYRUN,no deletion took place")

    print("Complete.  Removed " + str(groups_removed_count) + " orphaned target groups with prefix " + prefix + " in " + str(args.region))

if __name__ == "__main__":
   main(sys.argv[1:])
