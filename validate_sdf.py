# Upload an sdf file and look for issues in each record. Create a new sdf file with processed data
# and any issues found.

import sys
import osdr_helper
from time import sleep
import json
import debugging

sdf_abs_path = sys.argv[1]
sdf_filename = sdf_abs_path[sdf_abs_path.rfind('/') + 1:]

token, oauth = osdr_helper.getToken()

# upload an sdf file and get BLOB ID
with open(sdf_abs_path, 'r') as f:
    result = oauth.post("{}/{}".format(osdr_helper.blob_host, osdr_helper.bucketId),
        files={'file': (sdf_filename, f.read(), 'multipart/form-data')}, verify=False).text
    blob_id = result[result.find('"') + 1 : result.rfind('"')]

# get file data through Nodes API, waiting until it's processed
processed = False
while not processed:
    sleep(2)
    children = oauth.get("{}/{}?&filter=".format(osdr_helper.host, "nodes",
        "Blob.Id eq '{}'".format(blob_id)), verify=False).text
    json_txt = json.loads(children)
    if (json_txt[0]['status'] == "Processed"): processed = True
    print("processed? ", processed)

# get records
new_sdf = 'processed_{}.sdf'.format(sdf_filename[:-4])
new_txt = ""
found_issues = False
for i, child in enumerate(children):
    #record = json.loads(api.api_entities_by_type_by_id_get("records", child['id'], _preload_content=False).read().decode('utf-8'))
    record = json.loads(oauth.get("{}/{}/{}/{}".format(
        osdr_helper.host, "entities", "records", child['_id']), verify=False).text)
    mol = blobs_api.api_blobs_by_bucket_by_id_get(osdr_token.bucketId, record['blob']['id'], _preload_content=False).read().decode('utf-8')
    new_sdf += mol
    for item in record["properties"]["fields"]:
        new_sdf += "> <{}>\n{}\n\n".format(item['name'], str(item['value']))
    for item in record["properties"]["chemicalProperties"]:
        new_sdf += "> <calc_{}>\n{}\n\n".format(item['name'], str(item['value']))
    if ('issues' in record['properties']):
        issues = record['properties']['issues']
        found_issues = True
        for j, issue in enumerate(issues):
            new_sdf += "> <ISSUE_{}>\n\n".format(j + 1)
            new_sdf += "{} ({}) {}\n".format(issue['severity'], issue['code'], issue['title'])
            print("Found an issue in record {}.".format(i + 1))
        new_sdf += "\n"
    new_sdf += "$$$$\n"
if not found_issues: print("No issues found.")
with open(new_sdf, 'w') as f:
    print("Creating {}.".format(new_sdf))
    f.write(new_txt)
