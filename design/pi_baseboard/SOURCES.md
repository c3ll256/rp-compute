# Source assets

- `source/footprints/L_Wurth_WE-LHMI-7030.kicad_mod`: Würth Elektronik WE-LHMI 7030 family footprint for selected 74437349010 (1 µH); SHA-256 `069c83f984321ecad859e92c06ad3d51305f95bc1445050b0436d787cf218959`.
- `source/footprints/L_Wurth_WE-LHMI-7050.kicad_mod`: Würth Elektronik WE-LHMI 7050 family footprint for selected 74437349022 (2.2 µH); SHA-256 `b295eceddb3d3f680e25355dab5b74d30e467fe79dcadf3fb39a04b41d8161a6`.

Both are unmodified entries extracted from Würth Elektronik `KiCad_WE-LHMI (rev26b).zip`, SHA-256 `a6f41e31d082062e5dc4c4eb4e9bd4e44cc83aeffc08deb04431025f7837e312`, linked from [WE-LHMI product catalog](https://www.we-online.com/en/components/products/WE-LHMI) and downloaded from [manufacturer archive](https://www.we-online.com/components/products/download/KiCad_WE-LHMI%20%28rev26b%29.zip) on 2026-09-24 (JST). The archive contains no separate licence notice visible in these two footprint files; usage terms must be checked before redistribution beyond this project.

Manufacturer dimension/land-pattern evidence: [74437349010](https://www.we-online.com/components/products/datasheet/74437349010.pdf) and [74437349022](https://www.we-online.com/components/products/datasheet/74437349022.pdf). The 7030/7050 family dimensions must be cross-checked against the released assembly model and actual reels before placement sign-off.

TPS61088RHLR C87357 uses KiCad's stock `Package_DFN_QFN/Texas_VQFN-RHL-20` footprint. The selected IC's [TI datasheet](https://www.ti.com/lit/ds/symlink/tps61088.pdf), package RHL0020A, p31, gives the same land pattern and labels eight thermal-pad vias optional by application; it recommends filled, plugged or tented vias if used under paste. This standard footprint has no embedded vias, avoiding an unqualified via-in-pad assembly process. It does not establish a thermal rating for the high-current boost stage.

The battery wire connection uses KiCad's stock `Connector_Wire/SolderWire-1sqmm_1x02_P5.4mm_D1.4mm_OD2.7mm_Relief` footprint (single strain-relief pair). This is an electrical draft connection for 1 mm² wires, not a promise that the battery harness or its bend clearance fits the enclosure.
