(define (domain sound_level)
  (:predicates (sound_on) (sound_off) (low_sound) (high_sound))

  (:action turn_on_sound_alert
    :precondition (high_sound)
    :effect (and (sound_on) (not (sound_off))))

  (:action turn_off_sound_alert
    :precondition (low_sound)
    :effect (and (sound_off) (not (sound_on))))
)
