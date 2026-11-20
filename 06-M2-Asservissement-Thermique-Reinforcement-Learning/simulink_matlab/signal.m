t = linspace(0, 2*pi, 2000);
x = sin(t);

phi = 2*pi/3;
x_shift = sin(t - phi);   % retard de +2pi/3 (avance -> sin(t + phi))

figure;
plot(t, x, 'LineWidth', 1.8); hold on;
plot(t, x_shift, 'LineWidth', 1.8);
grid on; xlim([0 2*pi]);

% Axe x en multiples de pi
xticks(0:pi/3:2*pi);
xticklabels({'0','\pi/3','2\pi/3','\pi','4\pi/3','5\pi/3','2\pi'});
set(gca,'TickLabelInterpreter','latex');

xlabel('t (rad)','Interpreter','latex');
ylabel('Amplitude','Interpreter','latex');
legend({'$x(t)=\sin(t)$', '$x_{shift}(t)=\sin(t-2\pi/3)$'}, ...
       'Interpreter','latex','Location','best');
title('Signal original vs décalé de $2\pi/3$','Interpreter','latex');
