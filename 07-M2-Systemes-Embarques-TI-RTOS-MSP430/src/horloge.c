/*
 * horloge.c
 *
 *
 */


#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#include <ti/sysbios/knl/Event.h>

/* TI-RTOS Header files */
#include <driverlib.h>


/* Board Header file */
#include "main.h"
#include "hal_LCD.h"
#include "horloge.h"

/* XDCtools Header files */
#include <xdc/std.h>
#include <xdc/runtime/System.h>
#include <xdc/cfg/global.h>




/**********************************************************************
 * Constantes
 *
 *********************************************************************/



/**********************************************************************
 * Variables globales
 *
 *********************************************************************/

Calendar Calendar_reg;

/**********************************************************************
 * init_rtc
 *********************************************************************/


void init_rtc(void)
{
    Calendar_reg.DayOfMonth = 0x7;
    Calendar_reg.DayOfWeek = 5;
    Calendar_reg.Hours = 8;
    Calendar_reg.Minutes = 30;
    Calendar_reg.Month = 01;
    Calendar_reg.Seconds = 8;
    Calendar_reg.Year = 2026;

    RTC_C_initCalendar(RTC_C_BASE, &Calendar_reg, RTC_C_FORMAT_BINARY);
    RTC_C_startClock(RTC_C_BASE);

    RTC_C_clearInterrupt(RTC_C_BASE, RTC_C_CLOCK_READ_READY_INTERRUPT);
    RTC_C_enableInterrupt(RTC_C_BASE, RTC_C_CLOCK_READ_READY_INTERRUPT);
}


/**********************************************************************
 * Irq_Rtc()
 *********************************************************************/

void Irq_Rtc(void)
{
    uint8_t status = RTC_C_getInterruptStatus(RTC_C_BASE, RTC_C_CLOCK_READ_READY_INTERRUPT);

    switch(status)
    {
        case RTC_C_CLOCK_READ_READY_INTERRUPT:
            Event_post(h_event0, EVENT_RTC);
            RTC_C_clearInterrupt(RTC_C_BASE, RTC_C_CLOCK_READ_READY_INTERRUPT);
            break;

        default:
            break;
    }
}

/**********************************************************************
 * Disp_RTC()
 *********************************************************************/
void Disp_RTC(void)
{
    Calendar_reg = RTC_C_getCalendarTime(RTC_C_BASE);

    ShowChar((Calendar_reg.Seconds) %10 + '0',pos6);
    ShowChar((Calendar_reg.Seconds) /10 + '0',pos5);

    ShowChar((Calendar_reg.Minutes) %10 + '0',pos4);
    ShowChar((Calendar_reg.Minutes) /10 + '0',pos3);

    ShowChar((Calendar_reg.Hours) %10 + '0',pos2);
    ShowChar((Calendar_reg.Hours) /10 + '0',pos1);

    ClockColon();


}


void RTC_Incr(uint8_t sel)
{
    Calendar time = RTC_C_getCalendarTime(RTC_C_BASE);

    switch(sel)
    {
    case 0 :
        time.Hours += 1;
        if (time.Hours >= 24) time.Hours = 0;
        break;

    case 1 :
        time.Minutes += 1;
        if (time.Minutes >= 60) time.Minutes = 0;
        break;

    case 2 :
        time.Seconds += 1;
        if (time.Seconds >= 60) time.Seconds = 0;
        break;
    }

    RTC_C_initCalendar(RTC_C_BASE, &time, RTC_C_FORMAT_BINARY);
    RTC_C_startClock(RTC_C_BASE);
    Disp_RTC();

}

void RTC_Blink(uint8_t sel)
{
    Calendar time = RTC_C_getCalendarTime(RTC_C_BASE);
    static bool blink = false;

    blink = !blink;
    Disp_RTC();

    if (blink)
    {
        switch (sel)
        {
        case 0: // Heures
            ShowChar(' ', pos2);
            ShowChar(' ', pos1);
            break;

        case 1: // Minutes
            ShowChar(' ', pos4);
            ShowChar(' ', pos3);
            break;

        case 2: // Secondes
            ShowChar(' ', pos6);
            ShowChar(' ', pos5);
            break;

        default:
            return; // sel invalide
        }
    }
    // Active les deux points du LCD (séparateurs)
    LCDM7   |= 0x04;
    LCDBM7  |= 0x04;
    LCDM20  |= 0x04;
    LCDBM20 |= 0x04;

    RTC_C_startClock(RTC_C_BASE);
    return;
}

