# Upload a chemical file to OSDR - here, using mol. Also downloads processed file data and thumbnails
# and writes them to new files in the current directory.

import sys
import osdr_helper
from time import sleep
import json

mol_abs_path = sys.argv[1]
mol_filename = mol_abs_path[mol_abs_path.rfind('/') + 1:]

token, oauth = osdr_helper.getToken()

# post mol file and get blob ID
with open(mol_abs_path, 'r') as f:
    result = oauth.post("{}/{}".format(osdr_helper.blob_host, osdr_helper.bucketId),
        files={'file': (mol_filename, f.read(), 'multipart/form-data')}, verify=False).text
    blob_id = result[result.find('"') + 1 : result.rfind('"')]

# get file data through Nodes API, waiting until it's processed
processed = False
while not processed:
    sleep(2)
    result = oauth.get("{}/{}?&filter=".format(osdr_helper.host, "nodes",
        "Blob.Id eq '{}'".format(blob_id)), verify=False).text
    json_txt = json.loads(result)
    if (json_txt[0]['status'] == "Processed"): processed = True

# write file data and thumbnail
pretty = json.dumps(json_txt, indent=4, sort_keys=True)
with open('{}.txt'.format(json_txt[0]['name']), 'w') as f:
    f.write(pretty)
parent_image = oauth.get("{}/{}/{}".format(osdr_helper.blob_host,
    osdr_helper.bucketId, json_txt[0]['images'][0]['_id']), verify=False)
with open('{}.svg'.format(json_txt[0]['name']), 'w') as f:
    f.write(parent_image.text)
parent = json_txt[0]['_id']

# get records and write file data and thumbnails
child = json.loads(oauth.get("{}/{}/{}".format(osdr_helper.host, "nodes", parent), verify=False).text)

# mol files only contain one record, so iterating is unnecessary
with open('{}.txt'.format(child['name']), 'w') as f:
    pretty = json.dumps(child, indent=4, sort_keys=True)
    f.write(pretty)
image = oauth.get("{}/{}/{}".format(osdr_helper.blob_host, osdr_helper.bucketId,
    child['images'][0]['id']), verify=False)
with open('{}.svg'.format(child['name']), 'w') as f:
    f.write(image.text)

print("File uploaded. Thumbnails and processing data have been saved as "\
    "{0}.txt and {0}.svg.".format(mol_filename))