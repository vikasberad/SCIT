(define (problem environment_control)
    (:domain environment_control)
    (:init
        (temp_high)
        (hum_high)
        (light_low)
        (motion_detected)
    )
    (:goal
        (and
            (fan_on)
            (dehumidifier_on)
            (light_on)
        )
    )
)
