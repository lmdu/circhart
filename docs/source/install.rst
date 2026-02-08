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

	chmod +x Circhart-vx.x.x-linux-x64.AppImage
	./Circhart-vx.x.x-linux-x64.AppImage

On MacOS
--------

#. Go to `https://github.com/lmdu/circhart/releases <https://github.com/lmdu/circhart/releases>`_ page. For intel CPU, you should click on ``Circhart-vx.x.x-macos-x64.dmg`` to download it. For Apple M-series CPU, you should click on ``Circhart-vx.x.x-macos-arm64.dmg`` to download it

#. Double click the downloaded dmg file, and then drag circhart to your application folder to install.

	.. figure:: _static/macins1.png
		:width: 500
		:align: center

#. When you run Circhart for the first time, you will see a prompt dialog, click the **Done** button.

	.. figure:: _static/macins2.png
		:width: 300
		:align: center

#. To allow Circhart to run on your Mac, go to **System Settings** > **Privacy & Security**.

	.. figure:: _static/macins3.png
		:width: 500
		:align: center

#. Scroll to **Security** section, you will see "Circhart" was blocked to protect you Mac. Click **Open Anyway**.

	.. figure:: _static/macins4.png
		:width: 500
		:align: center

#. Then, you will see a prompt dialog, click the **Open Anyway** button.

	.. figure:: _static/macins5.png
		:width: 300
		:align: center

#. Finally, you will be prompted to enter your password. The Circhart will be run successfully.

	.. figure:: _static/macins6.png
		:width: 500
		:align: center


Circos dependencies
-------------------

If you draw circos plots on Linux and MacOS, you must install missing perl modules needed by circos.

.. note::

	**On Windows, circos can run without any dependency, just ignore this step**. 

#. Go to **Tools** menu, click **Check Circos Dependencies** to open a dialog, where you can see the missing perl modules.

	.. figure:: _static/perlmodules.png
		:width: 400
		:align: center

#. You can view the cpan documentation for finding `How to install CPAN modules <https://www.cpan.org/modules/INSTALL.html>`_.

#. First, install ``cpanm`` to make installing other modules easier. Open the Linux or MacOS terminal and type the command:

	.. code:: shell

		cpan App::cpanminus

#. Now you can install the missing modules using command ``cpanm``, for example:

	.. code:: shell

		cpanm Config::General

#. When module successfully installed, you can click the **Refresh** button on dialog to view module status.

#. When status of all Perl modules displays ok, you can run Circhart to draw circos plots.
