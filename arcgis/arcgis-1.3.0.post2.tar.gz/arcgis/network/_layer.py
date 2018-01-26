from arcgis.gis import Layer, _GISResource


class NetworkLayer(Layer):
    """
    NetworkLayer represents a single network layer. It provides basic
    information about the network layer such as its name, type, and network
    classes. Additionally, depending on the layer type, it provides different
    pieces of information.

    It is a base class for RouteLayer, ServiceAreaLayer, and
    ClosestFacilityLayer.
    """
    def retrieve_travel_modes(self):
        """identify all the valid travel modes that have been defined on the
        network dataset or in the portal if the GIS server is federated"""
        url = self._url + "/retrieveTravelModes"
        params = {"f":"json"}
        return self._con.get(path=url,
                         params=params, token=self._token)


class RouteLayer(NetworkLayer):
    """
    The Route Layer which has common properties of Network Layer
    as well as some attributes unique to Route Network Layer only.
    """
    def solve(self, stops,
              barriers=None,
              polyline_barriers=None,
              polygon_barriers=None,
              travel_mode=None,
              attribute_parameter_values=None,
              return_directions=None,
              return_routes=True,
              return_stops=False,
              return_barriers=False,
              return_polyline_barriers=True,
              return_polygon_barriers=True,
              out_sr=None,
              ignore_invalid_locations=True,
              output_lines=None,
              find_best_sequence=False,
              preserve_first_stop=True,
              preserve_last_stop=True,
              use_time_windows=False,
              start_time=None,
              start_time_is_utc=False,
              accumulate_attribute_names=None,
              impedance_attribute_name=None,
              restriction_attribute_names=None,
              restrict_u_turns=None,
              use_hierarchy=True,
              directions_language=None,
              directions_output_type=None,
              directions_style_name=None,
              directions_length_units=None,
              directions_time_attribute_name=None,
              output_geometry_precision=None,
              output_geometry_precision_units=None,
              return_z=False
              ):
        """The solve operation is performed on a network layer resource.
        The solve operation is supported on a network layer whose layerType
        is esriNAServerRouteLayer. You can provide arguments to the solve
        route operation as query parameters.
        Inputs:
            stops - The set of stops loaded as network locations during analysis.
                    Stops can be specified using a simple comma / semi-colon
                    based syntax or as a JSON structure. If stops are not
                    specified, preloaded stops from the map document are used in
                    the analysis.
            barriers - The set of barriers loaded as network locations during
                       analysis. Barriers can be specified using a simple comma
                       / semi-colon based syntax or as a JSON structure. If
                       barriers are not specified, preloaded barriers from the
                       map document are used in the analysis. If an empty json
                       object is passed ('{}') preloaded barriers are ignored.
            polylineBarriers - The set of polyline barriers loaded as network
                               locations during analysis. If polyline barriers
                               are not specified, preloaded polyline barriers
                               from the map document are used in the analysis.
                               If an empty json object is passed ('{}')
                               preloaded polyline barriers are ignored.
            polygonBarriers - The set of polygon barriers loaded as network
                              locations during analysis. If polygon barriers
                              are not specified, preloaded polygon barriers
                              from the map document are used in the analysis.
                              If an empty json object is passed ('{}') preloaded
                              polygon barriers are ignored.

            travelMode - Travel modes provide override values that help you
                         quickly and consistently model a vehicle or mode of
                         transportation. The chosen travel mode must be
                         preconfigured on the network dataset that the routing
                         service references.
            attributeParameterValues - A set of attribute parameter values that
                                       can be parameterized to determine which
                                       network elements can be used by a vehicle.
            returnDirections - If true, directions will be generated and returned
                               with the analysis results. Default is true.
            returnRoutes - If true, routes will be returned with the analysis
                           results. Default is true.
            returnStops -  If true, stops will be returned with the analysis
                           results. Default is false.
            returnBarriers -  If true, barriers will be returned with the analysis
                              results. Default is false.
            returnPolylineBarriers -  If true, polyline barriers will be returned
                                      with the analysis results. Default is false.
            returnPolygonBarriers - If true, polygon barriers will be returned with
                                    the analysis results. Default is false.
            outSR - The spatial reference of the geometries returned with the
                    analysis results.
            ignoreInvalidLocations - If true, the solver will ignore invalid
                                     locations. Otherwise, it will raise an error.
                                     The default is as defined in the network layer.
            outputLines - The type of output lines to be generated in the result.
                          The default is as defined in the network layer.
            findBestSequence - If true, the solver should re-sequence the route in
                               the optimal order. The default is as defined in the
                               network layer.
            preserveFirstStop - If true, the solver should keep the first stop
                                fixed in the sequence. The default is as defined
                                in the network layer.
            preserveLastStop - If true, the solver should keep the last stop fixed
                               in the sequence. The default is as defined in the
                               network layer.
            useTimeWindows - If true, the solver should consider time windows.
                             The default is as defined in the network layer.
            startTime - The time the route begins. If not specified, the solver
                        will use the default as defined in the network layer.
            startTimeIsUTC - The time zone of the startTime parameter.
            accumulateAttributeNames - The list of network attribute names to be
                                       accumulated with the analysis. The default is
                                       as defined in the network layer. The value
                                       should be specified as a comma separated list
                                       of attribute names. You can also specify a
                                       value of none to indicate that no network
                                       attributes should be accumulated.
            impedanceAttributeName - The network attribute name to be used as the
                                     impedance attribute in analysis. The default is
                                     as defined in the network layer.
            restrictionAttributeNames -The list of network attribute names to be
                                       used as restrictions with the analysis. The
                                       default is as defined in the network layer.
                                       The value should be specified as a comma
                                       separated list of attribute names. You can
                                       also specify a value of none to indicate that
                                       no network attributes should be used as
                                       restrictions.
            restrictUTurns -  Specifies how U-Turns should be restricted in the
                              analysis. The default is as defined in the network
                              layer. Values: esriNFSBAllowBacktrack |
                              esriNFSBAtDeadEndsOnly | esriNFSBNoBacktrack |
                              esriNFSBAtDeadEndsAndIntersections
            useHierarchy -  If true, the hierarchy attribute for the network should
                            be used in analysis. The default is as defined in the
                            network layer.
            directionsLanguage - The language to be used when computing directions.
                                 The default is as defined in the network layer. The
                                 list of supported languages can be found in REST
                                 layer description.
            directionsOutputType -  Defines content, verbosity of returned
                                    directions. The default is esriDOTStandard.
                                    Values: esriDOTComplete | esriDOTCompleteNoEvents
                                    | esriDOTInstructionsOnly | esriDOTStandard |
                                    esriDOTSummaryOnly
            directionsStyleName - The style to be used when returning the directions.
                                  The default is as defined in the network layer. The
                                  list of supported styles can be found in REST
                                  layer description.
            directionsLengthUnits - The length units to use when computing directions.
                                    The default is as defined in the network layer.
                                    Values: esriNAUFeet | esriNAUKilometers |
                                    esriNAUMeters | esriNAUMiles |
                                    esriNAUNauticalMiles | esriNAUYards |
                                    esriNAUUnknown
            directionsTimeAttributeName - The name of network attribute to use for
                                          the drive time when computing directions.
                                          The default is as defined in the network
                                          layer.
            outputGeometryPrecision -  The precision of the output geometry after
                                       generalization. If 0, no generalization of
                                       output geometry is performed. The default is
                                       as defined in the network service
                                       configuration.
            outputGeometryPrecisionUnits - The units of the output geometry
                                           precision. The default value is
                                           esriUnknownUnits. Values: esriUnknownUnits
                                           | esriCentimeters | esriDecimalDegrees |
                                           esriDecimeters | esriFeet | esriInches |
                                           esriKilometers | esriMeters | esriMiles |
                                           esriMillimeters | esriNauticalMiles |
                                           esriPoints | esriYards
            returnZ - If true, Z values will be included in the returned routes and
                       compressed geometry if the network dataset is Z-aware.
                       The default is false.
        """

        if not self.properties.layerType == "esriNAServerRouteLayer":
            raise ValueError("The solve operation is supported on a network "
                             "layer of Route type only")

        url = self._url + "/solve"
        params = {
                    "f" : "json",
                    "stops": stops
                 }

        if not barriers is None:
            params['barriers'] = barriers
        if not polyline_barriers is None:
            params['polylineBarriers'] = polyline_barriers
        if not polygon_barriers is None:
            params['polygonBarriers'] = polygon_barriers
        if not travel_mode is None:
            params['travelMode'] = travel_mode
        if not attribute_parameter_values is None:
            params['attributeParameterValues'] = attribute_parameter_values
        if not return_directions is None:
            params['returnDirections'] = return_directions
        if not return_routes is None:
            params['returnRoutes'] = return_routes
        if not return_stops is None:
            params['returnStops'] = return_stops
        if not return_barriers is None:
            params['returnBarriers'] = return_barriers
        if not return_polyline_barriers is None:
            params['returnPolylineBarriers'] = return_polyline_barriers
        if not return_polygon_barriers is None:
            params['returnPolygonBarriers'] = return_polygon_barriers
        if not out_sr is None:
            params['outSR'] = out_sr
        if not ignore_invalid_locations is None:
            params['ignoreInvalidLocations'] = ignore_invalid_locations
        if not output_lines is None:
            params['outputLines'] = output_lines
        if not find_best_sequence is None:
            params['findBestSequence'] = find_best_sequence
        if not preserve_first_stop is None:
            params['preserveFirstStop'] = preserve_first_stop
        if not preserve_last_stop is None:
            params['preserveLastStop'] = preserve_last_stop
        if not use_time_windows is None:
            params['useTimeWindows'] = use_time_windows
        if not start_time is None:
            params['startTime'] = start_time
        if not start_time_is_utc is None:
            params['startTimeIsUTC'] = start_time_is_utc
        if not accumulate_attribute_names is None:
            params['accumulateAttributeNames'] = accumulate_attribute_names
        if not impedance_attribute_name is None:
            params['impedanceAttributeName'] = impedance_attribute_name
        if not restriction_attribute_names is None:
            params['restrictionAttributeNames'] = restriction_attribute_names
        if not restrict_u_turns is None:
            params['restrictUTurns'] = restrict_u_turns
        if not use_hierarchy is None:
            params['useHierarchy'] = use_hierarchy
        if not directions_language is None:
            params['directionsLanguage'] = directions_language
        if not directions_output_type is None:
            params['directionsOutputType'] = directions_output_type
        if not directions_style_name is None:
            params['directionsStyleName'] = directions_style_name
        if not directions_length_units is None:
            params['directionsLengthUnits'] = directions_length_units
        if not directions_time_attribute_name is None:
            params['directionsTimeAttributeName'] = directions_time_attribute_name
        if not output_geometry_precision is None:
            params['outputGeometryPrecision'] = output_geometry_precision
        if not output_geometry_precision_units is None:
            params['outputGeometryPrecisionUnits'] = output_geometry_precision_units
        if not return_z is None:
            params['returnZ'] = return_z

        return self._con.post(path=url,
                              postdata=params, token=self._token)


class ServiceAreaLayer(NetworkLayer):
    """
    The Service Area Layer which has common properties of Network
    Layer as well as some attributes unique to Service Area Layer
    only.
    """
    def solve_service_area(self, facilities,
                           barriers=None,
                           polyline_barriers=None,
                           polygon_barriers=None,
                           travel_mode=None,
                           attribute_parameter_values=None,
                           default_breaks=None,
                           exclude_sources_from_polygons=None,
                           merge_similar_polygon_ranges=None,
                           output_lines=None,
                           output_polygons=None,
                           overlap_lines=None,
                           overlap_polygons=None,
                           split_lines_at_breaks=None,
                           split_polygons_at_breaks=None,
                           trim_outer_polygon=None,
                           trim_polygon_distance=None,
                           trim_polygon_distance_units=None,
                           return_facilities=False,
                           return_barriers=False,
                           return_polyline_barriers=False,
                           return_polygon_barriers=False,
                           out_sr=None,
                           accumulate_attribute_names=None,
                           impedance_attribute_name=None,
                           restriction_attribute_names=None,
                           restrict_u_turns=None,
                           output_geometry_precision=None,
                           output_geometry_precision_units='esriUnknownUnits',
                           use_hierarchy=None,
                           time_of_day=None,
                           time_of_day_is_utc=None,
                           travel_direction=None,
                           return_z=False):
        """ The solve service area operation is performed on a network layer
        resource of type service area (layerType is esriNAServerServiceArea).
        You can provide arguments to the solve service area operation as
        query parameters.
        Inputs:
            facilities - The set of facilities loaded as network locations
                         during analysis. Facilities can be specified using
                         a simple comma / semi-colon based syntax or as a
                         JSON structure. If facilities are not specified,
                         preloaded facilities from the map document are used
                         in the analysis. If an empty json object is passed
                         ('{}') preloaded facilities are ignored.
            barriers - The set of barriers loaded as network locations during
                       analysis. Barriers can be specified using a simple
                       comma/semicolon-based syntax or as a JSON structure.
                       If barriers are not specified, preloaded barriers from
                       the map document are used in the analysis. If an empty
                       json object is passed ('{}'), preloaded barriers are
                       ignored.
            polylineBarriers - The set of polyline barriers loaded as network
                               locations during analysis. If polyline barriers
                               are not specified, preloaded polyline barriers
                               from the map document are used in the analysis.
                               If an empty json object is passed ('{}'),
                               preloaded polyline barriers are ignored.
            polygonBarriers - The set of polygon barriers loaded as network
                              locations during analysis. If polygon barriers
                              are not specified, preloaded polygon barriers
                              from the map document are used in the analysis.
                              If an empty json object is passed ('{}'),
                              preloaded polygon barriers are ignored.
            travelMode - Travel modes provide override values that help you
                         quickly and consistently model a vehicle or mode of
                         transportation. The chosen travel mode must be
                         preconfigured on the network dataset that the
                         service area service references.
            attributeParameterValues - A set of attribute parameter values that
                                       can be parameterized to determine which
                                       network elements can be used by a vehicle.
            defaultBreaks - A comma-separated list of doubles. The default is
                            defined in the network analysis layer.
            excludeSourcesFromPolygons - A comma-separated list of string names.
                                         The default is defined in the network
                                         analysis layer.

            mergeSimilarPolygonRanges - If true, similar ranges will be merged
                                        in the result polygons. The default is
                                        defined in the network analysis layer.
            outputLines - The type of lines(s) generated. The default is as
                          defined in the network analysis layer.
            outputPolygons - The type of polygon(s) generated. The default is
                             as defined in the network analysis layer.
            overlapLines - Indicates if the lines should overlap from multiple
                           facilities. The default is defined in the network
                           analysis layer.
            overlapPolygons - Indicates if the polygons for all facilities
                              should overlap. The default is defined in the
                              network analysis layer.
            splitLinesAtBreaks - If true, lines will be split at breaks. The
                                 default is defined in the network analysis
                                 layer.
            splitPolygonsAtBreaks - If true, polygons will be split at breaks.
                                    The default is defined in the network
                                    analysis layer.
            trimOuterPolygon -  If true, the outermost polygon (at the maximum
                                break value) will be trimmed. The default is
                                defined in the network analysis layer.
            trimPolygonDistance -  If polygons are being trimmed, provides the
                                   distance to trim. The default is defined in
                                   the network analysis layer.
            trimPolygonDistanceUnits - If polygons are being trimmed, specifies
                                       the units of the trimPolygonDistance. The
                                       default is defined in the network analysis
                                       layer.
            returnFacilities - If true, facilities will be returned with the
                               analysis results. Default is false.
            returnBarriers - If true, barriers will be returned with the analysis
                             results. Default is false.
            returnPolylineBarriers - If true, polyline barriers will be returned
                                     with the analysis results. Default is false.
            returnPolygonBarriers - If true, polygon barriers will be returned
                                    with the analysis results. Default is false.
            outSR - The well-known ID of the spatial reference for the geometries
                    returned with the analysis results. If outSR is not specified,
                    the geometries are returned in the spatial reference of the map.
            accumulateAttributeNames - The list of network attribute names to be
                                       accumulated with the analysis. The default
                                       is as defined in the network analysis layer.
                                       The value should be specified as a comma
                                       separated list of attribute names. You can
                                       also specify a value of none to indicate that
                                       no network attributes should be accumulated.
            impedanceAttributeName - The network attribute name to be used as the
                                     impedance attribute in analysis. The default
                                     is as defined in the network analysis layer.
            restrictionAttributeNames - The list of network attribute names to be
                                        used as restrictions with the analysis. The
                                        default is as defined in the network analysis
                                        layer. The value should be specified as a
                                        comma separated list of attribute names.
                                        You can also specify a value of none to
                                        indicate that no network attributes should
                                        be used as restrictions.
            restrictUTurns - Specifies how U-Turns should be restricted in the
                             analysis. The default is as defined in the network
                             analysis layer. Values: esriNFSBAllowBacktrack |
                             esriNFSBAtDeadEndsOnly | esriNFSBNoBacktrack |
                             esriNFSBAtDeadEndsAndIntersections
            outputGeometryPrecision - The precision of the output geometry after
                                      generalization. If 0, no generalization of
                                      output geometry is performed. The default is
                                      as defined in the network service configuration.
            outputGeometryPrecisionUnits - The units of the output geometry precision.
                                           The default value is esriUnknownUnits.
                                           Values: esriUnknownUnits | esriCentimeters |
                                           esriDecimalDegrees | esriDecimeters |
                                           esriFeet | esriInches | esriKilometers |
                                           esriMeters | esriMiles | esriMillimeters |
                                           esriNauticalMiles | esriPoints | esriYards
            useHierarchy - If true, the hierarchy attribute for the network should be
                           used in analysis. The default is as defined in the network
                           layer. This cannot be used in conjunction with outputLines.
            timeOfDay - The date and time at the facility. If travelDirection is set
                        to esriNATravelDirectionToFacility, the timeOfDay value
                        specifies the arrival time at the facility. if travelDirection
                        is set to esriNATravelDirectionFromFacility, the timeOfDay
                        value is the departure time from the facility. The time zone
                        for timeOfDay is specified by timeOfDayIsUTC.
            timeOfDayIsUTC - The time zone or zones of the timeOfDay parameter. When
                             set to false, which is the default value, the timeOfDay
                             parameter refers to the time zone or zones in which the
                             facilities are located. Therefore, the start or end times
                             of the service areas are staggered by time zone.
            travelDirection - Options for traveling to or from the facility. The
                              default is defined in the network analysis layer.
            returnZ - If true, Z values will be included in saPolygons and saPolylines
                      geometry if the network dataset is Z-aware.
    """
        if not self.properties.layerType == "esriNAServerServiceAreaLayer":
            raise TypeError("The solveServiceArea operation is supported on a network "
                             "layer of Service Area type only")

        url = self._url + "/solveServiceArea"
        params = {
                "f" : "json",
                "facilities": facilities
                }

        if not barriers is None:
            params['barriers'] = barriers
        if not polyline_barriers is None:
            params['polylineBarriers'] = polyline_barriers
        if not polygon_barriers is None:
            params['polygonBarriers'] = polygon_barriers
        if not travel_mode is None:
            params['travelMode'] = travel_mode
        if not attribute_parameter_values is None:
            params['attributeParameterValues'] = attribute_parameter_values
        if not default_breaks is None:
            params['defaultBreaks'] = default_breaks
        if not exclude_sources_from_polygons is None:
            params['excludeSourcesFromPolygons'] = exclude_sources_from_polygons
        if not merge_similar_polygon_ranges is None:
            params['mergeSimilarPolygonRanges'] = merge_similar_polygon_ranges
        if not output_lines is None:
            params['outputLines'] = output_lines
        if not output_polygons is None:
            params['outputPolygons'] = output_polygons
        if not overlap_lines is None:
            params['overlapLines'] = overlap_lines
        if not overlap_polygons is None:
            params['overlapPolygons'] = overlap_polygons
        if not split_lines_at_breaks is None:
            params['splitLinesAtBreaks'] = split_lines_at_breaks
        if not split_polygons_at_breaks is None:
            params['splitPolygonsAtBreaks'] = split_polygons_at_breaks
        if not trim_outer_polygon is None:
            params['trimOuterPolygon'] = trim_outer_polygon
        if not trim_polygon_distance is None:
            params['trimPolygonDistance'] = trim_polygon_distance
        if not trim_polygon_distance_units is None:
            params['trimPolygonDistanceUnits'] = trim_polygon_distance_units
        if not return_facilities is None:
            params['returnFacilities'] = return_facilities
        if not return_barriers is None:
            params['returnBarriers'] = return_barriers
        if not return_polyline_barriers is None:
            params['returnPolylineBarriers'] = return_polyline_barriers
        if not return_polygon_barriers is None:
            params['returnPolygonBarriers'] = return_polygon_barriers
        if not out_sr is None:
            params['outSR'] = out_sr
        if not accumulate_attribute_names is None:
            params['accumulateAttributeNames'] = accumulate_attribute_names
        if not impedance_attribute_name is None:
            params['impedanceAttributeName'] = impedance_attribute_name
        if not restriction_attribute_names is None:
            params['restrictionAttributeNames'] = restriction_attribute_names
        if not restrict_u_turns is None:
            params['restrictUTurns'] = restrict_u_turns
        if not output_geometry_precision is None:
            params['outputGeometryPrecision'] = output_geometry_precision
        if not output_geometry_precision_units is None:
            params['outputGeometryPrecisionUnits'] = output_geometry_precision_units
        if not use_hierarchy is None:
            params['useHierarchy'] = use_hierarchy
        if not time_of_day is None:
            params['timeOfDay'] = time_of_day
        if not time_of_day_is_utc is None:
            params['timeOfDayIsUTC'] = time_of_day_is_utc
        if not travel_direction is None:
            params['travelDirection'] = travel_direction
        if not return_z is None:
            params['returnZ'] = return_z

        return self._con.post(path=url,
                              postdata=params, token=self._token)


class ClosestFacilityLayer(NetworkLayer):
    """
    The Closest Facility Network Layer which has common properties of Network
    Layer as well as some attributes unique to Closest Facility Layer
    only.
    """
    def solve_closest_facility(self, incidents, facilities,
                               barriers=None,
                               polyline_barriers=None,
                               polygon_barriers=None,
                               travel_mode=None,
                               attribute_parameter_values=None,
                               return_directions=None,
                               directions_language=None,
                               directions_style_name=None,
                               directions_length_units=None,
                               directions_time_attribute_name=None,
                               return_cf_routes=True,
                               return_facilities=False,
                               return_incidents=False,
                               return_barriers=False,
                               return_polyline_barriers=False,
                               return_polygon_barriers=False,
                               output_lines=None,
                               default_cutoff=None,
                               default_target_facility_count=None,
                               travel_direction=None,
                               out_sr=None,
                               accumulate_attribute_names=None,
                               impedance_attribute_name=None,
                               restriction_attribute_names=None,
                               restrict_u_turns=None,
                               use_hierarchy=True,
                               output_geometry_precision=None,
                               output_geometry_precision_units=None,
                               time_of_day=None,
                               time_of_day_is_utc=None,
                               time_of_day_usage=None,
                               return_z=False):
        """The solve operation is performed on a network layer resource of
        type closest facility (layerType is esriNAServerClosestFacilityLayer).
        You can provide arguments to the solve route operation as query
        parameters.
        Inputs:
            facilities  - The set of facilities loaded as network locations
                          during analysis. Facilities can be specified using
                          a simple comma / semi-colon based syntax or as a
                          JSON structure. If facilities are not specified,
                          preloaded facilities from the map document are used
                          in the analysis.
            incidents - The set of incidents loaded as network locations
                        during analysis. Incidents can be specified using
                        a simple comma / semi-colon based syntax or as a
                        JSON structure. If incidents are not specified,
                        preloaded incidents from the map document are used
                        in the analysis.
            barriers - The set of barriers loaded as network locations during
                       analysis. Barriers can be specified using a simple comma
                       / semi-colon based syntax or as a JSON structure. If
                       barriers are not specified, preloaded barriers from the
                       map document are used in the analysis. If an empty json
                       object is passed ('{}') preloaded barriers are ignored.
            polylineBarriers - The set of polyline barriers loaded as network
                               locations during analysis. If polyline barriers
                               are not specified, preloaded polyline barriers
                               from the map document are used in the analysis.
                               If an empty json object is passed ('{}')
                               preloaded polyline barriers are ignored.
            polygonBarriers - The set of polygon barriers loaded as network
                              locations during analysis. If polygon barriers
                              are not specified, preloaded polygon barriers
                              from the map document are used in the analysis.
                              If an empty json object is passed ('{}') preloaded
                              polygon barriers are ignored.
            travelMode - Travel modes provide override values that help you
                         quickly and consistently model a vehicle or mode of
                         transportation. The chosen travel mode must be
                         preconfigured on the network dataset that the routing
                         service references.
            attributeParameterValues - A set of attribute parameter values that
                                       can be parameterized to determine which
                                       network elements can be used by a vehicle.
            returnDirections - If true, directions will be generated and returned
                               with the analysis results. Default is true.
            directionsLanguage - The language to be used when computing directions.
                                 The default is as defined in the network layer. The
                                 list of supported languages can be found in REST
                                 layer description.
            directionsOutputType -  Defines content, verbosity of returned
                                    directions. The default is esriDOTStandard.
                                    Values: esriDOTComplete | esriDOTCompleteNoEvents
                                    | esriDOTInstructionsOnly | esriDOTStandard |
                                    esriDOTSummaryOnly
            directionsStyleName - The style to be used when returning the directions.
                                  The default is as defined in the network layer. The
                                  list of supported styles can be found in REST
                                  layer description.
            directionsLengthUnits - The length units to use when computing directions.
                                    The default is as defined in the network layer.
                                    Values: esriNAUFeet | esriNAUKilometers |
                                    esriNAUMeters | esriNAUMiles |
                                    esriNAUNauticalMiles | esriNAUYards |
                                    esriNAUUnknown
            directionsTimeAttributeName - The name of network attribute to use for
                                          the drive time when computing directions.
                                          The default is as defined in the network
                                          layer.
            returnCFRoutes - If true, closest facilities routes will be returned
                             with the analysis results. Default is true.
            returnFacilities -  If true, facilities  will be returned with the
                                analysis results. Default is false.
            returnIncidents - If true, incidents will be returned with the
                              analysis results. Default is false.
            returnBarriers -  If true, barriers will be returned with the analysis
                              results. Default is false.
            returnPolylineBarriers -  If true, polyline barriers will be returned
                                      with the analysis results. Default is false.
            returnPolygonBarriers - If true, polygon barriers will be returned with
                                    the analysis results. Default is false.
            outputLines - The type of output lines to be generated in the result.
                          The default is as defined in the network layer.
            defaultCutoff - The default cutoff value to stop traversing.
            defaultTargetFacilityCount - The default number of facilities to find.
            travelDirection - Options for traveling to or from the facility.
                              The default is defined in the network layer.
                              Values: esriNATravelDirectionFromFacility |
                              esriNATravelDirectionToFacility
            outSR - The spatial reference of the geometries returned with the
                    analysis results.
            accumulateAttributeNames - The list of network attribute names to be
                                       accumulated with the analysis. The default is
                                       as defined in the network layer. The value
                                       should be specified as a comma separated list
                                       of attribute names. You can also specify a
                                       value of none to indicate that no network
                                       attributes should be accumulated.
            impedanceAttributeName - The network attribute name to be used as the
                                     impedance attribute in analysis. The default is
                                     as defined in the network layer.
            restrictionAttributeNames -The list of network attribute names to be
                                       used as restrictions with the analysis. The
                                       default is as defined in the network layer.
                                       The value should be specified as a comma
                                       separated list of attribute names. You can
                                       also specify a value of none to indicate that
                                       no network attributes should be used as
                                       restrictions.
            restrictUTurns -  Specifies how U-Turns should be restricted in the
                              analysis. The default is as defined in the network
                              layer. Values: esriNFSBAllowBacktrack |
                              esriNFSBAtDeadEndsOnly | esriNFSBNoBacktrack |
                              esriNFSBAtDeadEndsAndIntersections
            useHierarchy -  If true, the hierarchy attribute for the network should
                            be used in analysis. The default is as defined in the
                            network layer.
            outputGeometryPrecision -  The precision of the output geometry after
                                       generalization. If 0, no generalization of
                                       output geometry is performed. The default is
                                       as defined in the network service
                                       configuration.
            outputGeometryPrecisionUnits - The units of the output geometry
                                           precision. The default value is
                                           esriUnknownUnits. Values: esriUnknownUnits
                                           | esriCentimeters | esriDecimalDegrees |
                                           esriDecimeters | esriFeet | esriInches |
                                           esriKilometers | esriMeters | esriMiles |
                                           esriMillimeters | esriNauticalMiles |
                                           esriPoints | esriYards
            timeOfDay - Arrival or departure date and time. Values: specified by
                        number of milliseconds since midnight Jan 1st, 1970, UTC.
            timeOfDayIsUTC - The time zone of the timeOfDay parameter. By setting
                             timeOfDayIsUTC to true, the timeOfDay parameter refers
                             to Coordinated Universal Time (UTC). Choose this option
                             if you want to find what's nearest for a specific time,
                             such as now, but aren't certain in which time zone the
                             facilities or incidents will be located.
            timeOfDayUsage - Defines the way timeOfDay value is used. The default
                             is as defined in the network layer.
                             Values: esriNATimeOfDayUseAsStartTime |
                             esriNATimeOfDayUseAsEndTime
            returnZ - If true, Z values will be included in the returned routes and
                       compressed geometry if the network dataset is Z-aware.
                       The default is false.
    """

        if not self.properties.layerType == "esriNAServerClosestFacilityLayer":
            raise TypeError("The solveClosestFacility operation is supported on a network "
                             "layer of Closest Facility type only")

        url = self._url + "/solveClosestFacility"
        params = {
                "f" : "json",
                "facilities": facilities,
                "incidents": incidents
                }

        if not barriers is None:
            params['barriers'] = barriers
        if not polyline_barriers is None:
            params['polylineBarriers'] = polyline_barriers
        if not polygon_barriers is None:
            params['polygonBarriers'] = polygon_barriers
        if not travel_mode is None:
            params['travelMode'] = travel_mode
        if not attribute_parameter_values is None:
            params['attributeParameterValues'] = attribute_parameter_values
        if not return_directions is None:
            params['returnDirections'] = return_directions
        if not directions_language is None:
            params['directionsLanguage'] = directions_language
        if not directions_style_name is None:
            params['directionsStyleName'] = directions_style_name
        if not directions_length_units is None:
            params['directionsLengthUnits'] = directions_length_units
        if not directions_time_attribute_name is None:
            params['directionsTimeAttributeName'] = directions_time_attribute_name
        if not return_cf_routes is None:
            params['returnCFRoutes'] = return_cf_routes
        if not return_facilities is None:
            params['returnFacilities'] = return_facilities
        if not return_incidents is None:
            params['returnIncidents'] = return_incidents
        if not return_barriers is None:
            params['returnBarriers'] = return_barriers
        if not return_polyline_barriers is None:
            params['returnPolylineBarriers'] = return_polyline_barriers
        if not return_polygon_barriers is None:
            params['returnPolygonBarriers'] = return_polygon_barriers
        if not output_lines is None:
            params['outputLines'] = output_lines
        if not default_cutoff is None:
            params['defaultCutoff'] = default_cutoff
        if not default_target_facility_count is None:
            params['defaultTargetFacilityCount'] = default_target_facility_count
        if not travel_direction is None:
            params['travelDirection'] = travel_direction
        if not out_sr is None:
            params['outSR'] = out_sr
        if not accumulate_attribute_names is None:
            params['accumulateAttributeNames'] = accumulate_attribute_names
        if not impedance_attribute_name is None:
            params['impedanceAttributeName'] = impedance_attribute_name
        if not restriction_attribute_names is None:
            params['restrictionAttributeNames'] = restriction_attribute_names
        if not restrict_u_turns is None:
            params['restrictUTurns'] = restrict_u_turns
        if not use_hierarchy is None:
            params['useHierarchy'] = use_hierarchy
        if not output_geometry_precision is None:
            params['outputGeometryPrecision'] = output_geometry_precision
        if not output_geometry_precision_units is None:
            params['outputGeometryPrecisionUnits'] = output_geometry_precision_units
        if not time_of_day is None:
            params['timeOfDay'] = time_of_day
        if not time_of_day_is_utc is None:
            params['timeOfDayIsUTC'] = time_of_day_is_utc
        if not time_of_day_usage is None:
            params['timeOfDayUsage'] = time_of_day_usage
        if not return_z is None:
            params['returnZ'] = return_z

        return self._con.post(path=url, postdata=params, token=self._token)


class NetworkDataset(_GISResource):
    """
    A network dataset containing a collection of network layers including route layers,
    service area layers and closest facility layers.
    """
    def __init__(self, url, gis=None):
        super(NetworkDataset, self).__init__(url, gis)
        try:
            from ..gis.server._service._adminfactory import AdminServiceGen
            self.service = AdminServiceGen(service=self, gis=gis)
        except: pass
        self._load_layers()

    @classmethod
    def fromitem(cls, item):
        """Creates a network dataset from a 'Network Analysis Service' Item in the GIS"""
        if not item.type == 'Network Analysis Service':
            raise TypeError("item must be a type of Network Analysis Service, not " + item.type)

        return cls(item.url, item._gis)

    #----------------------------------------------------------------------
    def _load_layers(self):
        """loads the various layer types"""
        self._closestFacilityLayers = []
        self._routeLayers = []
        self._serviceAreaLayers = []
        params = {
            "f" : "json",
        }
        json_dict = self._con.get(path=self._url, params=params, token=self._token)
        for k,v in json_dict.items():
            if k == "routeLayers" and json_dict[k]:
                self._routeLayers = []
                for rl in v:
                    self._routeLayers.append(
                        RouteLayer(url=self._url + "/%s" % rl,
                                   gis=self._gis))
            elif k == "serviceAreaLayers" and json_dict[k]:
                self._serviceAreaLayers = []
                for sal in v:
                    self._serviceAreaLayers.append(
                        ServiceAreaLayer(url=self._url + "/%s" % sal,
                                         gis=self._gis))
            elif k == "closestFacilityLayers" and json_dict[k]:
                self._closestFacilityLayers = []
                for cf in v:
                    self._closestFacilityLayers.append(
                        ClosestFacilityLayer(url=self._url + "/%s" % cf,
                                             gis=self._gis))
    #----------------------------------------------------------------------
    @property
    def route_layers(self):
        """List of route layers in this network dataset"""
        if self._routeLayers is None:
            self._load_layers()
        return self._routeLayers
    #----------------------------------------------------------------------
    @property
    def service_area_layers(self):
        """List of service area layers in this network dataset"""
        if self._serviceAreaLayers is None:
            self._load_layers()
        return self._serviceAreaLayers
    #----------------------------------------------------------------------
    @property
    def closest_facility_layers(self):
        """List of closest facility layers in this network dataset"""
        if self._closestFacilityLayers is None:
            self._load_layers()
        return self._closestFacilityLayers
