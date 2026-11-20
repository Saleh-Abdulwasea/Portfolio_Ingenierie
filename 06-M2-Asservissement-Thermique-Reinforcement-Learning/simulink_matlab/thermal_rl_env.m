%% === Environnement RL pour le modèle thermique ===
% Définition des vecteurs SIMULINK



Rv_max = 50;      % ventilo OFF
Rv_min = 0.02;    % ventilo MAX


% Nom du modèle Simulink
mdl = 'Rl_toy';       

% Ouvrir le modèle
open_system(mdl);

%% Temps d'échantillonnage du RL (même que dans le bloc RL Agent)
Ts = 0.5;   % par exemple 0.5 s entre 2 décisions de l'agent
            % (à adapter si besoin)

% (IMPORTANT : dans le bloc RL Agent, mets aussi Sample time = Ts)

%% Définir l'espace d'observation
% Ici on a 1 seule observation : l'erreur de température e_T
obsInfo = rlNumericSpec([1 1], ...
    'Name', 'e_T');

%% Définir l'espace d'action
% L'action = commande du ventilateur u_fan (sortie de l'agent),
% on suppose qu'elle est bornée entre 0 et 1
actInfo = rlNumericSpec([1 1], ...
    'LowerLimit', 0, ...
    'UpperLimit', 1, ...
    'Name', 'u_fan');

%% Créer l'environnement Simulink pour le RL
agentBlock = [mdl '/RL Agent'];   % chemin du bloc dans le modèle

env = rlSimulinkEnv(mdl, agentBlock, obsInfo, actInfo);

% Afficher pour vérifier
disp('Environnement thermique RL créé :');
env



%% Récupérer les infos d'observation et d'action de l'environnement thermique
obsInfo = getObservationInfo(env);
actInfo = getActionInfo(env);

% afficher pour vérifier
obsInfo
actInfo

%% Créer un agent DDPG de base pour ce système
agent = rlDDPGAgent(obsInfo, actInfo);


%% Options d'entraînement pour le modèle thermique
trainOpts = rlTrainingOptions( ...
    'MaxEpisodes', 100, ...          % nombre d'épisodes
    'MaxStepsPerEpisode', 5000, ...   % nombre de pas par épisode
    'StopTrainingCriteria', 'AverageReward', ...
    'StopTrainingValue', -10, ...    % objectif de récompense moyenne (à ajuster)
    'ScoreAveragingWindowLength', 20, ...
    'Verbose', true, ...
    'Plots', 'training-progress');   % ouvre la fenêtre de suivi
trainingStats = train(agent, env, trainOpts);


% Sauvegarde de l'agent entraîné dans un fichier .mat
save('agent_thermal_RL.mat','agent');