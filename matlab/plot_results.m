function plot_results(folder)
%PLOT_RESULTS Plot CSV BER using base MATLAB/Octave functions.
if nargin<1,folder='results/matlab';end
fid=fopen(fullfile(folder,'awgn.csv'),'r');assert(fid>=0);
r=textscan(fid,'%s%f%f%f%f%f%f%f','Delimiter',',','HeaderLines',1);fclose(fid);
figure;hold on;grid on;
for name={'BPSK','DSSS'}
 idx=strcmp(r{1},name{1});semilogy(r{2}(idx),max(r{5}(idx),1./r{3}(idx)),'-o','DisplayName',name{1});
end
x=linspace(0,8,100);semilogy(x,dsss('theory',x),'k--','DisplayName','BPSK theory');set(gca,'YScale','log');xlabel('Eb/N0 (dB)');ylabel('BER (zeros at 1/N)');title('Equal information-bit energy');legend('show');print(fullfile(folder,'awgn.png'),'-dpng','-r150');
end
