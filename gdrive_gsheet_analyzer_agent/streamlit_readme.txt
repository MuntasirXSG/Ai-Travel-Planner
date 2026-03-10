
#######command prompt##########
1. to run streamlit the terminal must be switched to command prompt mode.(*the powershell gives error with uv env. but works with conda env.  error: uv trampoline failed to canonicalize script path)


2. RUN : streamlit run app.py in terminal

#### powershell######

if command prompt is in power shell then run : python -m streamlit run app.py to load the app

with this the app will run 



AI insights: 

PowerShell had trouble resolving the uv launcher script path.

uv creates a wrapper (trampoline) script to run programs like Streamlit.

PowerShell sometimes fails to resolve that wrapper path on Windows, causing the error:
uv trampoline failed to canonicalize script path.

Command Prompt handles .exe launchers more directly, so it finds the correct path and runs Streamlit normally.

✅ So the problem was PowerShell path resolution with the uv wrapper, not Streamlit itself.