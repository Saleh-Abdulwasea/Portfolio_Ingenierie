
/*
 *  ======== empty_min.c ========
 */
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* XDCtools Header files */
#include <xdc/std.h>
#include <xdc/runtime/System.h>
#include <xdc/cfg/global.h>

/* BIOS Header files */
#include <ti/sysbios/BIOS.h>
#include <ti/sysbios/knl/Task.h>
#include <ti/sysbios/knl/Event.h>
#include <ti/sysbios/knl/Semaphore.h>
#include <ti/sysbios/knl/Mailbox.h>
/* TI-RTOS Header files */
#include <driverlib.h>


/* Board Header file */
#include "main.h"
#include "hal_LCD.h"
#include "horloge.h"
#include "degre.h"



/*******************************************************************************
 * VARIABLES GLOBALES
 *
 ********************************************************************************/

typedef struct MsgObj {
    int val;
    char Id;
    char Buffer[10];
}MsgObj;

MsgObj Msgx;
MsgObj Msgx2;


uint8_t mode = 0;
uint8_t mode_ht = 0;
uint8_t incr = 0;



/*********************************************************************************
 * Prototype
 *********************************************************************************/
void Init_GPIO(void);
void Event_BTN1(UArg arg0, UArg arg1);
void Event_BTN2(UArg arg0, UArg arg1);

/**************************************************************************
 *  ======== heartBeatFxn ========
 *  Toggle the Board_LED0. The Task_sleep is determined by arg0 which
 *  is configured for the heartBeat Task instance.
 **************************************************************************/
void Task_Heart(UArg arg0, UArg arg1)
{
   // uint8_t counter;
    while (1)
    {
        Heart_Point();
        Task_sleep(1000);   //1s
        Heart_Clr();
        Task_sleep(1000);   //1s
	}
}



/**************************************************************************
*
***************************************************************************/

void Task_LedV(UArg arg0, UArg arg1)
{
    while (1)
    {
        GPIO_toggleOutputOnPin(GPIO_PORT_P9, LEDV);
        Task_sleep(500);   //0.5s
    }
}

/*********************************************************************************
 *  ======== main ========
 *********************************************************************************/
int main(void)
{
    WDT_A_hold(WDT_A_BASE);
    PM5CTL0 &= ~LOCKLPM5;

    Init_GPIO();
    Init_LCD();
    Timer_Point(); // Exigence 1 : affichage icone chronometre au demarrage
    init_rtc();
    Init_ADC();




    /* Start BIOS */
    BIOS_start();

    return (0);
}


/*********************************************************************************
 *  ======== Init_GPIO ========
 *********************************************************************************/
void Init_GPIO(void)
{
    //PORT1
    GPIO_setAsOutputPin(GPIO_PORT_P1, LEDR);
    GPIO_setOutputLowOnPin(GPIO_PORT_P1, LEDR);

    GPIO_setAsInputPin(GPIO_PORT_P1, BOUTON1+BOUTON2); //ou logique (OR)


    //PORT9
    GPIO_setAsOutputPin(GPIO_PORT_P9, LEDV);
    GPIO_setOutputLowOnPin(GPIO_PORT_P9, LEDV);

    //INTERRUPTION
    GPIO_setAsInputPinWithPullUpResistor(GPIO_PORT_P1, BOUTON1+BOUTON2);
    GPIO_selectInterruptEdge(GPIO_PORT_P1, BOUTON1+BOUTON2, GPIO_HIGH_TO_LOW_TRANSITION);

    GPIO_clearInterrupt(GPIO_PORT_P1, BOUTON1+BOUTON2);
    GPIO_enableInterrupt(GPIO_PORT_P1, BOUTON1+BOUTON2);
}

/*********************************************************************************
 *  ======== IRQ_PORT1 ========
 *********************************************************************************/
void Irq_Port1(unsigned nIrq)
{
    uint16_t statusIrq = GPIO_getInterruptStatus(GPIO_PORT_P1, BOUTON1+BOUTON2);

    switch(statusIrq)
    {
    case BOUTON1:

        Event_post(h_event0, EVENT_BTN1);

        GPIO_clearInterrupt(GPIO_PORT_P1, BOUTON1);
        break;

    case BOUTON2:
        Event_post(h_event0, EVENT_BTN2);

        GPIO_clearInterrupt(GPIO_PORT_P1, BOUTON2);
        break;
    }


}



/*****************************************
 * Appui long
 *
 ****************************************/

static bool IsLongPress(uint16_t pinMask, uint32_t durationMs)
{
    uint32_t t = 0;

    // bouton appuye = 0
    while(GPIO_getInputPinValue(GPIO_PORT_P1, pinMask) == 0)
    {
        Task_sleep(10);
        t += 10;

        if(t >= durationMs)
            return true;
    }

    return false;
}


/**************************************************************************
*
***************************************************************************/
void Event_BTN1(UArg arg0, UArg arg1)
{
    uint16_t posted;

    while (1)
    {
        posted = Event_pend(h_event0,
                            Event_Id_NONE,
                            EVENT_BTN1,
                            TIMEOUT_EVENT);

        switch(posted)
        {
            case EVENT_BTN1:

                // En  mode affichage temperature : BTN1 ne fait rien
                if(mode_ht == 1)
                    break;

                //  MODE NORMAL : appui long BTN1 : entrer mode reglage
                if(mode == 0)
                {
                    if(IsLongPress(BOUTON1, LONG_PRESS_MS))
                    {
                        mode = 1;    // entrer reglage directement sur l'heure
                        break;
                    }
                    else
                    {
                        // appui court en mode normal : rien ne se passe
                        break;
                    }
                }

                // MODE REGLAGE : appui court BTN1 => deplacer le curseur H->M->S
                // Ici on sort du reglage avec BTN2 long
                if(mode == 1)      mode = 2;   // H -> M
                else if(mode == 2) mode = 3;   // M -> S
                else if(mode == 3) mode = 1;   // S -> H
                break;
        }

        Task_sleep(300);
    }
}



void Task_Timer_Point(UArg arg0, UArg arg1)
{
    while(1){
        if(mode_ht == 0){ //MODE HEURE

            if(mode == 0){
                Clock_OFF();
                Task_sleep(1000);   //1s
                //break;
            }

            if(mode != 0){
                Clock_ON();
                Task_sleep(1000);   //1s
                Clock_OFF();
                Task_sleep(1000);   //1s
            }


        }
        else if(mode_ht == 1){
                Clock_OFF();
                Task_sleep(1000);   //1s
        }
    }
}

void Event_BTN2(UArg arg0, UArg arg1)
{
    uint16_t posted;

    while (1)
    {
        posted = Event_pend(h_event0,
                            Event_Id_NONE,
                            EVENT_BTN2,
                            TIMEOUT_EVENT);

        switch(posted)
        {
            case EVENT_BTN2:

                // MODE REGLAGE : appui long BTN2 => sortie reglage
                if(mode != 0 && mode_ht == 0)
                {
                    if(IsLongPress(BOUTON2, LONG_PRESS_MS))
                    {
                        mode = 0;        // retour repos

                        break;
                    }
                }

                //  MODE NORMAL : BTN2 court => Heure <-> Temperature
                if(mode == 0)
                {
                    if(mode_ht == 0) mode_ht = 1;   // H -> T
                    else             mode_ht = 0;   // T -> H
                    break;
                }

                //MODE REGLAGE : BTN2 court => incrementer lelement selectionne
                if(mode_ht == 0)
                {
                    if(mode == 1)      RTC_Incr(0);   // Heure
                    else if(mode == 2) RTC_Incr(1);   // Minutes
                    else if(mode == 3) RTC_Incr(2);   // Secondes

                    Task_sleep(400); // debounce increment
                }
                break;
        }

        Task_sleep(300); // anti-rebond global
    }
}




void Task_RTC(UArg arg0, UArg arg1)
{
    uint16_t posted;

    while (1)
    {
        posted = Event_pend(h_event0,
                            Event_Id_NONE, //Mask AND
                            EVENT_RTC, //Mask OR
                            TIMEOUT_EVENT//Timeout
                );

        switch(posted)
                {
                case EVENT_RTC:
                   if(mode_ht == 1){

                       Start_Conversion();
                       Task_sleep(100);
                       break;
                   }

                   else if(mode_ht == 0){
                       if(mode == 0){
                           Disp_RTC();
                           Task_sleep(100);
                           break;
                       }
                       else if(mode == 1){
                           RTC_Blink(0);
                           Task_sleep(100);
                           break;
                       }
                       else if(mode == 2){
                           RTC_Blink(1);
                           Task_sleep(100);
                           break;
                       }
                       else if(mode == 3){
                           RTC_Blink(2);
                           Task_sleep(100);
                           break;
                       }

                   }

                }
        Task_sleep(300);
    }
}









