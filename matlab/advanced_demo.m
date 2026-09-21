function advanced_demo(out)
%ADVANCED_DEMO Acquired packet, pulse shaping, PSD and Rayleigh fading.
if nargin<1,out='results/matlab';end
if ~exist(out,'dir'),mkdir(out);end
rng(99,'twister');c=dsss('code',127);pre=dsss('spread',randi([0 1],16,1),c);bits=dsss('frame',uint8('DSSS: Tripoli to Edinburgh'));
x=[pre;dsss('spread',bits,c)];r=[zeros(29,1);dsss('oscillator',x,.0002,.83);zeros(64,1)];
[d,~,est]=dsss('receive_burst',r,pre,numel(bits),c,64,[-.0002 0 .0002]);[data,ok]=dsss('unframe',d);assert(ok && est.delay==29);fprintf('Recovered packet: %s\n',char(data'));
fid=fopen(fullfile(out,'pulse_shaping.csv'),'w');fprintf(fid,'rolloff,obw99_hz,bits,errors,ber\n');
b=randi([0 1],4000,1);chips=dsss('spread',b,c);
for beta=[.2 .35 .7]
 h=dsss('rrc',beta,10,4);x=dsss('shape',chips,h,4);z=dsss('matched_pulse',dsss('awgn',x,8),h,4,numel(chips));[d,~]=dsss('despread',z,c);m=dsss('metrics',b,d);[~,~,bw]=dsss('spectrum',x,8e6);
 fprintf(fid,'%g,%.12g,%d,%d,%.12g\n',beta,bw,m.bits,m.errors,m.ber);
end
fclose(fid);
fid=fopen(fullfile(out,'spectrum.csv'),'w');fprintf(fid,'model,obw99_hz\n');
for mode=1:2
 code=c;name='DSSS';if mode==1,code=ones(127,1);name='BPSK';end
 [~,~,bw]=dsss('spectrum',dsss('spread',b,code,4),8e6);fprintf(fid,'%s,%.12g\n',name,bw);
end
fclose(fid);
fade=(randn(numel(b),1)+1i*randn(numel(b),1))/sqrt(2);x=dsss('spread',b,c).*kron(fade,ones(127,1));[~,soft]=dsss('despread',dsss('awgn',x,8),c);d=double(real(conj(fade).*soft)<0);m=dsss('metrics',b,d);
fid=fopen(fullfile(out,'rayleigh.csv'),'w');fprintf(fid,'ebn0_db,bits,errors,ber,theory\n8,%d,%d,%.12g,%.12g\n',m.bits,m.errors,m.ber,.5*(1-sqrt(10^.8/(1+10^.8))));fclose(fid);
end
