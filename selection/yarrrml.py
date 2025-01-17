import yaml
import re
import os
import selection.resourcesFromSparql as rscSparql
import json

def getCleanYarrrml (mappingPath="./tmp/annotations/mapping.yaml"):
    """
    Generate RML mapping without functions:
        - yarrrml mapping
    return dict with the functions (mapping and reference where to apply them) and rml mapping in disk
    """
    functions = {}
    data = yaml.load(open(mappingPath), Loader=yaml.FullLoader)
    for tm in data["mappings"]:
        i = 0
        source = data["mappings"][tm]["sources"][0][0]
        for pom in data["mappings"][tm]["po"]:
            if 'p' in pom:
                predicate = re.sub("^.*:", "", pom["p"])
                object = pom["o"]
                #if it is a basic function
                if 'function' in object[0]:
                    if tm not in functions.keys():
                        functions[tm] = []
                    functions[tm].append({"source": source, "params": object[0], "column": predicate})
                    data["mappings"][tm]["po"][i] = [pom["p"], "$("+predicate+")"]
                #if it is a join
                else:
                    t = 0
                    for jc in object:
                        parameters = jc["condition"]["parameters"]
                        j = 0
                        for param in parameters:
                            if 'parameter' in param:
                                if tm not in functions.keys():
                                    functions[tm] = []
                                if param["parameter"] == 'str1':
                                    functions[tm].append({"source": source, "params": param, "column": predicate})
                                    data["mappings"][tm]["po"][i]["o"][t]["condition"]["parameters"][j] = [
                                        param["parameter"], "$(" + predicate + "_child)"]
                                else:
                                    parent_source = data["mappings"][jc["mapping"]]["sources"][0][0]
                                    functions[tm].append({"source": parent_source, "params": param, "column": predicate})
                                    data["mappings"][tm]["po"][i]["o"][t]["condition"]["parameters"][j] = [
                                        param["parameter"], "$(" + predicate + "_parent)"]
                            j += 1
                        t += 1
            i += 1
    return functions, data


# change source by table in the mapping for translating to R2RML
def fromSourceToTables(mapping):

    for tm in mapping["mappings"]:
        source = mapping["mappings"][tm]["sources"][0][0].split("/")[-1].replace(".csv~csv","")
        mapping["mappings"][tm]["sources"] = [{"table": source.upper()}]
    mapping = poToLowerCase(mapping)
    f = open("./tmp/annotations/mapping.yaml", "w+")
    dumpedYaml = sanitizeYaml(mapping)
    f.write(dumpedYaml)
    f.close()
    os.system("bash ./bash/yarrrml-parser.sh")
def sanitizeYaml(mapping):
    for tm in mapping["mappings"]:
        for i,po in enumerate(mapping["mappings"][tm]["po"]):
            if(type(po) is list):
                if(' ' in po[1] or '[' in po[1] or ']' in po[1] or ':' in po[1]):
                    mapping["mappings"][tm]["po"][i][1] = '"' + po[1] + '"'
    dumpedYaml =  str(yaml.dump(mapping, default_flow_style=None)).replace("'\"", '"').replace("\"'",'"').replace('\'', '')
    return dumpedYaml
def poToLowerCase(mapping):
    cols = rscSparql.getColPatterns(mapping)
    for col in cols:
        mapping = str(mapping).replace(col, col.lower())
#    print("********MAPPING*********** YARRML.py")
    mapping = mapping.replace("'", '"')
    return json.loads(mapping)

