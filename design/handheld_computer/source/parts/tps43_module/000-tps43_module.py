d=part('shell')
# Mount with the populated side down and the populated half to machine right.
# Azoteq v1.06 figs 1.1, 2.1, 2.2. Reserve the maximum stack across all but
# the far left bare strip. This is a keep-out, not a component-placement STEP.
stack=param('tps43_nominal_stack',2.03)
stack_tolerance=param('tps43_fractional_stack_tol',0.10)
max_stack=stack*(1+stack_tolerance)
bare_stack=param('laminate_and_psa_limit',1.25)
bare_strip=param('unpopulated_edge_allowance',9.0)
w=d.board_w+d.board_tol
h=d.board_d+d.board_tol
top=d.FACE_WORLD*Pos(0,0,-d.face_t)
laminate=Pos(0,0,-bare_stack/2)*Box(w,h,bare_stack)
components=Pos(bare_strip/2,0,-max_stack/2)*Box(w-bare_strip,h,max_stack)
envelope=top*(laminate+components)
envelope.color=Color(0.14,0.36,0.25)
publish('tps43',envelope,'TPS43-201A-S oriented fit envelope (incl. PSA)',role='reference')