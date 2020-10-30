%% first, run SCRIPT_Manually_Identify_SWRs.m
% output should be *ManualIV.mat file with manually identified SWRs
% rest of this script is modified from aacarey's GenCandidateEvents.m to work on shortcut data

%%
cfg_def.verbose = 0; % i don't want to see what the internal functions have to say 
cfg_def.load_questionable_cells = 1;
cfg_def.SWRmethod = 'AM'; % 'AM' for amSWR (frequency content similarity), 'HT' for OldWizard (hilbert transform), 'TR' for photonic (transient detection), or 'none' to skip
cfg_def.MUAmethod = 'AM'; % 'AM' for amMUA, or 'none' for skip MUA detection
cfg_def.weightby = 'amplitude'; % this applies to 'AM' amSWR and 'TR' photonic, but not 'HT' OldWizard
cfg_def.stepSize = 1;
cfg_def.ThreshMethod = 'zscore';
cfg_def.DetectorThreshold = 3; % the threshold you want for generating IV data
cfg_def.mindur = 0.02; % in seconds, the minumum duration for detected events to be kept
cfg_def.SpeedLimit = 10; % pixels per second
cfg_def.ThetaThreshold = 2; % power, std above mean
cfg_def.minCells = 5; % minimum number of active cells for the event to be kept. if this is empty [], this step is skipped
cfg_def.expandIV = [0 0]; % amount to add to the interval (catch borderline missed spikes)
cfg_def.allowOverlap = 0; % don't allow the expanded intervals to overlap one another

cfg = ProcessConfig(cfg_def,[]);

%% load things
LoadExpKeys
please = []; please.fc = ExpKeys.goodSWR(1); please.resample = 2000;
CSC = LoadCSC(please);

cfg_temp = []; cfg_temp.getRatings = 0; cfg_temp.load_questionable_cells = cfg.load_questionable_cells; cfg_temp.verbose = cfg.verbose;
S = LoadSpikes(cfg_temp);
S = RemoveInterneuronsHC([], S, CSC);

load(FindFile('*vt.mat')); % creates pos_tsd variable
if ~exist('pos_tsd')
    pos_tsd = pos; clear pos;
end

%% compute SWR score (can be slow)
switch cfg.SWRmethod
    case 'AM'
        load(FindFile('*ManualIV.mat')); % creates evt variable with SWR intervals
        ncfs = SWRfreak([], evt, CSC);
        cfg_temp = []; cfg_temp.verbose = cfg.verbose; cfg_temp.weightby = cfg.weightby; cfg_temp.stepSize = cfg.stepSize;
        [SWR,~,~] = amSWR(cfg_temp, ncfs, CSC);
        
    case 'HT'
        cfg.stepSize = [];
        cfg.weightby = [];
        cfg_temp = []; cfg_temp.verbose = cfg.verbose; cfg_temp.rippleband = [140 250]; cfg_temp.smooth = 1; cfg_temp.kernel = [];
        SWR = OldWizard(cfg_temp,CSC);
        
    case 'TR'
        cfg.stepSize = [];
        
        cfg_temp =[]; cfg_temp.type = 'fdesign'; cfg_temp.f = [140 250];
        CSCr = filterLFP(cfg_temp,CSC);
        
        cfg_temp.weightby = cfg.weightby; cfg_temp.kernel = 'gauss';
        SWR = photonic(cfg_temp,CSCr);
        
    case 'none'
        cfg.stepSize = [];
        cfg.weightby = [];
        SWR = [];
end

%% MUA score
if ~strcmp(cfg.MUAmethod,'none'); disp(' '); disp('***Working on MUA detection.....'); end

switch cfg.MUAmethod
    case 'AM'
        cfg_temp = [];
        cfg_temp.verbose = cfg.verbose;
        [MUA,~,~] = amMUA(cfg_temp,S,CSC.tvec);
        
    case 'none'
        MUA = [];
end

%% Combine the detectors
disp(' ')
disp('***Compiling and thresholding detection scores....')

if ~isempty(SWR)
    SWR = rescmean(SWR,1); % this was a step in precand()
elseif isempty(SWR) && ~isempty(MUA)
    SWR = MUA; % for getting geometric mean...if SWR == MUA , then gm(SWR,MUA) = MUA
end

if ~isempty(MUA)
    %MUA = rescmean(MUA,1); % rescaling of MUA was not performed in precand()
elseif isempty(MUA) && ~isempty(SWR)
    MUA = SWR;
end

cfg_temp =[];
cfg_temp.method = 'geometricmean'; cfg_temp.verbose = cfg.verbose;
score = MergeTSD(cfg_temp, SWR, MUA);

score = rescmean(score, 0.5); % this was a step in precand(), doing same to preserve

% threshold
cfg_temp = [];
cfg_temp.threshold = cfg.DetectorThreshold; cfg_temp.verbose = cfg.verbose; cfg_temp.method = cfg.ThreshMethod;
cfg_temp.operation = '>';
evt = TSDtoIV2(cfg_temp,score);

% remove short intervals
cfg_temp = []; cfg_temp.verbose = cfg.verbose; cfg_temp.mindur = cfg.mindur;
evt = RemoveIV(cfg_temp,evt);

evt.data = score.data; evt.tvec = score.tvec;


%%
if ~isempty(cfg.SpeedLimit)
    disp(' ')
    disp('***Limiting output based on speed...')
    
    cfg_temp = []; cfg_temp.verbose = cfg.verbose;
    spd = getLinSpd(cfg_temp,pos_tsd);
    
    cfg_temp.threshold = cfg.SpeedLimit; cfg_temp.operation = '<'; cfg_temp.method = 'raw'; cfg_temp.verbose = cfg.verbose;
    cfg_temp.dcn = '<';
    low_spd_iv = TSDtoIV(cfg_temp,spd);
    
    evt = restrict(evt,low_spd_iv);
    disp(['***',num2str(length(evt.tstart)),' speed-limited candidates found.'])
end

%%
if ~isempty(cfg.ThetaThreshold)
    disp(' ')
    disp('***Limiting output based on theta power..')
    
    % remove events during high theta
    % 4th order, passband [6 10]
    cfg_temp = []; cfg_temp.f = [6 10]; cfg_temp.order = 4; cfg_temp.display_filter = 0; cfg_temp.type = 'fdesign'; cfg_temp.verbose = cfg.verbose;
    lfp_theta_filtered = FilterLFP(cfg_temp,CSC);
    
    % create tsd with theta power (lfp_theta is the output from LoadCSC)
    cfg_temp = []; cfg_temp.verbose = cfg.verbose;
    tpow = LFPpower(cfg_temp,lfp_theta_filtered);
    
    % detect intervals with "low theta" (z-score below 2)
    cfg_temp = []; cfg_temp.method = 'zscore'; cfg_temp.threshold = cfg.ThetaThreshold; cfg_temp.dcn =  '<'; cfg_temp.verbose = cfg.verbose;
    cfg_temp.operation =  '<';
    low_theta_iv = TSDtoIV(cfg_temp,tpow);
    
    % restrict candidate events to only those inside low theta intervals
    evt = restrict(evt,low_theta_iv);
    
    disp(['***',num2str(length(evt.tstart)),' theta-limited candidates found.'])
end


%% Number of active cells thresholding (this is done last because it's slower than speed and theta thresholding)
disp(' ')
cfg_temp =[]; cfg_temp.verbose = cfg.verbose;
evt = AddNActiveCellsIV(cfg_temp,evt,S);
if ~isempty(cfg.minCells)
    
    disp('***Limiting output based on number of active cells.')
    cfg_temp = []; cfg_temp.operation = '>='; cfg_temp.threshold = cfg.minCells;
    evt = SelectIV(cfg_temp,evt,'nActiveCells');
end

%% Expand intervals to catch missed spikes
if abs(prod(cfg.expandIV))> 0
    disp(' ')
    disp('***Expanding intervals of remaining events')
    
    cfg_temp = [];
    cfg_temp.d = cfg.expandIV; cfg_temp.allowOverlap = cfg.allowOverlap;
    evt = ResizeIV(cfg_temp,evt);
    if ~cfg.allowOverlap
        evt = MergeIV([],evt);
    end
end

% tell me how many you found
disp(' '); disp(['***Finished detection: ',num2str(length(evt.tstart)),' candidates found.']); disp(' ')

%% plot

%cfg_mr = []; cfg_mr.lfp = csc; cfg_mr.evt = evt;
%MultiRaster(cfg_mr, S);

%% remember to save evt variable manually if you want to keep these candidates!
