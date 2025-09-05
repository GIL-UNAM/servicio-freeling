# servicio-freeling
Sistema de consulta via web de Freeling

# requisitos previos y puesta en funcionamiento
1. Instalar free-ling

``` shell
sudo apt-get install libboost-regex-dev libicu-dev zlib1g-dev libboost-dev
sudo apt-get install libboost-system-dev libboost-program-options-dev libboost-thread-dev
```
Obtener el paquete oficial de FreeLing 4.2 para Ubuntu Focal de la página oficial:
``` shell
wget https://github.com/TALP-UPC/FreeLing/releases/download/4.2/freeling-4.2-focal-amd64.deb
wget https://github.com/TALP-UPC/FreeLing/releases/download/4.2/freeling-langs-4.2.deb
```

``` shell
sudo dpkg -i freeling-4.2-focal-amd64.deb
sudo dpkg -i freeling-langs-4.2.deb
```

2. instalar PHP, la que se instaló fue php7.4

```
sudo apt install -y php7.4
```

3. verificar que esté corriendo el servicio de apache y si no instalrlo o levantarlo

```
sudo service apache2 status
sudo service apache2 start
```

4. tener instalado python3 e instalar el módulo langid
```
sudo pip3 install langid

Collecting langid
  Downloading langid-1.1.6.tar.gz (1.9 MB)
...
...
Successfully built langid
Installing collected packages: numpy, langid
Successfully installed langid-1.1.6 numpy-1.20.3
```
6. Crear un directorio dentro de /var/www/html para servicio-freeling (recomendamos que se llame así) pués será la ruta del servidor para ofrecer el servicio

   http://mi.servidor.org/servicio-freeling
   
8. descargar en ese directorio el git
9. usar el script start.sh para arrancar los demonios de freeling, tomar en cuenta que puede ser necesario:

Editar start.sh de ser necesario para que el COMMAND sea la ruta del comando del analizador (analyzer)
Editar functions.php de ser necesario para que CLIENTPATH sea la ruta del cliente (analyzerclient)
Ejecutar start.sh para iniciar todos los procesos servidores de freeling

```
source start.sh
```

10. **Servicio con freeling**
    
Para dejar un servicio que levante freeling aun despues de reiniciar el servidor
crea un usuario para aislar posibles fallas de seguridad

``` shell
sudo useradd --system --no-create-home --shell /usr/sbin/nologin freeling
```

copia el archivo que define el servicio a init.d asegurate que tenga derechos de ejecución y registralo en systemd
``` shell
sudo cp servicio-freeling /etc/init.d/.
sudo chmod +x /etc/init.d/servicio-freeling
sudo update-rc.d servicio-freeling defaults
```
prueba su funcionamiento:

``` shell
sudo service servicio-freeling stop
sudo service servicio-freeling start
sudo service servicio-freeling status
```


# problemas encontrados y cómo los solucioné:

Al instalar freeling

``` 
gcastilloh@PC-001:~$ sudo dpkg -i freeling-4.2-focal-amd64.deb
Selecting previously unselected package freeling.
(Reading database ... 55702 files and directories currently installed.)
...
...
dpkg: dependency problems prevent configuration of freeling:
 freeling depends on libboost-filesystem1.71.0 (>= 1.71); however:
  Package libboost-filesystem1.71.0 is not installed.
 freeling depends on libboost-iostreams1.71.0 (>= 1.71); however:
  Package libboost-iostreams1.71.0 is not installed.

dpkg: error processing package freeling (--install):
 dependency problems - leaving unconfigured
Errors were encountered while processing:
 freeling
```

Los resolví desintalando las libboost ejecutando el fix-broken y voviendo a instalar las librerias

```
apt --fix-broken install
sudo apt-get install libboost-regex-dev libicu-dev zlib1g-dev libboost-dev
sudo apt-get install libboost-system-dev libboost-program-options-dev libboost-thread-dev
```


## LOG de operaciones del error encontrado:

Para el registro aquí dejo los problemas que registré:

```
gcastilloh@PC-001:~$ sudo dpkg -i freeling-4.2-focal-amd64.deb
Selecting previously unselected package freeling.
(Reading database ... 55702 files and directories currently installed.)
Preparing to unpack freeling-4.2-focal-amd64.deb ...
Unpacking freeling (4.2) ...
dpkg: dependency problems prevent configuration of freeling:
 freeling depends on libboost-filesystem1.71.0 (>= 1.71); however:
  Package libboost-filesystem1.71.0 is not installed.
 freeling depends on libboost-iostreams1.71.0 (>= 1.71); however:
  Package libboost-iostreams1.71.0 is not installed.

dpkg: error processing package freeling (--install):
 dependency problems - leaving unconfigured
Errors were encountered while processing:
 freeling

gcastilloh@PC-001:~$ sudo apt-get remove libboost-system-dev libboost-program-options-dev libboost-thread-dev
Reading package lists... Done
Building dependency tree
Reading state information... Done
You might want to run 'apt --fix-broken install' to correct these.
The following packages have unmet dependencies:
 freeling : Depends: libboost-filesystem1.71.0 (>= 1.71) but it is not going to be installed
            Depends: libboost-iostreams1.71.0 (>= 1.71) but it is not going to be installed
E: Unmet dependencies. Try 'apt --fix-broken install' with no packages (or specify a solution).

gcastilloh@PC-001:~$ sudo apt-get remove libboost-regex-dev libicu-dev zlib1g-dev libboost-dev
Reading package lists... Done
Building dependency tree
Reading state information... Done
You might want to run 'apt --fix-broken install' to correct these.
The following packages have unmet dependencies:
 freeling : Depends: libboost-filesystem1.71.0 (>= 1.71) but it is not going to be installed
            Depends: libboost-iostreams1.71.0 (>= 1.71) but it is not going to be installed
 libboost-regex1.71-dev : Depends: libicu-dev but it is not going to be installed
 python3.8-dev : Depends: zlib1g-dev but it is not going to be installed
E: Unmet dependencies. Try 'apt --fix-broken install' with no packages (or specify a solution).

gcastilloh@PC-001:~$ sudo apt-get remove libboost-system-dev libboost-program-options-dev libboost-thread-dev
Reading package lists... Done
Building dependency tree
Reading state information... Done
Correcting dependencies... Done
The following packages were automatically installed and are no longer required:
  libtaglibs-standard-impl-java libtaglibs-standard-spec-java
Use 'sudo apt autoremove' to remove them.
The following additional packages will be installed:
  libboost-filesystem1.71.0 libboost-iostreams1.71.0
The following NEW packages will be installed:
  libboost-filesystem1.71.0 libboost-iostreams1.71.0
0 upgraded, 2 newly installed, 0 to remove and 66 not upgraded.
1 not fully installed or removed.
Need to get 479 kB of archives.
After this operation, 4284 kB of additional disk space will be used.
Do you want to continue? [Y/n] y
Get:1 http://archive.ubuntu.com/ubuntu focal/main amd64 libboost-filesystem1.71.0 amd64 1.71.0-6ubuntu6 [242 kB]
Get:2 http://archive.ubuntu.com/ubuntu focal/main amd64 libboost-iostreams1.71.0 amd64 1.71.0-6ubuntu6 [237 kB]
Fetched 479 kB in 1s (389 kB/s)
Selecting previously unselected package libboost-filesystem1.71.0:amd64.
(Reading database ... 57461 files and directories currently installed.)
Preparing to unpack .../libboost-filesystem1.71.0_1.71.0-6ubuntu6_amd64.deb ...
Unpacking libboost-filesystem1.71.0:amd64 (1.71.0-6ubuntu6) ...
Selecting previously unselected package libboost-iostreams1.71.0:amd64.
Preparing to unpack .../libboost-iostreams1.71.0_1.71.0-6ubuntu6_amd64.deb ...
Unpacking libboost-iostreams1.71.0:amd64 (1.71.0-6ubuntu6) ...
Setting up libboost-filesystem1.71.0:amd64 (1.71.0-6ubuntu6) ...
Setting up libboost-iostreams1.71.0:amd64 (1.71.0-6ubuntu6) ...
Setting up freeling (4.2) ...
Processing triggers for libc-bin (2.31-0ubuntu9.2) ...

gcastilloh@PC-001:~$ sudo apt-get install libboost-regex-dev libicu-dev zlib1g-dev libboost-dev
Reading package lists... Done
Building dependency tree
Reading state information... Done
libboost-dev is already the newest version (1.71.0.0ubuntu2).
libicu-dev is already the newest version (66.1-2ubuntu2).
libboost-regex-dev is already the newest version (1.71.0.0ubuntu2).
zlib1g-dev is already the newest version (1:1.2.11.dfsg-2ubuntu1.2).
The following packages were automatically installed and are no longer required:
  libtaglibs-standard-impl-java libtaglibs-standard-spec-java
Use 'sudo apt autoremove' to remove them.
0 upgraded, 0 newly installed, 0 to remove and 66 not upgraded.

gcastilloh@PC-001:~$ sudo apt-get install libboost-system-dev libboost-program-options-dev libboost-thread-dev
Reading package lists... Done
Building dependency tree
Reading state information... Done
libboost-program-options-dev is already the newest version (1.71.0.0ubuntu2).
libboost-system-dev is already the newest version (1.71.0.0ubuntu2).
libboost-thread-dev is already the newest version (1.71.0.0ubuntu2).
The following packages were automatically installed and are no longer required:
  libtaglibs-standard-impl-java libtaglibs-standard-spec-java
Use 'sudo apt autoremove' to remove them.
0 upgraded, 0 newly installed, 0 to remove and 66 not upgraded.

gcastilloh@PC-001:~$ sudo apt --fix-broken install
Reading package lists... Done
Building dependency tree
Reading state information... Done
The following packages were automatically installed and are no longer required:
  libtaglibs-standard-impl-java libtaglibs-standard-spec-java
Use 'sudo apt autoremove' to remove them.
0 upgraded, 0 newly installed, 0 to remove and 66 not upgraded.

```


