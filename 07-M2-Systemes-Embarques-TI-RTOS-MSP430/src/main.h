/*
 * main.h
 *
 *
 */

#ifndef MAIN_H_
#define MAIN_H_

//PORT1
#define LEDR          GPIO_PIN0
#define BOUTON1       GPIO_PIN1
#define BOUTON2       GPIO_PIN2

//PORT 9
#define LEDV          GPIO_PIN7

//EVENT
#define TIMEOUT_EVENT   10

#define EVENT_BTN1      Event_Id_01
#define EVENT_BTN2      Event_Id_02

#define EVENT_RTC      Event_Id_03

//EVENT ADC
#define EVENT_ADC_CONV Event_Id_04

#define LONG_PRESS_MS   800     // Duree appui long (ms)

#endif /* MAIN_H_ */
