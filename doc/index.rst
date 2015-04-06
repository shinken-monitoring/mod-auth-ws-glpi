.. _gpli_ws_authentication_module:

===========================
Shinken GLPI authentication
===========================


This module allows Web UI users to be authenticated with user accounts from GLPI.

For people not familiar with GLPI, it is an Open-Source CMDB. Applicable to servers, routers, printers or anything you want for that matter. It is also a help-desk tool. GLPI also integrates with tools like FusionInventory for IT inventory management. Of course, GLPI also integrates with Shinken an is able to build Shinken configuration from GLPI database thanks to GLPI Monitoring plugin and Shinken import-glpi module

Requirements 
=============

The current version needs: 
 - plugin WebServices for GLPI

 See https://forge.indepnet.net to get the plugins.


Enabling module 
=============================

To use the auth-ws-glpi module you must declare it in your WebUI configuration.

::

  define module {
      module_name     webui
      ... 

      modules	..., auth-ws-glpi, ...

  }


The module configuration is defined in the file: auth-ws-glpi.cfg.

Default configuration needs to be tuned up to your Glpi configuration. 

At first, you need to activate and configure the GLPI WebServices to allow 
connection from your Shinken server.
Then you need to set the WS URI (uri) parameter in the configuration file.

Each time a user will try to log in in the Web UI, the module will try
to connect with username and password. If connection is successful the 
user will be logged in the Web UI.


Please note that a Shinken contact must exist with the same name as the 
username ! This contact may be a locally flat file contact or a contact 
fetched from Glpi thanks to import-glpi module.



It's done :)
