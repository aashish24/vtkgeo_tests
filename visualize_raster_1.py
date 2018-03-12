#!/bin/env python

"""
Load DSM

Transform panchromatic image

Load DSM and Panchromatic image together

Load Vector

Load Point Cloud
"""

import vtk

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

def renderMultiblockData(vtk_data):
    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)

    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    style = vtk.vtkInteractorStyleTrackballCamera()
    iren.SetInteractorStyle(style)

    mapper = vtk.vtkCompositePolyDataMapper()
    mapper.SetInputDataObject(vtk_data)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    ren.AddActor(actor)
    ren.SetBackground(0.1, 0.1, 0.1)

    # enable user interface interactor
    iren.Initialize()
    renWin.Render()
    iren.Start()

def runRasterExample(filename):
    # Create a rendering window and renderer
    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.SetSize(800, 600)
    renWin.AddRenderer(ren)
    # Create a RenderWindowInteractor to permit manipulating the camera
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    style = vtk.vtkInteractorStyleTrackballCamera()
    iren.SetInteractorStyle(style)

    vtkdata = loadData(filename)
    ren.AddActor(vtkDataToActor(vtkdata))
    ren.SetBackground(0.1, 0.1, 0.1)

    # enable user interface interactor
    iren.Initialize()
    renWin.Render()
    iren.Start()

def loadData(filename):
    reader = vtk.vtkGDALRasterReader()
    reader.SetFileName(filename)
    reader.Update()
    vtkdata = reader.GetOutput()
    return vtkdata

def vtkDataToActor(vtkdata):
    actor = vtk.vtkImageActor()
    actor.SetInputData(vtkdata)
    return actor

def runVectorExample(filename):
    reader = vtk.vtkGDALVectorReader()
    reader.SetFileName(filename)

    # trans_filter = vtk.vtkTransformFilter()
    # geo_trans = vtk.vtkGeoTransform()
    # src_proj = vtk.vtkGeoProjection()
    # src_proj.SetName("merc")
    # dest_proj = vtk.vtkGeoProjection()
    # dest_proj.SetName("eqc")
    # geo_trans.SetSourceProjection(src_proj)
    # geo_trans.SetDestinationProjection(dest_proj)

    trans_filter.SetTransform(geo_trans)
    trans_filter.SetInputConnection(reader.GetOutputPort())
    trans_filter.Update()
    reader.Update()
    vtkdata = reader.GetOutput()
    renderMultiblockData(vtkdata)

#render("./data/o_14DEC14WV031100014DEC14160402-P1BS-500648062060_01_P001_________AAE_0AAAAABPABS0_utm.tif")

runRasterExample("./data/dsm.tif")
runVectorExample("./data/countries/countries.shp")
runVectorPlusRasteExample("")
runVectorPlusRasterPlusPointCloudExample("")
runClipVectorExample("")
runSegYExample("")
runPointCloudExample("")
runSegY2DExample("")