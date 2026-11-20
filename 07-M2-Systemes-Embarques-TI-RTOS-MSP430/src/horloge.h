/*
 * horloge.h
 *
 *
 */

#ifndef HORLOGE_H_
#define HORLOGE_H_


void init_rtc(void);
void Disp_RTC(void);
void RTC_Incr(uint8_t sel);
void RTC_Blink(uint8_t sel);


#endif /* HORLOGE_H_ */
