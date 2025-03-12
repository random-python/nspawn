//

function arkon_init_ks_ng_actions() {
	if (window.ks_ng_actions) {

		ks_ng_actions.arkon_markasjunk = function(context, rcmailobj, windowobj) {
			rcmailobj.command('plugin.markasjunk');
			return false;
		}

		ks_ng_actions.arkon_firstmessage = function(context, rcmailobj,
				windowobj) {
			rcmailobj.command('firstmessage');
			return false;
		}

		ks_ng_actions.arkon_lastmessage = function(context, rcmailobj,
				windowobj) {
			rcmailobj.command('lastmessage');
			return false;
		}
		
		//

		ks_ng_actions.arkon_contact_create = function(context, rcmailobj,
				windowobj) {
			var command = 'plugin.contextmenu_folder.contact_create';
			rcmailobj.command(command);
			return false;
		}

		ks_ng_actions.arkon_folder_create = function(context, rcmailobj,
				windowobj) {
			var command = 'plugin.contextmenu_folder.folder_create';
			rcmailobj.command(command);
			return false;
		}

		ks_ng_actions.arkon_folder_delete = function(context, rcmailobj,
				windowobj) {
			var command = 'plugin.contextmenu_folder.folder_delete';
			rcmailobj.command(command);
			return false;
		}

		ks_ng_actions.arkon_folder_rename = function(context, rcmailobj,
				windowobj) {
			var command = 'plugin.contextmenu_folder.folder_rename';
			rcmailobj.command(command);
			return false;
		}

		ks_ng_actions.arkon_folder_locate = function(context, rcmailobj,
				windowobj) {
			var command = 'plugin.contextmenu_folder.folder_locate';
			rcmailobj.command(command);
			return false;
		}

		ks_ng_actions.arkon_readfolder = function(context, rcmailobj, windowobj) {
			var command = 'plugin.contextmenu_folder.folder_tree_read';
			rcmailobj.command(command);
			return false;
		}
		
		//
		
		ks_ng_actions.arkon_message_copy = function(context, rcmailobj, windowobj) {
			var command = 'plugin.contextmenu_folder.message_transfer';
			rcmailobj.command(command);
			return false;
		}


		ks_ng_actions.arkon_message_move = function(context, rcmailobj, windowobj) {
			var command = 'plugin.contextmenu_folder.message_transfer';
			rcmailobj.command(command);
			return false;
		}


	} else {

		console.log('arkon: ks_ng_actions: failed to init');

	}

}

function arkon_init_message_part_frame() {
	var frame = $('#messagepartframe');
	var style = "<style type='text/css'> img { max-width:100%; max-height:100%; } </style>";
	frame.load(function() {
		var head = frame.contents().find('head');
		head.append($(style));
	});
}

function arkon_init_topline() {
	console.log('topline: ' + $('#topline').length);
	$('#topline').empty();
	$('#topline').remove();
	console.log('topline: ' + $('#topline').length);
}

// ###

$(document).ready(function() {
	// arkon_init_topline();
});

if (window.rcmail) {

	rcmail.addEventListener('init', function(param) {

		// arkon_init_ks_ng_actions();

		arkon_init_message_part_frame();

	});

}
