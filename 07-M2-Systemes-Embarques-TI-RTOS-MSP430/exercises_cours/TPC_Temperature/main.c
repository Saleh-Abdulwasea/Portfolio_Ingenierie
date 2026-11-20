/******************************************************************************
 * Copyright (c) 2015, Texas Instruments Incorporated
 * All rights reserved.
 *
 *****************************************************************************/

/*
 *  ======== empty_min.c ========
 */

#include "string.h"
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
#include "Capteur_Temp.h"

extern bool FlagConv;

//************************************************************************
typedef struct MailObj {
    uint8_t Id;
    char Buffer[20];
    uint8_t Objet;
} MailObj;

MailObj MsgMail;


/*******************************************************************************
 * Prototype
 *******************************************************************************/
void Init_GPIO(void);
void Blink_LedV(UArg arg0, UArg arg1);
void heartBeatFxn(UArg arg0, UArg arg1);
void Event_Btn1(UArg arg0, UArg arg1);
void Event_Btn2(UArg arg0, UArg arg1);
void Mail_Btn1(UArg arg0, UArg arg1);
void Mail_Btn2(UArg arg0, UArg arg1);

/******************************************************************************
 *  ======== main ========
 ******************************************************************************/
int main(void)
{
    WDT_A_hold(WDT_A_BASE);
    PM5CTL0 &= ~LOCKLPM5;

    Init_GPIO();
    Init_LCD();
    Init_CapteurTemp();

    /* Start BIOS */
    BIOS_start();

    return (0);
}

/******************************************************************************
 * Init GPIO
 ******************************************************************************/
void Init_GPIO(void)
{
    //PORT1
    GPIO_setAsOutputPin(GPIO_PORT_P1, LEDR);
    GPIO_setOutputLowOnPin(GPIO_PORT_P1, LEDR);
    GPIO_setAsInputPinWithPullUpResistor(GPIO_PORT_P1,BTN1+BTN2);

    //PORT9
    GPIO_setAsOutputPin(GPIO_PORT_P9, LEDV);
    GPIO_setOutputLowOnPin(GPIO_PORT_P9, LEDV);

    //IRQ
    GPIO_selectInterruptEdge(GPIO_PORT_P1,
                             BTN1 + BTN2,
                             GPIO_HIGH_TO_LOW_TRANSITION);

    GPIO_clearInterrupt(GPIO_PORT_P1, BTN1+BTN2);
    GPIO_enableInterrupt(GPIO_PORT_P1, BTN1+BTN2);
}

/******************************************************************************
 *  ======== heartBeatFxn ========
 *  Toggle the Board_LED0. The Task_sleep is determined by arg0 which
 *  is configured for the heartBeat Task instance.
 ******************************************************************************/
void heartBeatFxn(UArg arg0, UArg arg1)
{
    while (1)
        {
        Task_sleep(500);
        GPIO_toggleOutputOnPin(GPIO_PORT_P1, LEDR);
        FlagConv = false;
        ReadTempSensor();
        }
}

/******************************************************************************
 *
 ******************************************************************************/
void Blink_LedV(UArg arg0, UArg arg1)
{
    while (1)
        {
        Task_sleep(1000);
        GPIO_toggleOutputOnPin(GPIO_PORT_P9, LEDV);
        }
}

/******************************************************************************
 *  Event BTN1
 ******************************************************************************/
void Event_Btn1(UArg arg0, UArg arg1)
{
    uint16_t posted;

    while(1)
        {
        posted = Event_pend(h_event0,       //handle
                            Event_Id_00,    //AND Mask
                            EVENT_BTN1 +
                            EVENT_CONVTEMP,     //OR Mask
                            EVENT_TIMEOUT); //timeout

        switch(posted)
            {
            case EVENT_BTN1:
                Semaphore_pend(h_semaphore0, BIOS_WAIT_FOREVER);
                DisplayScrollText("AZERTYUIOP", 500);
                Semaphore_post(h_semaphore0);
                GPIO_setOutputHighOnPin(GPIO_PORT_P9, LEDV);
                break;

            case EVENT_CONVTEMP:
                ClearDIGIT();
                ReadTempSensor();
            }

        Task_sleep(10);
        }
}

/******************************************************************************
 *  Event BTN2
 ******************************************************************************/
void Event_Btn2(UArg arg0, UArg arg1)
{
    uint16_t posted;

    while(1)
        {
        posted = Event_pend(h_event0,       //handle
                            Event_Id_00,    //AND Mask
                            EVENT_BTN2,     //OR Mask
                            EVENT_TIMEOUT); //timeout

        switch(posted)
            {
            case EVENT_BTN2:
                Semaphore_pend(h_semaphore0, BIOS_WAIT_FOREVER);
                DisplayScrollText("QSDFGHJKLM", 500);
                Semaphore_post(h_semaphore0);
                GPIO_setOutputLowOnPin(GPIO_PORT_P9, LEDV);
                break;
            }

        Task_sleep(1);
        }
}

/******************************************************************************
 *  Mail_Btn1
 ******************************************************************************/
void Mail_Btn1(UArg arg0, UArg arg1)
{
    while(1)
        {
        Mailbox_pend(h_mailbox0, &MsgMail, BIOS_WAIT_FOREVER);

        switch(MsgMail.Id)
            {
            case 1:
                Heart_Point();
                DisplayScrollText(MsgMail.Buffer, 100);
                break;
            }

        Task_sleep(1);
        }
}

/******************************************************************************
 *  Mail_Btn2
 ******************************************************************************/
void Mail_Btn2(UArg arg0, UArg arg1)
{
    while(1)
        {
        Mailbox_pend(h_mailbox0, &MsgMail, BIOS_WAIT_FOREVER);

        switch(MsgMail.Id)
            {
            case 2:
                Heart_Clr();
                DisplayScrollText(MsgMail.Buffer, 100);
                break;
            }

        Task_sleep(1);
        }
}

/******************************************************************************
 *  Irq_PORT1
 ******************************************************************************/
void Irq_Port1(unsigned Val_irq)
{
    uint16_t status = GPIO_getInterruptStatus(GPIO_PORT_P1, BTN1+BTN2);

    switch(status)
        {
        case BTN1:
            Event_post(h_event0, EVENT_CONVTEMP);
            //MsgMail.Id = 1;
            //strcpy(MsgMail.Buffer, "BOUTON 1");
            //MsgMail.Objet = 2;
            //Mailbox_post(h_mailbox0, &MsgMail, BIOS_NO_WAIT);
            GPIO_clearInterrupt(GPIO_PORT_P1, BTN1);
            break;

        case BTN2:
            //Event_post(h_event0, EVENT_BTN2);
            MsgMail.Id = 2;
            strcpy(MsgMail.Buffer, "BOUTON 2");
            MsgMail.Objet = 3;
            Mailbox_post(h_mailbox0, &MsgMail, BIOS_NO_WAIT);
            GPIO_clearInterrupt(GPIO_PORT_P1, BTN2);
            break;
        }
}













