REM get this folder here as a reference
set mypath=%~dp0
 
 
REM git clone https://github.com/smartyal/21datalab.git %mypath%21datalab
REM create virtual environment for this project
python -m venv %mypath%..\venv
REM %mypath%..\venv\Scripts\pip.exe install --upgrade pip
%mypath%..\venv\Scripts\pip.exe install -r %mypath%..\requirements.txt

REM download the web packages
REM goto exit

mkdir %mypath%temp
curl -L https://github.com/twbs/bootstrap/releases/download/v4.5.0/bootstrap-4.5.0-dist.zip --output %mypath%temp\bootstrap.zip
curl -L https://github.com/snapappointments/bootstrap-select/archive/v1.13.14.zip --output %mypath%temp\select.zip
curl -L https://github.com/mladenplavsic/bootstrap-navbar-sidebar/archive/refs/tags/v4.0.2.zip --output %mypath%temp\navsidebar.zip
curl -L https://github.com/thomaspark/bootswatch/archive/refs/tags/v4.6.0.zip --output %mypath%temp\bootswatch.zip
curl -L https://use.fontawesome.com/releases/v5.7.2/fontawesome-free-5.7.2-web.zip --output %mypath%temp\font.zip
curl -L https://code.jquery.com/jquery-3.6.0.min.js --output %mypath%temp\jquery.js
curl -L https://github.com/vakata/jstree/zipball/3.3.11 --output %mypath%temp\jstree.zip
curl -L https://github.com/deitch/jstree-grid/archive/refs/tags/v3.9.4.zip --output %mypath%temp\jsgrid.zip
curl -L https://cdnjs.cloudflare.com/ajax/libs/popper.js/2.6.0/umd/popper.min.js --output %mypath%temp\popper.min.js
curl -L https://momentjs.com/downloads/moment.js --output %mypath%temp\moment.min.js
curl -L https://momentjs.com/downloads/moment-timezone-with-data.min.js --output %mypath%temp\moment-timezone-with-data.min.js
curl -L https://github.com/blueimp/jQuery-File-Upload/archive/refs/tags/v10.31.0.zip --output %mypath%temp\fileupload.zip
curl -L https://jqueryui.com/resources/download/jquery-ui-1.12.1.zip --output %mypath%temp\jqueryui.zip
curl -L https://github.com/smartyal/supercontextmenu/archive/refs/heads/master.zip --output %mypath%temp\supercontext.zip
:skipdownload



tar xopf %mypath%temp\bootstrap.zip -C %mypath%..\web\modules
tar xopf %mypath%temp\select.zip -C %mypath%..\web\modules
tar xopf %mypath%temp\navsidebar.zip -C %mypath%..\web\modules
tar xopf %mypath%temp\bootswatch.zip -C %mypath%..\web\modules
tar xopf %mypath%temp\font.zip -C %mypath%..\web\modules
mkdir %mypath%..\web\modules\jquery
copy %mypath%temp\jquery.js %mypath%..\web\modules\jquery
tar xopf %mypath%temp\jstree.zip -C %mypath%..\web\modules
tar xopf %mypath%temp\jsgrid.zip -C %mypath%..\web\modules\
mkdir %mypath%..\web\modules\other
copy %mypath%temp\popper.min.js %mypath%..\web\modules\other
mkdir %mypath%..\web\modules\moment
copy %mypath%temp\moment.min.js %mypath%..\web\modules\moment
copy %mypath%temp\moment-timezone-with-data.min.js %mypath%..\web\modules\moment
tar xopf %mypath%temp\fileupload.zip -C %mypath%..\web\modules
tar xopf %mypath%temp\jqueryui.zip -C %mypath%..\web\modules
tar xopf %mypath%temp\supercontext.zip -C %mypath%..\web\modules

 

cd %mypath%..\web\modules

rename "bootstrap-4.5.0-dist" bootstrap
rename "bootstrap-select-1.13.14" "bootstrap-select"
rename "bootstrap-navbar-sidebar-4.0.2" "bootstrap-navbar-sidebar"
rename "bootswatch-4.6.0" bootswatch"
rename "fontawesome-free-5.7.2-web" "font-awesome"
rename "vakata-jstree-4a77e59" "jstree"
rename "jstree-grid-3.9.4" "jstree-grid"
rename "jQuery-File-Upload-10.31.0" "jQuery-File-Upload"
rename "jquery-ui-1.12.1" "jquery-ui"

cd %mypath%

rmdir /s/q temp

rem finally fix the active.bat ! change delims=:" to delims=:."
python fix_activate.py

:exit
 