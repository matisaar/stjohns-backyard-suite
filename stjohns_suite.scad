// ============================================================
// St. John's 430 sqft Backyard Suite — OpenSCAD BIM Model
// All dimensions from Kent.ca / Home Depot product listings
// ============================================================
// Building: 21'-6" x 20'-0", mono-slope roof
//   High wall (left/back): 9'-6"  |  Low wall (right): 7'-0"
//   2x6 wood frame, FPSF slab-on-grade
// ============================================================

// ── Units: inches throughout ──
in = 1;
ft = 12;

// ── Building Envelope ──
BLDG_W   = 21*ft + 6;      // 258" = 21'-6" (east-west, front wall)
BLDG_D   = 20*ft;          // 240" = 20'-0" (north-south, depth)
WALL_H_HI = 9*ft + 6;      // 114" left wall height (high side)
WALL_H_LO = 7*ft;          //  84" right wall height (low side)
WALL_T   = 5.5;            // 2x6 actual thickness
SLAB_T   = 4;              // 4" concrete slab
GRAVEL_T = 4;              // 4" gravel base
XPS_T    = 2;              // 2" rigid insulation under slab

// ── Lumber Actual Dims (from standard dressed sizes) ──
STUD_W   = 1.5;            // 2x6 actual width
STUD_D   = 5.5;            // 2x6 actual depth
RAFTER_W = 1.5;            // 2x12 actual width
RAFTER_D = 11.25;          // 2x12 actual depth
INT_STUD_D = 3.5;          // 2x4 actual depth (interior walls)

// ── Windows: Kent Atlantic Windows 36"x40" Casement (SKU 1107802) ──
WIN_W    = 36;             // width
WIN_H    = 40;             // height
WIN_D    = 4.5;            // frame depth (standard vinyl casement)
WIN_SILL = 36;             // sill height from floor

// ── Door: Dusco Moderna 34"x80" Full Lite (Home Depot SKU 1001728121) ──
DOOR_W   = 34;             // 34" wide
DOOR_H   = 80;             // 80" tall (6'-8")
DOOR_D   = 7.25;           // 7-1/4" jamb depth (from product: "34 x 80 x 7-1/4")

// ── Interior Pocket Doors: 30" Modern White (Kent SKU 1389850) ──
PDOOR_W  = 30;
PDOOR_H  = 80;

// ── Roof ──
ROOF_SHEATHING = 0.625;    // 5/8" plywood (Kent SKU 1015826)
SHINGLE_T = 0.375;         // IKO Cambridge architectural (Kent SKU 1010785)
OVERHANG = 24;             // 2' overhang on all sides

// ── Plumbing Fixtures ──
// Toilet: Clarovista Tidal 1-piece elongated (Kent SKU 1579329)
//   16.5" bowl height, standard 1-piece dims
TOILET_W = 15;  TOILET_D = 28;  TOILET_H = 28;

// Vanity: 24" with drawer, white ceramic top (Kent SKU 1697660)
VANITY_W = 24;  VANITY_D = 18;  VANITY_H = 34;

// Shower Base: Maax Finesse 4832 (Kent SKU 1023986) — "48x32"
SHOWER_W = 32;  SHOWER_D = 48;  SHOWER_H = 78;  // 78" to showerhead

// Water Heater: GSW 182L Space-Saver electric (Kent SKU 1766016)
//   Standard space-saver: 18" dia x 48" tall
WH_DIA = 18;  WH_H = 48;

// ── Kitchen Appliances ──
// Range: Whirlpool 24" Electric (Kent SKU 1461599, model YWFE50M4HS)
//   "24" width, 42-1/2" depth with door open 90°" → body ~24"W x 25"D x 36"H
RANGE_W = 24;  RANGE_D = 25;  RANGE_H = 36;

// Fridge: Whirlpool 24" Bottom-Freezer 12.9cf (Kent SKU 1461451, model WRB543CMJV)
//   Standard 24" compact: 24"W x 29"D x 60"H
FRIDGE_W = 24;  FRIDGE_D = 29;  FRIDGE_H = 60;

// Range Hood: Bosch 500 Series 24" Under-Cabinet (Kent SKU 1462473)
HOOD_W = 24;  HOOD_D = 20;  HOOD_H = 10;

// Kitchen Sink: 25" Undermount SS (Kent SKU 1391411)
SINK_W = 25;  SINK_D = 18;  SINK_H = 9;

// Countertop: 8' white laminate, 25" deep (Kent SKU 1015537)
COUNTER_W = 96;  COUNTER_D = 25;  COUNTER_H = 1.5;
COUNTER_HT = 36;  // standard 36" counter height

// ── HVAC ──
// Mini-split condenser: Perfect Aire 18kBTU (Kent SKU 1034429)
//   Standard 18kBTU outdoor: ~33"W x 12"D x 24"H
COND_W = 33;  COND_D = 12;  COND_H = 24;

// Mini-split indoor head: ~32"W x 8"D x 12"H
HEAD_W = 32;  HEAD_D = 8;  HEAD_H = 12;

// HRV: Venmar HRV110 (Kent SKU 1400849) — standard unit ~24"W x 17"D x 12"H
HRV_W = 24;  HRV_D = 17;  HRV_H = 12;

// Baseboard heater: 1500W 66" (Kent SKU 1652016)
BASEBOARD_W = 66;  BASEBOARD_H = 8;  BASEBOARD_D = 3;

// ── Electrical ──
// Sub-panel: Schneider QO 100A 8/15 (Kent SKU 1013553) ~15"W x 3.75"D x 20"H
PANEL_W = 15;  PANEL_D = 3.75;  PANEL_H = 20;

// Washer/Dryer Combo: GE 24" Front Load (Kent SKU 1462204)
WASHER_W = 24;  WASHER_D = 25;  WASHER_H = 34;

// ── Colours ──
COL_CONCRETE = [0.65, 0.65, 0.65];
COL_GRAVEL   = [0.5, 0.48, 0.45];
COL_XPS_BLUE = [0.2, 0.5, 0.85];
COL_FRAMING  = [0.85, 0.72, 0.5];
COL_PLYWOOD  = [0.76, 0.65, 0.48];
COL_TYVEK    = [0.92, 0.92, 0.92];
COL_SIDING   = [0.52, 0.58, 0.52];  // Mitten Oregon Pride
COL_SHINGLE  = [0.18, 0.18, 0.18];  // IKO Dual Black
COL_WINDOW   = [0.5, 0.75, 0.88, 0.4];
COL_WIN_FRAME= [0.95, 0.95, 0.95];
COL_DOOR_BLK = [0.08, 0.08, 0.12];
COL_DOOR_GL  = [0.6, 0.7, 0.8, 0.3];
COL_DRYWALL  = [0.95, 0.95, 0.95];
COL_LVP      = [0.24, 0.16, 0.09];  // Volcano Pewter dark walnut
COL_TOILET   = [0.98, 0.98, 0.98];
COL_VANITY   = [0.12, 0.12, 0.12];  // matte black cabinet
COL_VANITY_TOP=[0.97, 0.97, 0.97];
COL_SHOWER   = [0.96, 0.96, 0.96];
COL_WH       = [0.88, 0.88, 0.88];
COL_RANGE    = [0.3, 0.3, 0.3];
COL_FRIDGE   = [0.3, 0.3, 0.3];
COL_HOOD     = [0.15, 0.15, 0.15];
COL_SINK     = [0.7, 0.72, 0.74];
COL_COUNTER  = [0.97, 0.97, 0.97];  // white laminate
COL_CABINET  = [0.15, 0.15, 0.17];  // IKEA NICKEBO anthracite
COL_CONDENSER= [0.85, 0.85, 0.85];
COL_HEAD     = [0.95, 0.95, 0.95];
COL_HRV      = [0.7, 0.7, 0.7];
COL_BASEBOARD= [0.95, 0.95, 0.95];
COL_PANEL    = [0.55, 0.55, 0.55];
COL_WASHER   = [0.95, 0.95, 0.95];
COL_PIPE_RED = [0.85, 0.2, 0.15];
COL_PIPE_BLUE= [0.15, 0.35, 0.85];
COL_PIPE_ABS = [0.12, 0.12, 0.12];
COL_WIRE_14  = [0.95, 0.95, 0.5];
COL_FASCIA   = [0.95, 0.95, 0.95];  // Frost White vinyl
COL_SOFFIT   = [0.93, 0.93, 0.93];
COL_INT_WALL = [0.92, 0.92, 0.90];

// ── Explode control — set > 0 to spread layers apart for inspection ──
EXPLODE = 0;  // try 2 or 5 to see assembly layers

// ══════════════════════════════════════════════
//  MODULES
// ══════════════════════════════════════════════

// ── Foundation Layers ──
module gravel_base() {
    color(COL_GRAVEL)
        translate([0, 0, -GRAVEL_T - XPS_T - SLAB_T - EXPLODE*3])
            cube([BLDG_W, BLDG_D, GRAVEL_T]);
}

module xps_under_slab() {
    color(COL_XPS_BLUE)
        translate([0, 0, -XPS_T - SLAB_T - EXPLODE*2])
            cube([BLDG_W, BLDG_D, XPS_T]);
}

module concrete_slab() {
    color(COL_CONCRETE)
        translate([0, 0, -SLAB_T - EXPLODE])
            cube([BLDG_W, BLDG_D, SLAB_T]);
}

module lvp_flooring() {
    // Volcano Pewter 5.3mm SPC Vinyl Plank (Kent SKU 1080257-PWT)
    color(COL_LVP)
        translate([WALL_T, WALL_T, 0])
            cube([BLDG_W - 2*WALL_T, BLDG_D - 2*WALL_T, 0.209]);  // 5.3mm
}

// ── Wall Helper — extruded wall with optional window/door cutouts ──
module wall_panel(w, h, t, cutouts=[]) {
    difference() {
        cube([w, t, h]);
        for (c = cutouts) {
            // c = [x_offset, z_offset, cut_w, cut_h]
            translate([c[0], -0.1, c[1]])
                cube([c[2], t + 0.2, c[3]]);
        }
    }
}

// ── Exterior Walls ──
module front_wall() {
    // Front wall (south, along X axis at Y=0)
    // 3 windows equally spaced + 1 entry door
    // Window positions: centered at ~50", ~129", ~208" (3 windows)
    // Door at ~20" from left edge
    win1_x = 60;
    win2_x = 130;
    win3_x = 200;
    door_x = 15;

    color(COL_SIDING)
        wall_panel(BLDG_W, WALL_H_HI, WALL_T, [
            [door_x,  0,        DOOR_W, DOOR_H],
            [win1_x,  WIN_SILL, WIN_W,  WIN_H],
            [win2_x,  WIN_SILL, WIN_W,  WIN_H],
            [win3_x,  WIN_SILL, WIN_W,  WIN_H],
        ]);

    // Door frame and glass
    translate([door_x, 0, 0]) entry_door();

    // Window units
    translate([win1_x, -0.5, WIN_SILL]) window_unit();
    translate([win2_x, -0.5, WIN_SILL]) window_unit();
    translate([win3_x, -0.5, WIN_SILL]) window_unit();
}

module back_wall() {
    // Back wall (north, along X at Y=BLDG_D - WALL_T)
    // No windows on back
    color(COL_SIDING)
        translate([0, BLDG_D - WALL_T, 0])
            wall_panel(BLDG_W, WALL_H_HI, WALL_T);
}

module left_wall() {
    // Left wall (west, high side 9'-6")
    // 1 window centered
    win_x = (BLDG_D - WIN_W) / 2;
    color(COL_SIDING)
        translate([0, 0, 0])
            rotate([0, 0, 90])
                translate([0, -WALL_T, 0])
                    wall_panel(BLDG_D, WALL_H_HI, WALL_T, [
                        [win_x, WIN_SILL, WIN_W, WIN_H],
                    ]);

    // Window
    translate([-0.5, win_x, WIN_SILL])
        rotate([0, 0, -90])
            window_unit();
}

module right_wall() {
    // Right wall (east, low side 7'-0")
    // 2 windows
    win1_x = BLDG_D * 0.3 - WIN_W/2;
    win2_x = BLDG_D * 0.7 - WIN_W/2;
    color(COL_SIDING)
        translate([BLDG_W, 0, 0])
            rotate([0, 0, 90])
                translate([0, -WALL_T, 0])
                    wall_panel(BLDG_D, WALL_H_LO, WALL_T, [
                        [win1_x, WIN_SILL, WIN_W, WIN_H],
                        [win2_x, WIN_SILL, WIN_W, WIN_H],
                    ]);

    // Windows
    translate([BLDG_W + 0.5, win1_x, WIN_SILL])
        rotate([0, 0, 90])
            window_unit();
    translate([BLDG_W + 0.5, win2_x, WIN_SILL])
        rotate([0, 0, 90])
            window_unit();
}

// ── Window Module (36"x40" casement) ──
module window_unit() {
    // Frame (white PVC)
    color(COL_WIN_FRAME) {
        frame_w = 2;
        // Bottom
        cube([WIN_W, WIN_D, frame_w]);
        // Top
        translate([0, 0, WIN_H - frame_w])
            cube([WIN_W, WIN_D, frame_w]);
        // Left
        cube([frame_w, WIN_D, WIN_H]);
        // Right
        translate([WIN_W - frame_w, 0, 0])
            cube([frame_w, WIN_D, WIN_H]);
        // Center mullion
        translate([WIN_W/2 - frame_w/2, 0, 0])
            cube([frame_w, WIN_D, WIN_H]);
    }
    // Glass panes (triple-pane, Low-E argon)
    color(COL_WINDOW)
        translate([2, WIN_D/2 - 0.25, 2])
            cube([WIN_W - 4, 0.5, WIN_H - 4]);
}

// ── Entry Door: Dusco Moderna 34"x80" Full Lite Black Steel ──
module entry_door() {
    // Steel frame
    color(COL_DOOR_BLK) {
        frame = 3;
        // Frame surround
        cube([frame, DOOR_D, DOOR_H]);                        // left jamb
        translate([DOOR_W - frame, 0, 0])
            cube([frame, DOOR_D, DOOR_H]);                    // right jamb
        translate([0, 0, DOOR_H - frame])
            cube([DOOR_W, DOOR_D, frame]);                     // header

        // 3 horizontal muntins dividing glass into 3 panels
        translate([frame, 0, DOOR_H * 0.32])
            cube([DOOR_W - 2*frame, 1.75, 1.5]);
        translate([frame, 0, DOOR_H * 0.64])
            cube([DOOR_W - 2*frame, 1.75, 1.5]);

        // Door slab edge
        cube([DOOR_W, 1.75, DOOR_H]);
    }
    // 3 frosted glass panels
    color(COL_DOOR_GL) {
        panel_w = DOOR_W - 6;
        panel1_h = DOOR_H * 0.32 - 3;
        panel2_h = DOOR_H * 0.32 - 1.5;
        panel3_h = DOOR_H * 0.36 - 4.5;
        translate([3, 0.5, 3])
            cube([panel_w, 0.75, panel1_h]);
        translate([3, 0.5, DOOR_H * 0.32 + 1.5])
            cube([panel_w, 0.75, panel2_h]);
        translate([3, 0.5, DOOR_H * 0.64 + 1.5])
            cube([panel_w, 0.75, panel3_h]);
    }
}

// ── Roof Assembly (Mono-slope) ──
module roof_assembly() {
    // Slope from WALL_H_HI (left/back) to WALL_H_LO (right/front-right)
    // Slope runs east-west (across BLDG_W)
    rise = WALL_H_HI - WALL_H_LO;
    run = BLDG_W;
    angle = atan2(rise, run);  // ~6.6° ≈ 3:12 pitch

    translate([-OVERHANG, -OVERHANG, WALL_H_HI + EXPLODE*2]) {
        // Roof sheathing (5/8" plywood — Kent SKU 1015826)
        color(COL_PLYWOOD)
            rotate([0, angle, 0])
                cube([sqrt(run*run + rise*rise) + 2*OVERHANG, BLDG_D + 2*OVERHANG, ROOF_SHEATHING]);

        // Shingles (IKO Cambridge Dual Black — Kent SKU 1010785)
        color(COL_SHINGLE)
            translate([0, 0, ROOF_SHEATHING])
                rotate([0, angle, 0])
                    cube([sqrt(run*run + rise*rise) + 2*OVERHANG, BLDG_D + 2*OVERHANG, SHINGLE_T]);
    }
}

// ── Rafters (2x12x16' SPF — Kent SKU 1016290) ──
module rafters() {
    rise = WALL_H_HI - WALL_H_LO;
    run = BLDG_W;
    angle = atan2(rise, run);
    rafter_len = sqrt(run*run + rise*rise) + 2*OVERHANG;
    spacing = 16;  // 16" OC
    count = floor(BLDG_D / spacing);

    color(COL_FRAMING)
        for (i = [0 : count]) {
            translate([-OVERHANG, i * spacing, WALL_H_HI - RAFTER_D])
                rotate([0, angle, 0])
                    cube([rafter_len, RAFTER_W, RAFTER_D]);
        }
}

// ── Fascia (8"x12' vinyl — Kent SKU 1016978, Frost White) ──
module fascia() {
    color(COL_FASCIA) {
        // Front fascia (low side)
        translate([-OVERHANG, -OVERHANG, WALL_H_LO - 8])
            cube([BLDG_W + 2*OVERHANG, 0.5, 8]);
        // Back fascia (high side)
        translate([-OVERHANG, BLDG_D + OVERHANG - 0.5, WALL_H_HI - 8])
            cube([BLDG_W + 2*OVERHANG, 0.5, 8]);
        // Left fascia (high)
        translate([-OVERHANG, -OVERHANG, WALL_H_HI - 8])
            cube([0.5, BLDG_D + 2*OVERHANG, 8]);
        // Right fascia (low)
        translate([BLDG_W + OVERHANG - 0.5, -OVERHANG, WALL_H_LO - 8])
            cube([0.5, BLDG_D + 2*OVERHANG, 8]);
    }
}

// ── Soffit (Double 5" perforated — Kent SKU 1021390) ──
module soffit() {
    color(COL_SOFFIT) {
        sof_t = 0.25;
        // Front soffit
        translate([-OVERHANG, -OVERHANG, WALL_H_LO - 0.5])
            cube([BLDG_W + 2*OVERHANG, OVERHANG, sof_t]);
        // Back soffit
        translate([-OVERHANG, BLDG_D, WALL_H_HI - 0.5])
            cube([BLDG_W + 2*OVERHANG, OVERHANG, sof_t]);
        // Left soffit
        translate([-OVERHANG, -OVERHANG, WALL_H_HI - 0.5])
            cube([OVERHANG, BLDG_D + 2*OVERHANG, sof_t]);
        // Right soffit
        translate([BLDG_W, -OVERHANG, WALL_H_LO - 0.5])
            cube([OVERHANG, BLDG_D + 2*OVERHANG, sof_t]);
    }
}

// ── Interior Partition Walls (2x4 KD — Kent SKU 1016318) ──
// Layout: 2 bedrooms back, 2 bathrooms, kitchen/living front
//
//   Back:  |  Bed 1  | Bath2 |  Bed 2   |
//          |---------|-------|----------|
//   Front: | Kitchen/Living  | Bath1 |Ldy|
//          | (entry door)            |   |
//
module interior_walls() {
    iw = 0.5 + INT_STUD_D + 0.5;  // 4.5" (stud + drywall both sides)

    color(COL_INT_WALL) {
        // East-west divider between front and back zones (at Y = 130")
        div_y = 130;
        translate([WALL_T, div_y, 0])
            cube([BLDG_W - 2*WALL_T, iw, 96]);

        // North-south divider: separates Bed1 from Bath2 (at X = 108")
        bed1_x = 108;
        translate([bed1_x, div_y, 0])
            cube([iw, BLDG_D - div_y - WALL_T, 96]);

        // North-south divider: separates Bath2 from Bed2 (at X = 156")
        bath2_x = 156;
        translate([bath2_x, div_y, 0])
            cube([iw, BLDG_D - div_y - WALL_T, 96]);

        // Bath1 walls in front-right area (at X = 196", from front wall to div_y)
        bath1_x = 196;
        translate([bath1_x, WALL_T, 0])
            cube([iw, div_y - WALL_T, 96]);

        // Laundry closet wall (at X = 230", short wall from front)
        laundry_x = 230;
        translate([laundry_x, WALL_T, 0])
            cube([iw, 48, 96]);
    }
}

// ── Toilet: Clarovista Tidal 1-Piece (Kent SKU 1579329) ──
module toilet() {
    color(COL_TOILET) {
        // Base/bowl
        translate([TOILET_W/2, TOILET_D/2, 0])
            scale([TOILET_W/2, TOILET_D/2, TOILET_H * 0.6])
                sphere(r=1, $fn=32);
        // Tank (integrated 1-piece)
        translate([1, TOILET_D - 8, 0])
            cube([TOILET_W - 2, 8, TOILET_H]);
        // Seat
        translate([0, 0, TOILET_H * 0.55])
            difference() {
                cube([TOILET_W, TOILET_D - 6, 1]);
                translate([2, 2, -0.1])
                    cube([TOILET_W - 4, TOILET_D - 10, 1.2]);
            }
    }
}

// ── Vanity: 24" w/ Drawer, Matte Black (Kent SKU 1697660) ──
module vanity() {
    // Cabinet body
    color(COL_VANITY)
        cube([VANITY_W, VANITY_D, VANITY_H - 1]);
    // White ceramic top with integrated sink
    color(COL_VANITY_TOP) {
        translate([0, 0, VANITY_H - 1])
            cube([VANITY_W, VANITY_D, 1]);
        // Sink basin (negative)
    }
    // Drawer pulls (matte black — Kent SKU 1010873)
    color([0.05, 0.05, 0.05]) {
        translate([VANITY_W/2 - 3, -0.2, VANITY_H * 0.3])
            cube([6, 0.4, 0.4]);
        translate([VANITY_W/2 - 3, -0.2, VANITY_H * 0.6])
            cube([6, 0.4, 0.4]);
    }
}

// ── Shower: Maax Finesse 4832 Base + Tile Walls (Kent SKU 1023986) ──
module shower_stall() {
    // Base pan
    color(COL_SHOWER)
        cube([SHOWER_W, SHOWER_D, 3]);  // 3" base height
    // Tile walls (12"x24" white ceramic — Kent SKU 1035109)
    color([0.96, 0.96, 0.98]) {
        // Back wall
        translate([0, SHOWER_D - 0.5, 3])
            cube([SHOWER_W, 0.5, SHOWER_H - 3]);
        // Left wall
        translate([0, 0, 3])
            cube([0.5, SHOWER_D, SHOWER_H - 3]);
        // Glass panel (frameless)
        color([0.7, 0.8, 0.9, 0.15])
            translate([SHOWER_W - 0.375, 0, 3])
                cube([0.375, SHOWER_D, SHOWER_H - 3]);
    }
    // Shower head
    color([0.2, 0.2, 0.2])
        translate([SHOWER_W/2, SHOWER_D - 3, SHOWER_H - 4])
            sphere(r=2, $fn=16);
}

// ── Water Heater: GSW 182L Space-Saver (Kent SKU 1766016) ──
module water_heater() {
    color(COL_WH) {
        translate([WH_DIA/2, WH_DIA/2, 0])
            cylinder(d=WH_DIA, h=WH_H, $fn=32);
        // Pipes on top
        color(COL_PIPE_RED)
            translate([WH_DIA/4, WH_DIA/2, WH_H])
                cylinder(d=0.75, h=6, $fn=12);
        color(COL_PIPE_BLUE)
            translate([WH_DIA*3/4, WH_DIA/2, WH_H])
                cylinder(d=0.75, h=6, $fn=12);
    }
}

// ── Kitchen Range: Whirlpool 24" Electric (Kent SKU 1461599) ──
module range() {
    color(COL_RANGE) {
        cube([RANGE_W, RANGE_D, RANGE_H]);
        // Backsplash/control panel
        translate([0, RANGE_D - 1, RANGE_H])
            cube([RANGE_W, 1, 6]);
    }
    // Burner circles on top
    color([0.2, 0.2, 0.2])
        translate([0, 0, RANGE_H]) {
            translate([6, 8, 0]) cylinder(d=7, h=0.1, $fn=24);
            translate([18, 8, 0]) cylinder(d=7, h=0.1, $fn=24);
            translate([6, 18, 0]) cylinder(d=5, h=0.1, $fn=24);
            translate([18, 18, 0]) cylinder(d=5, h=0.1, $fn=24);
        }
}

// ── Fridge: Whirlpool 24" Bottom-Freezer (Kent SKU 1461451) ──
module fridge() {
    color(COL_FRIDGE) {
        cube([FRIDGE_W, FRIDGE_D, FRIDGE_H]);
        // Handle
        color([0.4, 0.4, 0.4])
            translate([-0.3, 1, FRIDGE_H * 0.4])
                cube([0.3, 0.8, FRIDGE_H * 0.35]);
    }
}

// ── Range Hood: Bosch 24" Under-Cabinet (Kent SKU 1462473) ──
module range_hood() {
    color(COL_HOOD) {
        cube([HOOD_W, HOOD_D, HOOD_H]);
        // Vent strip
        color([0.3, 0.3, 0.3])
            translate([2, 2, -0.5])
                cube([HOOD_W - 4, HOOD_D - 4, 0.5]);
    }
}

// ── Kitchen Cabinets: IKEA METOD + NICKEBO Anthracite (8 LF) ──
module kitchen_cabinets() {
    // Base cabinets: 4 LF (48") x 24" deep x 34.5" high
    base_h = 34.5;
    base_d = 24;

    color(COL_CABINET) {
        // Base cabinet run
        cube([COUNTER_W, base_d, base_h]);
        // Upper cabinets: 4 LF (48") starting at ~54" height, 12" deep, 30" tall
        translate([0, 0, 54])
            cube([48, 12, 30]);
    }
    // Countertop (white laminate — Kent SKU 1015537)
    color(COL_COUNTER)
        translate([0, 0, base_h])
            cube([COUNTER_W, COUNTER_D, COUNTER_H]);

    // Sink cutout area (Kent SS sink SKU 1391411)
    color(COL_SINK)
        translate([50, 3, base_h + COUNTER_H])
            cube([SINK_W, SINK_D, 0.5]);

    // Faucet (Banting matte black — Kent SKU 1199456)
    color([0.08, 0.08, 0.08])
        translate([62, 6, base_h + COUNTER_H]) {
            cylinder(d=1.5, h=14, $fn=12);
            translate([0, 0, 14])
                rotate([0, 90, 0])
                    cylinder(d=1, h=8, $fn=12);
        }
}

// ── Mini-Split Condenser: Perfect Aire 18kBTU (Kent SKU 1034429) ──
module condenser() {
    color(COL_CONDENSER) {
        cube([COND_W, COND_D, COND_H]);
        // Fan grille
        color([0.3, 0.3, 0.3])
            translate([COND_W/2, -0.1, COND_H/2])
                rotate([-90, 0, 0])
                    cylinder(d=COND_H * 0.7, h=0.2, $fn=32);
    }
}

// ── Mini-Split Indoor Head ──
module mini_split_head() {
    color(COL_HEAD) {
        // Main body — slightly curved
        cube([HEAD_W, HEAD_D, HEAD_H]);
        // Air deflector
        translate([2, -1, 0])
            cube([HEAD_W - 4, 1, 1.5]);
    }
}

// ── HRV: Venmar HRV110 (Kent SKU 1400849) ──
module hrv_unit() {
    color(COL_HRV) {
        cube([HRV_W, HRV_D, HRV_H]);
        // Duct connections (6" diameter — Kent SKU 1014547)
        translate([4, HRV_D/2, HRV_H])
            cylinder(d=6, h=3, $fn=24);
        translate([20, HRV_D/2, HRV_H])
            cylinder(d=6, h=3, $fn=24);
    }
}

// ── Baseboard Heater: 1500W 66" (Kent SKU 1652016) ──
module baseboard() {
    color(COL_BASEBOARD)
        cube([BASEBOARD_W, BASEBOARD_D, BASEBOARD_H]);
}

// ── Sub-Panel: Schneider QO 100A (Kent SKU 1013553) ──
module sub_panel() {
    color(COL_PANEL) {
        cube([PANEL_W, PANEL_D, PANEL_H]);
        // Breaker slots
        color([0.2, 0.2, 0.2])
            for (i = [0:7])
                translate([2, -0.1, 2 + i*2])
                    cube([PANEL_W - 4, 0.2, 1.5]);
    }
}

// ── Washer/Dryer: GE 24" Combo (Kent SKU 1462204) ──
module washer_dryer() {
    color(COL_WASHER) {
        cube([WASHER_W, WASHER_D, WASHER_H]);
        // Drum door (front circle)
        color([0.7, 0.7, 0.7])
            translate([WASHER_W/2, -0.1, WASHER_H * 0.55])
                rotate([-90, 0, 0])
                    cylinder(d=18, h=0.2, $fn=32);
    }
}

// ── PEX Supply Runs (Kent SKU 1036755: 1/2" x 100') ──
module pex_supply() {
    // Hot (red) main run along back wall
    color(COL_PIPE_RED)
        translate([WALL_T + 2, BLDG_D - WALL_T - 4, 12])
            rotate([0, 90, 0])
                cylinder(d=0.5, h=BLDG_W * 0.6, $fn=8);

    // Cold (blue) main run parallel
    color(COL_PIPE_BLUE)
        translate([WALL_T + 2, BLDG_D - WALL_T - 6, 12])
            rotate([0, 90, 0])
                cylinder(d=0.5, h=BLDG_W * 0.6, $fn=8);

    // Vertical risers to fixtures
    color(COL_PIPE_RED) {
        // Kitchen hot
        translate([80, BLDG_D - WALL_T - 4, 0])
            cylinder(d=0.5, h=36, $fn=8);
        // Bath1 hot
        translate([200, 60, 0])
            cylinder(d=0.5, h=48, $fn=8);
        // Bath2 hot
        translate([135, 170, 0])
            cylinder(d=0.5, h=48, $fn=8);
    }
    color(COL_PIPE_BLUE) {
        // Kitchen cold
        translate([82, BLDG_D - WALL_T - 6, 0])
            cylinder(d=0.5, h=36, $fn=8);
        // Bath1 cold
        translate([202, 60, 0])
            cylinder(d=0.5, h=48, $fn=8);
        // Bath2 cold
        translate([137, 170, 0])
            cylinder(d=0.5, h=48, $fn=8);
    }
}

// ── ABS Drain Pipes (Kent SKU 1001871: 3" ABS) ──
module drain_pipes() {
    color(COL_PIPE_ABS) {
        // Main 3" drain running front-to-back under slab
        translate([BLDG_W/2, 0, -SLAB_T/2])
            rotate([-90, 0, 0])
                cylinder(d=3, h=BLDG_D, $fn=16);
        // Branch 2" drains
        // Kitchen
        translate([80, 120, -SLAB_T/2])
            rotate([0, 90, 0])
                cylinder(d=2, h=50, $fn=12);
        // Bath1
        translate([200, 40, -SLAB_T/2])
            rotate([-90, 0, 0])
                cylinder(d=2, h=30, $fn=12);
        // Bath2
        translate([135, 160, -SLAB_T/2])
            rotate([-90, 0, 0])
                cylinder(d=2, h=30, $fn=12);
        // Vent stack (3" through roof)
        translate([BLDG_W/2, BLDG_D/2, -SLAB_T])
            cylinder(d=3, h=WALL_H_HI + 24, $fn=16);
    }
}

// ── Electrical Wiring (NMD90 — Kent SKUs 1026025, 1026699) ──
module wiring_runs() {
    // 14/2 runs at ~48" height in walls (yellow)
    color(COL_WIRE_14) {
        // Front wall run
        translate([WALL_T, WALL_T, 48])
            rotate([0, 90, 0])
                cylinder(d=0.4, h=BLDG_W - 2*WALL_T, $fn=6);
        // Back wall run
        translate([WALL_T, BLDG_D - WALL_T, 48])
            rotate([0, 90, 0])
                cylinder(d=0.4, h=BLDG_W - 2*WALL_T, $fn=6);
        // Left wall run
        translate([WALL_T, WALL_T, 48])
            rotate([-90, 0, 0])
                cylinder(d=0.4, h=BLDG_D - 2*WALL_T, $fn=6);
    }
}


// ══════════════════════════════════════════════
//  FULL ASSEMBLY
// ══════════════════════════════════════════════

module foundation() {
    gravel_base();
    xps_under_slab();
    concrete_slab();
    lvp_flooring();
}

module exterior_shell() {
    front_wall();
    back_wall();
    left_wall();
    right_wall();
}

module roof_system() {
    rafters();
    roof_assembly();
    fascia();
    soffit();
}

module interior_layout() {
    interior_walls();

    // ── Bath 1 (front-right, X=196-258, Y=5.5-130) ──
    // Toilet
    translate([210, 20, 0]) toilet();
    // Vanity with drawer
    translate([200, 80, 0]) vanity();
    // Shower
    translate([200, 40, 0]) shower_stall();
    // Baseboard (Kent SKU 1652016)
    translate([200, 100, 0]) baseboard();

    // ── Bath 2 (back-center, X=108-156, Y=130-240) ──
    translate([115, 180, 0]) toilet();
    translate([115, 145, 0]) vanity();
    translate([120, 195, 0]) shower_stall();
    // Baseboard
    translate([115, 165, 0]) baseboard();

    // ── Kitchen/Living (front, X=5.5-196, Y=5.5-130) ──
    // Cabinets + counter + sink along back of front zone
    translate([60, 115, 0]) kitchen_cabinets();

    // Range next to cabinets
    translate([60, 90, 0]) range();

    // Range hood above range (at 54" height)
    translate([60, 90, 54]) range_hood();

    // Fridge
    translate([36, 90, 0]) fridge();

    // ── Laundry closet (front-far-right, X=230-258, Y=5.5-53) ──
    translate([234, 10, 0]) washer_dryer();
}

module mechanical() {
    // Water heater in utility area (back-left corner)
    translate([10, 205, 0]) water_heater();

    // HRV mounted on ceiling in utility area
    translate([10, 180, 84]) hrv_unit();

    // Sub-panel on left wall
    translate([WALL_T, 200, 48]) sub_panel();

    // Mini-split indoor head (high on living room wall, Y=130 divider)
    translate([80, 130, 84]) mini_split_head();

    // Condenser (outside, right side)
    translate([BLDG_W + 12, BLDG_D/2 - COND_W/2, 6]) condenser();
}

module rough_ins() {
    pex_supply();
    drain_pipes();
    wiring_runs();
}


// ══════════════════════════════════════════════
//  RENDER
// ══════════════════════════════════════════════

// Toggle sections — set false to hide
SHOW_FOUNDATION = true;
SHOW_EXTERIOR   = true;
SHOW_ROOF       = true;
SHOW_INTERIOR   = true;
SHOW_MECHANICAL = true;
SHOW_ROUGH_INS  = true;

if (SHOW_FOUNDATION) foundation();
if (SHOW_EXTERIOR)   exterior_shell();
if (SHOW_ROOF)       roof_system();
if (SHOW_INTERIOR)   interior_layout();
if (SHOW_MECHANICAL) mechanical();
if (SHOW_ROUGH_INS)  rough_ins();
