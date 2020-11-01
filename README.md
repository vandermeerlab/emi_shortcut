Shortcut task description	
=========================
Below is a brief overview of shortcut experiment task and analysis work flow.	

Objectives
----------
The main objective of this task was to determine whether hippocampal place	
cells during replay events represent novel behaviorally-relevant shortcut trajectories that the subject has not yet physically encountered.
This was accomplished with the following analysis:
* Behavior-only analyses
* Place cell dynamics
* Sharp-wave ripple statistics
* Replay statistics
* Replay content via Bayesian decoding

Subjects
--------
Four male Long-Evans rats (Harlan; Mississauga, Canada), 5-12 months old, whose identifiers are R063, R066, R067, and R068.

Task Description
----------------
![Shortcut task](task-description.pdf)

Each recording session had the structure outlined in the above figure. Briefly, a recording session consisted of three main running blocks (Phase 1, Phase 2 and Phase 3), each bracketed by a rest period on a nearby pedestal (Pre-task, Pause A, Pause B and Post-task). The task phases started with Phase 1 in which only the familiar common core route was available. In Phase 2 the novel shortcut and dead-end trajectories were present but unavailable as their entrances were blocked by transparent barriers. Finally, Phase 3 allowed access to the full maze. In total, there were 8 recording sessions, each with a unique shortcut and dead-end path.

Analysis
--------
Each recording session contains a unique `json` file that has the meta data for that session, housed in the info directory. Meta data including commonly used variables is in meta.py. meta_session.py contains session loading and grouping info. Functions are set up with doit dependencies, such that the dependencies can be forgotten and downstream analyses will rerun.

For emi thesis:
The thesis repository should be in the same folder as emi_shortcut (eg. code) and contain: thesis>images and thesis>generated.
* Start from a fresh `doit forget` state (or forget specific tasks)
* Figure generation: `doit copy_figures`
* Variable generation: `doit copy_tex`