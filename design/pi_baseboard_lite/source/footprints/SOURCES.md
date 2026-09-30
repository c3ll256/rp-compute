# Connector footprint and model provenance

HLE copper: official KiCad Connector_Samtec_HLE_SMD footprint installed with KiCad; https://gitlab.com/kicad/libraries/kicad-footprints/-/blob/master/Connector_Samtec_HLE_SMD.pretty/Samtec_HLE-104-02-xxx-DV_2x04_P2.54mm_Horizontal.kicad_mod . Licence GPL3 with KiCad library exception. The unavailable model reference alone is removed; all pads, mask, paste and courtyard geometry are unchanged. Original SHA256 bf43f4c413bd6e8136582d7cc66ba52116a9004bd580a3ca0c9c15d1ca7ca000; local SHA256 277f7073a3ca72cd462730ac083e16a8b461dc8d9efea81f041f8802fbaabda0.

ESQ copper remains exact supplier C3319198. Its downloaded STEP has excessive tails (4.915mm above the reverse PCB face); nominal selected tail is2.29mm.

Both new STEP files are deliberately modeled **nominal drawing references**, not supplier/manufacturer STEP assets. Build123d source and tool exports are stored as connector_fit_references and hle_fit_reference designs. Housing sizes, lead span and pitch come from https://suddendocs.samtec.com/catalog_english/esq_th.pdf and https://suddendocs.samtec.com/prints/hle-1xx-02-xxx-dv-xx-xx-x-xx-mkt.pdf . Cavities indicate pin locations only; internal contacts, latch force and solder shape are omitted. Geometry validates enclosure envelopes; physical mating and retention remain prototype checks.

esq-120-12-g-d-drawing-reference.step SHA256 1c4e4fd307d7f8a48d0965b581b95c1e37590160069f9e4f6665a3c083be10fc
hle-104-02-g-dv-drawing-reference.step SHA256 33dce5b72ab2367bfa9f56eeb865dfe7837cbf12eb2d9434a77a5909335b00b0
