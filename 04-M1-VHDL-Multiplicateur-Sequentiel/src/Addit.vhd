library IEEE;
use IEEE.STD_LOGIC_1164.ALL;   -- Pour utiliser std_logic et std_logic_vector
use IEEE.NUMERIC_STD.ALL;      -- Pour les opérations arithmétiques sur unsigned et signed

entity adder_9_bits is
    Port (
        msb_acc : in  std_logic_vector(7 downto 0);   -- Accumulateur 8 bits
        and_result : in std_logic_vector(7 downto 0); -- Résultat de la porte AND
        add_result : out std_logic_vector(8 downto 0) -- Résultat de 9 bits (avec retenue)
    );
end adder_9_bits;

architecture Behavioral of adder_9_bits is
begin
    add_process: process(msb_acc, and_result)
    begin
        -- Conversion des std_logic_vector en unsigned avec extension à 9 bits
        add_result <= std_logic_vector(
                        unsigned('0' & msb_acc) +  -- Ajout d'un '0' comme MSB pour étendre à 9 bits
                        unsigned('0' & and_result) -- Ajout d'un '0' comme MSB pour étendre à 9 bits
                     );
    end process;
end Behavioral;


library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity tb_adder_9_bits is
end entity tb_adder_9_bits;

architecture behavior of tb_adder_9_bits is
    signal msb_acc    : std_logic_vector(7 downto 0) := (others => '0');
    signal and_result : std_logic_vector(7 downto 0) := (others => '0');
    signal add_result : std_logic_vector(8 downto 0);

    component adder_9_bits
        Port (
            msb_acc : in std_logic_vector(7 downto 0);
            and_result : in std_logic_vector(7 downto 0);
            add_result : out std_logic_vector(8 downto 0)
        );
    end component;

begin
    uut: adder_9_bits
        port map (
            msb_acc => msb_acc,
            and_result => and_result,
            add_result => add_result
        );

    process
    begin
        -- Test 1
        msb_acc <= "00000001";
        and_result <= "00000001";
        wait for 10 ns;

        -- Test 2
        msb_acc <= "11111111";
        and_result <= "00000001";
        wait for 10 ns;

        -- Test 3
        msb_acc <= "01100100";
        and_result <= "00110010";
        wait for 10 ns;

        -- Fin du test
        wait;
    end process;

end behavior;
