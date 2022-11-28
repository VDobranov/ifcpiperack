# Импортируем библиотеки:
# для работы со временем: time
# для работы с IFC: ifcopenshell
# для математических операций: math

import time
import ifcopenshell as ios
import math


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

PRWidth = 9000.0
PRSpans = [6000.0,6000.0,9000.0,6000.0,6000.0]
PRLength = sum(PRSpans)

PRIfcOrigin = originPoint
PRIfcEnd = ifc.createIfcCartesianPoint(
	[originPoint.Coordinates[0] + PRLength, originPoint.Coordinates[1], originPoint.Coordinates[2]])

# Функции

# Creates an IfcAxis2Placement3D from Location, Axis and RefDirection

def create_ifcaxis2placement(ifcfile=ifc, point=originPoint, dir1=globalAxisZ, dir2=globalAxisX):
	if point == originPoint and dir1 == globalAxisZ and dir2 == globalAxisX:
		axis2placement = worldCoordinateSystem
	else:
		axis2placement = ifcfile.createIfcAxis2Placement3D(point, dir1, dir2)
	return axis2placement

# Creates an IfcLocalPlacement from Location, Axis, RefDirection and relative placement

def create_ifclocalplacement(ifcfile=ifc, point=originPoint, dir1=globalAxisZ, dir2=globalAxisX, relative_to=None):
	if point == originPoint and dir1 == globalAxisZ and dir2 == globalAxisX:
		axis2placement = worldCoordinateSystem
	else:
		axis2placement = ifcfile.createIfcAxis2Placement3D(point, dir1, dir2)
	ifclocalplacement2 = ifcfile.createIfcLocalPlacement(
		relative_to, axis2placement)
	return ifclocalplacement2


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

planContext = ifc.createIfcGeometricRepresentationContext()
planContext.ContextType = 'Plan'
planContext.CoordinateSpaceDimension = 2
planContext.Precision = 0.001
planContext.WorldCoordinateSystem = worldCoordinateSystem

# Создание проекта

project = ifc.createIfcProject(ios.guid.new())
project.OwnerHistory = ownerHistory
project.Name = '1st Try'
project.Description = 'Creation of an IFC-file from the scratch with the ifcopenshell library.'
project.UnitsInContext = myUnits
project.RepresentationContexts = [modelContext, planContext]

# Создание площадки

sitePlacement = create_ifclocalplacement()

site = ifc.createIfcSite(ios.guid.new())
site.Name = "Площадка строительства"
site.ObjectPlacement = sitePlacement

siteContainer = ifc.createIfcRelAggregates()
siteContainer.RelatingObject = project
siteContainer.RelatedObjects = [site]

# Создание сетки осей

PRMainAxis = ifc.createIfcGridAxis()
PRMainAxis.AxisTag = "Piperack Axis"
PRMainAxis.AxisCurve = ifc.createIfcPolyline([PRIfcOrigin, PRIfcEnd])
PRMainAxis.SameSense = True

PRCrossAxes = []
PRCrossAxesPolylines = []
for a in range(len(PRSpans)+1):
	p1 = ifc.createIfcCartesianPoint([float(sum(PRSpans[:a])), -PRWidth/2, 0.])
	p2 = ifc.createIfcCartesianPoint([float(sum(PRSpans[:a])), PRWidth/2, 0.])
	axis = ifc.createIfcGridAxis()
	axis.AxisTag = f"{a+1}"
	axis.AxisCurve = ifc.createIfcPolyline(
	[p1, p2])
	PRCrossAxes.append(axis)
	PRCrossAxesPolylines.append(axis.AxisCurve)

PRMainGridPlacement = create_ifclocalplacement(relative_to=sitePlacement)

PRMainGridGeomCurveSet = ifc.createIfcGeometricCurveSet(
	[PRMainAxis.AxisCurve] + PRCrossAxesPolylines)

PRMainGridShapeRepresent = ifc.createIfcShapeRepresentation()
PRMainGridShapeRepresent.ContextOfItems = footprintContext
PRMainGridShapeRepresent.RepresentationIdentifier = 'FootPrint'
PRMainGridShapeRepresent.RepresentationType = 'GeometricCurveSet'
PRMainGridShapeRepresent.Items = [PRMainGridGeomCurveSet]

PRMainGridProductDefShape = ifc.createIfcProductDefinitionShape()
PRMainGridProductDefShape.Representations = [PRMainGridShapeRepresent]

PRMainGrid = ifc.createIfcGrid(ios.guid.new())
PRMainGrid.UAxes = [PRMainAxis]
PRMainGrid.VAxes = PRCrossAxes
PRMainGrid.ObjectPlacement = PRMainGridPlacement
PRMainGrid.Representation = PRMainGridProductDefShape

PRMainGridSpatialContainer = ifc.createIfcRelContainedInSpatialStructure()
PRMainGridSpatialContainer.Name = 'Piperack Main Grid Container'
PRMainGridSpatialContainer.RelatingStructure = site
PRMainGridSpatialContainer.RelatedElements = [PRMainGrid]

# Создание эстакады

piperackPlacement = create_ifclocalplacement(relative_to=sitePlacement)

piperack = ifc.createIfcBuilding(ios.guid.new())
piperack.Name = "Трубопроводная эстакада"
piperack.CompositionType = 'COMPLEX'
piperack.ObjectPlacement = piperackPlacement

piperackContainer = ifc.createIfcRelAggregates()
piperackContainer.Name = "Piperack Container"
piperackContainer.RelatingObject = site
piperackContainer.RelatedObjects = [piperack]

# Создание участков эстакады

srp1Placement = create_ifclocalplacement(relative_to=piperackPlacement)
srp2Placement = create_ifclocalplacement(relative_to=piperackPlacement)
# srp2Placement = ifc.createIfcGridPlacement()
# srp2Placement.PlacementLocation = ifc.createIfcVirtualGridIntersection(
# 	[PRMainAxis, PRCrossAxes[4]])

srp1 = ifc.createIfcBuilding(ios.guid.new())
srp1.Name = "Участок 1"
srp1.CompositionType = 'PARTIAL'
srp1.ObjectPlacement = srp1Placement

srp2 = ifc.createIfcBuilding(ios.guid.new())
srp2.Name = "Участок 2"
srp2.CompositionType = 'PARTIAL'
srp2.ObjectPlacement = srp2Placement

srpsContainer = ifc.createIfcRelAggregates()
srpsContainer.Name = "SRPs Container"
srpsContainer.RelatingObject = piperack
srpsContainer.RelatedObjects = [srp1, srp2]

# Создание ярусов эстакады

def TierCreation (_name, _srp, _elevation):
	_tier = ifc.createIfcBuildingStorey(ios.guid.new())
	_tier.Name = _srp.Name + ". " + _name
	# _tier.Name = _name
	_tier.Elevation = _elevation
	_tierContainer = ifc.createIfcRelAggregates()
	_tierContainer.Name = f"{_elevation}m Tier Container"
	_tierContainer.RelatingObject = _srp
	_tierContainer.RelatedObjects = [_tier]

for _srp in srpsContainer.RelatedObjects:
	TierCreation('Уровень земли', _srp, 0)
	TierCreation('Первый ярус', _srp, 6000)
	TierCreation('Второй ярус', _srp, 9000)

# print(project)

ifc.write('new_model.ifc')
