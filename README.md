# aws-target-group-cleanup
Remove ALB target groups that are not assigned to load balancers

# Purpose
Clean up target groups that no longer have a load balancer assigned


# Prerequisites
* `pip install boto3`
* Either an AWS role (if running on EC2) or an access key/secret key

# Usage

Dry run mode:
```bash
python aws-target-group-cleanup.py -r us-west-2 -p myprefix
```

Removal mode:
```bash
python aws-target-group-cleanup.py -r us-west-2 -p myprefix -f
```

Where:

* -r is the region
* -p is an optional prefix (ie. only remove target groups starting with this)
* -f will turn on the removal (run in dryrun mode without this flag)
