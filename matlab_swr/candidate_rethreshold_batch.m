%% set path, mine is:
% restoredefaultpath;
% addpath(genpath('C:\Users\mvdm\Documents\GitHub\vandermeerlab\code-matlab\shared'));
% addpath(genpath('C:\Users\mvdm\Documents\GitHub\vandermeerlab\code-matlab\tasks\Alyssa_Tmaze'));
% addpath(genpath('C:\Users\mvdm\Documents\GitHub\papers\Carey_etal_submitted')); % probably dont' need this one
% disp('SWR analysis path set.');

%% cfg
cfg_master = [];
cfg_master.verbose = 0;
cfg_master.saveOutput = 1;
cfg_master.fn_append = '-ext';

%% cd to data folder (could be in loop)

rats = {'R063', 'R066', 'R067', 'R068'};

for ix=1:length(rats)
    rat = rats{ix};
    
    folder = strcat('E:\\code\\emi_placefields\\data\\', rat, '_EI\\');
    
    session_folders = dir(folder);
    for jx=1:length(session_folders)
        session_folder = session_folders(jx).name;
        if length(session_folder) ~= 25 || ~strcmp(session_folder(16:25), '_recording')
            continue
        end
        
        session_id = session_folder(1:15);
        fc = strcat(folder, session_folder, '\\', session_id, '-SWRcandidates.mat');

        load(fc);

        if cfg_master.verbose
            figure;
            subplot(121)
            hist(evt.tend - evt.tstart);
            title('input iv lengths')
        end

        score_tsd = tsd(evt.tvec, zscore(evt.data));

        cfg = [];
        cfg.threshold = 0;
        iv_out = ResizeIVfromTSD(cfg, evt, score_tsd);

        if cfg_master.verbose
            subplot(122)
            hist(iv_out.tend - iv_out.tstart);
            title('output iv lengths')
        end

        % do some checks
        if length(evt.tstart) ~= length(iv_out.tstart)
            error('unequal lengths');
        end

        if ~CheckIV(iv_out)
            error('iv check fail');
        end

        evt = iv_out;

        % save if requested
        if cfg_master.saveOutput
            [fp fn fe] = fileparts(fc);
            fout = fullfile(fp, strcat(fn, cfg_master.fn_append, fe));
            disp(strcat('Saving ', fout));
            save(fout, 'evt');
        end
    end
end
