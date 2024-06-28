file_path = 'D:\data.txt';
data = importdata(file_path);
last_array = data(end,:);
last_array = last_array(:);
frequencies_array = last_array;
frequencies = reshape(frequencies_array, 3, 10);
disp('Frequencies Matrix:');
disp(frequencies);
time_interval = 0.5;
time = 0:time_interval:(size(frequencies, 2)-1)*time_interval;
frequency_bins = linspace(0, 1/(2*time_interval), size(frequencies, 1));
[Time, Frequency] = meshgrid(time, frequency_bins);
fig = figure;
surf(Time, Frequency, frequencies);
xlabel('Time(s)');
ylabel('Frequency(Hz)');
zlabel('Frequency');
title('3D Graph of Frequencies');
colormap('jet');
colorbar;
angle = 0;
rotateGraph = @(h) view(h, angle, 60);
rotateTimer = timer('ExecutionMode', 'fixedRate', 'Period', 0.1, ...
    'TimerFcn', {@(~, ~) updateView(fig)});
start(rotateTimer);
function updateView(fig)
    ax = fig.CurrentAxes;
    ax.View = [mod(ax.View(1)+1, 360), 60];
end
