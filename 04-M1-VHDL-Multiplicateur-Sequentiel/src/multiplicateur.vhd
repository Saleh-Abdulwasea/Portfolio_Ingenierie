library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity multiplier_register is
    Generic (
        M : integer := 8 -- Taille du registre
    );
    Port (
        clk         : in  std_logic;          -- Signal d'horloge
        load        : in  std_logic;          -- Signal de chargement
        shift_right : in  std_logic;          -- Signal de décalage à droite
        data_in     : in  std_logic_vector(M-1 downto 0); -- Entrée des données
        data_out    : out std_logic_vector(M-1 downto 0)  -- Sortie du registre
    );
end multiplier_register;

architecture Behavioral of multiplier_register is
    signal reg : std_logic_vector(M-1 downto 0); -- Registre interne
begin

    process(clk)
    begin
        if rising_edge(clk) then
            if load = '1' then
                -- Charger les données d'entrée dans le registre
                reg <= data_in;
            elsif shift_right = '1' then
                -- Décalage à droite avec insertion d'un '0' à gauche
                reg <= '0' & reg(M-1 downto 1);
            end if; -- Si aucune condition n'est remplie, garder la valeur précédente
        end if;
    end process;

    -- Connecter le registre interne à la sortie
    data_out <= reg;

end Behavioral;

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity tb_multiplier_register is
end tb_multiplier_register;

architecture Behavioral of tb_multiplier_register is
    constant M : integer := 8; -- Taille du registre
    signal clk         : std_logic := '0';
    signal load        : std_logic := '0';
    signal shift_right : std_logic := '0';
    signal data_in     : std_logic_vector(M-1 downto 0) := (others => '0');
    signal data_out    : std_logic_vector(M-1 downto 0);

    component multiplier_register
        Generic (
            M : integer := 8
        );
        Port (
            clk         : in  std_logic;
            load        : in  std_logic;
            shift_right : in  std_logic;
            data_in     : in  std_logic_vector(M-1 downto 0);
            data_out    : out std_logic_vector(M-1 downto 0)
        );
    end component;

begin
    uut: multiplier_register
        generic map (
            M => M
        )
        port map (
            clk         => clk,
            load        => load,
            shift_right => shift_right,
            data_in     => data_in,
            data_out    => data_out
        );

    -- Génération de l'horloge
    clk_process : process
    begin
        while true loop
            clk <= '0';
            wait for 10 ns;
            clk <= '1';
            wait for 10 ns;
        end loop;
    end process;

    -- Stimuli pour le test
    stimulus_process : process
    begin
        -- Initialisation
        load <= '0'; 
	shift_right <= '0';
        data_in <= "10101010";
        wait for 20 ns;

        -- Charger une valeur
        load <= '1';
        wait for 20 ns;
        load <= '0';

        -- Décalage à droite
        shift_right <= '1';
        wait for 20 ns;
	data_in <= "11001100";
	load <= '1';
	wait for 20 ns;
	load <= '0';
	
        -- Décalage supplémentaire
        shift_right <= '1';
        wait for 20 ns;
        shift_right <= '0';

        -- Fin de simulation
        wait for 40 ns;
        assert false report "Simulation terminée" severity note;
        wait;
    end process;

end Behavioral;