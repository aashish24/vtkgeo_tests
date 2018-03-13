#!/bin/env python

"""
VTK Geospatial Examples
"""

import argparse, sys
import vtk
from extrude_buildings import runExtrusionExample
from vtk_segy import renderSegY

# Globals
iren = None
renWin = None

def init():
    global renWin
    global iren

    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.SetSize(1920, 1080)
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
    actor.GetProperty().SetPointSize(2.0)
    ren.AddActor(actor)

    return actor

def renderImageData(ren, vtkidata):
    actor = vtkImageDataToActor(vtkidata)
    ren.AddActor(actor)

def renderMultiblockData(ren, vtkmdata):
    mapper = vtk.vtkCompositePolyDataMapper()
    mapper.SetInputDataObject(vtkmdata)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    ren.AddActor(actor)
    return actor

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

def loadGeoJSONData(filename):
    geoString = None

    with open(filename, 'r') as f:
        geoString = f.read()

    reader = vtk.vtkGeoJSONReader()
    reader.StringInputModeOn()
    reader.SetStringInput(geoString)

    reader.Update()
    dataset = reader.GetOutput()

    return dataset

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
    comp_filter = vtk.vtkCompositeDataGeometryFilter()
    comp_filter.SetInputData(vtkdata)
    comp_filter.Update()
    renderPolyData(init(), comp_filter.GetOutput())
    # renderMultiblockData(init(), vtkdata)
    run()

def runVectorCompositeExample(filename):
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

def runGeoJSONCropExample(input_filename, bbox_filename):
    inputDataset = loadGeoJSONData(input_filename)
    bboxDataset = loadGeoJSONData(bbox_filename)

    # Use the bounds from the bounding box to create an implicit function
    queryBounds = list(bboxDataset.GetBounds())
    bbox = vtk.vtkPlanes()
    bbox.SetBounds(queryBounds)

    # This filter uses the implicit function to extract the data
    bboxFilter = vtk.vtkExtractPolyDataGeometry()
    bboxFilter.SetInputData(inputDataset)
    bboxFilter.SetImplicitFunction(bbox)
    # Exclude (set to 0) or include (set to 1) districts on the boundary
    bboxFilter.SetExtractBoundaryCells(0)

    # Get the cropped region and write it to disk
    bboxFilter.Update()
    croppedDataset = bboxFilter.GetOutput()
    outputWriter = vtk.vtkGeoJSONWriter()
    outputWriter.SetFileName('cropped_output.geojson')
    outputWriter.SetInputData(croppedDataset)
    outputWriter.Write()

    renderer = init()
    inputActor = renderPolyData(renderer, inputDataset)
    bboxActor = renderPolyData(renderer, bboxDataset)
    cropActor = renderPolyData(renderer, croppedDataset)

    # Set rendering type and color on the actors
    inputActor.GetProperty().SetRepresentationToWireframe()
    inputActor.GetProperty().SetColor(0.0, 1.0, 0.0)
    bboxActor.GetProperty().SetRepresentationToWireframe()
    bboxActor.GetProperty().SetColor(1.0, 0.0, 0.0)
    cropActor.GetProperty().SetRepresentationToWireframe()
    cropActor.GetProperty().SetColor(1.0, 0.0, 1.0)

    run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run VTK Geospatial Examples')
    parser.add_argument("-e", "--example", type=int, default=0, help="Enter an example number (1 - 8)")
    args = parser.parse_args()

    if args.example == 0:
        print('Provide an example to run via the --example (-e) argument')
        sys.exit(1)

    if args.example == 1:
        # Example 1
        runRasterExample("./data/o_14DEC14WV031100014DEC14160402-pans-utm.tif")
    elif args.example == 2:
        # Example 2
        runVectorExample("./data/jacksonville/jacksonville_3d_bldgs_1.shp")
    elif args.example == 3:
        # Example 3
        runVectorCompositeExample("./data/jacksonville/jacksonville_3d_bldgs_1.shp")
    elif args.example == 4:
        # Example 4
        runPointCloudExample("./data/tp_manual_20171031104346_flt.bpf")
    elif args.example == 5:
        # Example 5
        runPointCloudPlusRasterExample("./data/tp_manual_20171031104346_flt.bpf",
                                       "./data/o_14DEC14WV031100014DEC14160402-P1BS-500648062060_01_P001_________AAE_0AAAAABPABS0_utm.tif")
    elif args.example == 6:
        # Example 6
        runGeoJSONCropExample("./data/baghdad_districts.geojson", "./data/baghdad_bbox.geojson")
    elif args.example == 7:
        # Example 7
        runExtrusionExample('./data/extrusion/AOI-D1-CLS.tif',
                            './data/extrusion/AOI-D1-DSM.tif',
                            './data/extrusion/AOI-D1-DTM.tif',
                            './AOI-D1-out.vtp')
    else:
        # Example 8
        renderSegY("./data/waha8.sgy")
