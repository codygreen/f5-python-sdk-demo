import getopt
import os
import sys
import yaml
import json
import jsonschema
import requests
from jinja2 import Environment, FileSystemLoader
from f5sdk.bigip import ManagementClient
from f5sdk.bigip.extension import AS3Client, DOClient
from f5sdk.logger import Logger

LOGGER = Logger(__name__).get_logger()


def create_declaration(data, atc_type):
    """ 
    create automation toolchain declaration 
    """
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)

    # load the template
    template_type = "as3_template"  if atc_type == "as3" else "do_template"
    template = env.get_template(data[template_type]+'.j2') 

    # render the template
    output = template.render(data = data)

    # write the template to file
    LOGGER.info('writing declaration for {}'.format(data['hostname']))
    f = open('./files/{}.{}.json'.format(data['hostname'].split('.')[0], atc_type), 'w')
    f.write(output)
    f.close()
    return True

def update_config(data, atc_type):
    """
    Update AS3 or DO configuration
    """
    # create management client
    mgmt_client = ManagementClient(
        data['f5SdkHost'],
        user = data['f5SdkUsername'],
        password = os.getenv('bigipPassword')
    )

    # create extension client
    client = AS3Client(mgmt_client) if atc_type == "as3" else DOClient(mgmt_client)

    # Get installed package version info
    version_info = client.package.is_installed()
    LOGGER.info(version_info['installed'])
    LOGGER.info(version_info['installed_version'])
    LOGGER.info(version_info['latest_version'])

    # Install package
    if not version_info['installed']:
        client.package.install()

    # ensure service is available
    client.service.is_available()

    # configure service
    return client.service.create(config_file='./files/{}.{}.json'.format(data['hostname'].split('.')[0], atc_type))

if __name__ == '__main__':
    # Read BIG-IP data from YAML file or environment variables
    inputfile = ''
    bigip_data = {}
    try:
        # Ensure data file is provided
        if len(sys.argv) == 1:
            print("Please provide a yaml file containing variables.\nExample:\n")
            print("python3 bigip.py data.yml\n")
       # Set BIG-IP data from the YAML file
        else:
            inputfile = sys.argv[1]
            stream = open(inputfile, 'r')
            bigip_data = yaml.load(stream, Loader=yaml.BaseLoader)
            stream.close()
    except OSError as err:
        print(str(err))
        sys.exit(2)

    # Loop through the BIG-IPs
    for bigip in bigip_data['bigips']:
        LOGGER.info(create_declaration({ **bigip,  **bigip_data['dataCenters'][bigip['dataCenter']] },"do"))
        LOGGER.info(create_declaration(bigip, "as3"))
        LOGGER.info(update_config(bigip, "do"))
        LOGGER.info(update_config(bigip, "as3"))