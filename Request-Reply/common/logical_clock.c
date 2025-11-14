#include "logical_clock.h"

void logical_clock_init(logical_clock_t* lc) {
    lc->clock = 1;
}

int64_t logical_clock_increment(logical_clock_t* lc) {
    lc->clock++;
    return lc->clock;
}

int64_t logical_clock_update(logical_clock_t* lc, int64_t received_clock) {
    if (received_clock > lc->clock) {
        lc->clock = received_clock + 1;
    } else {
        lc->clock++;
    }
    return lc->clock;
}

int64_t logical_clock_get(logical_clock_t* lc) {
    return lc->clock;
}