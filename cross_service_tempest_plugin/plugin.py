# Copyright 2017 Andrea Frittoli
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


import os

from tempest import config
from tempest.test_discover import plugins

from cross_service_tempest_plugin import config as cs_config


class CrossServiceTempestPlugin(plugins.TempestPlugin):
    def load_tests(self):
        base_path = os.path.split(os.path.dirname(
            os.path.abspath(__file__)))[0]
        test_dir = "cross_service_tempest_plugin/tests"
        full_test_dir = os.path.join(base_path, test_dir)
        return full_test_dir, base_path

    def register_opts(self, conf):
        conf.register_group(cs_config.cross_service_group)
        conf.register_opts(cs_config.CrossServiceGroup,
                           cs_config.cross_service_group)

    def get_opt_lists(self):
        return [
            (cs_config.cross_service_group.name,
             cs_config.CrossServiceGroup),
        ]

    def get_service_clients(self):
        # No extra service client defined by this plugin
        return []
