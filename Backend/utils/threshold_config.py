# All tunable alert thresholds in one place.
# Change these values without touching business logic.

THRESHOLDS = {
    "crowd_density": {
        "human_count_limit": 50,          # max humans before alert triggers
        "consecutive_seconds": 10,         # must persist this long to confirm alert
    },
    "vehicle_accident": {
        "iou_overlap_threshold": 0.3,      # bounding box overlap ratio (0 to 1)
        "consecutive_frames": 5,           # overlap must persist across frames
    },
    "wrong_lane": {
        "direction_deviation_degrees": 150, # angle difference to flag wrong direction
    },
    "congestion": {
        "vehicle_count_limit": 20,         # max vehicles before congestion alert
        "zone_area": 250000,               # monitored zone area in pixels squared
    }
}