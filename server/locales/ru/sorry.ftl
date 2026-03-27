# Sorry localization

game-name-sorry = Sorry!
category-board-games = Настольные игры

# Turn actions
sorry-draw-card = Взять карту
sorry-move-slot = Вариант хода { $slot }
sorry-move-slot-fallback = Выберите ход

# Move labels (for dynamic move menu entries)
sorry-move-start = Вывести фишку { $pawn } со старта
sorry-move-forward = Продвинуть фишку { $pawn } вперёд на { $steps } { $steps ->
    [one] клетку
    [few] клетки
   *[other] клеток
}
sorry-move-backward = Подвинуть фишку { $pawn } назад на { $steps } { $steps ->
    [one] клетку
    [few] клетки
   *[other] клеток
}
sorry-move-swap = Поменять фишку { $pawn } местами с фишкой { $target_pawn } игрока { $target_player }
sorry-move-sorry = Заменить фишку { $target_pawn } игрока { $target_player } своей фишкой { $pawn }
sorry-move-split7 = Разделить 7: фишка { $pawn_a } на { $steps_a }, фишка { $pawn_b } на { $steps_b }

# Gameplay announcements
sorry-card-sorry = Sorry!
sorry-draw-announcement = { $player } берёт карту: { $card }.
sorry-no-legal-moves = У игрока { $player } нет доступных ходов для карты { $card }.
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
   *[other] клеток
}.
sorry-play-backward = { $player } moves pawn { $pawn } backward { $steps }. Pawn { $pawn } is now { $zone ->
        [track] on track square { $position }
        [home_path] on home path step { $home_steps }
        [home] home
       *[other] in start
    }.
   *[other] клеток
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
sorry-option-rules-profile = Профиль правил: { $rules_profile }
sorry-option-select-rules-profile = Выберите профиль правил
sorry-option-changed-rules-profile = Профиль правил изменён на { $rules_profile }.
sorry-rules-profile-classic-00390 = Классика 00390
sorry-rules-profile-a5065-core = A5065 (базовый)
sorry-option-auto-apply-single-move = Автоход при единственном варианте: { $auto_apply_single_move }
sorry-option-faster-setup-one-pawn-out = Быстрый старт (одна фишка сразу на поле): { $faster_setup_one_pawn_out }
sorry-option-changed-auto-apply-single-move = Автоход при единственном варианте: { $auto_apply_single_move }.
sorry-option-changed-faster-setup-one-pawn-out = Быстрый старт: { $faster_setup_one_pawn_out }.