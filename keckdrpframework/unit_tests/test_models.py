#
# Test models package
#
# Created: 2019-09-26, skwok
#
import pytest

from keckdrpframework.models.arguments import Arguments
from keckdrpframework.models.event import Event
from keckdrpframework.models.processing_context import Processing_context
from keckdrpframework.models.data_set import Data_set

from keckdrpframework.utils.DRPF_logger import getLogger
from keckdrpframework.config.framework_config import ConfigClass
from keckdrpframework.core.queues import Simple_event_queue

import time


#
# Arguments tests
#


def test_arguments_1():
    args = Arguments (name='test', a=1, b=2, c="3")
    
    assert args.a == 1 and args.b == 2 and args.c == "3", "Arguments do not  match"


def test_arguments_2():
    args = Arguments (name='test', a=1, b=2, c="3")
    
    s = args.__str__()
    
    assert s == "name: test, a: 1, b: 2, c: 3", "Arguments str() failed"
    
#
# Processing context tests
#

@pytest.fixture
def init_context ():
    config = ConfigClass ()
    logger = getLogger (config.logger_config_file, name="DRPF")      
    eq = Simple_event_queue()
    eqhi = Simple_event_queue()
    
    # The regular event queue can be local or shared via proxy manager    
    pc = Processing_context(eq, eqhi, logger, config)
    return pc
    
def test_context_new (init_context):
    """
    Context creation
    """        
    pc = init_context
    assert pc is not None, "No context created"
    
    
#
# Data_set tests
#

@pytest.fixture
def init_data_set ():
    config = ConfigClass ()
    logger = getLogger(config.logger_config_file, name="DRPF")   
    
    data_set = Data_set ("test_files", logger, config)
    return data_set
    
def test_data_set_1 (init_data_set):
    """
    Creattion
    """      
    data_set = init_data_set   
    assert data_set is not None, "Could not create data set"
    
def test_data_set_start (init_data_set):
    data_set = init_data_set    
    data_set.start_monitor()
    
        
def test_data_set_stop (init_data_set):    
    data_set = init_data_set        
    time.sleep (2)
    data_set.stop_monitor()