(define (domain environment_control)
    (:predicates
        (temp_high)
        (temp_low)
        (heater_on)
        (heater_off)
        (fan_on)
        (fan_off)
        (motion_detected)
        (no_motion)
        (hum_high)
        (hum_low)
        (dehumidifier_on)
        (dehumidifier_off)
        (light_high)
        (light_low)
        (light_on)
        (light_off)
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

    (:action turn_on_dehumidifier
        :precondition (hum_high)
        :effect (and (dehumidifier_on) (not (dehumidifier_off)))
    )

    (:action turn_off_dehumidifier
        :precondition (hum_low)
        :effect (and (dehumidifier_off) (not (dehumidifier_on)))
    )

    (:action turn_on_light
        :precondition (light_low)
        :effect (and (light_on) (not (light_off)))
    )

    (:action turn_off_light
        :precondition (light_high)
        :effect (and (light_off) (not (light_on)))
    )
)
