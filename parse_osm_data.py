#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json
from process_network import parse_network_str,validate_uk_postcodes
from datetime import datetime
"""
Your task is to wrangle the data and transform the shape of the data
into the model we mentioned earlier. The output should be a list of dictionaries
that look like this:

{
"id": "2406124091",
"type: "node",
"visible":"true",
"created": {
          "version":"2",
          "changeset":"17206049",
          "timestamp":"2013-08-03T16:43:42Z",
          "user":"linuxUser16",
          "uid":"1219059"
        },
"pos": [41.9757030, -87.6921867],
"address": {
          "housenumber": "5157",
          "postcode": "60625",
          "street": "North Lincoln Ave"
        },
"amenity": "restaurant",
"cuisine": "mexican",
"name": "La Cabana De Don Luis",
"phone": "1 (773)-271-5176"
}

You have to complete the function 'shape_element'.
We have provided a function that will parse the map file, and call the function with the element
as an argument. You should return a dictionary, containing the shaped data for that element.
We have also provided a way to save the data in a file, so that you could use
mongoimport later on to import the shaped data into MongoDB.

Note that in this exercise we do not use the 'update street name' procedures
you worked on in the previous exercise. If you are using this code in your final
project, you are strongly encouraged to use the code from previous exercise to
update the street names before you save them to JSON.

In particular the following things should be done:
- you should process only 2 types of top level tags: "node" and "way"
- all attributes of "node" and "way" should be turned into regular key/value pairs, except:
    - attributes in the CREATED array should be added under a key "created"
    - attributes for latitude and longitude should be added to a "pos" array,
      for use in geospacial indexing. Make sure the values inside "pos" array are floats
      and not strings.
- if second level tag "k" value contains problematic characters, it should be ignored
- if second level tag "k" value starts with "addr:", it should be added to a dictionary "address"
- if second level tag "k" value does not start with "addr:", but contains ":", you can process it
  same as any other tag.
- if there is a second ":" that separates the type/direction of a street,
  the tag should be ignored, for example:

<tag k="addr:housenumber" v="5158"/>
<tag k="addr:street" v="North Lincoln Avenue"/>
<tag k="addr:street:name" v="Lincoln"/>
<tag k="addr:street:prefix" v="North"/>
<tag k="addr:street:type" v="Avenue"/>
<tag k="amenity" v="pharmacy"/>

  should be turned into:

{...
"address": {
    "housenumber": 5158,
    "street": "North Lincoln Avenue"
}
"amenity": "pharmacy",
...
}

- for "way" specifically:

  <nd ref="305896090"/>
  <nd ref="1719825889"/>

should be turned into
"node_refs": ["305896090", "1719825889"]
"""


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
addr_colon=re.compile(r'^addr:([a-z_]*$)')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]


def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way" :
        # YOUR CODE HERE
        node["type"]=element.tag

        for k in element.attrib:
            if k in CREATED:
                if "created" not in node:
                    node["created"]={}
                #if k=="timestamp":
                #    dt_obj=datetime.strptime(element.attrib[k],"%Y-%m-%dT%H:%M:%SZ")
                #    node["created"].update({"time_s":{}})
                #    node["created"]["time_s"].update({"year":dt_obj.year,"month":dt_obj.month,"day":dt_obj.day})

                node["created"].update({k:element.attrib[k]})
            else:

                if k not in node:
                    node[k]=element.attrib[k]
                else:
                    node[k].append(element.attrib[k])

        for tag in element.iter("tag"):
            atb=tag.attrib["k"]
            if problemchars.search(atb):
                continue
            else:
                m=addr_colon.match(atb)
                if m:
                    if "address" not in node.keys():
                        node["address"]={m.group(1):tag.attrib["v"]}
                        if m.group(1)=="postcode":
                            area_code,unit_code=validate_uk_postcodes(tag.attrib["v"])
                            node["address"].update({"postcode_area":area_code,
                                                    "postcode_unit":unit_code})

                    else:
                        node["address"].update({m.group(1):tag.attrib["v"]})
                else:
                    atrb=tag.attrib["k"]
                    atrb_v=tag.attrib["v"]

                    # Deal with the conflicts of tag names
                    if atrb=="address" or atrb=="type":
                        atrb=atrb+"_tag"
                    elif atrb=="network":
                        atrb_v=parse_network_str(atrb_v)

                    node[atrb]=atrb_v

        for tag in element.iter("nd"):
            if "node_refs" not in node:
                node["node_refs"]=[]
            node["node_refs"].append(tag.attrib["ref"])

        # Merge 'lat' and 'lon'

        if ('lat' in node) and ('lon' in node):
            node['pos']=[float(node['lat']),float(node['lon'])]
            del node['lat']
            del node['lon']


        return node
    else:
        return None



def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w",encoding="utf-8") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2,ensure_ascii=False))
                    fo.write("\n")
                else:
                    outputStr=json.dumps(el,ensure_ascii=True)
                    outputStr.replace("\n","")
                    fo.write(outputStr)
                    fo.write("\n")
    return data

def test():
    # NOTE: if you are running this code on your computer, with a larger dataset,
    # call the process_map procedure with pretty=False. The pretty=True option adds
    # additional spaces to the output, making it significantly larger.
    data = process_map('./L6 problems/example_5.osm', True)
    #pprint.pprint(data)

    correct_first_elem = {
        "id": "261114295",
        "visible": "true",
        "type": "node",
        "pos": [41.9730791, -87.6866303],
        "created": {
            "changeset": "11129782",
            "user": "bbmiller",
            "version": "7",
            "uid": "451048",
            "timestamp": "2012-03-28T18:31:23Z"
        }
    }
    print(data[0])
    assert data[0] == correct_first_elem
    assert data[-1]["address"] == {
        "street": "West Lexington St.",
        "housenumber": "1412"
    }
    print(data[-1])
    assert data[-1]["node_refs"] == [ "2199822281", "2199822390",  "2199822392", "2199822369",
                                      "2199822370", "2199822284", "2199822281"]

if __name__ == "__main__":

    test()
    data=process_map("./osm data/london_england.osm",True)

