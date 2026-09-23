# Source assets

- `source/footprints/L_Wurth_WE-LHMI-7030.kicad_mod`: Würth Elektronik WE-LHMI 7030 family footprint for selected 74437349010 (1 µH); SHA-256 `069c83f984321ecad859e92c06ad3d51305f95bc1445050b0436d787cf218959`.
- `source/footprints/L_Wurth_WE-LHMI-7050.kicad_mod`: Würth Elektronik WE-LHMI 7050 family footprint for selected 74437349022 (2.2 µH); SHA-256 `b295eceddb3d3f680e25355dab5b74d30e467fe79dcadf3fb39a04b41d8161a6`.

Both are unmodified entries extracted from Würth Elektronik `KiCad_WE-LHMI (rev26b).zip`, SHA-256 `a6f41e31d082062e5dc4c4eb4e9bd4e44cc83aeffc08deb04431025f7837e312`, linked from [WE-LHMI product catalog](https://www.we-online.com/en/components/products/WE-LHMI) and downloaded from [manufacturer archive](https://www.we-online.com/components/products/download/KiCad_WE-LHMI%20%28rev26b%29.zip) on 2026-09-24 (JST). The archive contains no separate licence notice visible in these two footprint files; usage terms must be checked before redistribution beyond this project.

Manufacturer dimension/land-pattern evidence: [74437349010](https://www.we-online.com/components/products/datasheet/74437349010.pdf) and [74437349022](https://www.we-online.com/components/products/datasheet/74437349022.pdf). The 7030/7050 family dimensions must be cross-checked against the released assembly model and actual reels before placement sign-off.

TPS61088RHLR C87357 uses the representation-corrected version (see below) of KiCad's stock `Package_DFN_QFN/Texas_VQFN-RHL-20` footprint. The selected IC's [TI datasheet](https://www.ti.com/lit/ds/symlink/tps61088.pdf), package RHL0020A, p31, gives the same land pattern and labels eight thermal-pad vias optional by application; it recommends filled, plugged or tented vias if used under paste. This standard footprint has no embedded vias, avoiding an unqualified via-in-pad assembly process. It does not establish a thermal rating for the high-current boost stage.

The battery wire connection uses KiCad's stock `Connector_Wire/SolderWire-1sqmm_1x02_P5.4mm_D1.4mm_OD2.7mm_Relief` footprint (single strain-relief pair). This is an electrical draft connection for 1 mm² wires, not a promise that the battery harness or its bend clearance fits the enclosure.

## Supervisor footprint bindings (2026-09-24)

The new controller parts use stock KiCad package footprints with their original
MPNs and supplier identities retained. These are native top-side library assets;
the compiler applies bottom-side placement. No coordinates were copied from a
mirrored preview. This also removes the new controller's dependency on live
supplier-footprint retrieval while investigating a compiler timeout.

| Ref | Exact package and KiCad footprint | Evidence |
| --- | --- | --- |
| U_MCU | SOIC-20W_7.5x12.8mm_P1.27mm | Microchip DS40002204A pp15,566,572–573: ATTINY1616-SN, 20 pins, 7.50 × 12.80 mm body, 1.27 mm pitch |
| U_HOST_TX/RX/REQ/ACK, U_CHG_PERMIT, U_RUN_PERMIT | SOT-23-5 | TI SN74LVC1G07 DBV; C7829 datasheet p3 pin map |
| U_POR | SOT-23-6 | TI TPS3808G33DBVR, DBV; interlock-por-ti.pdf |
| U_SCHMITT | SOT-363_SC-70-6 | TI SN74LVC2G17DCKR, DCK; interlock-schmitt-ti.pdf |
| U_LATCH | VSSOP-8_2.3x2mm_P0.5mm | TI SN74LVC1G74DCUR, DCU; interlock-latch-ti.pdf |
| U_AUX_LIMIT | SOT-23-6 | TI TPS2553DBVR, DBV; tps2553-ti.pdf pp5,25 |

Board-wide vias restored to 0.6 mm pads / 0.3 mm drills. The former 0.4/0.2 mm
setting had no documented whole-board manufacturing justification. Fine-pitch
power escape still requires actual local geometry and a wide trunk; no escape
length or current requirement has been relaxed.

## RHL exposed-pad representation correction

The routing DSN converted the stock RHL custom concave EP into its convex hull.
That hull fills the notches beside pads 1 and 10; BOOST_VCC and BOOST_SS stayed
unrouted in the complete check. The project-local
`Texas_VQFN-RHL-20_RectangularEP.kicad_mod` changes only that custom EP into two
overlapping **pad 21** rectangles: 2.05 × 3.05 mm and 0.75 × 3.85 mm, centered at
the native library origin. Their union is exactly the original cross outline,
area 6.8525 mm². Pad number, copper/mask layers, solid zone connection, paste
islands, all peripheral pads and pin-1 orientation remain unchanged. This is a
representation repair to the standard footprint, not a new land pattern. The
native installed KiCad file, not placed output, supplied every dimension.

Long semantic reference text on compact components is suppressed in PCB source;
full references remain in schematic/BOM and assembly data. Native pin-1 and
polarity graphics and short service labels are retained. Actual silk clearance
is still checked by the normal gates.

The native RHL file SHA-256 is
`bf6fd2cac81cb373b9dccd59445786341e76d3f4acbf023a9d9ac3bc478766d4`;
the repaired file SHA-256 is
`45ecee07eecaf9be909e3c497278c0a9a6000d5973bd2036f776adcc581ff069`.

## Fine-pitch ground access and numeric precision

BQ25622 RYK lands have about 0.176 mm edge gaps. A 0.30 mm pour clearance
cuts off their ground pad; moving the standard pads is not permissible.
Ground clearance and pour pad margin are set to the existing 0.15 mm
manufacturing floor, with 0.25 mm trace margin and unchanged edge margin.
This requires a fabrication process that actually supports that declared
geometry; no supplier capability is certified here. High-current width and
escape-length limits are unchanged.

For CHG_PMID/REGN/ILIM/TS/INT/SDA/SCL only, the supplier's 0.2240026 mm pad
width is represented by an explicit 0.224 mm net minimum, matching the export
grid. Nominal routing widths are unchanged. This removes a nanometre-scale
numeric mismatch, not a physical current-capacity failure. High-current nets
remain blocked until they have appropriate wide copper.

The TPS259470 RPW adjacent signal land edges are about 0.200 mm apart.
LCD_ILM and V5_LCD explicitly use the existing 0.15 mm clearance floor,
without lowering their width or current targets. R_LCD_ILM is placed near
U_LCD_EFUSE, C_LCD_DVDT is separated from its courtyard, and UPDI is moved
away from the lid-reset escape. Final routing results are recorded in README.md.
