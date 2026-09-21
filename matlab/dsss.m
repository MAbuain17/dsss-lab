function varargout = dsss(action, varargin)
%DSSS Toolbox-free reference primitives; vectors are columns.
% Mapping: bit 0 -> +1, bit 1 -> -1. Discrete energy Eb=1.
% See docs/methodology.md. No Communications Toolbox required.
switch lower(action)
case 'pn'
    n=varargin{1}; state=0; if numel(varargin)>1, state=varargin{2}; end
    assert(n>=1 && n==floor(n) && state>=0 && state<127 && state==floor(state));
    states=zeros(n,1); bits=zeros(n,1);
    for k=1:n
        states(k)=state; bits(k)=bitget(uint8(state),7);
        fb=1-double(xor(bitget(uint8(state),7),bitget(uint8(state),1)));
        state=floor(state/2)+64*fb;
    end
    varargout={bits,states};
case 'code'
    n=127; if ~isempty(varargin), n=varargin{1}; end
    assert(n>=1 && n==floor(n)); [b,~]=dsss('pn',127); c=1-2*b;
    c=c(mod((0:n-1)',127)+1);
    if numel(varargin)>1, c=circshift(c,varargin{2}); end
    varargout={c};
case 'spread'
    b=checkbits(varargin{1}); c=varargin{2}(:); sps=1;
    if numel(varargin)>2, sps=varargin{3}; end
    assert(all(abs(c)==1) && sps>=1 && sps==floor(sps));
    p=kron(c,ones(sps,1)); x=reshape(p*(1-2*b).',[],1)/sqrt(numel(p));
    varargout={x};
case 'despread'
    y=varargin{1}(:);c=varargin{2}(:);sps=1;
    if numel(varargin)>2, sps=varargin{3}; end
    p=kron(c,ones(sps,1));assert(mod(numel(y),numel(p))==0);
    soft=(p.'*reshape(y,numel(p),[])).'/sqrt(numel(p));
    varargout={double(real(soft)<0),soft};
case 'awgn'
    x=varargin{1}; eb=varargin{2}; assert(isfinite(eb) || eb==Inf);
    sd=sqrt(.5*10^(-eb/10));varargout={x+sd*(randn(size(x))+1i*randn(size(x)))};
case 'theory'
    varargout={.5*erfc(sqrt(10.^(varargin{1}/10)))};
case 'metrics'
    a=checkbits(varargin{1});b=checkbits(varargin{2});assert(numel(a)==numel(b));
    n=numel(a);k=sum(a~=b);p=k/n;z=1.95996398454;den=1+z*z/n;
    center=(p+z*z/(2*n))/den;rad=z*sqrt(p*(1-p)/n+z*z/(4*n*n))/den;
    varargout={struct('bits',n,'errors',k,'ber',p,'ci95_low',max(0,center-rad),'ci95_high',min(1,center+rad))};
case 'acf'
    c=varargin{1}(:);varargout={real(ifft(abs(fft(c)).^2))/numel(c)};
case 'oscillator'
    x=varargin{1}(:);freq=varargin{2};phase=varargin{3};
    p=phase+2*pi*freq*(0:numel(x)-1)';
    if numel(varargin)>3, p=p+cumsum(sqrt(2*pi*varargin{4})*randn(size(x))); end
    varargout={x.*exp(1i*p)};
case 'delay'
    x=varargin{1}(:);d=varargin{2};t=(0:numel(x)-1)';
    varargout={interp1(t,x,t-d,'linear',0)};
case 'quantize'
    x=varargin{1};bits=varargin{2};fs=varargin{3};assert(bits>=2 && bits==floor(bits) && fs>0);
    levels=2^bits-1;q=@(v) round((min(fs,max(-fs,v))+fs)/(2*fs)*levels)/levels*(2*fs)-fs;
    varargout={q(real(x))+1i*q(imag(x))};
case 'iq'
    x=varargin{1};g=10^(varargin{2}/20);p=varargin{3}*pi/180;
    varargout={real(x)-g*sin(p)*imag(x)+1i*g*cos(p)*imag(x)};
case 'interference'
    n=varargin{1};js=varargin{2};power=varargin{3};kind=varargin{4};
    t=(0:n-1)';phase=2*pi*rand-pi;
    switch kind
        case {'tone','tone_outofband'},j=exp(1i*(2*pi*.037*t+phase));
        case 'tone_inband',j=exp(1i*(2*pi*.001*t+phase));
        case 'chirp',j=exp(1i*(2*pi*(-.01*t+.01*t.*t/n)+phase));
        case 'burst',j=(randn(n,1)+1i*randn(n,1))/sqrt(2).*(mod(t,1000)<100);
        case 'noise',j=(randn(n,1)+1i*randn(n,1))/sqrt(2);
        otherwise,error('Unknown interference type');
    end
    varargout={j*sqrt(power*10^(js/10)/mean(abs(j).^2))};
case 'channel'
    delays=varargin{1};gains=varargin{2};assert(numel(delays)==numel(gains) && all(delays>=0) && all(delays==floor(delays)));
    h=zeros(max(delays)+1,1);
    for k=1:numel(delays),h(delays(k)+1)=h(delays(k)+1)+gains(k);end
    assert(norm(h)>0);varargout={h/norm(h)};
case 'matched'
    r=varargin{1}(:);h=varargin{2}(:);n=varargin{3};y=conv(r,conj(flipud(h)));
    varargout={y(numel(h):numel(h)+n-1)/sum(abs(h).^2)};
case 'acquire'
    r=varargin{1}(:);p=varargin{2}(:);md=varargin{3};grid=varargin{4};m=numel(p);
    assert(numel(r)>=m+md);best=-Inf;est=struct();
    for f=grid(:).'
        t=p.*exp(2i*pi*f*(0:m-1)');corr=conv(r(1:m+md),conj(flipud(t)),'valid');
        [score,idx]=max(abs(corr));score=score/sum(abs(p).^2);
        if score>best,best=score;est=struct('delay',idx-1,'cfo',f,'phase',angle(corr(idx)),'score',score);end
    end
    varargout={est};
case 'payload'
    kind=varargin{1};n=varargin{2};
    switch kind
        case 'random',b=randi([0 1],n,1);
        case 'alternating',b=mod((0:n-1)',2);
        case 'bursts',b=mod(floor((0:n-1)'/32),2);
        case 'zeros',b=zeros(n,1);
        case 'ones',b=ones(n,1);
        case 'text',b=bytes_to_bits(uint8(varargin{3}));
        case 'pcm8'
            t=(0:n-1)'/8000;a=.6*sin(2*pi*440*t)+.25*sin(2*pi*880*t);
            b=bytes_to_bits(uint8(round((max(-1,min(1,a))+1)*127.5)));
        otherwise,error('Unknown payload');
    end
    varargout={b};
case 'pcm8_decode'
    varargout={double(bits_to_bytes(varargin{1}))/127.5-1};
case 'frame'
    data=uint8(varargin{1}(:));n=numel(data);assert(n<=65535);
    body=[uint8(floor(n/256));uint8(mod(n,256));data];crc=crc32_local(body);
    trailer=uint8([bitand(bitshift(crc,-24),255);bitand(bitshift(crc,-16),255);bitand(bitshift(crc,-8),255);bitand(crc,255)]);
    varargout={bytes_to_bits([body;trailer])};
case 'unframe'
    b=checkbits(varargin{1});data=uint8([]);ok=false;
    if mod(numel(b),8)==0 && numel(b)>=48
        raw=bits_to_bytes(b);n=double(raw(1))*256+double(raw(2));data=raw(3:end-4);
        crc=uint32(0);for k=numel(raw)-3:numel(raw),crc=bitor(bitshift(crc,8),uint32(raw(k)));end
        ok=numel(raw)==n+6 && crc32_local(raw(1:end-4))==crc;
    end
    varargout={data,ok};
case 'repeat_encode'
    varargout={kron(checkbits(varargin{1}),ones(3,1))};
case 'repeat_decode'
    varargout={double(real(sum(reshape(varargin{1},3,[]),1)).'<0)};
case 'hardware'
    b=checkbits(varargin{1});sf=varargin{2};sps=varargin{3};assert(sps>=2 && mod(sps,2)==0);
    data=kron(b,ones(sf*sps,1));pn=kron(dsss('pn',numel(b)*sf),ones(sps,1));n=numel(data);
    ca=double(mod((0:n-1)',sps)>=sps/2);ss=double(xor(data,pn));tx=double(xor(ss,ca));rx=double(xor(xor(tx,pn),ca));
    varargout={[(0:n-1)'/(2e6*sps),data,pn,ca,ss,tx,rx]};
case 'rrc'
    beta=varargin{1};span=varargin{2};sps=varargin{3};assert(beta>0 && beta<=1 && mod(span,2)==0 && sps>=2);
    t=(-span*sps/2:span*sps/2)'/sps;h=zeros(size(t));
    for k=1:numel(t)
        v=t(k);
        if abs(v)<1e-12,h(k)=1+beta*(4/pi-1);
        elseif abs(abs(v)-1/(4*beta))<1e-12,h(k)=beta/sqrt(2)*((1+2/pi)*sin(pi/(4*beta))+(1-2/pi)*cos(pi/(4*beta)));
        else,h(k)=(sin(pi*v*(1-beta))+4*beta*v*cos(pi*v*(1+beta)))/(pi*v*(1-(4*beta*v)^2));end
    end
    varargout={h/norm(h)};
case 'shape'
    x=varargin{1}(:);h=varargin{2}(:);sps=varargin{3};u=zeros((numel(x)-1)*sps+1,1);u(1:sps:end)=x;varargout={conv(u,h)};
case 'matched_pulse'
    y=varargin{1};h=varargin{2};sps=varargin{3};n=varargin{4};z=conv(y,conj(flipud(h)));varargout={z(numel(h):sps:numel(h)+(n-1)*sps)};
case 'spectrum'
    x=varargin{1}(:);fs=varargin{2};L=min(4096,numel(x));step=max(1,floor(L/2));w=.5-.5*cos(2*pi*(0:L-1)'/L);p=zeros(L,1);count=0;
    for start=1:step:numel(x)-L+1,p=p+abs(fft(x(start:start+L-1).*w)).^2;count=count+1;end
    p=fftshift(p/(count*fs*sum(w.^2)));f=(-floor(L/2):ceil(L/2)-1)'*fs/L;cum=cumsum(p)/sum(p);lo=find(cum>=.005,1);hi=find(cum>=.995,1);varargout={f,p,f(hi)-f(lo)};
case 'receive_burst'
    r=varargin{1}(:);pre=varargin{2}(:);nb=varargin{3};c=varargin{4};md=varargin{5};grid=varargin{6};
    est=dsss('acquire',r,pre,md,grid);n=numel(pre)+nb*numel(c);assert(numel(r)>=est.delay+n);
    y=r(est.delay+(1:n)).*exp(-1i*(est.phase+2*pi*est.cfo*(0:n-1)'));
    [b,soft]=dsss('despread',y(numel(pre)+1:end),c);varargout={b,soft,est};
otherwise,error('Unknown DSSS action: %s',action);
end
end

function a=checkbits(b)
a=double(b(:));assert(~isempty(a) && all(a==0 | a==1));
end
function bits=bytes_to_bits(data)
x=uint8(data(:));m=zeros(numel(x),8);
for k=1:8,m(:,k)=double(bitget(x,9-k));end
bits=reshape(m.',[],1);
end
function data=bits_to_bytes(bits)
b=checkbits(bits);assert(mod(numel(b),8)==0);data=uint8((2.^(7:-1:0))*reshape(b,8,[])).';
end
function c=crc32_local(data)
c=uint32(hex2dec('FFFFFFFF'));poly=uint32(hex2dec('EDB88320'));
for byte=uint8(data(:)).'
    c=bitxor(c,uint32(byte));
    for j=1:8
        low=bitand(c,uint32(1));c=bitshift(c,-1);if low,c=bitxor(c,poly);end
    end
end
c=bitxor(c,uint32(hex2dec('FFFFFFFF')));
end
