
        (define (problem temp_control_problem)
          (:domain temperature_control)
          (:objects)
          (:init (temp_high) (motion_detected) (heater_off) (fan_off))
          (:goal (and (heater_on) (fan_on)))
        )
        