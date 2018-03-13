#!/bin/env python

import argparse, sys
import vtk

def renderSegY(fname):
    ren_win = vtk.vtkRenderWindow()
    ren_win.SetSize(300, 300)
    ren = vtk.vtkRenderer()
    ren_win.AddRenderer(ren)
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(ren_win)

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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Render SegY file')
    parser.add_argument("--file", default=None, help="Path to segy file to render")
    args = parser.parse_args()

    if not args.file:
        print('Please provide path to segy file via --file argument')
        sys.exit(1)

    renderSegY(args.file)
