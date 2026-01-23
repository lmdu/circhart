Installation
============

Circhart is a standalone desktop software designed to run on Windows, Linux and MacOS.

Circhart download: `https://github.com/lmdu/circhart/releases <https://github.com/lmdu/circhart/releases>`_

中国镜像下载地址: `https://big.cdu.edu.cn/software/circhart <https://big.cdu.edu.cn/software/circhart>`_

On Windows
----------

Go to `https://github.com/lmdu/circhart/releases <https://github.com/lmdu/circhart/releases>`_ page, click on ``Circhart-vx.x.x-win-x64.exe`` to download it. Then double click the downloaded installer to install the program following the on-screen instructions.

On Linux
--------

#. Go to `https://github.com/lmdu/circhart/releases <https://github.com/lmdu/circhart/releases>`_ page, click on ``Circhart-vx.x.x-linux-x64.AppImage`` to download it. You can double click the .AppImage file to run it.

#. Or, you can run it in terminal like this:

.. code:: shell

	./Circhart-vx.x.x-linux-x64.AppImage

On MacOS
--------

#. Go to `https://github.com/lmdu/circhart/releases <https://github.com/lmdu/circhart/releases>`_ page. For intel CPU, you should click on ``Circhart-vx.x.x-macos-x64.dmg`` to download it. For Apple  M-series CPU, you should click on ``Circhart-vx.x.x-macos-arm64.dmg`` to download it

#. Double click the downloaded dmg file, and then drag circhart to your application folder to install.

#. To allow Circhart to run on your Mac, go to **System Settings** > **Privacy & Security**, find the prompt to open the app, click **Open Anyway**, and confirm with your password.


Circos dependencies
-------------------

On Windows, circos can run without any dependency, just ignore this step. If you draw circos plots on Linux and MacOS, you must install missing perl modules needed by circos.

#. Go to **Tools** menu, click **Check Circos Dependencies** to open a dialog, where you can see the missing perl modules.

#. You can view the cpan documentation for finding `How to install CPAN modules <https://www.cpan.org/modules/INSTALL.html>`_.

#. First, install ``cpanm`` to make installing other modules easier. Open the Linux or MacOS terminal and type the command:

.. code:: shell

	cpan App::cpanminus

#. Now you can install the missing modules using command ``cpanm``, for example:

.. code:: shell

	cpanm Config::General

#. When module successfully installed, you can click the **Refresh** button on dialog to view module status.
