#!/usr/bin/python

# -*- coding: utf-8 -*-

# Copyright (C) 2009-2016:
#    Frederic Mohier, frederic.mohier@gmail.com
#
# This file is part of Shinken.
#
# Shinken is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Shinken is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Shinken.  If not, see <http://www.gnu.org/licenses/>.

"""
This class is for authenticating a user with Glpi Web Service login
"""

import xmlrpclib
import traceback

from shinken.basemodule import BaseModule
from shinken.log import logger

properties = {
    'daemons': ['broker', 'webui'],
    'type': 'authentication',
    'external': False
}


# called by the plugin manager
def get_instance(plugin):
    logger.info("[Auth WS Glpi] Get a Glpi WS authentication module for plugin %s" % plugin.get_name())

    instance = WS_Glpi_Webui(plugin)
    return instance


class WS_Glpi_Webui(BaseModule):
    def __init__(self, modconf):
        BaseModule.__init__(self, modconf)

        logger.info("[Auth WS Glpi] Trying to initialize the Glpi WS authentication module")
        try:
            self.uri = getattr(modconf, 'uri', 'http://localhost/glpi/plugins/webservices/xmlrpc.php')
        except AttributeError:
            logger.error("[Auth WS Glpi] The module is missing a property, check module configuration in auth-ws-glpi.cfg")
            raise

    # Try to connect if we got true parameter
    def init(self):
        logger.info("[Auth WS Glpi] Connecting to Glpi ...")
        self.ws_connection = xmlrpclib.ServerProxy(self.uri)
        logger.info("[Auth WS Glpi] Connection opened")

    # To load the webui application
    def load(self, app):
        self.app = app

    def check_auth(self, user, password):
        # If user is not a contact, bail out ...
        c = self.app.datamgr.get_contact(user)
        if not c:
            return False

        self.session = None
        self.user_info = None
        try:
            logger.info("[Auth WS Glpi] Authenticating user: %s ..." % user)
            arg = {'login_name': user, 'login_password': password}
            result = self.ws_connection.glpi.doLogin(arg)
            self.session = result['session']

            # Get user info
            arg = {'session': self.session, 'iso8859': '1', 'id2name': '1'}
            result = self.ws_connection.glpi.getMyInfo(arg)
            self.user_info = result

            # Get user allowed entities
            # Removed: too much verbose!
            # result = self.ws_connection.glpi.listMyEntities(arg)
            # self.user_info['entities']=result

            # Get user allowed profiles
            # Removed: too much verbose!
            # result = self.ws_connection.glpi.listMyProfiles(arg)
            # self.user_info['profiles']=result

            logger.info("[Auth WS Glpi] Authenticated, session : %s, info: %s" % (self.session, self.user_info))
        except Exception:
            logger.error("[Auth WS Glpi] Authentication failed: %s." % traceback.format_exc())
            return False

        return True

    # Get the WS session identifier ...
    def get_session(self):
        logger.debug("[Auth WS Glpi] get_session")

        return self.session

    # Get the user information ...
    def get_user_info(self):
        logger.debug("[Auth WS Glpi] get_user_info")

        return self.user_info
