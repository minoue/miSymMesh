# miSymMesh

**WORK IN PROGRESS**

Mirror/Symmetry checking tool inspired by abSymMesh.

https://user-images.githubusercontent.com/7100231/188402042-24fa5f19-3c1d-4e78-b38b-9927bed2216d.mp4

### Why
Maya has built-in topological symmetry tool but it only 'symmetrize' and 'flip' and doesn't provide a way to 'find' asym vertices.
Maya Artisan BrushTool also doesn't support topological symmetry for weight painting.

## Requirements

[symmetryTable](https://github.com/minoue/symmetryTable)

## Install
Copy miSymMesh folder to maya script directory.

## How to use
```python
from miSymMesh import symMesh
reload(symMesh)
symMesh.main()

```

## Credit

[apiundo](https://github.com/mottosso/apiundo) by mottosso
