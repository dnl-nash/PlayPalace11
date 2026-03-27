# Sorry localization

game-name-sorry = Sorry!
category-board-games = Board Games

# Turn actions
sorry-draw-card = Draw card
sorry-move-slot = Move option { $slot }
sorry-move-slot-fallback = Choose move

# Move labels (for dynamic move menu entries)
sorry-move-start = Move pawn { $pawn } out of start
sorry-move-forward = Move pawn { $pawn } forward { $steps }
sorry-move-backward = Move pawn { $pawn } backward { $steps }
sorry-move-swap = Swap pawn { $pawn } with { $target_player } pawn { $target_pawn }
sorry-move-sorry = Move pawn { $pawn } to replace { $target_player } pawn { $target_pawn }
sorry-move-split7 = Split 7: pawn { $pawn_a } moves { $steps_a }, pawn { $pawn_b } moves { $steps_b }

# Gameplay announcements
sorry-card-sorry = Sorry!
sorry-draw-announcement = { $player } draws { $card }.
sorry-no-legal-moves = { $player } has no legal moves for { $card }.
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
sorry-option-rules-profile = Rules profile: { $rules_profile }
sorry-option-select-rules-profile = Select rules profile
sorry-option-changed-rules-profile = Rules profile set to { $rules_profile }.
sorry-rules-profile-classic-00390 = Classic 00390
sorry-rules-profile-a5065-core = A5065 Core
sorry-option-auto-apply-single-move = Auto apply single move: { $auto_apply_single_move }
sorry-option-faster-setup-one-pawn-out = Faster setup (one pawn out): { $faster_setup_one_pawn_out }
sorry-option-changed-auto-apply-single-move = Auto apply single move set to { $auto_apply_single_move }.
sorry-option-changed-faster-setup-one-pawn-out = Faster setup set to { $faster_setup_one_pawn_out }.
