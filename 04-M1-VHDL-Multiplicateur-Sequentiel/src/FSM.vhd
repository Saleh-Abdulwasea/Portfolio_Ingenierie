library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity FSM is
    Port (
        clk                 : in  std_logic;    -- Horloge
        reset               : in  std_logic;    -- Réinitialisation
        start               : in  std_logic;    -- Signal de démarrage
        counter_done        : in  std_logic;    -- Signal indiquant si le compteur a atteint N-1
        load_multiplicande  : out std_logic;    -- Charge le multiplicande
        load_multiplicateur : out std_logic;    -- Charge le multiplicateur
        shift_multiplicateur: out std_logic;    -- Décale le multiplicateur
        reset_produit       : out std_logic;    -- Réinitialise le registre produit
        load_produit        : out std_logic;    -- Charge le registre produit
        shift_produit       : out std_logic;    -- Décale le produit
        done                : out std_logic     -- Signal de fin
    );
end FSM;

architecture Behavioral of FSM is
    -- Déclaration des états
    type state_type is (S0, S1, S2, S3, S4);
    signal current_state, next_state : state_type;

begin
    -- Processus de transition d'état
    process(clk, reset)
    begin
        if reset = '1' then
            current_state <= S0;
        elsif rising_edge(clk) then
            current_state <= next_state;
        end if;
    end process;

    -- Processus pour déterminer le prochain état
    process(current_state, start, counter_done)
    begin
        -- Valeur par défaut
        next_state <= current_state;

        case current_state is
            when S0 =>  -- Reset
                if start = '1' then
                    next_state <= S1;  -- Passer à l'état de chargement
                end if;

            when S1 =>  -- Load Multiplicande, Multiplicateur et Reset Produit
                next_state <= S2;

            when S2 =>  -- Load Produit
                next_state <= S3;

            when S3 =>  -- Décalage et Vérification du Compteur
                if counter_done = '1' then
                    next_state <= S4;  -- Si le compteur est terminé, passer à "Done"
                else
                    next_state <= S2;  -- Sinon, revenir à S2 pour continuer
                end if;

            when S4 =>  -- Done
                next_state <= S0;  -- Retour à Reset après la fin

            when others =>
                next_state <= S0;  -- Par défaut, retour à Reset
        end case;
    end process;

    -- Processus pour générer les sorties
    process(current_state)
    begin
        -- Valeurs par défaut
        load_multiplicande  <= '0';
        load_multiplicateur <= '0';
        shift_multiplicateur <= '0';
        reset_produit       <= '0';
        load_produit        <= '0';
        shift_produit       <= '0';
        done                <= '0';

        case current_state is
            when S0 =>
                -- Aucun signal activé dans cet état

            when S1 =>
                reset_produit <= '1';  -- Réinitialiser le registre produit
                load_multiplicande <= '1';  -- Charger le multiplicande
                load_multiplicateur <= '1'; -- Charger le multiplicateur

            when S2 =>
                load_produit <= '1';  -- Charger le produit depuis l'additionneur

            when S3 =>
                shift_multiplicateur <= '1'; -- Décaler le multiplicateur
                shift_produit <= '1';       -- Décaler le produit

            when S4 =>
                done <= '1';  -- Indiquer que le calcul est terminé

            when others =>
                -- Aucun comportement par défaut
        end case;
    end process;

end Behavioral;

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity tb_FSM is
end tb_FSM;

architecture behavior of tb_FSM is
    -- Signaux pour connecter à l'UUT (Unit Under Test)
    signal clk                 : std_logic := '0';
    signal reset               : std_logic := '0';
    signal start               : std_logic := '0';
    signal counter_done        : std_logic := '0';
    signal load_multiplicande  : std_logic;
    signal load_multiplicateur : std_logic;
    signal shift_multiplicateur: std_logic;
    signal reset_produit       : std_logic;
    signal load_produit        : std_logic;
    signal shift_produit       : std_logic;
    signal done                : std_logic;

    -- Déclaration de l'UUT
    component FSM
        Port (
            clk                 : in  std_logic;
            reset               : in  std_logic;
            start               : in  std_logic;
            counter_done        : in  std_logic;
            load_multiplicande  : out std_logic;
            load_multiplicateur : out std_logic;
            shift_multiplicateur: out std_logic;
            reset_produit       : out std_logic;
            load_produit        : out std_logic;
            shift_produit       : out std_logic;
            done                : out std_logic
        );
    end component;

begin
    -- Instanciation de l'UUT
    uut: FSM
        port map (
            clk                 => clk,
            reset               => reset,
            start               => start,
            counter_done        => counter_done,
            load_multiplicande  => load_multiplicande,
            load_multiplicateur => load_multiplicateur,
            shift_multiplicateur => shift_multiplicateur,
            reset_produit       => reset_produit,
            load_produit        => load_produit,
            shift_produit       => shift_produit,
            done                => done
        );

    -- Génération de l'horloge
    clk_process : process
    begin
        while true loop
            clk <= not clk;
            wait for 5 ns; -- Période d'horloge de 10 ns
        end loop;
    end process;

    -- Processus de stimulation avec nombres binaires
    stim_proc: process
    begin
        -- Initialisation : Réinitialisation
        reset <= '1';  -- Activer la réinitialisation
        start <= '0';
        counter_done <= '0';
        wait for 20 ns;

        -- Relâcher la réinitialisation
        reset <= '0';
        wait for 10 ns;

        -- Test 1 : Passage de S0 à S1 (Démarrage avec `start`)
        start <= '1';  -- Activer le signal de démarrage
        wait for 20 ns;

        -- Test 2 : Passage de S1 à S2 (Chargement des registres)
        start <= '0';  -- Désactiver `start`
        wait for 20 ns;

        -- Test 3 : Passage de S2 à S3 (Chargement du produit)
        counter_done <= '0';  -- Compteur pas encore terminé
        wait for 20 ns;

        -- Test 4 : Compteur pas terminé, revenir à S2
        wait for 20 ns;  -- Laissez le signal "compteur terminé" désactivé

        -- Test 5 : Compteur terminé, passer à S5
        counter_done <= '1';  -- Compteur atteint sa limite
        wait for 20 ns;

        -- Test 6 : Retour à S0 après S5
        wait for 20 ns;

        -- Fin de la simulation
        wait;
    end process;

end behavior;



