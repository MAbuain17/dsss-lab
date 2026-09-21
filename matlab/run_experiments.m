function run_experiments(out, nbits)
%RUN_EXPERIMENTS Toolbox-free CSV experiments; MATLAB RNG differs from NumPy.
% Usage: addpath('matlab'); test_dsss; run_experiments('results/matlab',12000)
if nargin<1,out='results/matlab';end
if nargin<2,nbits=12000;end
if ~exist(out,'dir'),mkdir(out);end
rng(20260920,'twister');c=dsss('code',127);plain=ones(127,1);
fid=fopen(fullfile(out,'awgn.csv'),'w');fprintf(fid,'model,ebn0_db,bits,errors,ber,ci95_low,ci95_high,theory\n');
for eb=0:2:8
 for mode=1:2
  code=plain;name='BPSK';if mode==2,code=c;name='DSSS';end
  b=randi([0 1],nbits,1);[d,~]=dsss('despread',dsss('awgn',dsss('spread',b,code),eb),code);m=dsss('metrics',b,d);
  fprintf(fid,'%s,%g,%d,%d,%.12g,%.12g,%.12g,%.12g\n',name,eb,m.bits,m.errors,m.ber,m.ci95_low,m.ci95_high,dsss('theory',eb));
 end
end
fclose(fid);
fid=fopen(fullfile(out,'interference.csv'),'w');fprintf(fid,'jammer,model,js_db,bits,errors,ber\n');
for kind={'tone_inband','tone_outofband','chirp','burst'}
 for js=[-10 0 10 20]
  for mode=1:2
   code=plain;name='BPSK';if mode==2,code=c;name='DSSS';end
   b=randi([0 1],nbits,1);x=dsss('spread',b,code);y=dsss('awgn',x,8)+dsss('interference',numel(x),js,mean(abs(x).^2),kind{1});[d,~]=dsss('despread',y,code);m=dsss('metrics',b,d);
   fprintf(fid,'%s,%s,%g,%d,%d,%.12g\n',kind{1},name,js,m.bits,m.errors,m.ber);
  end
 end
end
fclose(fid);
fid=fopen(fullfile(out,'payloads.csv'),'w');fprintf(fid,'payload,bits,errors,ber\n');
for kind={'random','alternating','bursts','zeros','ones','text','pcm8'}
 b=dsss('payload',kind{1},512,'DSSS | Mohamed Abuain');[d,~]=dsss('despread',dsss('awgn',dsss('spread',b,c),8),c);m=dsss('metrics',b,d);fprintf(fid,'%s,%d,%d,%.12g\n',kind{1},m.bits,m.errors,m.ber);
end
fclose(fid);
fid=fopen(fullfile(out,'multipath.csv'),'w');fprintf(fid,'receiver,path_delay_chips,bits,errors,ber\n');
b=randi([0 1],5000,1);x=dsss('spread',b,c);
for delay=[1 8 64]
 h=dsss('channel',[0 delay],[1 .8*exp(.7i)]);r=dsss('awgn',conv(x,h),8);
 for mode=1:2
  y=r(1:numel(x))/h(1);name='single_finger';if mode==2,y=dsss('matched',r,h,numel(x));name='known_channel_matched';end
  [d,~]=dsss('despread',y,c);m=dsss('metrics',b,d);fprintf(fid,'%s,%d,%d,%d,%.12g\n',name,delay,m.bits,m.errors,m.ber);
 end
end
fclose(fid);
fid=fopen(fullfile(out,'acquisition.csv'),'w');fprintf(fid,'ebn0_db,trials,correct_joint_estimates,success_rate\n');
pre=dsss('spread',randi([0 1],16,1),c);grid=[-.0002 0 .0002];
for eb=[-5 0 5]
 success=0;trials=30;
 for k=1:trials
  delay=randi([0 64]);freq=grid(randi(3));r=[zeros(delay,1);dsss('oscillator',pre,freq,2*pi*rand-pi);zeros(64-delay,1)];est=dsss('acquire',dsss('awgn',r,eb),pre,64,grid);success=success+(est.delay==delay && abs(est.cfo-freq)<1e-12);
 end
 fprintf(fid,'%g,%d,%d,%.12g\n',eb,trials,success,success/trials);
end
fclose(fid);
fid=fopen(fullfile(out,'impairments.csv'),'w');fprintf(fid,'impairment,value,bits,errors,ber,evm_rms\n');
b=randi([0 1],4000,1);x=dsss('spread',b,c,4);
for mode=1:6
 switch mode
 case 1,name='phase_degrees';values=[15 45 80];
 case 2,name='cfo_cycles_per_bit';values=[.001 .01 .05];
 case 3,name='delay_chips';values=[.25 .5 1];
 case 4,name='adc_bits';values=[2 4 8];
 case 5,name='phase_noise';values=[1e-7 1e-6];
 case 6,name='iq_gain_db';values=[1 3];
 end
 for value=values
  switch mode
  case 1,y=dsss('oscillator',x,0,value*pi/180);
  case 2,y=dsss('oscillator',x,value/(127*4),0);
  case 3,y=dsss('delay',x,value*4);
  case 4,y=dsss('quantize',dsss('awgn',x,8),value,.5);
  case 5,y=dsss('oscillator',x,0,0,value);
  case 6,y=dsss('iq',x*exp(1i*pi/4),value,5)*exp(-1i*pi/4);
  end
  if mode~=4,y=dsss('awgn',y,8);end
  [d,soft]=dsss('despread',y,c,4);m=dsss('metrics',b,d);e=sqrt(mean(abs(soft-(1-2*b)).^2));fprintf(fid,'%s,%.12g,%d,%d,%.12g,%.12g\n',name,value,m.bits,m.errors,m.ber,e);
 end
end
fclose(fid);
fid=fopen(fullfile(out,'packets.csv'),'w');fprintf(fid,'ebn0_db,packets,crc_failures,packet_error_rate\n');
for eb=[0 4 8]
 failed=0;for k=1:60,b=dsss('frame',uint8(sprintf('DSSS packet %04d',k)));[d,~]=dsss('despread',dsss('awgn',dsss('spread',b,c),eb),c);[~,ok]=dsss('unframe',d);failed=failed+~ok;end
 fprintf(fid,'%g,60,%d,%.12g\n',eb,failed,failed/60);
end
fclose(fid);
fid=fopen(fullfile(out,'repetition.csv'),'w');fprintf(fid,'ebn0_db,code_rate,bits,errors,ber\n');
for eb=[0 4 8]
 b=randi([0 1],6000,1);enc=dsss('repeat_encode',b);[~,soft]=dsss('despread',dsss('awgn',dsss('spread',enc,c)/sqrt(3),eb),c);d=dsss('repeat_decode',soft);m=dsss('metrics',b,d);fprintf(fid,'%g,%.12g,%d,%d,%.12g\n',eb,1/3,m.bits,m.errors,m.ber);
end
fclose(fid);
fid=fopen(fullfile(out,'near_far.csv'),'w');fprintf(fid,'interferer_to_user_db,bits,errors,ber\n');
second=c.*c(mod(3*(0:126)',127)+1);b=randi([0 1],6000,1);other=randi([0 1],6000,1);
for nf=[-10 0 10 20 30]
 y=dsss('awgn',dsss('spread',b,c)+10^(nf/20)*dsss('spread',other,second),8);[d,~]=dsss('despread',y,c);m=dsss('metrics',b,d);fprintf(fid,'%g,%d,%d,%.12g\n',nf,m.bits,m.errors,m.ber);
end
fclose(fid);
[b,s]=dsss('pn',127);dlmwrite(fullfile(out,'pn_sequence.csv'),[(0:126)' s b],'precision',17);
dlmwrite(fullfile(out,'hardware_trace_excerpt.csv'),dsss('hardware',[0 1 1 0],1000,8),'precision',17);
fid=fopen(fullfile(out,'runtime.txt'),'w');fprintf(fid,'Runtime: %s\nSeed: 20260920 (twister)\nSimulation only. Random streams differ from Python.\n',version);fclose(fid);
fprintf('MATLAB/Octave experiments written to %s\n',out);
end
