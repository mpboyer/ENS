import sys

# Source - https://stackoverflow.com/a/48525873
# Posted by ababak
# Retrieved 2026-03-21, License - CC BY-SA 3.0

models = sys.argv
for m in models: 
    with open(m) as f:
        lines = f.readlines()

    vertices = len([line for line in lines if line.startswith('v ')])
    faces = len([line for line in lines if line.startswith('f ')])

    print(f"Model {m}\n\tVertices: {vertices}\n\tFaces: {faces}")
