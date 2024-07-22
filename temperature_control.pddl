(define (domain temperature_control)
  (:predicates 
    (temp_high)
    (temp_low)
    (heater_on)
    (heater_off)
    (fan_on)
    (fan_off)
    (motion_detected)
    (no_motion)
  )

  (:action turn_on_heater
    :precondition (and (temp_low) (motion_detected))
    :effect (and (heater_on) (not (heater_off)))
  )

  (:action turn_off_heater
    :precondition (or (temp_high) (no_motion))
    :effect (and (heater_off) (not (heater_on)))
  )

  (:action turn_on_fan
    :precondition (and (temp_high) (motion_detected))
    :effect (and (fan_on) (not (fan_off)))
  )

  (:action turn_off_fan
    :precondition (or (temp_low) (no_motion))
    :effect (and (fan_off) (not (fan_on)))
  )
)
