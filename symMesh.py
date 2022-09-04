from pymel import core as pm
from maya.api import OpenMaya
from maya import cmds
from functools import partial
from . import apiundo

__VERSION__ = "0.1"


pluginName = "symmetryTable.so"
try:
    if not pm.pluginInfo(pluginName, q=True, loaded=True):
        pm.loadPlugin(pluginName)
except RuntimeError:
    pm.displayError("Failed to load plugin")


class MiSymMesh():
    def __init__(self):

        self.mesh = None
        self.L_vertices = None
        self.R_vertices = None

        self.createUI()

    def createUI(self):
        windowName = "miSymMesh"

        if pm.window(windowName, q=True, exists=True):
            pm.deleteUI(windowName)

        self.win = pm.window(
            windowName,
            width=300,
            title="miSymMesh v{}".format(__VERSION__))

        pm.columnLayout(adj=True)

        # Tolerance
        pm.rowLayout(numberOfColumns=2, adj=True)
        pm.text("Global Tolerance: ")
        self.tolerance = pm.textField()
        self.tolerance.setText("0.001")
        pm.setParent('..')

        # Direction
        self.side = pm.radioButtonGrp(
            numberOfRadioButtons=2,
            label="Check: ",
            labelArray2=("Left", "Left"),
            columnAlign=(1, 'left'),
            # adjustableColumn=True,
            select=1)

        pm.separator()
        pm.button("Select middle edge", command=self.createTable)
        self.meshTextField = pm.textField(editable=False)
        pm.separator()

        pm.button("Check Symmetry", c=self.checkSymmetry, h=40)
        pm.separator()

        pm.text("Vertex Positions")
        pm.button("Mirror selected vertices", c=self.mirrorSelected)
        pm.button(
            "Flip selected vertices", c=partial(self.mirrorSelected, True))
        pm.separator()

        pm.text("Vertex Weights")
        pm.button(label="Blendshape weights", enable=False)
        pm.button(label="Skin cluster weights", enable=False)

        pm.text("Vertex Colors")
        pm.button(enable=False)

        pm.setParent('..')

    def show(self):
        self.win.show()

    def createTable(self, *args):
        vtxs = cmds.createSymmetryTable(half=True)

        # Extract only one side
        numVert = len(vtxs)
        self.left_vertices = {
            n: int(vtxs[n]) for n in range(numVert) if vtxs[n] != -1}
        self.right_vertices = {v: k for k, v in self.left_vertices.items()}

        sel = OpenMaya.MGlobal.getActiveSelectionList()
        dagPath = sel.getDagPath(0)

        self.meshTextField.setText(dagPath.getPath())
        self.mesh = OpenMaya.MFnMesh(dagPath)

    def checkSymmetry(self, *args):
        """ docstring """

        if self.mesh is None:
            cmds.warning("Mesh is not set")
            return

        points = self.mesh.getPoints()

        tol = float(self.tolerance.getText())

        pointsNotMatching = []
        verts = []

        side = self.side.getSelect()
        if side == 1:
            # left
            verts = self.left_vertices
        else:
            # right
            verts = self.right_vertices

        for k, v in verts.items():
            p1 = points[k]
            p2 = points[v]

            p2.x = -p2.x

            isEquivalent = p1.isEquivalent(p2, tol)

            if not isEquivalent:
                pointsNotMatching.append(k)

        name = self.meshTextField.getText()
        out = [name + ".vtx[{}]".format(i) for i in pointsNotMatching]
        pm.select(out, r=True)

    def mirrorSelected(self, flip=False, *args):
        # type:(bool) -> None
        """ Mirror or flip selected vertices """

        sel = OpenMaya.MGlobal.getActiveSelectionList()

        try:
            dag, components = sel.getComponent(0)
        except IndexError:
            cmds.warning("Nothing is selected")
            return

        points = self.mesh.getPoints()

        # Store hisotry for undo
        oldPoints = [(p.x, p.y, p.z) for p in points]

        itVerts = OpenMaya.MItMeshVertex(dag, components)
        while not itVerts.isDone():
            index = itVerts.index()

            try:
                oppIndex = self.left_vertices[index]
            except KeyError:
                oppIndex = self.right_vertices[index]

            # p = itVerts.position()
            currentPosition = itVerts.position()
            oppositePosition = points[oppIndex]

            newCurrentPosition = self.flip(currentPosition)
            newOppositePosition = self.flip(oppositePosition)

            points[oppIndex] = newCurrentPosition

            if flip is True:
                points[index] = newOppositePosition

            itVerts.next()

        self.doIt(points)

        apiundo.commit(undo=partial(self.undoIt, oldPoints), redo=self.doIt)

    def flip(self, point):
        # type:(OpenMaya.MPoint) -> OpenMaya.MPoint
        """ Flip point along X axis """

        x = point.x
        y = point.y
        z = point.z

        p = OpenMaya.MPoint((-x, y, z))
        return p

    def doIt(self, pointPositions):
        # type:(OpenMaya.MPointArray) -> None

        self.mesh.setPoints(pointPositions)
        self.mesh.updateSurface()

    def undoIt(self, points):
        # type:(list) -> None
        """ undo function """

        old_points = OpenMaya.MPointArray()
        for i in points:
            p = OpenMaya.MPoint(i)
            old_points.append(p)
        self.mesh.setPoints(old_points)
        self.mesh.updateSurface()


def main():
    w = MiSymMesh()
    w.show()


if __name__ == "__main__":
    w = MiSymMesh()
    w.show()
