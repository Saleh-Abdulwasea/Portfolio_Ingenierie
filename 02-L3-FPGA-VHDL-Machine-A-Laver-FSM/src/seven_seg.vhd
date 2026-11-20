library ieee;

use ieee.std_logic_1164.all;

USE ieee.numeric_std.all ;

entity seven_seg is
port ( fsm_output: in signed(2 downto 0);
       
		 seg7: out signed(6 downto 0)
		 );
end;

architecture seven_seg_a of seven_seg is

begin
         
			    seg7 <= "0001000"when fsm_output ="000" else -- A = Arret
				        "0001100"when fsm_output ="001" else -- P = prélavage
						  "1000111"when fsm_output ="010" else -- L = Lavage
				        "0000110"when fsm_output ="110" else -- r = rinçage
						  "0000110"when fsm_output ="100" else -- E = Essorage
						  "0110110"; --tous les cas restantS
end;
---------------