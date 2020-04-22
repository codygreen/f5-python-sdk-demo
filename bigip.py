import getopt
import os
import sys
import yaml
import json
import jsonschema
import requests
from jinja2 import Environment, FileSystemLoader
from f5sdk.bigip import ManagementClient
from f5sdk.bigip.extension import DOClient
from f5sdk.logger import Logger

LOGGER = Logger(__name__).get_logger()


def create_declaration(data, atc_type):
    """ 
    create automation toolchain declaration 
    """
    print(data)
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