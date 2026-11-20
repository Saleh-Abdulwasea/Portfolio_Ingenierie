library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity product_register is
    Port (
        clk          : in  std_logic;                       -- Signal d'horloge
        reset        : in  std_logic;                       -- Signal de réinitialisation
        load         : in  std_logic;                       -- Signal de chargement
        shift_right  : in  std_logic;                       -- Signal de décalage à droite
        add_result   : in  std_logic_vector(8 downto 0);    -- Résultat de l'additionneur (9 bits)
        product_out  : out std_logic_vector(16 downto 0)    -- Registre produit (17 bits)
    ); 
end product_register;

architecture Behavioral of product_register is
    signal product : std_logic_vector(16 downto 0);         -- Registre interne pour stocker les 17 bits
begin
    process(clk)
    begin
        if rising_edge(clk) then
            if reset = '1' then
                -- Réinitialisation : mettre tous les bits à 0
                product <= (others => '0');
            elsif load = '1' then
                -- Charger les 9 bits du résultat de l'additionneur dans les bits [16..8]
                product(16 downto 8) <= add_result;
                -- Les bits [7..0] restent inchangés
            elsif shift_right = '1' then
                -- Décalage à droite avec insertion de '0' en MSB
                product <= '0' & product(16 downto 1);
            end if;
        end if;
    end process;

    -- Assignation de la sortie
    product_out <= product;

end Behavioral;



library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity tb_product_register is
end tb_product_register;

architecture behavior of tb_product_register is
    signal clk          : std_logic := '0';
    signal reset        : std_logic := '0';
    signal load         : std_logic := '0';
    signal shift_right  : std_logic := '0';
    signal add_result   : std_logic_vector(8 downto 0) := (others => '0');
    signal product_out  : std_logic_vector(16 downto 0);

    component product_register
        Port (
            clk          : in  std_logic;
            reset        : in  std_logic;
            load         : in  std_logic;
            shift_right  : in  std_logic;
            add_result   : in  std_logic_vector(8 downto 0);
            product_out  : out std_logic_vector(16 downto 0)
        );
    end component;

begin
    -- Instanciation du registre produit
    uut: product_register
        port map (
            clk          => clk,
            reset        => reset,
            load         => load,
            shift_right  => shift_right,
            add_result   => add_result,
            product_out  => product_out
        );

    -- Génération de l'horloge
    clk_process : process
    begin
        while true loop
            clk <= not clk;
            wait for 5 ns; -- Période de 10 ns
        end loop;
    end process;

    -- Processus de stimulation
    stim_proc: process
    begin
        -- Test 1 : Réinitialisation
        reset <= '1';
        wait for 10 ns;
        reset <= '0';
        wait for 15 ns;

        -- Test 2 : Charger une valeur dans le registre
        add_result <= "111111111"; -- Exemple : 5
        load <= '1';
        wait for 10 ns;
        load <= '0';
        wait for 10 ns;

        -- Test 3 : Décalage à droite
        shift_right <= '1';
        wait for 10 ns;
        shift_right <= '0';
        wait for 10 ns;
	
	

        -- Test 4 : Charger une autre valeur
        add_result <= "111111111"; -- Exemple : 11
        load <= '1';
        wait for 10 ns;
        load <= '0';
	wait for 30 ns;

	-- Test 5 : Shift et Load activés simultanément
        add_result <= "111111111"; -- Exemple : 15
        load <= '0';
	--wait for 20 ns;
        shift_right <= '1';
        wait for 10 ns;
        load <= '1';
        shift_right <= '0';

        -- Fin de la simulation
        wait;
    end process;

end behavior;

