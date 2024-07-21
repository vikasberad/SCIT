(define (domain light_control)
  (:predicates (light_on) (light_off) (low_light) (sufficient_light))

  (:action turn_on_light
    :precondition (low_light)
    :effect (and (light_on) (not (light_off))))

  (:action turn_off_light
    :precondition (sufficient_light)
    :effect (and (light_off) (not (light_on))))
)
