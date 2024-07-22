
        (define (problem temperature_problem)
          (:domain temperature_control)
          (:init  (temp_high) (heater_off) (fan_off) (motion_detected))
          (:goal (and (fan_on) (heater_off)))
        )
        