# Sorry localization

game-name-sorry = Izvini!
category-board-games = igre na tabli

# Turn actions
sorry-draw-card = Izvuci kartu
sorry-move-slot = Pomeri opciju { $slot }
sorry-move-slot-fallback = Izaberite pomeranje

# Move labels (for dynamic move menu entries)
sorry-move-start = Pomeri pešaka { $pawn } sa početka
sorry-move-forward = Pomeri pešaka { $pawn } napred { $steps }
sorry-move-backward = Pomeri pešaka { $pawn } nazad { $steps }
sorry-move-swap = Zameni pešaka { $pawn } sa pešakom igrača { $target_player }  { $target_pawn }
sorry-move-sorry = Pomeri pešaka { $pawn } kako bi zamenio pešaka igrača { $target_player }  { $target_pawn }
sorry-move-split7 = Split 7: Pešak { $pawn_a } se pomera { $steps_a }, pešak { $pawn_b } se pomera { $steps_b }

# Gameplay announcements
sorry-card-sorry = Izvini!
sorry-draw-announcement = { $player } vuče { $card }.
sorry-no-legal-moves = { $player } nema dozvoljenih poteza za { $card }.
sorry-play-start = { $player } moves pawn { $pawn } out of start. Pawn { $pawn } is now { $zone ->
        [track] on track square { $position }
        [home_path] on home path step { $home_steps }
        [home] home
       *[other] in start
    }.
sorry-play-forward = { $player } moves pawn { $pawn } forward { $steps }. Pawn { $pawn } is now { $zone ->
        [track] on track square { $position }
        [home_path] on home path step { $home_steps }
        [home] home
       *[other] in start
    }.
sorry-play-backward = { $player } moves pawn { $pawn } backward { $steps }. Pawn { $pawn } is now { $zone ->
        [track] on track square { $position }
        [home_path] on home path step { $home_steps }
        [home] home
       *[other] in start
    }.
sorry-play-swap = { $player } swaps pawn { $pawn } with { $target_player } pawn { $target_pawn }. Pawn { $pawn } is now { $zone ->
        [track] on track square { $position }
        [home_path] on home path step { $home_steps }
        [home] home
       *[other] in start
    }, { $target_player } pawn { $target_pawn } is now { $target_zone ->
        [track] on track square { $target_position }
        [home_path] on home path step { $target_home_steps }
        [home] home
       *[other] in start
    }.
sorry-play-sorry = Sorry! { $player } replaces { $target_player } pawn { $target_pawn } with pawn { $pawn }. Pawn { $pawn } is now { $zone ->
        [track] on track square { $position }
        [home_path] on home path step { $home_steps }
        [home] home
       *[other] in start
    }.
sorry-play-split7 = { $player } splits 7: pawn { $pawn_a } moves { $steps_a }, pawn { $pawn_b } moves { $steps_b }. Pawn { $pawn_a } is now { $a_zone ->
        [track] on track square { $a_position }
        [home_path] on home path step { $a_home_steps }
        [home] home
       *[other] in start
    }, pawn { $pawn_b } is now { $b_zone ->
        [track] on track square { $b_position }
        [home_path] on home path step { $b_home_steps }
        [home] home
       *[other] in start
    }.



# Home arrival announcements
sorry-pawn-home = { $player } pawn { $pawn } has arrived home!
sorry-you-pawn-home = Your pawn { $pawn } has arrived home!

# Options
sorry-option-rules-profile = Profil pravila: { $rules_profile }
sorry-option-select-rules-profile = Izaberite profil pravila
sorry-option-changed-rules-profile = Profil pravila podešen na { $rules_profile }.
sorry-rules-profile-classic-00390 = Klasičan 00390
sorry-rules-profile-a5065-core = A5065 Core
sorry-option-auto-apply-single-move = Automatski odigraj jedan potez: { $auto_apply_single_move }
sorry-option-faster-setup-one-pawn-out = Brži početak (jedan pešak van): { $faster_setup_one_pawn_out }
sorry-option-changed-auto-apply-single-move = Automatsko primenjivanje jednog poteza set to { $auto_apply_single_move }.
sorry-option-changed-faster-setup-one-pawn-out = Brži početak { $faster_setup_one_pawn_out }.
