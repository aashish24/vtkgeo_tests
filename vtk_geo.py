#!/bin/env python

"""
Load DSM

Transform panchromatic image

Load DSM and Panchromatic image together

Load Vector

Load Point Cloud
"""

import vtk

# Globals
iren = None
renWin = None

def init():
    global renWin
    global iren

    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)

    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    style = vtk.vtkInteractorStyleTrackballCamera()
    iren.SetInteractorStyle(style)

    ren.SetBackground(0.1, 0.1, 0.1)
    return ren

def run():
     # enable user interface interactor
    iren.Initialize()
    renWin.Render()
    iren.Start()

def renderPolyData(ren, vtk_data):
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(vtk_data)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    ren.AddActor(actor)

def renderImageData(ren, vtkidata):
    ren.AddActor(vtkImageDataToActor(vtkidata))

def renderMultiblockData(ren, vtkmdata):
    mapper = vtk.vtkCompositePolyDataMapper()
    mapper.SetInputDataObject(vtkmdata)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    ren.AddActor(actor)

def renderStructureGridData(vtk_data):
    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)

    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    style = vtk.vtkInteractorStyleTrackballCamera()
    iren.SetInteractorStyle(style)

    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputData(vtk_data)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    ren.AddActor(actor)
    ren.SetBackground(0.1, 0.1, 0.1)

    # enable user interface interactor
    iren.Initialize()
    renWin.Render()
    iren.Start()

def loadRasterData(filename):
    reader = vtk.vtkGDALRasterReader()
    reader.SetFileName(filename)
    reader.Update()
    vtkdata = reader.GetOutput()
    return vtkdata

def vtkImageDataToActor(vtkdata):
    actor = vtk.vtkImageActor()
    actor.SetInputData(vtkdata)
    return actor

def prepareRasterExample(filename):
    vtkdata = loadRasterData(filename)
    return vtkdata

def prepareVectorExample(filename):
    reader = vtk.vtkGDALVectorReader()
    reader.SetFileName(filename)
    reader.Update()
    vtkdata = reader.GetOutput()

    return vtkdata

def preparePointCloudExample(filename):
    reader = vtk.vtkPDALReader()
    reader.SetFileName(filename)

    # trans_filter = vtk.vtkTransformFilter()
    # geo_trans = vtk.vtkGeoTransform()
    # src_proj = vtk.vtkGeoProjection()
    # src_proj.SetName("merc")
    # dest_proj = vtk.vtkGeoProjection()
    # dest_proj.SetName("eqc")
    # geo_trans.SetSourceProjection(src_proj)
    # geo_trans.SetDestinationProjection(dest_proj)

    reader.Update()
    vtkdata = reader.GetOutput()

    bounds = vtkdata.GetBounds()
    minz = bounds[4]
    maxz = bounds[5]

    colorLookupTable = vtk.vtkLookupTable()
    colorLookupTable.SetTableRange(minz, maxz)
    colorLookupTable.SetNumberOfColors(10)
    colorLookupTable.Build();

    colors = vtk.vtkUnsignedCharArray()
    colors.SetNumberOfComponents(3)
    colors.SetName("Colors")

    for i in range(vtkdata.GetNumberOfPoints()):
        p = vtkdata.GetPoint(i)
        dcolor = [0, 0, 0]
        colorLookupTable.GetColor(p[2], dcolor)

        color = [0, 0, 0]
        for j in range(0, 3):
            color[j] = 255 * dcolor[j]

        colors.InsertNextTuple3(color[0], color[1], color[2])

    vtkdata.GetPointData().SetScalars(colors)
    return vtkdata

def runRasterExample(filename):
    vtkdata = prepareRasterExample(filename)
    renderImageData(init(), vtkdata)
    run()

def runVectorExample(filename):
    vtkdata = prepareVectorExample(filename)
    renderMultiblockData(init(), vtkdata)
    run()

def runPointCloudExample(filename):
    vtkdata = preparePointCloudExample(filename)
    renderPolyData(init(), vtkdata)
    run()

def runPointCloudPlusRasterExample(p_filename, r_filename):
    vtkdata = preparePointCloudExample(p_filename)
    vtkidata = prepareRasterExample(r_filename)
    ren = init()
    renderPolyData(ren, vtkdata)
    renderImageData(ren, vtkidata)
    run()

runRasterExample("./data/o_14DEC14WV031100014DEC14160402-pans-utm.tif")
# runVectorExample("./data/jacksonville/jacksonville_3d_bldgs_1.shp")
# runPointCloudExample("./data/tp_manual_20171031104346_flt.bpf")
# runPointCloudPlusRasterExample("./data/tp_manual_20171031104346_flt.bpf",
#                                "./data/o_14DEC14WV031100014DEC14160402-P1BS-500648062060_01_P001_________AAE_0AAAAABPABS0_utm.tif")

# Cropping - Scott
# Building extraction example - Scott/Dan/Aashish
# SegY 3D visualization - Aashish/Scott

# runHeightExtractionExample("")
# runVectorExample("./data/countries/countries.shp")
# runVectorPlusRasteExample("")
# runVectorPlusRasterPlusPointCloudExample("")
# runClipVectorExample("")
# runSegYExample("")
# runPointCloudExample("")
# runSegY2DExample("")