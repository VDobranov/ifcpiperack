# Импортируем библиотеки:
# для работы со временем: time
# для работы с IFC: ifcopenshell
# для математических операций: math

import time
import ifcopenshell as ios
# import math

import bpy

# Создаём пустой файл IFC

ifc = ios.file()

# Мировые константы

pO = 0., 0., 0.
dX = 1., 0., 0.
dY = 0., 1., 0.
dZ = 0., 0., 1.

globalAxisX = ifc.createIfcDirection(dX)
globalAxisY = ifc.createIfcDirection(dY)
globalAxisZ = ifc.createIfcDirection(dZ)
originPoint = ifc.createIfcCartesianPoint(pO)

worldCoordinateSystem = ifc.createIfcAxis2Placement3D(originPoint, globalAxisZ, globalAxisX)

# Константы эстакады

PRWidth = 6000.0
PRSpans = [12000.0,21000.0,6000.0,9000.0,6000.0,9000.0,6000.0,9000.0]
PRLength = sum(PRSpans)
PRLevels = {
    'Ground Level': 0.,
    'Tier 1': 6400.,
    'Tier 2': 10000.
}
PRSrps = [[1,3],[4,9]]

PRIfcOrigin = originPoint
PRIfcEnd    = ifc.createIfcCartesianPoint([
    originPoint.Coordinates[0] + PRLength,
    originPoint.Coordinates[1],
    originPoint.Coordinates[2]
])



# Функции

# Creates an IfcAxis2Placement3D from Location, Axis and RefDirection

def create_ifcaxis2placement(
    ifcfile     =   ifc,
    point       =   originPoint,
    dir1        =   globalAxisZ,
    dir2        =   globalAxisX
):
    if point == originPoint and dir1 == globalAxisZ and dir2 == globalAxisX:
        axis2placement = worldCoordinateSystem
    else:
        axis2placement = ifcfile.createIfcAxis2Placement3D(point, dir1, dir2)
    return axis2placement

# Creates an IfcLocalPlacement from Location, Axis, RefDirection and relative placement

def create_ifclocalplacement(
    ifcfile     =   ifc,
    point       =   originPoint,
    dir1        =   globalAxisZ,
    dir2        =   globalAxisX,
    relativeTo =   None
):
    if point == originPoint and dir1 == globalAxisZ and dir2 == globalAxisX:
        axis2placement = worldCoordinateSystem
    else:
        axis2placement = ifcfile.createIfcAxis2Placement3D(point, dir1, dir2)
    ifclocalplacement2 = ifcfile.createIfcLocalPlacement(
        relativeTo, axis2placement)
    return ifclocalplacement2


def find_axes_intersection(a1, a2):
    p11 = a1.AxisCurve.Points[0]
    p12 = a1.AxisCurve.Points[1]
    p21 = a2.AxisCurve.Points[0]
    p22 = a2.AxisCurve.Points[1]
    z0 = p11.Coordinates[2]
    x11 = p11.Coordinates[0]
    x12 = p12.Coordinates[0]
    y11 = p11.Coordinates[1]
    y12 = p12.Coordinates[1]
    x21 = p21.Coordinates[0]
    x22 = p22.Coordinates[0]
    y21 = p21.Coordinates[1]
    y22 = p22.Coordinates[1]
    A1 = y12 - y11
    B1 = x12 - x11
    C1 = y11 * (x12 - x11) - x11 * (y12 - y11)
    A2 = y22 - y21
    B2 = x22 - x21
    C2 = y21 * (x22 - x21) - x21 * (y22 - y21)
    x0 = (B1 * C2 - B2 * C1) / (A1 * B2 - A2 * B1)
    y0 = (C1 * A2 - C2 * A1) / (A1 * B2 - A2 * B1)
    return [x0, y0, z0]


def create_customgridplacement(axis1, axis2, dir1=globalAxisZ, dir2=globalAxisX):
    point = ifc.createIfcCartesianPoint(find_axes_intersection(axis1, axis2))
    axis2Placement = ifc.createIfcAxis2Placement3D(point, dir1, dir2)
    localPlacement = ifc.createIfcLocalPlacement(None, axis2Placement)
    return localPlacement

# Юридическая информация

engineer = ifc.createIfcActorRole('ENGINEER')
contractor = ifc.createIfcActorRole('CONTRACTOR')
owner = ifc.createIfcActorRole('OWNER')
projectManager = ifc.createIfcActorRole('PROJECTMANAGER')

myself = ifc.createIfcPerson()
myself.FamilyName = 'Dobranov'
myself.GivenName = 'Vyacheslav'
myself.Roles = [projectManager, owner, engineer]

myOrganization = ifc.createIfcOrganization()
myOrganization.Name = 'Klockwerk Kat'
myOrganization.Roles = [contractor]

meInMyOrg = ifc.createIfcPersonAndOrganization()
meInMyOrg.ThePerson = myself
meInMyOrg.TheOrganization = myOrganization
meInMyOrg.Roles = [owner]

myApp = ifc.createIfcApplication()
myApp.ApplicationDeveloper = myOrganization
myApp.Version = '0.0.1'
myApp.ApplicationFullName = 'KK-IFC'

# creationDate = ifc.createIfcTimeStamp(int(time.time()))
ownerHistory = ifc.createIfcOwnerHistory()
ownerHistory.OwningUser = meInMyOrg
ownerHistory.OwningApplication = myApp
ownerHistory.CreationDate = int(time.time())

# Единицы измерения

lengthUnit = ifc.createIfcSIUnit()
lengthUnit.UnitType = "LENGTHUNIT"
lengthUnit.Prefix = "MILLI"
lengthUnit.Name = "METRE"

areaUnit = ifc.createIfcSIUnit()
areaUnit.UnitType = "AREAUNIT"
areaUnit.Name = "SQUARE_METRE"

volumeUnit = ifc.createIfcSIUnit()
volumeUnit.UnitType = "VOLUMEUNIT"
volumeUnit.Name = "CUBIC_METRE"

planeAngleUnit = ifc.createIfcSIUnit()
planeAngleUnit.UnitType = "PLANEANGLEUNIT"
planeAngleUnit.Name = "RADIAN"

myUnits = ifc.createIfcUnitAssignment(
    [lengthUnit, areaUnit, volumeUnit, planeAngleUnit])

# Общая геометрия

# globalAxisX = ifc.createIfcDirection(dX)
# globalAxisY = ifc.createIfcDirection(dY)
# globalAxisZ = ifc.createIfcDirection(dZ)
# originPoint = ifc.createIfcCartesianPoint(pO)

# worldCoordinateSystem = create_ifcaxis2placement(ifc)
# worldCoordinateSystem = ifc.createIfcAxis2Placement3D()
# worldCoordinateSystem.Location = originPoint
# worldCoordinateSystem.Axis = globalAxisZ
# worldCoordinateSystem.RefDirection = globalAxisX

modelContext = ifc.createIfcGeometricRepresentationContext()
modelContext.ContextType = 'Model'
modelContext.CoordinateSpaceDimension = 3
modelContext.Precision = 0.001
modelContext.WorldCoordinateSystem = worldCoordinateSystem
# modelContext.TrueNorth = globalAxisY

footprintContext = ifc.createIfcGeometricRepresentationSubContext()
footprintContext.ContextIdentifier = 'Footprint'
footprintContext.ContextType = 'Model'
footprintContext.ParentContext = modelContext
footprintContext.TargetView = 'MODEL_VIEW'

bodyContext = ifc.createIfcGeometricRepresentationSubContext()
bodyContext.ContextIdentifier = 'Body'
bodyContext.ContextType = 'Model'
bodyContext.ParentContext = modelContext
bodyContext.TargetView = 'MODEL_VIEW'

planContext = ifc.createIfcGeometricRepresentationContext()
planContext.ContextType = 'Plan'
planContext.CoordinateSpaceDimension = 2
planContext.Precision = 0.001
planContext.WorldCoordinateSystem = worldCoordinateSystem

# Создание проекта

project = ifc.createIfcProject(ios.guid.new())
project.OwnerHistory = ownerHistory
project.Name = 'Piperack test project'
project.Description = 'Creation of an IFC-file from the scratch with the ifcopenshell library.'
project.UnitsInContext = myUnits
project.RepresentationContexts = [modelContext, planContext]

# Создание площадки

sitePlacement = create_ifclocalplacement()

site = ifc.createIfcSite(ios.guid.new())
site.Name = "Construction Site"
site.ObjectPlacement = sitePlacement

siteContainer = ifc.createIfcRelAggregates()
siteContainer.RelatingObject = project
siteContainer.RelatedObjects = [site]

# Создание сетки осей

PRMainAxes = []
PRMainAxesPolylines = []

for a in range(3):
    p1 = ifc.createIfcCartesianPoint([
        originPoint.Coordinates[0],
        PRWidth/2*(a-1),
        0.
    ])
    p2 = ifc.createIfcCartesianPoint([
        originPoint.Coordinates[0] + PRLength,
        PRWidth/2*(a-1),
        0.
    ])
    axis = ifc.createIfcGridAxis()
    if p1.Coordinates[1] < 0: axis.AxisTag = "A"
    elif p1.Coordinates[1] == 0:
        axis.AxisTag = "Piperack Axis"
        PRMainAxis = axis
    else: axis.AxisTag = "B"
    axis.AxisCurve = ifc.createIfcPolyline([p1, p2])
    PRMainAxes.append(axis)
    PRMainAxesPolylines.append(axis.AxisCurve)

#PRMainAxis = ifc.createIfcGridAxis()
#PRMainAxis.AxisTag = "Piperack Axis"
#PRMainAxis.AxisCurve = ifc.createIfcPolyline([PRIfcOrigin, PRIfcEnd])
#PRMainAxis.SameSense = True

PRCrossAxes = []
PRCrossAxesPolylines = []
for a in range(len(PRSpans)+1):
    p1 = ifc.createIfcCartesianPoint([
        float(sum(PRSpans[:a])),
        -PRWidth/2,
        0.
    ])
    p2 = ifc.createIfcCartesianPoint([
        float(sum(PRSpans[:a])),
        PRWidth/2,
        0.
    ])
    axis = ifc.createIfcGridAxis()
    axis.AxisTag = f"{a+1}"
    axis.AxisCurve = ifc.createIfcPolyline([p1, p2])
    PRCrossAxes.append(axis)
    PRCrossAxesPolylines.append(axis.AxisCurve)

PRCrossAxis=PRCrossAxes[0]

PRMainGridPlacement = create_ifclocalplacement(relativeTo=sitePlacement)

PRMainGridGeomCurveSet = ifc.createIfcGeometricCurveSet(PRMainAxesPolylines + PRCrossAxesPolylines)

PRMainGridShapeRepresent = ifc.createIfcShapeRepresentation()
PRMainGridShapeRepresent.ContextOfItems = footprintContext
PRMainGridShapeRepresent.RepresentationIdentifier = 'FootPrint'
PRMainGridShapeRepresent.RepresentationType = 'GeometricCurveSet'
PRMainGridShapeRepresent.Items = [PRMainGridGeomCurveSet]

PRMainGridProductDefShape = ifc.createIfcProductDefinitionShape()
PRMainGridProductDefShape.Representations = [PRMainGridShapeRepresent]

PRMainGrid = ifc.createIfcGrid(ios.guid.new(),ownerHistory)
PRMainGrid.Name = 'Piperack Grid'
PRMainGrid.UAxes = PRMainAxes
PRMainGrid.VAxes = PRCrossAxes
PRMainGrid.ObjectPlacement = PRMainGridPlacement
PRMainGrid.Representation = PRMainGridProductDefShape

PRMainGridSpatialContainer = ifc.createIfcRelContainedInSpatialStructure()
PRMainGridSpatialContainer.Name = 'Piperack Main Grid Container'
PRMainGridSpatialContainer.RelatingStructure = site
PRMainGridSpatialContainer.RelatedElements = [PRMainGrid]

# Создание эстакады

piperackPlacement = create_ifclocalplacement(relativeTo=sitePlacement)

piperack = ifc.createIfcBuilding(ios.guid.new())
piperack.Name = "Piperack"
piperack.CompositionType = 'COMPLEX'
piperack.ObjectPlacement = piperackPlacement

piperackContainer = ifc.createIfcRelAggregates()
piperackContainer.Name = "Piperack Container"
piperackContainer.RelatingObject = site
piperackContainer.RelatedObjects = [piperack]

# Создание участков эстакады

#srp1Placement = create_ifclocalplacement(relativeTo=piperackPlacement)
#srp2Placement = create_ifclocalplacement(relativeTo=piperackPlacement)
#srp2Placement = ifc.createIfcGridPlacement()
#srp2Placement.PlacementLocation = ifc.createIfcVirtualGridIntersection(
# 	[PRMainAxis, PRCrossAxes[4]])

srps = []
srpsPlacement = []
srpsAxes = {}

def SrpCreation(_axesNums, _gridPlacement=False):
    _crossAxis = ''
    for ax in ifc.by_type('IfcGridAxis'):
        if ax.AxisTag == str(_axesNums[0]):
            _crossAxis = ax
            break
    if _gridPlacement:
        _srpPlacement = create_customgridplacement(
            PRMainAxis, _crossAxis)
    else:
        _globalOrigin = piperackPlacement.RelativePlacement.Location
        _origin = ifc.createIfcCartesianPoint([
            _globalOrigin.Coordinates[0] + _crossAxis.AxisCurve.Points[0].Coordinates[0],
            _globalOrigin.Coordinates[1],
            _globalOrigin.Coordinates[2]
        ])
        _axis2placement = ifc.createIfcAxis2Placement3D(_origin, globalAxisZ, globalAxisX)
        _srpPlacement = ifc.createIfcLocalPlacement(piperackPlacement, _axis2placement)
    _srp = ifc.createIfcBuilding(ios.guid.new(), ownerHistory)
    _srp.Name = 'Tag ' + str(PRSrps.index(_axesNums) + 1)
    _srp.CompositionType = 'COMPLEX'
    _srp.ObjectPlacement = _srpPlacement
    srps.append(_srp)
    srpsPlacement.append(_srpPlacement)
    _x = _axesNums[0]
    srpsAxes[_srp.Name] = []
    while _x <= _axesNums[-1]:
        srpsAxes[_srp.Name].append(PRCrossAxes[_x-1])
        _x += 1
    # _srp.Description = str(srpsAxes[_srp.Name])


for _axes in PRSrps:
    SrpCreation(_axes, True)

#srp1 = ifc.createIfcBuilding(ios.guid.new())
#srp1.Name = "Участок 1"
#srp1.CompositionType = 'PARTIAL'
#srp1.ObjectPlacement = srp1Placement

#srp2 = ifc.createIfcBuilding(ios.guid.new())
#srp2.Name = "Участок 2"
#srp2.CompositionType = 'PARTIAL'
#srp2.ObjectPlacement = srp2Placement

srpsContainer = ifc.createIfcRelAggregates()
srpsContainer.Name = "SRPs Container"
srpsContainer.RelatingObject = piperack
srpsContainer.RelatedObjects = srps

# Создание ярусов эстакады

def TierCreation (_name, _srp, _elevation):
    _tier = ifc.createIfcBuildingStorey(ios.guid.new(), ownerHistory)
    _tier.Name = _srp.Name + ". " + _name
    # _tier.Name = _name
    _tier.Elevation = _elevation
    _tierContainer = ifc.createIfcRelAggregates()
#	_tierContainer.Name = f"{_elevation} Tier Container"
    _tierContainer.RelatingObject = _srp
    _tierContainer.RelatedObjects = [_tier]

for _srp in srps:
    for k, v in PRLevels.items():
        TierCreation(k, _srp, v)

# Создание рам

frames = []

for _srp in srps:
    _frames = []
    for _axis in srpsAxes[_srp.Name]:
        _frame = ifc.createIfcBuilding(ios.guid.new(), ownerHistory)
        _frame.Name = 'Frame on Axis ' + _axis.AxisTag
        _frame.ObjectPlacement = create_customgridplacement(PRMainAxis, _axis)
        _frames.append(_frame)
        frames.append(_frame)
    _frameContainer = ifc.createIfcRelAggregates()
    _frameContainer.RelatingObject = _srp
    _frameContainer.RelatedObjects = _frames
        

# Создание колонн


def ColumnCreation(
    _XDim=600.,
    _YDim=600.,
    _Depth=6000.,
    _Name='Precast Column',
    _Tag='PCC',
    _RelatingStructure=site,
    _Side=1
):
    _columnProfile = ifc.createIfcRectangleProfileDef()
    _columnProfile.ProfileType = 'AREA'
    _columnProfile.ProfileName = f'{_XDim}x{_YDim}'
    _columnProfile.XDim, _columnProfile.YDim = _XDim, _YDim

    _columnEAS = ifc.createIfcExtrudedAreaSolid()
    _columnEAS.SweptArea = _columnProfile
    _columnEAS.ExtrudedDirection = globalAxisZ
    _columnEAS.Depth = _Depth

    _columnSP = ifc.createIfcShapeRepresentation()
    _columnSP.ContextOfItems = bodyContext
    _columnSP.RepresentationIdentifier = 'Body'
    _columnSP.RepresentationType = 'SweptSolid'
    _columnSP.Items = [_columnEAS]

    _columnPDS = ifc.createIfcProductDefinitionShape()
    _columnPDS.Representations = [_columnSP]

    _columnPoint = ifc.createIfcCartesianPoint(
        [0., _Side*PRWidth/2, PRLevels['Ground Level']])
    _columnPlacement = create_ifclocalplacement(point=_columnPoint,relativeTo=_RelatingStructure.ObjectPlacement)

    _column = ifc.createIfcColumn(ios.guid.new(), ownerHistory)
    _column.Name = _Name
    _column.Tag = _Tag
    _column.PredefinedType = 'COLUMN'
    _column.ObjectPlacement = _columnPlacement
    _column.Representation = _columnPDS

    return _column

for _frame in frames:
    _Tag = 'PCC' + str(frames.index(_frame) + 1)
    _Depth = PRLevels['Tier 2']-PRLevels['Ground Level'],
    # _Depth, = _Depth
    _Depth = _Depth[0]
    _leftColumn = ColumnCreation(_RelatingStructure=_frame, _Tag=_Tag, _Depth=_Depth)
    _rightColumn = ColumnCreation(
        _RelatingStructure=_frame, _Tag=_Tag, _Depth=_Depth, _Side=-1)
    _columnsContainer = ifc.createIfcRelContainedInSpatialStructure()
    _columnsContainer.RelatingStructure = _frame
    _columnsContainer.RelatedElements = [_leftColumn, _rightColumn]

# print(project)

# path = 'H:\\PY\\new_model.ifc'
path = '/Users/vdobranov/Yandex.Disk.localized/Python/Mac/ifcopenshell/new_model.ifc'
ifc.write(path)

def load_ifc_automatically(f):
    if (bool(f)) == True:
        _project = f.by_type('IfcProject')
        
        if _project != None:
            for i in _project:
                _collection_name = 'IfcProject/' + i.Name
            
            _collection = bpy.data.collections.get(str(_collection_name))
            
            if _collection != None:
                for _obj in _collection.objects:
                    bpy.data.objects.remove(_obj, do_unlink=True)
                    
                bpy.data.collections.remove(_collection)
        
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
        bpy.ops.bim.load_project(filepath=path)

load_ifc_automatically(ifc)