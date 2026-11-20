
#include "system.h"
#include "altera_avalon_timer_regs.h"
#include "altera_avalon_pio_regs.h"

int main() {
    int last_keys = 0x3;
    int heure = 0, minute = 0, seconde = 0;
    int alarm_heure = 0, alarm_minute = 0;
    int led_clignote_state = 0;
    init_sys_timer();
    set_alarme_freq(melodie1[0]);

    while (1) {
        int sw = IORD_ALTERA_AVALON_PIO_DATA(INTERRUPTEURS_BASE);
        int keys = IORD_ALTERA_AVALON_PIO_DATA(BOUTON_POUSSOIRS_BASE) & 0x3;

        int sw0 = (sw >> 0) & 1;
        int sw1 = (sw >> 1) & 1;
        int sw2 = (sw >> 2) & 1;
        int sw3 = (sw >> 3) & 1;
        int sw5 = (sw >> 5) & 1;

        int affichage_uniquement = (sw3 == 1);
        int afficher_alarme = (sw0 == 1 || sw1 == 1);
        int format_12h = (sw1 == 1);  // SW1 active le 12h
        int alarme_active_condition = (sw2 == 1);

        // LED0 = ON si alarme activée
        if (alarme_active_condition) {
            IOWR_ALTERA_AVALON_PIO_DATA(LEDR_BASE, 0x01);
        } else {
            IOWR_ALTERA_AVALON_PIO_DATA(LEDR_BASE, 0x00);
        }

        // Affichage logique
        if (afficher_alarme) {
            afficher_heure(alarm_heure, alarm_minute, 0, format_12h);
        } else {
            afficher_heure(heure, minute, seconde, 0);  // format 24h par défaut
        }

        // Réglage autorisé uniquement si SW3 = 0
        if (!affichage_uniquement) {
            if ((last_keys & 0x1) && !(keys & 0x1)) {
                if (afficher_alarme)
                    alarm_minute = (alarm_minute + 1) % 60;
                else
                    minute = (minute + 1) % 60;
            }
            if ((last_keys & 0x2) && !(keys & 0x2)) {
                if (afficher_alarme)
                    alarm_heure = (alarm_heure + 1) % 24;
                else
                    heure = (heure + 1) % 24;
            }
        }

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

            if (alarme_active && sw5) {
                led_clignote_state = !led_clignote_state;
                IOWR_ALTERA_AVALON_PIO_DATA(LEDR_BASE, led_clignote_state ? 0x3FF : 0x00);
            }
        }

        if (alarme_active_condition && heure == alarm_heure && minute == alarm_minute) {
            if (!alarme_active) {
                melodie_active = melodie1;
                taille_melodie = 3;
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
