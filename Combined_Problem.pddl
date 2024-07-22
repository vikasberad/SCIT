(define (problem environment_control)
  (:domain environment_control)
  (:init 
    (temp_high)          ;; Add appropriate initial predicates based on the current environment state
    (hum_high)           ;; Replace or remove predicates as needed
    (light_low)          ;; Replace or remove predicates as needed
    (motion_detected)    ;; Assume motion is detected
  )
  (:goal 
    (and 
      (heater_on)
      (dehumidifier_on)
      (light_on)
      (fan_on)
    )
  )
)
