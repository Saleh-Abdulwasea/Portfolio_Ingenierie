#include "system.h"
#include "altera_avalon_timer_regs.h"
#include "altera_avalon_pio_regs.h"
#include <stdio.h>

#define LIRE_SWITCHES() IORD_ALTERA_AVALON_PIO_DATA(INTERRUPTEURS_BASE)
#define LIRE_BOUTONS()  IORD_ALTERA_AVALON_PIO_DATA(BOUTON_POUSSOIRS_BASE)
#define ECRIRE_LEDS(val) IOWR_ALTERA_AVALON_PIO_DATA(LEDR_BASE, (val))

const char hex_digits[10] = {
    0x3F, 0x06, 0x5B, 0x4F,
    0x66, 0x6D, 0x7D, 0x07,
    0x7F, 0x6F
};

int heure = 0, minute = 0, seconde = 0;
int alarm_heure = 0, alarm_minute = 0;
int is_12h = 0;
int alarme_active = 0;
int buzzer_state = 0;
int note_index = 0;
int led_clignote_state = 0;
int* melodie_active;
int taille_melodie;
int prev_keys = 0x3;

int melodie1[] = {659, 698, 659, 784, 698, 659, 587, 784, 698};
int melodie2[] = {659, 784, 880, 988, 1047, 988, 880, 784};
int melodie3[] = {659, 698, 784, 523, 587, 659, 440, 698};

void afficher_heure(int h, int m, int s) {
    int data_h = (hex_digits[h / 10] << 8) | hex_digits[h % 10];
    int data_ms = (hex_digits[m / 10] << 24) |
                  (hex_digits[m % 10] << 16) |
                  (hex_digits[s / 10] << 8) |
                   hex_digits[s % 10];
    IOWR_ALTERA_AVALON_PIO_DATA(HEXA1_HEXA0_BASE, ~data_h);
    IOWR_ALTERA_AVALON_PIO_DATA(HEX3_HEX0_BASE, ~data_ms);
}

void init_sys_timer() {
    IOWR_ALTERA_AVALON_TIMER_PERIODL(SYS_CLK_TIMER_BASE, 50000000 & 0xFFFF);
    IOWR_ALTERA_AVALON_TIMER_PERIODH(SYS_CLK_TIMER_BASE, (50000000 >> 16) & 0xFFFF);
    IOWR_ALTERA_AVALON_TIMER_CONTROL(SYS_CLK_TIMER_BASE, 0x6);
}

void init_continu_timer() {
    IOWR_ALTERA_AVALON_TIMER_CONTROL(TIMER_CONTINU_BASE, 0);
    IOWR_ALTERA_AVALON_TIMER_STATUS(TIMER_CONTINU_BASE, 0);
    IOWR_ALTERA_AVALON_TIMER_PERIODL(TIMER_CONTINU_BASE, (50000000 / 2) & 0xFFFF);
    IOWR_ALTERA_AVALON_TIMER_PERIODH(TIMER_CONTINU_BASE, (50000000 / 2) >> 16);
    IOWR_ALTERA_AVALON_TIMER_CONTROL(TIMER_CONTINU_BASE, 0x0);
}

void set_alarme_freq(int freq_hz) {
    int periode = 50000000 / (freq_hz * 2);
    IOWR_ALTERA_AVALON_TIMER_PERIODL(ALARME_TIMER_BASE, periode & 0xFFFF);
    IOWR_ALTERA_AVALON_TIMER_PERIODH(ALARME_TIMER_BASE, (periode >> 16) & 0xFFFF);
    IOWR_ALTERA_AVALON_TIMER_CONTROL(ALARME_TIMER_BASE, 0x6);
}

void selectionner_melodie(int sw) {
    if (sw & 0x100) {
        melodie_active = melodie2; taille_melodie = 8;
    } else if (sw & 0x200) {
        melodie_active = melodie3; taille_melodie = 8;
    } else {
        melodie_active = melodie1; taille_melodie = 9;
    }
    note_index = 0;
    set_alarme_freq(melodie_active[note_index]);
}

int main() {
    init_sys_timer();
    init_continu_timer();
    selectionner_melodie(0);
    static int was_pressed = 0;

    while (1) {
        int sw = LIRE_SWITCHES();
        int keys_raw = LIRE_BOUTONS();

        int key0_pressed = (keys_raw & 0x1);
        int key1_pressed = (keys_raw & 0x2);

        int sw0 = sw & 0x1;
        int sw1 = sw & 0x2;
        int sw2 = sw & 0x4;
        int format_12h = sw & 0x8;
        int mode_successive = sw & 0x10;
        int cligno = sw & 0x20;
        int sw6 = sw & 0x40;

        int any_pressed = key0_pressed || key1_pressed;

        if (!mode_successive && (sw1 || sw2)) {
            if (any_pressed && !was_pressed) {
                IOWR_ALTERA_AVALON_TIMER_CONTROL(TIMER_CONTINU_BASE, 0x6);
            }

            int t1_status = IORD_ALTERA_AVALON_TIMER_STATUS(TIMER_CONTINU_BASE);

            if ((t1_status & 0x1) && any_pressed) {
                IOWR_ALTERA_AVALON_TIMER_STATUS(TIMER_CONTINU_BASE, 0);
                IOWR_ALTERA_AVALON_TIMER_CONTROL(TIMER_CONTINU_BASE, 0x6);

                if (sw2) {
                    if (key0_pressed) minute = sw6 ? (minute - 1 + 60) % 60 : (minute + 1) % 60;
                    if (key1_pressed) heure  = sw6 ? (heure - 1 + 24) % 24 : (heure + 1) % 24;
                }
                if (sw1) {
                    if (key0_pressed) alarm_minute = sw6 ? (alarm_minute - 1 + 60) % 60 : (alarm_minute + 1) % 60;
                    if (key1_pressed) alarm_heure  = sw6 ? (alarm_heure - 1 + 24) % 24 : (alarm_heure + 1) % 24;
                }
            }

            if (!any_pressed) {
                IOWR_ALTERA_AVALON_TIMER_CONTROL(TIMER_CONTINU_BASE, 0);
                IOWR_ALTERA_AVALON_TIMER_STATUS(TIMER_CONTINU_BASE, 0);
            }

            was_pressed = any_pressed;
        }

        if (mode_successive) {
            if (sw2) {
                if (key0_pressed && !(prev_keys & 0x1)) minute = sw6 ? (minute - 1 + 60) % 60 : (minute + 1) % 60;
                if (key1_pressed && !(prev_keys & 0x2)) heure  = sw6 ? (heure - 1 + 24) % 24 : (heure + 1) % 24;
            } else if (sw1) {
                if (key0_pressed && !(prev_keys & 0x1)) alarm_minute = sw6 ? (alarm_minute - 1 + 60) % 60 : (alarm_minute + 1) % 60;
                if (key1_pressed && !(prev_keys & 0x2)) alarm_heure  = sw6 ? (alarm_heure - 1 + 24) % 24 : (alarm_heure + 1) % 24;
            }
        }

        int h_affiche = format_12h ? (heure % 12 ? heure % 12 : 12) : heure;
        int h_alarm_affiche = format_12h ? (alarm_heure % 12 ? alarm_heure % 12 : 12) : alarm_heure;

        if (sw2) afficher_heure(h_affiche, minute, 0);
        else if (sw1) afficher_heure(h_alarm_affiche, alarm_minute, 0);
        else afficher_heure(h_affiche, minute, seconde);

        int status = IORD_ALTERA_AVALON_TIMER_STATUS(SYS_CLK_TIMER_BASE);
        if (status & 0x1) {
            IOWR_ALTERA_AVALON_TIMER_STATUS(SYS_CLK_TIMER_BASE, 0);
            seconde++;
            if (seconde == 60) {
                seconde = 0;
                minute++;
                if (minute == 60) {
                    minute = 0;
                    heure = (heure + 1) % 24;
                }
            }

            int led_state = sw & 0x3FF;
            if (sw & (1 << 3)) {
                int heure_ref = (sw1) ? alarm_heure : heure;
                if (heure_ref >= 12) led_state |= (1 << 3);
                else led_state &= ~(1 << 3);
            }

            if (sw0) led_state |= 0x01;

            if (alarme_active && cligno) {
                led_clignote_state = !led_clignote_state;
                ECRIRE_LEDS(led_clignote_state ? 0x3FF : 0x00);
            } else {
                ECRIRE_LEDS(led_state);
            }
        }

        if (sw0 && heure == alarm_heure && minute == alarm_minute) {
            if (!alarme_active) {
                selectionner_melodie(sw);
                alarme_active = 1;
                note_index = 0;
            }
            int a_status = IORD_ALTERA_AVALON_TIMER_STATUS(ALARME_TIMER_BASE);
            if (a_status & 0x1) {
                IOWR_ALTERA_AVALON_TIMER_STATUS(ALARME_TIMER_BASE, 0);
                buzzer_state = !buzzer_state;
                IOWR_ALTERA_AVALON_PIO_DATA(GPIO_BASE, buzzer_state ? 17 : 0);
                static int compteur = 0;
                compteur++;
                if (compteur >= 500) {
                    compteur = 0;
                    note_index = (note_index + 1) % taille_melodie;
                    set_alarme_freq(melodie_active[note_index]);
                }
            }
        } else {
            alarme_active = 0;
            buzzer_state = 0;
            led_clignote_state = 0;
            IOWR_ALTERA_AVALON_PIO_DATA(GPIO_BASE, 0);
        }

        prev_keys = keys_raw;
    }
    return 0;
}
