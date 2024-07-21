(define (domain humidity_control)
  (:predicates (hum_high) (hum_low) (humidity_on) (humidity_off))

  (:action turn_on_humidity
    :precondition (hum_low)
    :effect (and (humidity_on) (not (humidity_off))))

  (:action turn_off_humidity
    :precondition (hum_high)
    :effect (and (humidity_off) (not (humidity_on))))
)
