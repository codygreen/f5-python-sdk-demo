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


def create_do_declaration(data):
    """ 
    create DO declaration from environment variables
    """
    print(data)
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)

    # load the DO GTM template
    template = env.get_template(data['do_template']+'.j2')

    # render the template
    output = template.render(data = data)

    # ensure the JSON is valid
    # json.loads(output)
    # schema = json.loads(requests.get(
    #     "https://raw.githubusercontent.com/F5Networks/f5-declarative-onboarding/master/src/schema/latest/base.schema.json").text)
    # # jsonschema.IValidator(output, schema)
    # jsonschema.Draft3Validator(schema).validate(output)

    # write the template to file
    LOGGER.info('writing DO declaration for {}'.format(data['hostname']))
    f = open('./files/{}.do.json'.format(data['hostname'].split('.')[0]), 'w')
    f.write(output)
    f.close()
    return True

if __name__ == '__main__':
    # Read BIG-IP data from YAML file or environment variables
    inputfile = ''
    bigip_data = {}
    try:
        # Set BIG-IP data from environment variables
        if len(sys.argv) == 1:
            print("Please provide a yaml file containing variables.\nExample:\n")
            print("python3 bigip.py data.yml\n")
       # Set BIG-IP data from the YAML file
        else:
            inputfile = sys.argv[1]
            stream = open(inputfile, 'r')
            bigip_data = yaml.load(stream, Loader=yaml.BaseLoader)
            stream.close()
        # print(bigip_data)
    except OSError as err:
        print(str(err))
        sys.exit(2)

    # Loop through the BIG-IPs
    for bigip in bigip_data['bigips']:
        # print(type(bigip))
        # print(bigip)
        # print(bigip_data['dataCenters'][bigip['dataCenter']])
        LOGGER.info(create_do_declaration({ **bigip,  **bigip_data['dataCenters'][bigip['dataCenter']] }))