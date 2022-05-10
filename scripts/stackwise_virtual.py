'''
ls.py

'''
# see https://pubhub.devnetcloud.com/media/pyats/docs/aetest/index.html
# for documentation on pyATS test scripts

# optional author information
# (update below with your contact information if needed)
__author__ = 'Cisco Systems Inc.'
__copyright__ = 'Copyright (c) 2019, Cisco Systems Inc.'
__contact__ = ['pawansi@cisco.com']
__credits__ = ['list', 'of', 'credit']
__version__ = 1.0

import logging
from pyats import aetest
# create a logger for this module
Logger = logging.getLogger(__name__)
from svlservices.svlservice import StackWiseVirtual
from pyats.aetest.steps import Steps

class CommonSetup(aetest.CommonSetup):
    @aetest.subsection
    def commonsetup_initialize_testbed(self, testbed):
        '''
            Establishes connection to all your testbed devices.
        '''
        # make sure testbed is provided
        assert testbed, 'Testbed is not provided!'

        #initilize StackWiseVirtual Class
        svl_handle = StackWiseVirtual(testbed)
        Logger.info(svl_handle)
        self.parent.parameters['svl_handle'] = svl_handle

class svlformation_and_validation(aetest.Testcase):
    '''svlformation
        The Testcase configure the Stackwise Virtual conifg on two switches provided in the testbed yaml.
    '''

    # testcase groups (uncomment to use)
    # groups = []

    @aetest.setup
    def setup_make_svl_pairs_from_testbed_input(self,svl_handle):
        '''
            This is to make SVL logical pair for further tests from testbed yaml inputfile.
        '''
        svl_handle.get_device_pairs()

    @aetest.test
    def test_pre_check_stackwise_virtual_links(self,svl_handle):
        '''
            This is precheck on links of the Stackwise virtual to see if both switches links are provided. 
        '''
        steps = Steps()
        result=True
        for stackpair in svl_handle.device_pair_list:
            with steps.start("Link Precheck",continue_= True) as step:
                if not svl_handle.check_links(stackpair):
                    Logger.error("The devices provided to be paired into SVL does not have any links connected to each others")
                    result=False
                    step.failed("The Prechecks failed. Fix Links before script run", goto = ['CommonCleanup'])
        if not result:
            self.failed("Precheck for links correctness failed on some of the Stackwise Virtual Pairs")

    @aetest.test
    def test_validate_console_connectivity_to_switches(self,svl_handle):
        '''
            This is a precheck test to check if connesol connectivity is established with the devices.
            If the console connectivity is not reached, script will not proceed further. User should fix console inputs and rerun.
        '''
        steps = Steps()
        result=True
        for stackpair in svl_handle.device_pair_list:
            with steps.start("Validation of console connectivity on Stackwise Virtual device pairs",continue_= True) as step:
                if not svl_handle.connect_to_stackpair(stackpair):
                    result=False
                    step.failed("Could not connect to devices, Can not proceed. for stackwise virtual pair :{}".format(stackpair))
        if not result:
            self.failed("Console connectivity to some or all of the devices could not  be established", goto = ['CommonCleanup'])

    @aetest.test
    def test_preches_validate_platform_and_version_match_and_minimum_version_req(self,svl_handle):
        '''
            This is a precheck test to validate:
            1. If the switches have the minimum version supported for Stackwise Virtual.
            2. If the platform type of the two switches part of stackwise Virtual are same.
            3. If the Software version of both switches are same. 
        '''
        steps = Steps()
        result=True
        for stackpair in svl_handle.device_pair_list:
            with steps.start("Platform and Version req precheck",continue_= True) as step:
                if not svl_handle.check_min_version_req(stackpair):
                    result=False
                    step.failed("Minimum Version and platform pre-check failed ", goto = ['CommonCleanup'])
        if not result:
            self.failed("Minimum Version and Platform check failed.", goto = ['CommonCleanup'])

    @aetest.test
    def test_configure_stackwise_virtual_configs_bringup_stackwiseVirtual(self,svl_handle):
        '''
            This is main test to perform confis for switches and reload step by step to form the stack wise virtual.
            1. Step1: Configure Switch number, Switch prioeiry, Stackwise Virtual Domain id and Stackwise Virtual global config.
            2. Step2: Save the configs on both switches and reload for configs to apply.
            3. Step3: Configure Stackwise virtual links config, links are provided in testbed yaml in topology section each 
                link should have STACKWISEVIRTUAL-LINK in the link name to be used for stackwise virtual link configs. 
            4. Step4: Save the configs on both switches and reload for configs to apply.
            5. Step5: Configure the Dual Active Detection (DAD) links as provided in the testbed yaml under topology section. 
                Each DAD link should have DAD-LINK in the link name to be configured as Dual Active detection link.
            6. Step6: Save the configs on both switches and reload for configs to apply.
        '''
        steps = Steps()
        result=True
        for stackpair in svl_handle.device_pair_list:
            with steps.start("Stackwise Virtual config") as step:
                if not svl_handle.configure_svl_step1(stackpair):
                    result=False
                    step.failed("Step1 Configure the step 1 config, switch number and domain configs on switches, failed")

                if not svl_handle.save_config_and_reload(stackpair):
                    result=False
                    step.failed("Step2 Save config and reload the switches, failed")

                if not svl_handle.configure_svl_step2_svllinkconfig(stackpair):
                    result=False
                    step.failed("Step3 Config stackwise Virtual links on switches, failed.")

                if not svl_handle.save_config_and_reload(stackpair):
                    result=False
                    step.failed("Step4 Save config and reload the switches, failed.")

                if not svl_handle.configure_svl_step3_dad_linkconfig(stackpair):
                    result=False
                    step.failed("Step5 Configuring stackwise Virtual Dual Active Detection Links, failed.")

                if not svl_handle.save_config_and_reload(stackpair):
                    result=False
                    step.failed("Step6 Save config and reload the switches, failed.")
        if not result:
            self.failed("Stackwise Virtual configuration failed on one or more switches. ")
        else:
            self.passed("Stackwise Virtual configurations are success.")

    @aetest.test
    def test_validate_configs_for_stackwise_virtual_pair(self,svl_handle):
        '''
            Validate configs for Stackwise Virtual Pair switches.
        '''
        result=True
        steps = Steps()
        for stackpair in svl_handle.device_pair_list:
            with steps.start("Validation of Stackwise Virtual configs",continue_= True) as step:
                if not svl_handle.check_stackwise_virtual_confgured(stackpair):
                    result=False
                    step.failed("Stackwise Virtual configs are still present on one or both of the switches of stackpair: {}".format(stackpair))
        if not result:
            self.failed("Stackwise virtual configs are not present on the switches")
        else:
            self.passed("Stackwise Virtual configuration are present on both switches as expected.")

    @aetest.test
    def test_configure_stackwise_virtual_configs_and_validate(self,svl_handle):
        '''
            Validate the 
        '''
        for stackpair in svl_handle.device_pair_list:            
            if not svl_handle.validate_stackwise_SVL_and_DAD_links_status(stackpair):
                self.failed("Stackwise Virtual link status validation failed for stack pair: {}".format(stackpair))
            else:
                Logger.info("Stackwise Virtual link status validation is success for stackpair: {}".format(stackpair))
    
class CommonCleanup(aetest.CommonCleanup):
    '''CommonCleanup Section

    < common cleanup docstring >

    '''

    # uncomment to add new subsections
    # @aetest.subsection
    # def subsection_cleanup_one(self):
    #     pass

if __name__ == '__main__':
    # for stand-alone execution
    import argparse
    from pyats import topology

    parser = argparse.ArgumentParser(description = "standalone parser")
    parser.add_argument('--testbed', dest = 'testbed',
                        help = 'testbed YAML file',
                        type = topology.loader.load,
                        default = None)

    # do the parsing
    args = parser.parse_known_args()[0]

    aetest.main(testbed = args.testbed)

