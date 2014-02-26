cd _LIB

:python-2.7.3.msi /passive
cd bradjasper-django-jsonfield-2f42736
setup.py install
cd ..
cd Django-1.4
setup.py install
cd ..
cd flup-1.0.2
setup.py install
cd ..

cd ..

net user judge judge /add
net localgroup guests judge /add
net localgroup users judge /delete
ntrights.exe -u judge +r SeServiceLogonRight
ntrights.exe -u judge +r SeDenyInteractiveLogonRight
ntrights.exe -u judge +r SeDenyBatchLogonRight

cd JUDGE
PySQOJJudgeServer.py --username .\judge --password judge --startup auto install
cd ..

cd NGINX
nginxServer.py --username .\judge --password judge --startup auto install
cd ..

cd WEB
PySQOJWebServer.py --username %.\judge --password judge --startup auto install
cd ..

pause