import re
import json
import sys

def new_node(name=None):
    if type(name) == tuple:
        return {'type': name[0], 'subtype': name[1]}
    else:
        return {'type': name}

def get_content(content):
    match = re.search("\+?\((.*?) (.*?) (.*?) -\)", line)
    if match:
        return {
            'token': match.group(1),
            'lemma': match.group(2),
            'tag': match.group(3),
        }

def build_tree(names, depths):
    root = []
    last_seen_parent = {x: None for x in set(depths)}
    for name,depth in zip(names,depths):
        node = new_node(name)
        if name == 'leaf' or format == 'dep':
            node["content"] = contents.pop(0)
        last_seen_parent[depth] = node
        if depth > 0:
            last_seen_parent[depth-1].setdefault('children', []).append(node)
        else:
            root.append(node)
    return root
            
trees = []
nodes = []
contents = []
depths = []
format = sys.argv[1]

for line in sys.stdin:
    if line.strip() == ']':
        continue
    line = line.rstrip()
    m = re.match("(\s*)[A-Za-z+_0-9()]", line)
    if not m:
        tree = build_tree(nodes,depths)
        if tree:
            trees.append(tree)
        nodes = []
        depths = []
        continue
    if format == "parsed":
        if line.endswith("_["):
            ntype = line.strip()[:-2]
            node_name = ntype
        else:
            content = line
            leaf = get_content(content)
            if not leaf is None:
              contents.append(leaf)
              node_name = "leaf"
    elif format == "dep":
        ntype, nsubtype, content = line.strip().split("/")
        node_name = (ntype, nsubtype)
        contents.append(get_content(content))
    depth = len(m.group(1)) / 2
    nodes.append(node_name)
    depths.append(depth)
  
print json.dumps(trees)
