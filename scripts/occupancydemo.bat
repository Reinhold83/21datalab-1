setlocal
set "HTTP_PROYX="
set "HTTPS_PROXY="
set "http_proxy="
set "https_proxy="

set mydrive=%~d0
%mydrive%
set mypath=%~dp0
cd %mypath%\..
start python restservice.py occupancydemo
start bokeh serve bokeh_web --allow-websocket-origin="*" --port 5006 --args http://127.0.0.1:6001/ root.visualization.workbench
start bokeh serve bokeh_web --allow-websocket-origin="*" --port 5010 --args http://127.0.0.1:6001/ root.visualization.selfservice0
endlocal