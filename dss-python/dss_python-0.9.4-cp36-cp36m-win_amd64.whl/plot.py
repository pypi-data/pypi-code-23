from matplotlib import pyplot as plt
'''

(All)
- Bus: Name, idx, x, y, CoordDefined ---- only buses and lines need special treatment
- Transformers: Enabled, Buses, IsSubstation
- RegControl: Enabled, Transformer, TapWinding,
- Storage: Enabled, Bus1, Storage
- Relay: Enabled, MonitoredObj, MonitoredTerm


'''




vizCURRENT = 1
vizVOLTAGE = 2
vizPOWER = 3

# TPlotType 
(ptAutoAddLogPlot, ptCircuitplot, ptGeneralDataPlot,
 ptGeneralCircuitPlot, ptMonitorPlot, ptDaisyPlot, ptMeterZones,
 ptLoadShape, ptTShape, ptPriceShape, ptProfile, ptScatterPlot,
 ptEvolutionPlot, ptMatrixplot) = range(14)


# TPlotQuantity
(pqVoltage, pqCurrent, pqPower, pqLosses, pqCapacity, pqNone) = range(6)

# From DSSGlobals
PROFILE3PH = 9999


Eps = 0.002

DSSG_LINECLASS = 1
DSSG_CIRCLECLASS = 2
DSSG_TEXTCLASS = 3
DSSG_MARKERCLASS = 4
DSSG_CURVECLASS = 5
DSSG_SUBSTCLASS = 6


clAqua  = '#FFFF00'
clBlack  = '#000000'
clBlue  = '#FF0000'
clCream  = '#F0FBFF'
clDkGray  = '#808080'
clFuchsia  = '#FF00FF'
clGray  = '#808080'
clGreen  = '#008000'
clLime  = '#00FF00'
clLtGray  = '#C0C0C0'
clMaroon  = '#000080'
clMedGray  = '#A4A0A0'
clMoneyGreen  = '#C0DCC0'
clNavy  = '#800000'
clOlive  = '#008080'
clPurple  = '#800080'
clRed  = '#0000FF'
clSilver  = '#C0C0C0'
clSkyBlue  = '#F0CAA6'
clTeal  = '#808000'
clWhite  = '#FFFFFF'
clYellow  = '#00FFFF'





#"""
class Plot: 
    '''
    An implementation of TDSSPlot based on Matplotlib.
    
    Most of the naming scheme is used to facilitate debugging in the alpha stage
    '''
    
    #private
    ColorArray: Array [1 .. 17] of Integer;
    pLine: TLineObj;
    pTransf: TTransfObj;
    Bus1Idx, Bus2Idx: Integer;
    FGeneralCircuitPlotQuantity: String;

    #public:
    FeederName: String;
    ValueIndex: Integer; # For General & AutoAdd 


    # Main procedures for the various types of plots ... called from execute 
    def _DoGeneralPlot(self):
        pass
        
    def _DoAutoAddPlot(self):
        pass
        
    def _DoTheDaisies(self):
        pass
        
    def _DoCircuitPlot(self):
        pass
        
    def _DoGeneralCircuitPlot(self):
        # LineStyleType: TPenStyle;
        #Draw the lines With the thickness proportional to the data loaded in the general line data file
        Line = dss.ActiveCircuit.Lines
        idxLine = Line.First

        while idxLine <> 0:
            if not Line.Enabled:
                idxLine = Line.Next
                continue 
                
            # pLine.Drawn := TRUE; ##TODO: why?
            Bus1Idx, Bus2Idx = line.Buses
            If not (Buses^[Bus1Idx].CoordDefined and Buses^[Bus2Idx].CoordDefined):
                idxLine = Line.Next
                continue 
            
            If pLine.IsSwitch:
                AddNewLine(Buses^[Bus1Idx].X, Buses^[Bus1Idx].Y,
                    Buses^[Bus2Idx].X, Buses^[Bus2Idx].Y, color='#0080FF', 1,
                    Style(1), Dots, ('Line.%s'%[pLine.Name]), MarkSwitches,
                    SwitchMarkerCode, NodeMarkerCode, NodeMarkerWidth)

            elseif Line.IsIsolated:
                AddNewLine(Buses^[Bus1Idx].X, Buses^[Bus1Idx].Y,
                    Buses^[Bus2Idx].X, Buses^[Bus2Idx].Y, clFuchsia, 3,
                    Style(1), Dots, ('Line.%s'%[pLine.Name]), MarkSwitches,
                    SwitchMarkerCode, NodeMarkerCode, NodeMarkerWidth)
            else:
                if Line.NPhases = 1:
                    LineStyleType = Style(SinglePhLineStyle)
                else:
                    LineStyleType = Style(ThreePhLineStyle)

                AddNewLine(Buses^[Bus1Idx].X, Buses^[Bus1Idx].Y,
                    Buses^[Bus2Idx].X, Buses^[Bus2Idx].Y, GetColor,
                    Thickness, LineStyleType, Dots, Format('Line.%s',[pLine.Name]),
                    FALSE, 0, NodeMarkerCode, NodeMarkerWidth)
            
            if self.Labels:
                self._do_bus_labels(Bus1Idx, Bus2Idx)
                
            idxLine = Line.Next


         
    
        
    def _DoMeterZonePlot(self):
        pass


    def _DoMonitorPlot(self):
        pass
        
    def _DoProfilePlot(self):
        pass

    # Misc support procedures
    def _MarkSubTransformers(self):
        pass

    def _MarkTheTransformers(self):
        pass

    def _MarkTheCapacitors(self):
        pass

    def _MarkTheRegulators(self):
        pass

    def _MarkThePVSystems(self):
        pass

    def _MarkTheStorage(self):
        pass

    def _MarkTheFuses(self):
        pass

    def _MarkTheReclosers(self):
        pass

    def _MarkTheRelays(self):
        pass

    def _MarkSpecialClasses(self):
        pass

    def _DoBusLabel(self, const Idx: Integer, const BusLabel: String):
        pass

    def _LoadGeneralLineData(self):
        pass

    def _SetColorArray(self):
        pass

    def _SetMaxScale(self):
        if self.MaxScaleIsSpecified: return
        
        if self.Quantity in (pqVoltage, pqCurrent, pqCapacity):
            return
            
        elif self.Quantity == pqLosses:
           maxScale := 0.0;
           pLine := ActiveCircuit.Lines.First;
           While pLine <> Nil Do
           Begin
              If pLine.Enabled Then
                 With pLine Do
                 Begin
                    # ----ActiveTerminalIdx := 1;
                    MaxScale := Max(MaxScale, abs(pLine.Losses.re / pLine.Len ))
                 End;
              pLine := ActiveCircuit.Lines.Next;
           End;
           MaxScale := MaxScale * 0.001;
        elif self.Quantity == pqPower:
           maxScale := 0.0;
           pLine := ActiveCircuit.Lines.First;
           While pLine <> Nil Do
           Begin
              If pLine.Enabled Then
                 With pLine Do
                 Begin
                    # ----ActiveTerminalIdx := 1;
                    MaxScale := Max(MaxScale, abs(Power[1].re))
                 End;
              pLine := ActiveCircuit.Lines.Next;
           End;
           MaxScale := MaxScale * 0.001;

        elif self.Quantity == pqNone:
          if self.plot_type == ptGeneralCircuitPlot:
             pLine := ActiveCircuit.Lines.First;
             While pLine <> Nil Do
             Begin
                If pLine.Enabled Then
                   With pLine Do
                   Begin
                      # ----ActiveTerminalIdx := 1;
                      MaxScale := Max(MaxScale, abs(GeneralPlotQuantity))
                   End;
                pLine := ActiveCircuit.Lines.Next;
             End;
               
    def _AddBusMarkers(self):
        pass

    def GetColor(self) => Integer:
        pass

    def Thickness(self) => Integer:
        pass

    def MaxCurrent(self) => Double:
        pass

    def NextColor(self) => TColor:
        pass

    def QuantityString(self): String:
        if self.Quantity == pqVoltage: 
            return 'Voltage'
        elif self.Quantity == pqPower:
            return 'Power'
        elif self.Quantity == pqCurrent:
            return 'Current'
        elif self.Quantity == pqLosses:
            return 'Loss Density'
        elif self.Quantity == pqCapacity:
            return 'Capacity'
        elif self.Quantity == pqNone:
            if self.plot_type == ptGeneralCircuitPlot:
               return self.FGeneralCircuitPlotQuantity #TODO?
       
        return ''

    
    
    
    def Style(self, Code: Integer): TPenStyle:
        pass

    def GetAutoColor(self, Scale: Double): TColor:
        pass

    def GetMarker(self, Idx: Integer): Byte:
        pass

    def CoordinateSame(self, i1, i2: Integer) => Boolean:
        pass

    def InterpolateGradientColor(self, Color1, Color2: TColor; Ratio: Double) => TColor:
        pass


    # Property support 
    @property
    def MaxLineThickness(self):
        return self._MaxLineThickness
    
    @MaxLineThickness.setter
    def Set_MaxLineThickness(self, value):
        if value > 0:
            self._MaxLineThickness = value

    def __init__(self):
       self.SetDefaults()
       self.DaisyBusList = []
       self.PhasesToPlot = PROFILE3PH
    
    def SetDefaults(self):
        self.max_scale = 0.0 # Find max_scale
        self.MaxScaleIsSpecified = False # indicates take the default
        self.min_scale = 0.0 # Find min_scale
        self.MinScaleIsSpecified = False # indicates take the default
        self.Dots = False
        self.Labels = False
        self.ShowLoops = False
        self.ShowSubs = False
        self.Quantity = pqPower
        self.plot_type = ptCircuitplot
        self.MarkerIdx = 24
        self.ObjectName = ''
        self._MaxLineThickness = 10
        self.Channels = [1, 3, 5]
        self.Bases = [1.0, 1.0, 1.0]
        self.Color1 = clBlue
        self.Color2 = clGreen
        self.Color3 = clRed
        self.TriColorMax = 0.85
        self.TriColorMid = 0.50
        self.ActiveColorIdx = 0
        self.ThreePhLineStyle = 1
        self.SinglePhLineStyle = 1
            
        self.color_array = ('#000000', '#0000FF', '#FF0000', '#FF00FF', '#008000', '#00FF80', '#4080FF', '#21DEDA', '#FF6AB5', '#004080', '#008080', '#A00000', '#8080FF', '#800000', '#7F7F7F', '#7B0F8E', '#8E9607')
        
        
    def Execute(self):
        # Init line.Drawn variable to Not Drawn
        # pLine = ActiveCircuit.Lines.First # TODO: how is this actually used?
        # while Assigned(pLine) do Begin
        #     pLine.Drawn = False
        #     pLine = ActiveCircuit.Lines.Next;
        # End;

        if (plot_type == ptCircuitplot) and (Quantity == pqNone) and (FileExists(ObjectName)):
            plot_type = ptGeneralCircuitPlot

        if plot_type == ptMonitorPlot: 
            # if MakeNewGraph(GetOutputDirectory + CircuitName_ + 'MONITOR-' + UpperCase(ObjectName) + ''.join(('-ch%d' % [Channels[i]])) for i in Channels) + '.DSV') > 0:
            self.DoMonitorPlot()
            return
            

        elif plot_type == ptLoadShape: 
            # if MakeNewGraph(GetOutputDirectory + CircuitName_ + ('Loadshape_%s.DSV' % [ObjectName])) > 0:
            self.DoLoadShapePlot(ObjectName)
            return # All we need to do here
             
        elif plot_type == ptTShape: 
            # if MakeNewGraph(GetOutputDirectory + CircuitName_ + ('TempShape_%s.DSV' % [ObjectName])) > 0:
            self.DoTempShapePlot(ObjectName);
            return # All we need to do here
             
        elif plot_type == ptPriceShape:
            # if MakeNewGraph(GetOutputDirectory + CircuitName_ + ('Priceshape_%s.DSV' % [ObjectName])) > 0:
            self.DoPriceShapePlot(ObjectName)
            return # All we need to do here

        elif plot_type == ptProfile: 
            #if MakeNewGraph(GetOutputDirectory + CircuitName_ + ('Profile%d.DSV' % [PhasesToPlot])) > 0:
            self.DoProfilePlot()
            return

        self.bus_labels = {}
        
        self.Get_Properties(DSSGraphProps)
        DSSGraphProps.GridStyle = gsNone
        DSSGraphProps.ChartColor = clWhite
        DSSGraphProps.WindColor = clWhite
        DSSGraphProps.Isometric = True
        DSSGraphProps.EnableClickonDiagram
        self.Set_Properties(DSSGraphProps)
        self.Set_XaxisLabel('X')
        self.Set_YaxisLabel('Y')

        self.Set_TextAlignment(1); # Left Justify; 2 = center; 3=right 
        self.Set_KeyClass(DSSG_LINECLASS) # Line for searches 

        if plot_type == ptAutoAddLogPlot:
            self.MarkerIdx = 26
            self.Set_KeyClass(DSSG_MARKERCLASS); # Marker
            self.DoAutoAddPlot()
            self.MarkSpecialClasses()

        elif plot_type == ptCircuitplot:
            self.SetMaxScale()
            self.Set_ChartCaption('%s:%s, max=%-6.3g' % [ActiveCircuit.CaseName, QuantityString, max_scale])
            self.DoCircuitPlot()
            self.MarkSpecialClasses()

        elif plot_type == ptGeneralDataPlot:
            self.Dots = False
            self.DoCircuitPlot()
            self.Set_KeyClass(DSSG_MARKERCLASS) # Marker 
            self.MarkerIdx = ActiveCircuit.NodeMarkerCode # 24
            self.DoGeneralPlot()
            self.MarkSpecialClasses()

        elif plot_type == ptGeneralCircuitPlot:
            self.LoadGeneralLineData()
            self.SetMaxScale()
            self.Set_ChartCaption('%s:%s, max=%-.3g' % [ActiveCircuit.CaseName, QuantityString, max_scale])
            self.DoGeneralCircuitPlot()
            self.MarkSpecialClasses()

        elif plot_type == ptMeterZones:
            self.DoMeterZonePlot()
            self.MarkSpecialClasses()
            
        elif plot_type == ptDaisyPlot:
            Set_ChartCaption('Device Locations / ' + QuantityString) #TODO
            if Labels:
                self.Labels = False # Temporarily turn off
                self.DoCircuitPlot()
                self.Labels = True # Turn back on to label generators 
            else:
                self.DoCircuitPlot()
                
            self.MarkSpecialClasses()
            self.DoTheDaisies()


        self._label_buses() # Add labels on top of lines 
        self.bus_labels = {}

        plt.Axes().set_aspect(1.5) # Default aspect ratio
        
        
    def DoLoadShapePlot(self, LoadShapeName):
        pass
        
    def DoTempShapePlot(self, TempShapeName):
        pass
        
    def DoPriceShapePlot(self, PriceShapeName):
        pass
        
    def DoDI_Plot(self, CaseName, CaseYear, iRegisters, PeakDay, MeterName):
        pass
        
    def DoCompareCases(self, CaseName1, CaseName2, WhichFile, Reg):
        pass
        
    def DoYearlyCurvePlot(self, CaseNames, WhichFile, iRegisters):
        pass
        
    def DoVisualizationPlot(self, Element, Quantity):
        pass
        

        
    def _label_buses(self):
        '''Adds text to plot labeling buses'''
        Bus = dss.ActiveCircuit.Buses
        for idx, label in self.bus_labels.items():
            if not label: continue
            Bus.idx = idx
            if idx != Bus.idx: continue # invalid bus
            if Bus.CoordDefined:
                plt.text(Bus.X, Bus.Y, label, color=clBlack, fontsize=8)
       
        
    def _do_bus_labels(self, idx1, idx2):
        if self.BusCoordinateSame(idx1, idx2):
            # Special label for overlapping labels
            del self.bus_labels[idx2]
            self._do_bus_label(idx1, ActiveCircuit.BusList.Get(idx1) + '/' + ActiveCircuit.BusList.Get(idx2), force=True)
        else:
            self._do_bus_label(idx1, ActiveCircuit.BusList.Get(Idx1))
            self._do_bus_label(idx2, ActiveCircuit.BusList.Get(Idx2))
    
    
    def _do_bus_label(self, idx, bus_label, force=False):
        if idx <= 0: return
       
        current_label = self.bus_labels.get(idx, '')
        if force or not current_label:
        # Only label a bus once 
            if self.plot_type == ptMeterZones:
                self.bus_labels[idx] = bus_label + '(' + self.FeederName + ')'
            else:
                self.bus_labels[idx] = bus_label
    

    def _do_auto_add_plot(self):
        Color1Save := Color1
        self.Dots := False
        self.Quantity = pqNone
        self.Color1 = clBlue
        self.DoCircuitPlot()
        self.Color1 = Color1Save
        self.DoGeneralPlot()

    def BusCoordinateSame(self, i1, i2):
        if i1 = 0 or i2 = 0: return False
        
        x1, y1 = self.bus_coords[i1] #TODO: create this
        x2, y2 = self.bus_coords[i2]
        
        try:
            if ((x1 == x2 or (abs(1.0 - abs(x1 / x2)) < Eps)) and
                (y1 == y2 or (abs(1.0 - abs(y1 / y2)) < Eps))):
                return True

        except:
            pass
            
        return False
        
    
#"""