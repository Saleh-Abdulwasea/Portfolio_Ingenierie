library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;  -- Standard recommandé pour les opérations numériques

entity multiplicand_register is
    Generic (
        N : integer := 8  -- Largeur du registre (nombre de bits)
    );
    Port (
        clk     : in  std_logic;          -- Signal d'horloge
        load    : in  std_logic;          -- Signal de chargement
        data_in : in  std_logic_vector(N-1 downto 0); -- Entrée du multiplicande
        data_out: out std_logic_vector(N-1 downto 0)  -- Sortie du multiplicande
    );
end multiplicand_register;

architecture Behavioral of multiplicand_register is
    signal reg_internal : std_logic_vector(N-1 downto 0); -- Registre interne
begin

    process(clk)
    begin
        if rising_edge(clk) then
            if load = '1' then
                reg_internal <= data_in;  -- Charger un nouveau multiplicande
            end if;  -- Sinon, garder la valeur actuelle
        end if;
    end process;

    -- Assignation de la sortie
    data_out <= reg_internal;

end Behavioral;



library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity tb_multiplicand_register is
end tb_multiplicand_register;

architecture Behavioral of tb_multiplicand_register is
    constant N : integer := 8; -- Taille des registres

    signal clk     : std_logic := '0';
    signal load    : std_logic := '0';
    signal data_in : std_logic_vector(N-1 downto 0) := (others => '0');
    signal data_out: std_logic_vector(N-1 downto 0);

    component multiplicand_register
        Generic (
            N : integer := 8
        );
        Port (
            clk     : in  std_logic;
            load    : in  std_logic;
            data_in : in  std_logic_vector(N-1 downto 0);
            data_out: out std_logic_vector(N-1 downto 0)
        );
    end component;

begin
    -- Instanciation de l'entité sous test (UUT)
    uut: multiplicand_register
        generic map (
            N => N
        )
        port map (
            clk     => clk,
            load    => load,
            data_in => data_in,
            data_out => data_out
        );

    -- Processus pour générer le signal d'horloge
    clk_process : process
    begin
        while true loop
            clk <= '0';
            wait for 10 ns;
            clk <= '1';
            wait for 10 ns;
        end loop;
    end process;

    -- Stimulus pour tester le comportement
    stimulus_process : process
    begin
        -- Initialisation
        load <= '0';
        data_in <= "00000000";
        wait for 20 ns;

        -- Cas 1 : Charger une première valeur
        load <= '1';
        data_in <= "10101010";
        wait for 20 ns;

        -- Cas 2 : Charger une deuxième valeur
        load <= '1';
        data_in <= "11001100";
        wait for 20 ns;

        -- Cas 3 : Mettre load à 0 et changer data_in
        load <= '0';
        data_in <= "11110000"; -- Nouvelle valeur d'entrée, mais load est désactivé
        wait for 40 ns;

        -- Cas 4 : Réactiver load avec une nouvelle valeur
        load <= '1';
        data_in <= "00001111";
        wait for 20 ns;

        -- Fin de simulation
        wait for 20 ns;
        assert false report "Simulation terminée" severity note;
        wait;
    end process;

end Behavioral;
