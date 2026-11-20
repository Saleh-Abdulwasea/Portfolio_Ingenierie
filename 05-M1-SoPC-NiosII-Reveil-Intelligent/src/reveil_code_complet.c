
#include "system.h"
#include "altera_avalon_timer_regs.h"
#include "altera_avalon_pio_regs.h"

const char hex_digits[10] = {
    0x3F, 0x06, 0x5B, 0x4F,
    0x66, 0x6D, 0x7D, 0x07,
    0x7F, 0x6F
};

int melodie1[] = {523, 587, 659};
int melodie2[] = {659, 784, 880, 988, 1047, 988, 880, 784};
int melodie3[] = {784, 880, 988};

int heure = 0, minute = 0, seconde = 0;
int alarm_heure = 0, alarm_minute = 0;
int buzzer_state = 0;
int alarme_active = 0;
int note_index = 0;
int* melodie_active = melodie1;
int taille_melodie = 3;
int led_clignote_state = 0;

void afficher_heure(int h, int m, int s, int is_12h) {
    int h_affiche = h;
    if (is_12h) {
        if (h == 0) h_affiche = 12;
        else if (h > 12) h_affiche = h - 12;
    }

    int data_h = (hex_digits[h_affiche / 10] << 8) | hex_digits[h_affiche % 10];
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

void set_alarme_freq(int freq_hz) {
    int periode = 50000000 / (freq_hz * 2);
    IOWR_ALTERA_AVALON_TIMER_PERIODL(ALARME_TIMER_BASE, periode & 0xFFFF);
    IOWR_ALTERA_AVALON_TIMER_PERIODH(ALARME_TIMER_BASE, (periode >> 16) & 0xFFFF);
    IOWR_ALTERA_AVALON_TIMER_CONTROL(ALARME_TIMER_BASE, 0x6);
}


int main() {
    int last_keys = 0x3;
    init_sys_timer();
    set_alarme_freq(melodie1[0]);  /* valeur par defaut */

    while (1) {
        int sw = IORD_ALTERA_AVALON_PIO_DATA(INTERRUPTEURS_BASE);
        int keys = IORD_ALTERA_AVALON_PIO_DATA(BOUTON_POUSSOIRS_BASE) & 0x3;

        /* Extraction des bits */
        int sw0 = (sw >> 0) & 1;
        int sw1 = (sw >> 1) & 1;
        int sw2 = (sw >> 2) & 1;
        int sw3 = (sw >> 3) & 1;
        int sw5 = (sw >> 5) & 1;

        /* Décision logique */
        int afficher_heure_actuelle = (sw2 == 0);  /* SW2 = 0 → heure actuelle */
        int format_12h = (sw1 == 1 && sw0 == 1) || (sw1 == 1 && sw0 == 0); /* 11 ou 10 */
        int affichage_uniquement = (sw3 == 1);
        int alarme_condition_active = (sw2 == 1 && sw1 == 0 && sw0 == 0);
        int alarme_condition_desactive = (sw2 == 0 && sw1 == 0 && sw0 == 1);

        /* Affichage */
        if (afficher_heure_actuelle) {
            afficher_heure(heure, minute, seconde, format_12h);
        } else {
            afficher_heure(alarm_heure, alarm_minute, 0, format_12h);
        }

        /* LED0 selon tableau */
        if (alarme_condition_active) {
            IOWR_ALTERA_AVALON_PIO_DATA(LEDR_BASE, 0x01); /* LED0 allumee */
        } else if (alarme_condition_desactive) {
            IOWR_ALTERA_AVALON_PIO_DATA(LEDR_BASE, 0x00); /* LED0 eteinte */
        }

        /* Reglage autorise si SW3 = 0 */
        if (!affichage_uniquement) {
            if ((last_keys & 0x1) && !(keys & 0x1)) {
                if (afficher_heure_actuelle)
                    minute = (minute + 1) % 60;
                else
                    alarm_minute = (alarm_minute + 1) % 60;
            }

            if ((last_keys & 0x2) && !(keys & 0x2)) {
                if (afficher_heure_actuelle)
                    heure = (heure + 1) % 24;
                else
                    alarm_heure = (alarm_heure + 1) % 24;
            }
        }

        /* Increment temps chaque seconde */
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

            /* Clignotement LED (si active) */
            if (alarme_active && sw5) {
                led_clignote_state = !led_clignote_state;
                IOWR_ALTERA_AVALON_PIO_DATA(LEDR_BASE, led_clignote_state ? 0x3FF : 0x00);
            }
        }

        /* Declenchement alarme */
        if (alarme_condition_active && heure == alarm_heure && minute == alarm_minute) {
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
            IOWR_ALTERA_AVALON_PIO_DATA(GPIO_BASE, 0);
        }

        last_keys = keys;
    }

    return 0;
}

