#ifndef LOGICAL_CLOCK_H
#define LOGICAL_CLOCK_H

#include <stdint.h>
typedef struct {
    int64_t clock;
} logical_clock_t;

void logical_clock_init(logical_clock_t* lc);
int64_t logical_clock_increment(logical_clock_t* lc);
int64_t logical_clock_update(logical_clock_t* lc, int64_t received_clock);
int64_t logical_clock_get(logical_clock_t* lc);

#endif