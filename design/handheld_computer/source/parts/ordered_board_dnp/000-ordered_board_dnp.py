board=asset("design/handheld_computer/source/assets/f4d1106e00ef9053f18fdde994fa0399b11c6b7e574b0a45fb63718ecb94f9ea.step")
nominal_w=param('board_reference_width',43.5)
assert abs(board.bounding_box().size.X-nominal_w)<1.0
publish('pi_baseboard_lite',board,'Single populated display, touch and audio board',role='reference')
fit('pi4b','pi_baseboard_lite',kind='nominal_contact',budget_mm=3.0,reason='Male GPIO shanks enter the unmodeled internal contact space beyond the nominal socket3mm visual cavity; pins aligned on the2.54mm grid, housing clearance checked separately. Actual generic contact geometry requires prototype mating.')