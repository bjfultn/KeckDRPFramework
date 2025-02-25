"""
Created on Jul 8, 2019

This is the base pipeline.

@author: skwok
"""

import sys
import importlib
from keckdrpframework.utils.DRPF_logger import getLogger
from keckdrpframework.models.arguments import Arguments


class Base_pipeline:
    """
    classdocs
    """

    def __init__(self):
        """
        Constructor
        """
        self.event_table0 = {
            "noop":     ("noop", None, None),
            "echo":      ("echo", "stop", None),
            "no_event": ("no_event", None, None),
            "info":     ("info", None, None),
            }
        self.logger = getLogger()

    def init_pipeline (self):
        pass
    
    def true (self, *args, **kargs):
        return True
    
    def set_logger (self, lger):
        self.logger = lger
        
    def not_found (self, name):
        """
        When no action is found, this method builds a dummy function that 
        returns a dummy arguments. 
        """

        def f (action, context, **kargs):
            return Arguments(kargs=kargs, not_found=name)

        self.logger.info(f"Action not found {name}")
        return f
    
    def _get_action_apply_method (self, klass):
        """
        Returns a function that instantiates the klass and calls apply()
        """

        def f (action, context):
            obj = klass (action, context)
            return obj.apply()

        return f
            
    def _find_import_action (self, module_name):
        """
        module_name is same as file name.
        For example: class abc is defined in primitives.abc.
        """ 
        prefixes = "primitives", "keckdrpframework", "keckdrpframework.primitives", ""
        for p in prefixes:  
            try:
                if p:
                    full_name = f"{p}.{module_name.lower()}"
                else:
                    full_name = module_name.lower()
                mod = importlib.import_module(full_name)        
                return self._get_action_apply_method(getattr (mod, module_name))  
            except Exception as e:
                pass
        raise Exception("Not found")      
    
    def _get_action (self, prefix, action):  
        """
        Returns a function for the given action name or true() if not found
        """      
        name = prefix + action
        
        try:
            # Is this name defined ?
            fn = getattr (sys.modules[self.__module__], name)
            
            # Name is defined, is it a class, convert it into a function
            if isinstance (fn, type):
                return self._get_action_apply_method(fn)
            # name is a function, return it
            return fn
        except Exception as e1:
            pass
        
        try:
            # Checks if method defined in the class
            return self.__getattribute__ (name)
        except Exception as e2:
            pass
    
        try:
            # Tries to look in the 'primitives' package
            return self._find_import_action (name)
        except Exception as e3:
            pass
        
        # Could not find the name for this action
        return None        
        
    def get_pre_action (self, action):
        f = self._get_action ("pre_", action)
        if f is None:
            return self.true
        return f
    
    def get_post_action (self, action):
        f = self._get_action ("post_", action)
        if f is None:
            return self.true
        return f
    
    def get_action (self, action):
        f = self._get_action("", action)
        if f is None:
            return self.not_found(action)
        return f
    
    def noop (self, action, context):
        self.logger.info ("NOOP action")
        
    def info (self, action, context):
        pending_events = context.event_queue.get_pending()
        self.logger.info ("Pending events " + str(pending_events))
    
    def no_more_action (self, action, context):
        self.logger.info ("No more action, terminating")
        
    def echo (self, action, context):
        """
        Test action 'echo'
        """
        self.logger.info  (f"Echo action {action}")
    
    def no_event (self, action, context):
        """
        The no_event event.
        """
        self.logger.info ("No event in queue")
        
    def _event_to_action (self, event, context):
        """
        Returns the event_info as (action, state, next_event)
        """
        noop_event = self.event_table0.get("noop")
        event_info = self.event_table0.get(event.name, noop_event)
        return event_info
    
    def event_to_action (self, event, context):
        """
        Checks the local event_table, 
        if no matching event found, then checks the table0.
        """
        event_info = self.event_table.get(event.name)
        if not event_info is None:
            return event_info
        return self._event_to_action(event, context)

