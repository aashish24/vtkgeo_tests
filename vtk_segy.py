#!/bin/env python

import vtk

def renderSegY():
    ren_win = vtk.vtkRenderWindow()
    ren_win.SetSize(300, 300)
    ren = vtk.vtkRenderer()
    ren_win.AddRenderer(ren)
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(ren_win)

    fname = "./data/waha8.sgy";
    lut = vtk.vtkColorTransferFunction()
    lut.AddRGBPoint(-127, 0.23, 0.30, 0.75);
    lut.AddRGBPoint(0.0, 0.86, 0.86, 0.86);
    lut.AddRGBPoint(126, 0.70, 0.02, 0.15);

    reader = vtk.vtkSegY3DReader()
    mapper = vtk.vtkDataSetMapper()
    actor = vtk.vtkActor()

    reader.SetFileName(fname);
    reader.Update();

    mapper.SetInputConnection(reader.GetOutputPort());
    mapper.SetLookupTable(lut);
    mapper.SetColorModeToMapScalars();

    actor.SetMapper(mapper);

    ren.AddActor(actor);
    ren.ResetCamera();

    ren.GetActiveCamera().Elevation(90);
    ren.GetActiveCamera().Zoom(5);

    ren_win.Render();

    iren.Start();

renderSegY()
