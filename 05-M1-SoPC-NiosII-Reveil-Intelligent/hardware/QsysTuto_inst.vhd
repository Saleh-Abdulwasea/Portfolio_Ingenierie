	component QsysTuto is
		port (
			bouton_poussoirs_external_connection_export : in  std_logic_vector(1 downto 0)  := (others => 'X'); -- export
			clk_clk                                     : in  std_logic                     := 'X';             -- clk
			gpio_external_connection_export             : out std_logic;                                        -- export
			hex3_hex0_external_connection_export        : out std_logic_vector(31 downto 0);                    -- export
			hexa1_hexa0_external_connection_export      : out std_logic_vector(15 downto 0);                    -- export
			interrupteurs_external_connection_export    : in  std_logic_vector(9 downto 0)  := (others => 'X'); -- export
			ledr_external_connection_export             : out std_logic_vector(9 downto 0);                     -- export
			reset_reset_n                               : in  std_logic                     := 'X'              -- reset_n
		);
	end component QsysTuto;

	u0 : component QsysTuto
		port map (
			bouton_poussoirs_external_connection_export => CONNECTED_TO_bouton_poussoirs_external_connection_export, -- bouton_poussoirs_external_connection.export
			clk_clk                                     => CONNECTED_TO_clk_clk,                                     --                                  clk.clk
			gpio_external_connection_export             => CONNECTED_TO_gpio_external_connection_export,             --             gpio_external_connection.export
			hex3_hex0_external_connection_export        => CONNECTED_TO_hex3_hex0_external_connection_export,        --        hex3_hex0_external_connection.export
			hexa1_hexa0_external_connection_export      => CONNECTED_TO_hexa1_hexa0_external_connection_export,      --      hexa1_hexa0_external_connection.export
			interrupteurs_external_connection_export    => CONNECTED_TO_interrupteurs_external_connection_export,    --    interrupteurs_external_connection.export
			ledr_external_connection_export             => CONNECTED_TO_ledr_external_connection_export,             --             ledr_external_connection.export
			reset_reset_n                               => CONNECTED_TO_reset_reset_n                                --                                reset.reset_n
		);

