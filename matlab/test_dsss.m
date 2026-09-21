function test_dsss()
% Deterministic MATLAB / GNU Octave checks, including Python golden vectors.
[b,s]=dsss('pn',128);assert(isequal(s(1:8)',[0 64 32 80 40 84 42 85]));assert(s(128)==0 && numel(unique(s(1:127)))==127);assert(sum(b(1:127))==63);
c=dsss('code',127);a=dsss('acf',c);assert(abs(a(1)-1)<1e-12 && max(abs(a(2:end)+1/127))<1e-12);
b=mod((0:100)',2);
for sf=[1 7 31 127]
 for sps=[1 4]
  c=dsss('code',sf);x=dsss('spread',b,c,sps);assert(abs(sum(x.^2)-numel(b))<1e-9);
  [d,s]=dsss('despread',x,c,sps);assert(isequal(b,d));assert(max(abs(s-(1-2*b)))<1e-12);
 end
end
f=dsss('frame',uint8('DSSS'));[data,ok]=dsss('unframe',f);assert(ok && isequal(data,uint8('DSSS')'));f(20)=1-f(20);[~,ok]=dsss('unframe',f);assert(~ok);
p=dsss('spread',b(1:12),dsss('code',31));r=[zeros(17,1);dsss('oscillator',p,.002,.7);zeros(23,1)];est=dsss('acquire',r,p,40,[-.002 0 .002]);assert(est.delay==17 && est.cfo==.002 && abs(est.phase-.7)<1e-10);
h=dsss('hardware',[0 1 0 1],1000,8);assert(isequal(h(:,2),h(:,7)));
root=fileparts(fileparts(mfilename('fullpath')));v=dlmread(fullfile(root,'tests','golden_vectors.csv'),',',1,0);
[d,soft]=dsss('despread',v(:,2)+1i*v(:,3),dsss('code',31));
expected=dlmread(fullfile(root,'tests','golden_decisions.csv'),',',1,0);
assert(isequal(d,expected(:,1)));assert(max(abs(soft-(expected(:,2)+1i*expected(:,3))))<1e-10);
frame_expected=dlmread(fullfile(root,'tests','golden_frame.csv'),',',1,0);assert(isequal(dsss('frame',uint8('DSSS')),frame_expected));
rng(17,'twister');b=randi([0 1],60000,1);c=dsss('code',7);[d,~]=dsss('despread',dsss('awgn',dsss('spread',b,c),2),c);m=dsss('metrics',b,d);p=dsss('theory',2);assert(abs(m.ber-p)<5*sqrt(p*(1-p)/numel(b)));
fprintf('All MATLAB/Octave DSSS assertions passed.\n');
end
