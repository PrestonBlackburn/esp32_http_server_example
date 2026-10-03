// structs to be shared between python parser + main C code

typedef struct {
    uint32_t uptime_s;
    size_t   heap_free;
    int8_t   rssi;
    float    ch1_gain_db;
    float    samples[8];
    bool     wifi_up;
} state_t;