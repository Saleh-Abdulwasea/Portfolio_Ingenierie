/*
 * degre.c
 *
 *
 */


#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* TI-RTOS Header files */
#include <driverlib.h>


/* Board Header file */
#include "main.h"
#include "hal_LCD.h"
#include "degre.h"

#include <ti/sysbios/knl/Event.h>

/* XDCtools Header files */
#include <xdc/std.h>
#include <xdc/runtime/System.h>
#include <xdc/cfg/global.h>


/************************************
 * Init_Variables
 ***********************************/
// ADC
ADC12_B_initParam Struc_ADC = {0};


// TEMP
#define CALADC_12V_30 *((unsigned int *) 0x1A1A)
#define CALADC_12V_85C *((unsigned int *) 0x1A1C)

int Temp;
int DegC;


/************************************
 * Init_ADC()
 ***********************************/

void Init_ADC(void)
{
// init reference de tension
    Ref_A_setReferenceVoltage(REF_A_BASE, REF_A_VREF1_2V);
    Ref_A_enableReferenceVoltage(REF_A_BASE);
//init capteur de t
    Ref_A_enableTempSensor(REF_A_BASE);
// init ADC
    Struc_ADC.clockSourceDivider = ADC12_B_CLOCKDIVIDER_1;
    Struc_ADC.clockSourcePredivider = ADC12_B_CLOCKPREDIVIDER__1;
    Struc_ADC.clockSourceSelect = ADC12_B_CLOCKSOURCE_ADC12OSC;
    Struc_ADC.internalChannelMap = ADC12_B_TEMPSENSEMAP;
    Struc_ADC.sampleHoldSignalSourceSelect = ADC12_B_SAMPLEHOLDSOURCE_SC;


    ADC12_B_init(ADC12_B_BASE, &Struc_ADC);
    ADC12_B_enable(ADC12_B_BASE);

    //init Sample_hold (echantilloneur bloqueur)
    ADC12_B_setupSamplingTimer(ADC12_B_BASE,
                               ADC12_B_CYCLEHOLD_256_CYCLES,
                               ADC12_B_CYCLEHOLD_4_CYCLES,
                               ADC12_B_MULTIPLESAMPLESDISABLE);

    //init memoire
    ADC12_B_configureMemoryParam Memory_Param = {0};
    Memory_Param.differentialModeSelect = ADC12_B_DIFFERENTIAL_MODE_DISABLE;
    Memory_Param.endOfSequence = ADC12_B_ENDOFSEQUENCE;
    Memory_Param.inputSourceSelect = ADC12_B_INPUT_TCMAP;
    Memory_Param.memoryBufferControlIndex = ADC12_B_MEMORY_0;
    Memory_Param.refVoltageSourceSelect = ADC12_B_VREFPOS_INTBUF_VREFNEG_VSS;
    Memory_Param.windowComparatorSelect = ADC12_B_WINDOW_COMPARATOR_DISABLE;


    ADC12_B_configureMemory(ADC12_B_BASE, &Memory_Param);

    ADC12_B_clearInterrupt(ADC12_B_BASE,
                             0,
                             ADC12_B_IFG0);

    ADC12_B_enableInterrupt(ADC12_B_BASE,
                             ADC12_B_IE0,
                             0,
                             ADC12_B_IFG0);

    //ADC12_B_startConversion(ADC12_B_BASE,ADC12_B_START_AT_ADC12MEMO,ADC12_B_SINGLECHANNEL)
};

/************************************
 * Irq_ADC()
 ***********************************/

void Irq_ADC(unsigned index)
{
    uint16_t status = ADC12_B_getInterruptStatus(ADC12_B_BASE,
                                                  0,
                                                  ADC12_B_IFG0 );

    switch(status)
    {
        case ADC12_B_IFG0:
            //Event_post(h_event0, EVENT_ADC_CONV);
            ADC12_B_clearInterrupt(ADC12_B_BASE, 0, ADC12_B_IFG0);
        break;

    }

}

/************************************
 * Disp_ADC()
 ***********************************/

void Disp_ADC(int Val)
{
    ClearDIGIT();

    if(Val >= 1000)
        ShowChar((Val/1000)%10 + '0', pos2);

    if(Val >= 100)
        ShowChar((Val/100)%10 + '0', pos3);

    if(Val >= 10)
        ShowChar((Val/10)%10 + '0', pos4);

    if(Val >= 1)
        ShowChar((Val/1)%10 + '0', pos5);

    LCDMEM[pos4+1] |= 0x01;
    LCDMEM[pos5+1] |= 0x04;
    ShowChar('C', pos6);

}


/************************************
 * Start_Conversion()
 ***********************************/


void Start_Conversion(void)
{
    ADC12_B_startConversion(ADC12_B_BASE,
                            ADC12_B_START_AT_ADC12MEM0,
                            ADC12_B_SINGLECHANNEL
                            );

    //while(ADC12_B_isBusy(ADC12_B_BASE) == ADC12_B_BUSY)

    Temp = (ADC12MEM0 - CALADC_12V_30);

    DegC = ((long)Temp * 10 * (85-30) * 10) / ((CALADC_12V_85C - CALADC_12V_30) * 10) + 300;

    Disp_ADC(DegC);
}


