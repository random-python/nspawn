<?php

class arkon extends rcube_plugin {

	public $task = '.*';
	
	function init() {

		$rcmail = rcube::get_instance();
		$output = $rcmail->output;
		$storage = $rcmail->storage;

        if ($rcmail->output->type == 'html') {
            $this->include_script('arkon.js');
            $this->include_stylesheet('arkon.css');
        }
            	
        if ($rcmail->task == 'mail') {
        	//
        }
                    	
	}
	
}

?>
