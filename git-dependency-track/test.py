import json
bom_file = '/alidata1/app/git-dependency-track/projects/git.zhonganinfo.com/seraph-metadata/target/bom.xml'
with open(bom_file, 'r') as f:

    data = {
        "project": 'seraph-metadata',
        "projectName": 'seraph-metadata',
        "projectVersion": 'master',
        "autoCreate": True,
        "bom": f.read()
    }
print(json.dumps(data))
