/******************************************************************************
 * Copyright (c) 2015, Texas Instruments Incorporated
 * All rights reserved.
 *
 *****************************************************************************/

/*
 *  ======== empty_min.c ========
 */
/* XDCtools Header files */
#include <xdc/std.h>
#include <xdc/runtime/System.h>
#include <xdc/cfg/global.h>
/* BIOS Header files */
#include <ti/sysbios/BIOS.h>
#include <ti/sysbios/knl/Task.h>

/* TI-RTOS Header files */
#include <driverlib.h>

/* Board Header file */
#include "main.h"

/*******************************************************************************
 * Prototype
 *******************************************************************************/
void Init_GPIO(void);
void Blink_LedV(UArg arg0, UArg arg1);
void heartBeatFxn(UArg arg0, UArg arg1);

/******************************************************************************
 *  ======== main ========
 ******************************************************************************/
int main(void)
{
    WDT_A_hold(WDT_A_BASE);
    PM5CTL0 &= ~LOCKLPM5;

    Init_GPIO();

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


