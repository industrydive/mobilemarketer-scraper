# converts jsonlines in mm_data.jl to fixture similar to 
# https://github.com/industrydive/divesite/blob/dea147db2a308dd3e0ce0ddaa65f824f0e201578/fixtures/mobile_marketer_test_data_tech-1167.json
import json
output = []
with open('mm_data.jl') as f:
    for line in f:
        json_line = json.loads(line)
        item = {
            'model': 'legacyapps.MobileMarketerStory',
            'fields': {
                'site_id': 19,
                'legacy_url_primary_path': json_line['url'],
                'custom_byline':  ', '.join(json_line['authors']),
                'title': json_line['title'],
                'body': json_line['body'],
                'pub_date': json_line['pub_date'],
            }
        }
        output.append(item)
with open('mm_fixture.json', 'w') as outfile:
    json.dump(output, outfile, indent=2)
