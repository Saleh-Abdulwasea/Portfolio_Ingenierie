library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity and_gate_array is
    Port (
        multiplicande : in  std_logic_vector(7 downto 0);
        lsb_multiplicateur : in std_logic;
        and_result : out std_logic_vector(7 downto 0)
    );
end and_gate_array;

architecture Behavioral of and_gate_array is
begin
    and_process: process(multiplicande, lsb_multiplicateur)
    begin
        for i in 0 to 7 loop
            and_result(i) <= multiplicande(i) and lsb_multiplicateur;
        end loop;
    end process;
end Behavioral;



library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity tb_and_gate_array is
    -- Pas de ports, entité de testbench
end tb_and_gate_array;

architecture Behavioral of tb_and_gate_array is

    -- Composant à tester
    component and_gate_array
        Port (
            multiplicande : in  STD_LOGIC_VECTOR(7 downto 0);
            lsb_multiplicateur           : in  STD_LOGIC;
            and_result    : out STD_LOGIC_VECTOR(7 downto 0)
        );
    end component;

    -- Signaux internes pour connecter les ports du composant
    signal multiplicande : STD_LOGIC_VECTOR(7 downto 0);
    signal lsb_multiplicateur           : STD_LOGIC;
    signal and_result    : STD_LOGIC_VECTOR(7 downto 0);

begin

    -- Instanciation du composant PorteAND
    uut: and_gate_array
        Port map (
            multiplicande => multiplicande,
            lsb_multiplicateur           => lsb_multiplicateur,
            and_result    => and_result
        );

    -- Processus de stimulation
    stim_proc: process
    begin
        -- Test 1: lsb = '0', multiplicande quelconque
        multiplicande <= "10101010";
        lsb_multiplicateur <= '0';
        wait for 10 ns;
        assert (and_result = "00000000") report "Test 1 failed" severity error;

        -- Test 2: lsb = '1', multiplicande = "10101010"
        multiplicande <= "10101010";
        lsb_multiplicateur <= '1';
        wait for 10 ns;
        assert (and_result = "10101010") report "Test 2 failed" severity error;

        -- Test 3: lsb = '1', multiplicande = "11111111"
        multiplicande <= "11111111";
        lsb_multiplicateur <= '1';
        wait for 10 ns;
        assert (and_result = "11111111") report "Test 3 failed" severity error;

        -- Test 4: lsb = '0', multiplicande = "11111111"
        multiplicande <= "11111111";
        lsb_multiplicateur <= '0';
        wait for 10 ns;
        assert (and_result = "00000000") report "Test 4 failed" severity error;

        -- Arrêt de la simulation
        wait;
    end process;

end Behavioral;
