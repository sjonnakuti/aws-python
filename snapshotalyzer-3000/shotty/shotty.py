import boto3
import click
import botocore

session = boto3.Session(profile_name='shotty')
ec2 = session.resource('ec2')

@click.group()
def cli():
    """Shotty manages snapshots"""

@cli.group('volumes')
def volumes():
    """Commands for volumes"""

@cli.group('instances')
def instances():
    """Commands for instances"""

@cli.group('snapshots')
def snapshots():
    """Commands for snapshots"""

@snapshots.command('list')
@click.option('--project', default=None, help='Only snapshots for project arg Project:<name>)')
def list_snapshots(project):
    "List snapshots"
    instances = get_instances(project)
    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(', '.join((
                    s.id,
                    v.id,
                    i.id,
                    s.state,
                    s.progress,
                    s.start_time.strftime('%c')
                )))


@volumes.command('list')
@click.option('--project',default=None, help='Only volumes for project ag Project:<name>)')
def list_volumes(project):
    "List Volumes"
    instances = get_instances(project)
    for i in instances:
        for v in i.volumes.all():
            print(', '.join((
                v.id,
                i.id,
                v.state,
                str(v.size)+"GiB",
                v.encrypted and "Encrypted" or "Not Encrypted"
            )))

@instances.command('list')
@click.option('--project', default=None, help='Only instances for project (ag Project:<name>)')
def list_instances(project):
    "List Instances"
    instances=get_instances(project)
    for i in instances:
        tags = {t['Key']:t['Value'] for t in i.tags or []}
        print(','.join((
            i.id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'],
            i.public_dns_name,
            i.image_id,
            tags.get('Project','<no project>')
        )))
    return

def get_instances(project):
    instances = []
    if project:
        filters = [{'Name': 'tag:Project', 'Values': [project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()
    return instances

@instances.command('stop')
@click.option('--project',default=None,help='ONly instances for project')
def stop_instances(project):
    "Stop EC2 instances"
    instances= get_instances(project)
    for i in instances:
        print('Stopping {0}'.format(i.id))
        try:
            i.stop()
        except botocore.exceptions.ClientError as e:
            print("Could not stop {0}.".format(i.id) + str(e))


@instances.command('start')
@click.option('--project',default=None, help='Only instances for project')
def start_instances(project):
    "Start EC2 instances"
    instances = get_instances(project)
    for i in instances:
        print('Starting {0}'.format(i.id))
        try:
            i.start()
        except botocore.exceptions.ClientError as e:
            print("Could not start {0}.".format(i.id) + str(e))


@instances.command('snapshot',help='Create snapshot of all volumes')
@click.option('--project',default=None,help='Only instances for project( tag Project:<name>)')
def create_snapshot(project):
    "Create snapshots for EC2 instances"
    instances = get_instances(project)
    for i in instances:
        print("Stopping {0} ...".format(i.id))
        i.stop()
        i.wait_until_stopped()
        for v in i.volumes.all():
            print("Creating snapshot of {0}".format(v.id))
            v.create_snapshot(Description="Created by snapshot analyzer 3000")
            print('Starting {0}...'.format(i.id))
            i.start()
            i.wait_until_running()
    print('Jobs done!!!')
    return

if __name__== '__main__':
    cli()

