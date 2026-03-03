# ----------------------------------------------------------------------
# Train Controller - Schedule of Events
# Mike Christle 2025
# ----------------------------------------------------------------------

import gpio_numbers_R2 as gn

SWITCH = 0  # set_switch(delay, sw_num, pos)
SPEED  = 1  # set_speed(delay, engine, speed)
SET_FN = 2  # set_func(delay, engine, func)
CLR_FN = 3  # clr_func(delay, engine, func)

# Switch States
STRAIGHT = 0
TURN = 1

# Function Options
BELL = 1
HORN = 2

# State
# 0-3   Sensor Number
# 4-11  State Number
# 12-15 Engine Number

# Switch No
# 0 2
# 1 3

event_sch = (

 # Engine 4, 3012
 (0x4001,    # State 0
  (0x4013,   # Next State
   (         # Actions
    (SPEED,       0, 4, 0),
    (SET_FN,      0, 4, HORN),
    (CLR_FN,  2_000, 4, HORN),
   )
  )
 ),
 (0x4013,    # State 1
  (0x4022,   # Next State
   (         # Actions
    (SET_FN,    000, 4, HORN),
    (SWITCH,    000, 0, STRAIGHT),
    (SWITCH,    500, 1, TURN),
    (CLR_FN,  2_000, 4, HORN),
    (SPEED,   2_000, 4, 40),
   )
  )
 ),
 (0x4022,    # State 2
  (0x4033,   # Next State
   (         # Actions
    (SET_FN,    000, 4, BELL),
    (SWITCH,    000, 2, TURN),
    (SWITCH,    500, 3, STRAIGHT),
    (CLR_FN,  2_000, 4, BELL),
    (SPEED,   4_000, 4, 40),
   )
  )
 ),
 (0x4033,    # State 3
  (0x4043,   # Next State
   (         # Actions
    (SPEED,       0, 4, 30),
    (SET_FN,      0, 4, BELL),
    (SWITCH,      0, 2, STRAIGHT),
    (SWITCH,      0, 3, STRAIGHT),
    (CLR_FN,  2_000, 4, BELL),
    (SPEED,   4_000, 4, 40),
   )
  )
 ),
 (0x4043,    # State 4
  (0x4050,   # Next State
   (         # Actions
    (SPEED,       0, 4, 30),
    (SET_FN,      0, 4, BELL),
    (SWITCH,      0, 2, STRAIGHT),
    (SWITCH,      0, 3, TURN),
    (CLR_FN,  2_000, 4, BELL),
    (SPEED,   4_000, 4, 40),
   )
  )
 ),
 (0x4050,    # State 5
  (0x4061,   # Next State
   (         # Actions
    (SPEED,       0, 4, 30),
    (SET_FN,      0, 4, BELL),
    (SWITCH,      0, 0, TURN),
    (SWITCH,      0, 1, STRAIGHT),
    (CLR_FN,  2_000, 4, BELL),
    (SPEED,   4_000, 4, 40),
   )
  )
 ),
 (0x4061,    # State 6
  (0x4001,   # Next State
   (         # Actions
    (SET_FN,      0, 4, BELL),
    (SWITCH,      0, 0, TURN),
    (SWITCH,      0, 1, TURN),
    (CLR_FN,  2_000, 4, BELL),
   )
  )
 ),


 # Engine 5, 3013
 (0x5043,    # State 4
  (0x5050,   # Next State
   (         # Actions
    (SPEED,       0, 5, 30),
    (SET_FN,      0, 5, BELL),
    (SWITCH,      0, 2, STRAIGHT),
    (SWITCH,      0, 3, TURN),
    (CLR_FN,  2_000, 5, BELL),
    (SPEED,   4_000, 5, 40),
   )
  )
 ),
 (0x5050,    # State 5
  (0x5061,   # Next State
   (         # Actions
    (SPEED,       0, 5, 30),
    (SET_FN,      0, 5, BELL),
    (SWITCH,      0, 0, TURN),
    (SWITCH,      0, 1, STRAIGHT),
    (CLR_FN,  2_000, 5, BELL),
    (SPEED,   4_000, 5, 40),
   )
  )
 ),
 (0x5061,    # State 6
  (0x5001,   # Next State
   (         # Actions
    (SET_FN,      0, 5, BELL),
    (SWITCH,      0, 0, TURN),
    (SWITCH,      0, 1, TURN),
    (CLR_FN,  2_000, 5, BELL),
   )
  )
 ),
 (0x5001,    # State 0
  (0x5013,   # Next State
   (         # Actions
    (SPEED,       0, 5, 0),
    (SET_FN,      0, 5, HORN),
    (CLR_FN,  2_000, 5, HORN),
   )
  )
 ),
 (0x5013,    # State 1
  (0x5022,   # Next State
   (         # Actions
    (SET_FN,    000, 5, HORN),
    (SWITCH,    000, 0, STRAIGHT),
    (SWITCH,    500, 1, TURN),
    (CLR_FN,  2_000, 5, HORN),
    (SPEED,   2_000, 5, 40),
   )
  )
 ),
 (0x5022,    # State 2
  (0x5033,   # Next State
   (         # Actions
    (SET_FN,    000, 5, BELL),
    (SWITCH,    000, 2, TURN),
    (SWITCH,    500, 3, STRAIGHT),
    (CLR_FN,  2_000, 5, BELL),
    (SPEED,   4_000, 5, 40),
   )
  )
 ),
 (0x5033,    # State 3
  (0x5043,   # Next State
   (         # Actions
    (SPEED,       0, 5, 30),
    (SET_FN,      0, 5, BELL),
    (SWITCH,      0, 2, STRAIGHT),
    (SWITCH,      0, 3, STRAIGHT),
    (CLR_FN,  2_000, 5, BELL),
    (SPEED,   4_000, 5, 40),
   )
  )
 ),
)


#     (SPEED,       0, 4, 0),
#     (SET_FN,  7_000, 4, BELL),
#     (SWITCH,  9_000, 0, TURN),
#     (SWITCH,  9_500, 1, TURN),
#     (CLR_FN, 10_000, 4, BELL),
#     (SPEED,  10_000, 4, 60),
#     (SWITCH, 15_000, 0, STRAIGHT),
#     (SWITCH, 15_500, 1, STRAIGHT),
#     (SPEED,  17_000, 4, 20),
#     (SET_FN, 17_000, 4, HORN),
#     (CLR_FN, 20_000, 4, HORN),
