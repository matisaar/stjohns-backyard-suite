#!/usr/bin/env python3
"""
Generate an IFC BIM model for the St. John's 430 sqft backyard suite.
Outputs: web/static/model.ifc

Building: 21'-6" x 20'-0" (6.553m x 6.096m), mono-slope roof
          Left wall 9'-6" (2.896m), Right wall 7'-0" (2.134m)
          4" concrete slab on grade, 2x6 framed walls
"""

import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.placement
import math
import time
import uuid

# ── Unit conversions ──
FT = 0.3048   # feet to metres
IN = 0.0254   # inches to metres

# ── Building dimensions (metres) ──
BLD_W = 21.5 * FT    # 6.553 m  (E-W, x-axis)
BLD_D = 20.0 * FT    # 6.096 m  (N-S, y-axis)
SLAB_T = 4 * IN      # 0.102 m
WALL_T = 6 * IN      # 0.152 m  (2x6 framing)
WALL_H_HIGH = 9.5 * FT   # 2.896 m  (left/west wall)
WALL_H_LOW  = 7.0 * FT   # 2.134 m  (right/east wall)
ROOF_OVERHANG = 12 * IN   # 0.305 m

# Window: 30"x48" casement
WIN_W = 30 * IN    # 0.762 m
WIN_H = 48 * IN    # 1.219 m
WIN_SILL = 36 * IN  # 0.914 m above slab

# Door: 34"x80" Dusco Moderna
DOOR_W = 34 * IN   # 0.864 m
DOOR_H = 80 * IN   # 2.032 m


def create_guid():
    return ifcopenshell.guid.compress(uuid.uuid1().hex)


def create_model():
    model = ifcopenshell.api.run("project.create_file", version="IFC4")

    # ── Project + Site + Building + Storey ──
    project = ifcopenshell.api.run("root.create_entity", model,
        ifc_class="IfcProject", name="SJ Backyard Suite")

    # Units: metres
    ifcopenshell.api.run("unit.assign_unit", model,
        length={"is_metric": True, "raw": "METRES"},
        area={"is_metric": True, "raw": "SQUARE_METRE"},
        volume={"is_metric": True, "raw": "CUBIC_METRE"})

    # Geometric context
    ctx = ifcopenshell.api.run("context.add_context", model, context_type="Model")
    body = ifcopenshell.api.run("context.add_context", model,
        context_type="Model", context_identifier="Body",
        target_view="MODEL_VIEW", parent=ctx)

    site = ifcopenshell.api.run("root.create_entity", model,
        ifc_class="IfcSite", name="97 Mayor Avenue")
    building = ifcopenshell.api.run("root.create_entity", model,
        ifc_class="IfcBuilding", name="Backyard Suite")
    storey = ifcopenshell.api.run("root.create_entity", model,
        ifc_class="IfcBuildingStorey", name="Ground Floor")

    ifcopenshell.api.run("aggregate.assign_object", model,
        relating_object=project, products=[site])
    ifcopenshell.api.run("aggregate.assign_object", model,
        relating_object=site, products=[building])
    ifcopenshell.api.run("aggregate.assign_object", model,
        relating_object=building, products=[storey])

    # ── Helper: create a simple extruded rectangle ──
    def make_rectangle_profile(w, d):
        return model.create_entity("IfcRectangleProfileDef",
            ProfileType="AREA",
            XDim=float(w),
            YDim=float(d))

    def make_axis2_placement_3d(x=0.0, y=0.0, z=0.0):
        point = model.create_entity("IfcCartesianPoint",
            Coordinates=(float(x), float(y), float(z)))
        return model.create_entity("IfcAxis2Placement3D", Location=point)

    def make_direction(x, y, z):
        return model.create_entity("IfcDirection",
            DirectionRatios=(float(x), float(y), float(z)))

    def make_local_placement(x=0.0, y=0.0, z=0.0, relative_to=None):
        axis2 = make_axis2_placement_3d(x, y, z)
        return model.create_entity("IfcLocalPlacement",
            PlacementRelTo=relative_to,
            RelativePlacement=axis2)

    def make_extruded_solid(profile, height, direction=None):
        if direction is None:
            direction = make_direction(0.0, 0.0, 1.0)
        return model.create_entity("IfcExtrudedAreaSolid",
            SweptArea=profile,
            Position=make_axis2_placement_3d(),
            ExtrudedDirection=direction,
            Depth=float(height))

    def assign_body(entity, solid):
        shape_rep = model.create_entity("IfcShapeRepresentation",
            ContextOfItems=body,
            RepresentationIdentifier="Body",
            RepresentationType="SweptSolid",
            Items=[solid])
        product_shape = model.create_entity("IfcProductDefinitionShape",
            Representations=[shape_rep])
        entity.Representation = product_shape

    def make_colour(r, g, b):
        """Create surface style with colour."""
        colour = model.create_entity("IfcColourRgb", Red=r, Green=g, Blue=b)
        rendering = model.create_entity("IfcSurfaceStyleRendering",
            SurfaceColour=colour,
            ReflectanceMethod="NOTDEFINED")
        style = model.create_entity("IfcSurfaceStyle",
            Side="BOTH",
            Styles=[rendering])
        return model.create_entity("IfcPresentationStyleAssignment",
            Styles=[style])

    def apply_colour(entity, r, g, b):
        """Apply colour to all shape representations of an entity."""
        if not entity.Representation:
            return
        style_assign = make_colour(r, g, b)
        for rep in entity.Representation.Representations:
            for item in rep.Items:
                styled = model.create_entity("IfcStyledItem",
                    Item=item,
                    Styles=[style_assign])

    storey_placement = make_local_placement(0, 0, 0)
    storey.ObjectPlacement = storey_placement

    # ══════════════════════════════════════════
    #  FOUNDATION — Concrete slab on grade
    # ══════════════════════════════════════════
    slab = ifcopenshell.api.run("root.create_entity", model,
        ifc_class="IfcSlab", name="Concrete Slab on Grade",
        predefined_type="FLOOR")
    slab.ObjectPlacement = make_local_placement(0, 0, 0, storey_placement)
    slab_profile = make_rectangle_profile(BLD_W, BLD_D)
    slab_solid = make_extruded_solid(slab_profile, SLAB_T)
    # Center the profile on the footprint
    slab_solid.Position = make_axis2_placement_3d(BLD_W / 2, BLD_D / 2, 0)
    assign_body(slab, slab_solid)
    apply_colour(slab, 0.53, 0.53, 0.53)  # concrete grey
    ifcopenshell.api.run("spatial.assign_container", model,
        relating_structure=storey, products=[slab])

    # Gravel base (below slab)
    gravel = ifcopenshell.api.run("root.create_entity", model,
        ifc_class="IfcSlab", name="Gravel Base (4 in)",
        predefined_type="BASESLAB")
    gravel.ObjectPlacement = make_local_placement(0, 0, -0.1, storey_placement)
    gravel_profile = make_rectangle_profile(BLD_W + 0.3, BLD_D + 0.3)
    gravel_solid = make_extruded_solid(gravel_profile, 0.1)
    gravel_solid.Position = make_axis2_placement_3d(BLD_W / 2, BLD_D / 2, 0)
    assign_body(gravel, gravel_solid)
    apply_colour(gravel, 0.4, 0.4, 0.35)
    ifcopenshell.api.run("spatial.assign_container", model,
        relating_structure=storey, products=[gravel])

    # XPS under-slab insulation
    xps = ifcopenshell.api.run("root.create_entity", model,
        ifc_class="IfcSlab", name="XPS Under-Slab R-10 (2 in)",
        predefined_type="FLOOR")
    xps.ObjectPlacement = make_local_placement(0, 0, -0.05, storey_placement)
    xps_profile = make_rectangle_profile(BLD_W, BLD_D)
    xps_solid = make_extruded_solid(xps_profile, 0.05)
    xps_solid.Position = make_axis2_placement_3d(BLD_W / 2, BLD_D / 2, 0)
    assign_body(xps, xps_solid)
    apply_colour(xps, 0.13, 0.53, 0.87)  # blue XPS
    ifcopenshell.api.run("spatial.assign_container", model,
        relating_structure=storey, products=[xps])

    # ══════════════════════════════════════════
    #  WALLS — 2x6 framed, mono-slope
    # ══════════════════════════════════════════
    wall_base = SLAB_T  # walls start on top of slab

    def create_wall(name, length, height, x, y, z, angle_deg=0):
        """Create a wall as an extruded rectangle rotated to position."""
        wall = ifcopenshell.api.run("root.create_entity", model,
            ifc_class="IfcWall", name=name,
            predefined_type="STANDARD")

        # Placement with rotation
        rad = math.radians(angle_deg)
        point = model.create_entity("IfcCartesianPoint",
            Coordinates=(float(x), float(y), float(z)))
        dir_z = make_direction(0.0, 0.0, 1.0)
        dir_x = make_direction(math.cos(rad), math.sin(rad), 0.0)
        axis2 = model.create_entity("IfcAxis2Placement3D",
            Location=point, Axis=dir_z, RefDirection=dir_x)
        wall.ObjectPlacement = model.create_entity("IfcLocalPlacement",
            PlacementRelTo=storey_placement,
            RelativePlacement=axis2)

        profile = make_rectangle_profile(length, WALL_T)
        solid = make_extruded_solid(profile, height)
        solid.Position = make_axis2_placement_3d(length / 2, WALL_T / 2, 0)
        assign_body(wall, solid)
        apply_colour(wall, 0.54, 0.6, 0.54)  # sage green siding
        ifcopenshell.api.run("spatial.assign_container", model,
            relating_structure=storey, products=[wall])
        return wall

    # Front wall (south, y=0) — full width, high side height
    front_wall = create_wall("Front Wall (South)", BLD_W, WALL_H_HIGH,
                             0, 0, wall_base, 0)

    # Back wall (north, y=BLD_D) — full width, high side height
    back_wall = create_wall("Back Wall (North)", BLD_W, WALL_H_HIGH,
                            0, BLD_D - WALL_T, wall_base, 0)

    # Left wall (west, x=0) — high side
    left_wall = create_wall("Left Wall (West) — High Side", BLD_D, WALL_H_HIGH,
                            0, 0, wall_base, 90)

    # Right wall (east, x=BLD_W) — low side
    right_wall = create_wall("Right Wall (East) — Low Side", BLD_D, WALL_H_LOW,
                             BLD_W, 0, wall_base, 90)

    # ══════════════════════════════════════════
    #  ROOF — Mono-slope (shed roof)
    # ══════════════════════════════════════════
    roof_base_z = wall_base + WALL_H_LOW  # low side
    roof_top_z = wall_base + WALL_H_HIGH   # high side
    roof_angle = math.atan2(roof_top_z - roof_base_z, BLD_W)

    roof_slab = ifcopenshell.api.run("root.create_entity", model,
        ifc_class="IfcRoof", name="Mono-Slope Roof — IKO Cambridge Shingles")

    # Roof as a tilted slab
    roof_run = BLD_W + ROOF_OVERHANG * 2
    roof_hyp = roof_run / math.cos(roof_angle)
    roof_depth = BLD_D + ROOF_OVERHANG * 2

    point = model.create_entity("IfcCartesianPoint",
        Coordinates=(float(-ROOF_OVERHANG), float(-ROOF_OVERHANG), float(roof_base_z)))
    dir_z_roof = make_direction(-math.sin(roof_angle), 0.0, math.cos(roof_angle))
    dir_x_roof = make_direction(math.cos(roof_angle), 0.0, math.sin(roof_angle))
    axis2_roof = model.create_entity("IfcAxis2Placement3D",
        Location=point, Axis=dir_z_roof, RefDirection=dir_x_roof)
    roof_slab.ObjectPlacement = model.create_entity("IfcLocalPlacement",
        PlacementRelTo=storey_placement,
        RelativePlacement=axis2_roof)

    roof_profile = make_rectangle_profile(roof_hyp, roof_depth)
    roof_solid = make_extruded_solid(roof_profile, 0.04)  # shingle layer thickness
    roof_solid.Position = make_axis2_placement_3d(roof_hyp / 2, roof_depth / 2, 0)
    assign_body(roof_slab, roof_solid)
    apply_colour(roof_slab, 0.17, 0.17, 0.19)  # dark shingle
    ifcopenshell.api.run("spatial.assign_container", model,
        relating_structure=storey, products=[roof_slab])

    # Fascia board — front
    fascia_f = ifcopenshell.api.run("root.create_entity", model,
        ifc_class="IfcMember", name="Fascia — Front",
        predefined_type="USERDEFINED")
    fascia_f.ObjectPlacement = make_local_placement(
        -ROOF_OVERHANG, -ROOF_OVERHANG, roof_base_z, storey_placement)
    fascia_profile = make_rectangle_profile(roof_hyp, 0.02)
    fascia_solid = make_extruded_solid(fascia_profile, 0.18)
    fascia_solid.Position = make_axis2_placement_3d(roof_hyp / 2, 0.01, 0)
    assign_body(fascia_f, fascia_solid)
    apply_colour(fascia_f, 0.1, 0.1, 0.12)  # dark metal
    ifcopenshell.api.run("spatial.assign_container", model,
        relating_structure=storey, products=[fascia_f])

    # ══════════════════════════════════════════
    #  WINDOWS — 6x triple-pane casement
    # ══════════════════════════════════════════
    def create_window(name, x, y, z, w, h, angle_deg=0):
        win = ifcopenshell.api.run("root.create_entity", model,
            ifc_class="IfcWindow", name=name)
        win.OverallWidth = float(w)
        win.OverallHeight = float(h)

        rad = math.radians(angle_deg)
        point = model.create_entity("IfcCartesianPoint",
            Coordinates=(float(x), float(y), float(z)))
        dir_z = make_direction(0.0, 0.0, 1.0)
        dir_x = make_direction(math.cos(rad), math.sin(rad), 0.0)
        axis2 = model.create_entity("IfcAxis2Placement3D",
            Location=point, Axis=dir_z, RefDirection=dir_x)
        win.ObjectPlacement = model.create_entity("IfcLocalPlacement",
            PlacementRelTo=storey_placement,
            RelativePlacement=axis2)

        # Frame + glass as nested extrusions
        # Outer frame
        frame_profile = make_rectangle_profile(w, WALL_T)
        frame_solid = make_extruded_solid(frame_profile, h)
        frame_solid.Position = make_axis2_placement_3d(w/2, WALL_T/2, 0)

        # Glass pane (thinner, inset)
        glass_profile = make_rectangle_profile(w - 0.08, 0.02)
        glass_solid = make_extruded_solid(glass_profile, h - 0.08)
        glass_solid.Position = make_axis2_placement_3d(w/2, WALL_T/2, 0.04)

        # Use frame for body representation
        shape_rep = model.create_entity("IfcShapeRepresentation",
            ContextOfItems=body,
            RepresentationIdentifier="Body",
            RepresentationType="SweptSolid",
            Items=[frame_solid, glass_solid])

        # Apply glass colour to glass, frame colour to frame
        frame_style = make_colour(0.9, 0.9, 0.9)  # white vinyl
        glass_style = make_colour(0.53, 0.73, 0.83)  # blue glass
        model.create_entity("IfcStyledItem", Item=frame_solid, Styles=[frame_style])
        model.create_entity("IfcStyledItem", Item=glass_solid, Styles=[glass_style])

        product_shape = model.create_entity("IfcProductDefinitionShape",
            Representations=[shape_rep])
        win.Representation = product_shape
        ifcopenshell.api.run("spatial.assign_container", model,
            relating_structure=storey, products=[win])
        return win

    sill_z = wall_base + WIN_SILL

    # Front wall — 3 windows
    create_window("Front Window 1", 0.8, 0, sill_z, WIN_W, WIN_H, 0)
    create_window("Front Window 2", 2.4, 0, sill_z, WIN_W, WIN_H, 0)
    create_window("Front Window 3", 4.0, 0, sill_z, WIN_W, WIN_H, 0)

    # Left wall — 1 window
    create_window("Left Window", 0, BLD_D * 0.4, sill_z, WIN_W, WIN_H, 90)

    # Right wall — 2 windows
    create_window("Right Window 1", BLD_W, BLD_D * 0.25, sill_z, WIN_W, WIN_H, 90)
    create_window("Right Window 2", BLD_W, BLD_D * 0.6, sill_z, WIN_W, WIN_H, 90)

    # ══════════════════════════════════════════
    #  ENTRY DOOR — Dusco Moderna
    # ══════════════════════════════════════════
    door = ifcopenshell.api.run("root.create_entity", model,
        ifc_class="IfcDoor", name="Dusco Moderna Full Lite Entry Door")
    door.OverallWidth = float(DOOR_W)
    door.OverallHeight = float(DOOR_H)
    door.ObjectPlacement = make_local_placement(5.0, 0, wall_base, storey_placement)

    door_profile = make_rectangle_profile(DOOR_W, WALL_T)
    door_solid = make_extruded_solid(door_profile, DOOR_H)
    door_solid.Position = make_axis2_placement_3d(DOOR_W / 2, WALL_T / 2, 0)

    # 3 glass panels
    glass_panels = []
    panel_h = DOOR_H * 0.27
    panel_w = DOOR_W * 0.75
    for i in range(3):
        pz = 0.15 + i * (panel_h + 0.06)
        gp = make_rectangle_profile(panel_w, 0.01)
        gs = make_extruded_solid(gp, panel_h)
        gs.Position = make_axis2_placement_3d(DOOR_W / 2, WALL_T / 2, pz)
        glass_panels.append(gs)

    shape_rep = model.create_entity("IfcShapeRepresentation",
        ContextOfItems=body,
        RepresentationIdentifier="Body",
        RepresentationType="SweptSolid",
        Items=[door_solid] + glass_panels)

    door_style = make_colour(0.07, 0.07, 0.09)  # black steel
    glass_style = make_colour(0.6, 0.67, 0.8)    # frosted glass
    model.create_entity("IfcStyledItem", Item=door_solid, Styles=[door_style])
    for gp in glass_panels:
        model.create_entity("IfcStyledItem", Item=gp, Styles=[glass_style])

    product_shape = model.create_entity("IfcProductDefinitionShape",
        Representations=[shape_rep])
    door.Representation = product_shape
    ifcopenshell.api.run("spatial.assign_container", model,
        relating_structure=storey, products=[door])

    # ══════════════════════════════════════════
    #  PLUMBING
    # ══════════════════════════════════════════
    def create_pipe(name, radius, length, x, y, z, dx=0, dy=0, dz=1, colour=(0.2, 0.2, 0.2)):
        pipe = ifcopenshell.api.run("root.create_entity", model,
            ifc_class="IfcPipeSegment", name=name,
            predefined_type="USERDEFINED")
        pipe.ObjectPlacement = make_local_placement(x, y, z, storey_placement)

        circle = model.create_entity("IfcCircleProfileDef",
            ProfileType="AREA", Radius=float(radius))
        direction = make_direction(dx, dy, dz)
        solid = make_extruded_solid(circle, length, direction)
        assign_body(pipe, solid)
        apply_colour(pipe, *colour)
        ifcopenshell.api.run("spatial.assign_container", model,
            relating_structure=storey, products=[pipe])
        return pipe

    # Main ABS drain under slab
    create_pipe("Main Drain (3\" ABS)", 0.038, BLD_D * 0.7,
                BLD_W * 0.4, BLD_D * 0.15, -0.02,
                dx=0, dy=1, dz=0, colour=(0.2, 0.2, 0.2))

    # Branch drains
    create_pipe("Branch Drain — Kitchen", 0.025, 1.5,
                BLD_W * 0.2, BLD_D * 0.15, -0.02,
                dx=1, dy=0, dz=0, colour=(0.2, 0.2, 0.2))
    create_pipe("Branch Drain — Bath", 0.025, 1.2,
                BLD_W * 0.55, BLD_D * 0.15, -0.02,
                dx=1, dy=0, dz=0, colour=(0.2, 0.2, 0.2))

    # Hot PEX supply
    create_pipe("Hot Supply (½\" PEX)", 0.013, BLD_D * 0.6,
                0.3, BLD_D * 0.15, wall_base + 0.5,
                dx=0, dy=1, dz=0, colour=(0.8, 0.2, 0.2))

    # Cold PEX supply
    create_pipe("Cold Supply (½\" PEX)", 0.013, BLD_D * 0.6,
                0.4, BLD_D * 0.15, wall_base + 0.45,
                dx=0, dy=1, dz=0, colour=(0.2, 0.3, 0.8))

    # Vent stack (vertical through roof)
    create_pipe("Vent Stack (2\" ABS)", 0.025, WALL_H_HIGH + 0.5,
                BLD_W * 0.4, BLD_D * 0.2, -0.05,
                dx=0, dy=0, dz=1, colour=(0.25, 0.25, 0.25))

    # Water heater (cylinder)
    heater = ifcopenshell.api.run("root.create_entity", model,
        ifc_class="IfcFlowStorageDevice", name="Water Heater (40 gal Electric)")
    heater.ObjectPlacement = make_local_placement(
        BLD_W * 0.15, BLD_D * 0.85, wall_base, storey_placement)
    heater_circle = model.create_entity("IfcCircleProfileDef",
        ProfileType="AREA", Radius=0.22)
    heater_solid = make_extruded_solid(heater_circle, 1.1)
    assign_body(heater, heater_solid)
    apply_colour(heater, 0.8, 0.8, 0.8)
    ifcopenshell.api.run("spatial.assign_container", model,
        relating_structure=storey, products=[heater])

    # ══════════════════════════════════════════
    #  ELECTRICAL
    # ══════════════════════════════════════════
    # Panel box
    panel = ifcopenshell.api.run("root.create_entity", model,
        ifc_class="IfcDistributionControlElement", name="100A Sub-Panel")
    panel.ObjectPlacement = make_local_placement(
        BLD_W - 0.2, BLD_D * 0.9, wall_base + 1.0, storey_placement)
    panel_profile = make_rectangle_profile(0.38, 0.1)
    panel_solid = make_extruded_solid(panel_profile, 0.55)
    panel_solid.Position = make_axis2_placement_3d(0.19, 0.05, 0)
    assign_body(panel, panel_solid)
    apply_colour(panel, 0.4, 0.4, 0.4)
    ifcopenshell.api.run("spatial.assign_container", model,
        relating_structure=storey, products=[panel])

    # Conduit runs (simplified as pipes)
    create_pipe("Main Conduit Run", 0.015, BLD_W * 0.7,
                BLD_W * 0.15, BLD_D * 0.5, wall_base + WALL_H_HIGH - 0.15,
                dx=1, dy=0, dz=0, colour=(0.85, 0.65, 0.2))

    for i in range(4):
        bx = 1.0 + i * 1.5
        create_pipe(f"Branch Conduit {i+1}", 0.012, BLD_D * 0.5,
                    bx, BLD_D * 0.25, wall_base + WALL_H_HIGH - 0.15,
                    dx=0, dy=1, dz=0, colour=(0.85, 0.65, 0.2))

    # ══════════════════════════════════════════
    #  HVAC
    # ══════════════════════════════════════════
    # Mini-split indoor head
    minisplit = ifcopenshell.api.run("root.create_entity", model,
        ifc_class="IfcUnitaryEquipment", name="Mini-Split Head (18kBTU)")
    minisplit.ObjectPlacement = make_local_placement(
        BLD_W * 0.5 - 0.425, 0.05, wall_base + WALL_H_HIGH - 0.35, storey_placement)
    ms_profile = make_rectangle_profile(0.85, 0.2)
    ms_solid = make_extruded_solid(ms_profile, 0.28)
    ms_solid.Position = make_axis2_placement_3d(0.425, 0.1, 0)
    assign_body(minisplit, ms_solid)
    apply_colour(minisplit, 0.9, 0.9, 0.9)
    ifcopenshell.api.run("spatial.assign_container", model,
        relating_structure=storey, products=[minisplit])

    # Outdoor condenser
    condenser = ifcopenshell.api.run("root.create_entity", model,
        ifc_class="IfcUnitaryEquipment", name="Outdoor Condenser Unit")
    condenser.ObjectPlacement = make_local_placement(
        BLD_W * 0.5 - 0.35, -0.5, 0, storey_placement)
    cond_profile = make_rectangle_profile(0.7, 0.3)
    cond_solid = make_extruded_solid(cond_profile, 0.6)
    cond_solid.Position = make_axis2_placement_3d(0.35, 0.15, 0)
    assign_body(condenser, cond_solid)
    apply_colour(condenser, 0.47, 0.47, 0.4)
    ifcopenshell.api.run("spatial.assign_container", model,
        relating_structure=storey, products=[condenser])

    # HRV ventilator
    hrv = ifcopenshell.api.run("root.create_entity", model,
        ifc_class="IfcUnitaryEquipment", name="HRV Ventilator")
    hrv.ObjectPlacement = make_local_placement(
        BLD_W * 0.8 - 0.3, BLD_D * 0.5 - 0.225, wall_base + WALL_H_HIGH - 0.3, storey_placement)
    hrv_profile = make_rectangle_profile(0.6, 0.45)
    hrv_solid = make_extruded_solid(hrv_profile, 0.25)
    hrv_solid.Position = make_axis2_placement_3d(0.3, 0.225, 0)
    assign_body(hrv, hrv_solid)
    apply_colour(hrv, 0.53, 0.53, 0.47)
    ifcopenshell.api.run("spatial.assign_container", model,
        relating_structure=storey, products=[hrv])

    # Line set (refrigerant, from indoor to outdoor)
    create_pipe("Refrigerant Line Set", 0.02, WALL_H_HIGH + 0.5,
                BLD_W * 0.5, 0.02, -0.15,
                dx=0, dy=0, dz=1, colour=(0.6, 0.3, 0.3))

    # HRV ducting
    create_pipe("HRV Duct — Supply", 0.06, 2.0,
                BLD_W * 0.8, BLD_D * 0.3, wall_base + WALL_H_HIGH - 0.18,
                dx=0, dy=1, dz=0, colour=(0.55, 0.55, 0.5))
    create_pipe("HRV Duct — Exhaust", 0.06, 2.0,
                BLD_W * 0.8, BLD_D * 0.5, wall_base + WALL_H_HIGH - 0.18,
                dx=0, dy=1, dz=0, colour=(0.55, 0.55, 0.5))

    # ── Write output ──
    output_path = "web/static/model.ifc"
    model.write(output_path)
    print(f"IFC model written to {output_path}")
    print(f"  Entities: {len(list(model))}")

    # Count elements by type
    for ifc_type in ["IfcWall", "IfcSlab", "IfcRoof", "IfcWindow", "IfcDoor",
                     "IfcPipeSegment", "IfcFlowStorageDevice", "IfcUnitaryEquipment",
                     "IfcDistributionControlElement", "IfcMember"]:
        count = len(model.by_type(ifc_type))
        if count:
            print(f"  {ifc_type}: {count}")

    return model


if __name__ == "__main__":
    create_model()
