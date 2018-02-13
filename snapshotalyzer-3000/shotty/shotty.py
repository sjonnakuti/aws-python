import boto3
import click

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
        i.stop()


@instances.command('start')
@click.option('--project',default=None, help='Only instances for project')
def start_instances(project):
    "Start EC2 instances"
    instances = get_instances(project)
    for i in instances:
        print('Starting {0}'.format(i.id))
        i.start()

if __name__== '__main__':
    cli()

