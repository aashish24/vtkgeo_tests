#!/usr/bin/env python

import argparse
import numpy
import sys
import vtk
from vtk.numpy_interface import dataset_adapter as dsa


def runExtrusionExample(seg, dsm, dtm, dest, debug=False, label=None, no_dec=False, no_render=False):
    # Read the terrain data
    dtmReader = vtk.vtkGDALRasterReader()
    dtmReader.SetFileName(dtm)
    dtmReader.Update()

    # Range of terrain data
    lo = dtmReader.GetOutput().GetScalarRange()[0]
    hi = dtmReader.GetOutput().GetScalarRange()[1]
    bds = dtmReader.GetOutput().GetBounds()
    #print("Bounds: {0}".format(bds))
    extent = dtmReader.GetOutput().GetExtent()
    #print("Extent: {0}".format(extent))
    origin = dtmReader.GetOutput().GetOrigin()
    #print("Origin: {0}".format(origin))
    spacing = dtmReader.GetOutput().GetSpacing()
    #print("Spacing: {0}".format(spacing))

    # Convert the terrain into a polydata.
    surface = vtk.vtkImageDataGeometryFilter()
    surface.SetInputConnection(dtmReader.GetOutputPort())

    # Make sure the polygons are planar, so need to use triangles.
    tris = vtk.vtkTriangleFilter()
    tris.SetInputConnection(surface.GetOutputPort())

    # Warp the surface by scalar values
    warp = vtk.vtkWarpScalar()
    warp.SetInputConnection(tris.GetOutputPort())
    warp.SetScaleFactor(1)
    warp.UseNormalOn()
    warp.SetNormal(0, 0, 1)
    warp.Update()

    # Read the segmentation of buildings
    segmentationReader = vtk.vtkGDALRasterReader()
    segmentationReader.SetFileName(seg)
    segmentationReader.Update()
    segmentation = segmentationReader.GetOutput()
    scalarName = segmentation.GetPointData().GetScalars().GetName()
    segmentationNp = dsa.WrapDataObject(segmentation)
    scalars = segmentationNp.PointData[scalarName]
    labels = numpy.unique(scalars)
    print("All labels: {}".format(labels))

    if (debug):
        segmentationWriter = vtk.vtkXMLImageDataWriter()
        segmentationWriter.SetFileName("segmentation.vti")
        segmentationWriter.SetInputConnection(segmentationReader.GetOutputPort())
        segmentationWriter.Update()

        segmentation = segmentationReader.GetOutput()
        sb = segmentation.GetBounds()
        print("segmentation bounds: \t{}".format(sb))

    # Extract polygons
    contours = vtk.vtkDiscreteFlyingEdges2D()
    #contours = vtk.vtkMarchingSquares()
    contours.SetInputConnection(segmentationReader.GetOutputPort())
    if (label):
        labels = label
    contours.SetNumberOfContours(len(labels))
    for i in range(len(labels)):
        contours.SetValue(i, labels[i])
    #print("DFE: {0}".format(contours.GetOutput()))

    if (debug):
        contoursWriter = vtk.vtkXMLPolyDataWriter()
        contoursWriter.SetFileName("contours.vtp")
        contoursWriter.SetInputConnection(contours.GetOutputPort())
        contoursWriter.Update()
        contoursData = contours.GetOutput()
        cb = contoursData.GetBounds()
        print("contours bounds: \t{}".format(cb))

    if (not no_dec):
        # combine lines into a polyline
        stripperContours = vtk.vtkStripper()
        stripperContours.SetInputConnection(contours.GetOutputPort())
        stripperContours.SetMaximumLength(3000)

        if (debug):
            stripperWriter = vtk.vtkXMLPolyDataWriter()
            stripperWriter.SetFileName("stripper.vtp")
            stripperWriter.SetInputConnection(stripperContours.GetOutputPort())
            stripperWriter.Update()

        # decimate polylines
        decimateContours = vtk.vtkDecimatePolylineFilter()
        decimateContours.SetMaximumError(0.01)
        decimateContours.SetInputConnection(stripperContours.GetOutputPort())

        if (debug):
            decimateWriter = vtk.vtkXMLPolyDataWriter()
            decimateWriter.SetFileName("decimate.vtp")
            decimateWriter.SetInputConnection(decimateContours.GetOutputPort())
            decimateWriter.Update()

        contours = decimateContours


    # Create loops
    loops = vtk.vtkContourLoopExtraction()
    loops.SetInputConnection(contours.GetOutputPort())

    if (debug):
        loopsWriter = vtk.vtkXMLPolyDataWriter()
        loopsWriter.SetFileName("loops.vtp")
        loopsWriter.SetInputConnection(loops.GetOutputPort())
        loopsWriter.Update()

    # Read the DSM
    dsmReader = vtk.vtkGDALRasterReader()
    dsmReader.SetFileName(dsm)
    dsmReader.Update()

    fit = vtk.vtkFitToHeightMapFilter()
    fit.SetInputConnection(loops.GetOutputPort())
    fit.SetHeightMapConnection(dsmReader.GetOutputPort())
    fit.UseHeightMapOffsetOn()
    fit.SetFittingStrategyToPointMaximumHeight()

    # Extrude polygon down to surface
    extrude = vtk.vtkTrimmedExtrusionFilter()
    #extrude.SetInputData(polygons)
    extrude.SetInputConnection(fit.GetOutputPort())
    extrude.SetTrimSurfaceConnection(warp.GetOutputPort())
    extrude.SetExtrusionDirection(0,0,1)
    extrude.CappingOn()

    extrudeWriter = vtk.vtkXMLPolyDataWriter()
    extrudeWriter.SetFileName(dest)
    extrudeWriter.SetInputConnection(extrude.GetOutputPort())
    extrudeWriter.Update()

    if (not no_render):
        # Create the RenderWindow, Renderer
        #
        ren = vtk.vtkRenderer()
        renWin = vtk.vtkRenderWindow()
        renWin.AddRenderer( ren )

        iren = vtk.vtkRenderWindowInteractor()
        iren.SetRenderWindow(renWin)

        # Create pipeline. Load terrain data.
        lut = vtk.vtkLookupTable()
        lut.SetHueRange(0.6, 0)
        lut.SetSaturationRange(1.0, 0)
        lut.SetValueRange(0.5, 1.0)


        # Show the terrain
        dtmMapper = vtk.vtkPolyDataMapper()
        dtmMapper.SetInputConnection(warp.GetOutputPort())
        dtmMapper.SetScalarRange(lo, hi)
        dtmMapper.SetLookupTable(lut)

        dtmActor = vtk.vtkActor()
        dtmActor.SetMapper(dtmMapper)

        # show the buildings
        trisExtrude = vtk.vtkTriangleFilter()
        trisExtrude.SetInputConnection(extrude.GetOutputPort())

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(trisExtrude.GetOutputPort())
        mapper.ScalarVisibilityOff()

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        # Render it
        ren.AddActor(dtmActor)
        ren.AddActor(actor)

        ren.GetActiveCamera().Elevation(-60)
        ren.ResetCamera()

        renWin.Render()
        iren.Start()



if __name__ == '__main__':
    # Demonstrate generation of extruded objects from a segmentation map, where
    # the extrusion is trimmed by a terrain surface.
    parser = argparse.ArgumentParser(
        description='Generate extruded buildings given a segmentation map, DSM and DTM')
    parser.add_argument("segmentation", help="Image with labeled buildings")
    parser.add_argument("dsm", help="Digital surface model (DSM)")
    parser.add_argument("dtm", help="Digital terain model (DTM)")
    parser.add_argument("destination", help="Extruded buildings polygonal file (.vtp)")
    parser.add_argument('-l', "--label", type=int, nargs="*",
                        help="Label value(s) used for buildings outlines."
                             "If not specified, all values are used.")
    parser.add_argument("--no_decimation", action="store_true",
                        help="Do not decimate the contours")
    parser.add_argument("--no_render", action="store_true",
                        help="Do not render")
    parser.add_argument("--debug", action="store_true",
                        help="Save intermediate results")
    args = parser.parse_args()

    runExtrusion(args.segmentation, args.dsm, args.dtm, args.destination,
        args.debug, args.label, args.no_decimation, args.no_render)

