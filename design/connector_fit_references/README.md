# Connector nominal references

The ESQ object is a historical drawing-based nominal reference for Samtec ESQ-120-12-G-D. Sources: https://suddendocs.samtec.com/catalog_english/esq_th.pdf and https://suddendocs.samtec.com/prints/hle-1xx-02-xxx-dv-xx-xx-x-xx-mkt.pdf .

The generic_40pin and generic_8pin objects support the user-selected through-hole PCB revision. They are deliberately modeled nominal references from supplied dimensions and recorded engineering defaults, not manufacturer STEP assets. The40-pin housing is51x5x8mm with3.5mm tails; the8-pin housing is nominal10.16x5.08x5mm with3mm tails. Both use2.54mm pitch/row spacing and0.64mm square tails. Cavities show mating locations only and do not specify insertion limits or contact geometry.

Each generic object uses the native KiCad socket frame: pin1 at(0,0), even pins atX-2.54, later pin pairs along negative modelY. Their display offsets areX80 andX100; remove these offsets when extracting the published STEP as PCB model inputs. Copper footprints remain the published KiCad library unchanged, with only its unrelated stock-model reference removed in project copies.

## Making and assembly

These are reference components, not parts to print. Purchase the sockets by the recorded specifications. Fit the through-hole connectors after top-side reflow. Prototype soldering, pin insertion, contact engagement, retention and actual connector tolerances remain physical checks; the module's mechanical screws carry its mounting load.
