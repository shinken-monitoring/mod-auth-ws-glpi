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
import time

from shinken.basemodule import BaseModule
from shinken.log import logger

properties = {
    'daemons': ['broker', 'webui'],
    'type': 'authentication',
    'external': False
}


# called by the plugin manager
def get_instance(plugin):
    logger.info("[auth-ws-glpi] Get a Glpi WS authentication module for plugin %s" % plugin.get_name())

    instance = WS_Glpi_Webui(plugin)
    return instance


class WS_Glpi_Webui(BaseModule):
    def __init__(self, modconf):
        BaseModule.__init__(self, modconf)

        logger.info("[auth-ws-glpi] Trying to initialize the Glpi WS authentication module")
        try:
            self.uri = getattr(modconf, 'uri', 'http://localhost/glpi/plugins/webservices/xmlrpc.php')
        except AttributeError:
            logger.error("[auth-ws-glpi] The module is missing a property, check module configuration in auth-ws-glpi.cfg")
            raise

    # Try to connect if we got true parameter
    def init(self):
        logger.info("[auth-ws-glpi] Connecting to Glpi ...")
        self.ws_connection = xmlrpclib.ServerProxy(self.uri)
        logger.info("[auth-ws-glpi] Connection opened")

    # To load the webui application
    def load(self, app):
        self.app = app

    def check_auth(self, user, password):
        # If user is not a contact, bail out ...
        c = self.app.datamgr.get_contact(user)
        if not c:
            return False

        now = time.time()

        self.session = None
        self.user_info = None
        try:
            logger.info("[auth-ws-glpi] Authenticating user: %s ..." % user)
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

            logger.info("[auth-ws-glpi] Authenticated, session : %s, info: %s" % (self.session, self.user_info))
        except xmlrpclib.Fault as err:
            logger.error("[auth-ws-glpi] Authentication refused, fault code: %d (%s)", err.faultCode, err.faultString)
        except Exception:
            logger.error("[auth-ws-glpi] Authentication failed: %s." % traceback.format_exc())
        logger.info("[auth-ws-glpi] time to authenticate (%3.4fs)", time.time() - now)

        return self.session

    # Get the WS session identifier ...
    def get_session(self):
        logger.debug("[auth-ws-glpi] get_session")

        return self.session

    # Get the user information ...
    def get_user_info(self):
        logger.debug("[auth-ws-glpi] get_user_info")

        return self.user_info
